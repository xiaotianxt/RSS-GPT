import feedparser
import configparser
import os
import httpx
from openai import OpenAI
from jinja2 import Template
from bs4 import BeautifulSoup
import re
import datetime
import requests
from fake_useragent import UserAgent
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Any, Optional
from pathlib import Path
import concurrent.futures

# 全局常量
MAX_ENTRIES = 10
MAX_CONCURRENT_REQUESTS = 10
REQUEST_TIMEOUT = 10

# 设置基本日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("RSS-GPT")

def setup_feed_logger(base_dir: str, feed_name: str):
    """为特定feed设置文件日志处理器"""
    log_file = os.path.join(base_dir, f"{feed_name}.log")
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=1024*1024,  # 1MB
        backupCount=3        # 保留3个备份
    )
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    return file_handler

def load_config(config_path: str = 'config.ini'):
    """加载配置文件和环境变量"""
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(config_path)
    
    # 创建配置字典
    cfg = {
        # 环境变量
        'openai_api_key': os.environ.get('OPENAI_API_KEY'),
        'username': os.environ.get('U_NAME'),
        'openai_proxy': os.environ.get('OPENAI_PROXY'),
        'openai_base_url': os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
        'custom_model': os.environ.get('CUSTOM_MODEL'),
        
        # 配置文件值
        'base_dir': config.get('cfg', 'BASE', fallback='').strip('"'),
        'keyword_length': int(config.get('cfg', 'keyword_length', fallback='5').strip('"')),
        'summary_length': int(config.get('cfg', 'summary_length', fallback='200').strip('"')),
        'language': config.get('cfg', 'language', fallback='en').strip('"'),
    }
    
    # 派生值
    cfg['deployment_url'] = f'https://{cfg["username"]}.github.io/RSS-GPT/' if cfg['username'] else ''
    
    # 获取启用的部分
    sections = config.sections()[1:] if len(config.sections()) > 1 else []
    cfg['sections'] = [section for section in sections if not config.has_option(section, 'disabled')]
    
    # 存储原始配置对象以便后续访问
    cfg['config'] = config
    
    # 创建基本目录
    Path(cfg['base_dir']).mkdir(exist_ok=True)
    
    return cfg

def fetch_feed(url: str):
    """获取RSS feed"""
    try:
        ua = UserAgent()
        headers = {'User-Agent': ua.random.strip()}
        
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            feed = feedparser.parse(response.text)
            logger.info(f"获取成功: {url}")
            return {'feed': feed, 'status': 'success'}
        else:
            logger.error(f"获取失败: HTTP {response.status_code} - {url}")
            return {'feed': None, 'status': response.status_code}
    except requests.RequestException as e:
        logger.error(f"获取失败: {str(e)} - {url}")
        return {'feed': None, 'status': 'failed'}

def clean_html(html_content: str) -> str:
    """清理HTML内容"""
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in ('script', 'style', 'img', 'a', 'video', 'audio', 'iframe', 'input'):
        for element in soup.find_all(tag):
            element.decompose()
    return soup.get_text()

def create_openai_client(cfg):
    """创建OpenAI客户端"""
    if not cfg['openai_api_key']:
        logger.warning("未找到OpenAI API密钥，将跳过摘要生成")
        return None
    
    client_args = {
        'api_key': cfg['openai_api_key'],
        'base_url': cfg['openai_base_url'],
    }
    
    if cfg['openai_proxy']:
        client_args['http_client'] = httpx.Client(proxy=cfg['openai_proxy'])
    
    return OpenAI(**client_args)

def create_summary_messages(text: str, cfg):
    """创建摘要提示消息"""
    if cfg['language'] == "zh":
        return [
            {"role": "user", "content": text},
            {"role": "assistant", "content": (
                f"请用中文总结这篇文章，先提取出{cfg['keyword_length']}个关键词，"
                f"在同一行内输出，然后换行，用中文在{cfg['summary_length']}字内写一个流畅自然的总结，"
                f"以连贯的段落形式呈现，避免使用编号列表，使用自然的语言过渡，"
                f"并按照以下格式输出'<br><br>总结:'，<br>是HTML的换行符，"
                f"输出时必须保留2个，并且必须在'总结:'二字之前"
            )}
        ]
    else:
        return [
            {"role": "user", "content": text},
            {"role": "assistant", "content": (
                f"Please summarize this article in {cfg['language']} language. "
                f"First, extract {cfg['keyword_length']} keywords and present them on a single line. "
                f"Then, write a natural, flowing summary of approximately {cfg['summary_length']} words "
                f"in {cfg['language']}. Present the summary as a cohesive paragraph rather than numbered points. "
                f"Use natural transitions between ideas and avoid numbered lists. "
                f"Format the output with '<br><br>Summary:' where <br> is the HTML line break. "
                f"The two <br> tags must appear directly before the word 'Summary:'"
            )}
        ]

def generate_summary(text: str, cfg, openai_client, model: str) -> Optional[str]:
    """使用OpenAI生成摘要"""
    if not openai_client:
        return None
    
    try:
        messages = create_summary_messages(text, cfg)
        completion = openai_client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"摘要生成失败: {str(e)}")
        return None

def filter_entry(entry, filter_apply, filter_type, filter_rule):
    """根据规则过滤条目"""
    # 如果没有配置过滤器，包括所有条目
    if not filter_apply or not filter_type or not filter_rule:
        return True
    
    # 获取要应用过滤器的文本
    if filter_apply == 'title':
        text = entry.title
    elif filter_apply == 'article':
        text = entry.article
    elif filter_apply == 'link':
        text = entry.link
    else:
        logger.warning(f"不支持的filter_apply: {filter_apply}")
        return True
    
    # 应用过滤器
    if filter_type == 'include':
        return bool(re.search(filter_rule, text))
    elif filter_type == 'exclude':
        return not bool(re.search(filter_rule, text))
    elif filter_type == 'regex match':
        return bool(re.search(filter_rule, text))
    elif filter_type == 'regex not match':
        return not bool(re.search(filter_rule, text))
    else:
        logger.warning(f"不支持的filter_type: {filter_type}")
        return True

def generate_untitled(entry):
    """为没有标题的条目生成标题"""
    try: 
        return entry.title
    except AttributeError: 
        try: 
            return entry.article[:50]
        except (AttributeError, IndexError): 
            return entry.link

def read_existing_entries(cfg, section):
    """读取现有的RSS条目"""
    section_name = cfg['config'].get(section, 'name', fallback='').strip('"')
    out_dir = os.path.join(cfg['base_dir'], section_name)
    try:
        with open(f"{out_dir}.xml", 'r') as f:
            rss = f.read()
        feed = feedparser.parse(rss)
        return feed.entries
    except (FileNotFoundError, IOError):
        logger.info(f"未找到{section}的现有feed文件")
        return []

def process_feed_entries(feed, existing_entries, filter_apply, filter_type, filter_rule, max_items, cfg, openai_client):
    """处理feed中的条目"""
    append_entries = []
    cnt = 0
    
    for entry in feed.entries:
        # 如果达到最大条目数，跳过
        if cnt >= MAX_ENTRIES:
            logger.info(f"跳过: [{entry.title}]({entry.link})")
            break
        
        # 清理v2ex链接
        if '#replay' in entry.link and 'v2ex' in entry.link:
            entry.link = entry.link.split('#')[0]
        
        # 如果条目已存在，跳过
        if entry.link in [x.link for x in existing_entries] or entry.link in [x.link for x in append_entries]:
            continue
        
        # 生成标题（如果缺失）
        entry.title = generate_untitled(entry)
        
        # 获取文章内容
        try:
            entry.article = entry.content[0].value
        except (AttributeError, IndexError):
            try: 
                entry.article = entry.description
            except AttributeError: 
                entry.article = entry.title
        
        # 清理HTML内容
        cleaned_article = clean_html(entry.article)
        
        # 应用过滤器
        if not filter_entry(entry, filter_apply, filter_type, filter_rule):
            logger.info(f"过滤: [{entry.title}]({entry.link})")
            continue
        
        # 增加计数器并生成摘要
        cnt += 1
        if cnt > max_items or not cfg['openai_api_key']:
            entry.summary = None
        else:
            # 尝试使用自定义模型
            if cfg['custom_model']:
                try:
                    entry.summary = generate_summary(cleaned_article, cfg, openai_client, cfg['custom_model'])
                    logger.info(f"使用{cfg['custom_model']}生成摘要，文本长度: {len(cleaned_article)}")
                    append_entries.append(entry)
                    logger.info(f"添加: [{entry.title}]({entry.link})")
                    continue
                except Exception as e:
                    logger.warning(f"自定义模型摘要生成失败: {str(e)}")
            
            # 尝试使用gpt-4o-mini，然后回退到gpt-4o
            try:
                entry.summary = generate_summary(cleaned_article, cfg, openai_client, "gpt-4o-mini")
                logger.info(f"使用gpt-4o-mini生成摘要，文本长度: {len(cleaned_article)}")
            except Exception:
                try:
                    entry.summary = generate_summary(cleaned_article, cfg, openai_client, "gpt-4o")
                    logger.info(f"使用GPT-4o生成摘要，文本长度: {len(cleaned_article)}")
                except Exception as e:
                    entry.summary = None
                    logger.error(f"摘要生成失败，将添加原始文章: {str(e)}")
        
        # 添加条目到追加列表
        append_entries.append(entry)
        logger.info(f"添加: [{entry.title}]({entry.link})")
    
    return append_entries

def generate_output_xml(feed, append_entries, existing_entries, out_dir):
    """生成输出XML文件"""
    try:
        with open('template.xml') as f:
            template_content = f.read()
        
        template = Template(template_content)
        rss = template.render(
            feed=feed, 
            append_entries=append_entries, 
            existing_entries=existing_entries[:MAX_ENTRIES]  # 限制条目数量
        )
        
        with open(f"{out_dir}.xml", 'w') as f:
            f.write(rss)
        
        logger.info(f'完成: {datetime.datetime.now()}')
        return True
    except Exception as e:
        logger.error(f"为{out_dir}渲染XML时出错: {str(e)}")
        return False

def process_single_feed(section, cfg, openai_client):
    """处理单个feed部分"""
    config = cfg['config']
    section_name = config.get(section, 'name', fallback='').strip('"')
    out_dir = os.path.join(cfg['base_dir'], section_name)
    
    # 为此feed添加临时文件处理器
    file_handler = setup_feed_logger(cfg['base_dir'], section_name)
    logger.addHandler(file_handler)
    
    try:
        # 获取feed配置
        rss_urls = config.get(section, 'url', fallback='').strip('"').split(',')
        filter_apply = config.get(section, 'filter_apply', fallback='').strip('"')
        filter_type = config.get(section, 'filter_type', fallback='').strip('"')
        filter_rule = config.get(section, 'filter_rule', fallback='').strip('"')
        
        # 验证过滤器配置
        if any([filter_apply, filter_type, filter_rule]) and not all([filter_apply, filter_type, filter_rule]):
            logger.error(f"部分{section}: filter_apply, type, rule必须一起设置")
            return {"url": "", "name": section_name}
        
        # 获取要摘要的最大项目数
        max_items = int(config.get(section, 'max_items', fallback='0').strip('"'))
        
        # 处理现有条目
        existing_entries = read_existing_entries(cfg, section)
        logger.info('------------------------------------------------------')
        logger.info(f'开始: {datetime.datetime.now()}')
        logger.info(f'现有条目: {len(existing_entries)}')
        
        append_entries = []
        last_feed = None
        
        # 处理feed中的每个URL
        for rss_url in rss_urls:
            rss_url = rss_url.strip()
            if not rss_url:
                continue
                
            logger.info(f"获取: {rss_url}")
            
            result = fetch_feed(rss_url)
            feed = result['feed']
            if not feed:
                continue
            
            last_feed = feed
            new_entries = process_feed_entries(
                feed, existing_entries + append_entries, 
                filter_apply, filter_type, filter_rule,
                max_items, cfg, openai_client
            )
            append_entries.extend(new_entries)
        
        # 记录结果
        logger.info(f'添加条目: {len(append_entries)}')
        
        # 生成输出XML
        if last_feed and append_entries:
            generate_output_xml(last_feed, append_entries, existing_entries, out_dir)
        
        # 返回feed信息以生成索引
        return {
            "url": config.get(section, 'url', fallback='').strip('"').replace(',', '<br>'),
            "name": section_name
        }
    finally:
        # 移除feed文件处理器以避免重复日志
        logger.removeHandler(file_handler)

def update_readme_files(links, cfg):
    """更新README文件"""
    for readme_file in ["README.md", "README-zh.md"]:
        try:
            # 读取现有README
            try:
                with open(readme_file, 'r') as f:
                    readme_lines = f.readlines()
            except FileNotFoundError:
                logger.warning(f"未找到{readme_file}，将创建新文件")
                readme_lines = []
            
            # 移除现有feed链接
            while readme_lines and (readme_lines[-1].startswith('- ') or readme_lines[-1] == '\n'):
                readme_lines = readme_lines[:-1]
            
            # 添加新的feed链接
            if readme_lines and not readme_lines[-1].endswith('\n'):
                readme_lines.append('\n')
            else:
                readme_lines.append('\n')
            readme_lines.extend(links)
            
            # 写回README
            with open(readme_file, 'w') as f:
                f.writelines(readme_lines)
                
            logger.info(f"已更新{readme_file}")
        except Exception as e:
            logger.error(f"更新{readme_file}时出错: {str(e)}")

def generate_index_html(feeds, cfg):
    """生成GitHub Pages的index.html"""
    try:
        with open('template.html') as f:
            template_content = f.read()
        
        template = Template(template_content)
        html = template.render(
            update_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            feeds=feeds
        )
        
        with open(os.path.join(cfg['base_dir'], 'index.html'), 'w') as f:
            f.write(html)
            
        logger.info("已生成index.html")
    except Exception as e:
        logger.error(f"生成index.html时出错: {str(e)}")

def process_all_feeds(cfg):
    """并行处理所有feeds"""
    feeds = []
    links = []
    
    # 创建OpenAI客户端
    openai_client = create_openai_client(cfg)
    
    # 并行处理feeds以提高性能
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
        future_to_section = {
            executor.submit(process_single_feed, section, cfg, openai_client): section 
            for section in cfg['sections']
        }
        
        for future in concurrent.futures.as_completed(future_to_section):
            section = future_to_section[future]
            try:
                feed = future.result()
                if feed and feed["name"]:
                    feeds.append(feed)
                    
                    # 为README创建链接
                    url = cfg['config'].get(section, 'url', fallback='').strip('"').replace(',', ', ')
                    name = feed['name']
                    links.append(f"- {url} -> {cfg['deployment_url']}{name}.xml\n")
            except Exception as e:
                logger.error(f"处理部分{section}时出错: {str(e)}")
    
    # 更新README文件
    update_readme_files(links, cfg)
    
    # 生成index.html
    generate_index_html(feeds, cfg)

def main():
    """主入口点"""
    try:
        # 加载配置
        cfg = load_config()
        
        # 处理所有feeds
        process_all_feeds(cfg)
        
        logger.info("所有处理完成")
    except Exception as e:
        logger.error(f"未处理的异常: {str(e)}")
        raise

if __name__ == "__main__":
    main()
