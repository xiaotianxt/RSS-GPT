# RSS-GPT

一个干净、高效的 RSS 聚合和 AI 摘要生成工具。

## 这是什么？

这是对原始 RSS-GPT 项目的完全重写和改进版本。代码已经重构，提高了可维护性、性能和仓库结构的清晰度。

使用 GitHub Actions 定期运行 Python 脚本：调用 OpenAI API 为 RSS 订阅源生成摘要，并将生成的内容推送到单独的内容分支。配置简单，无需服务器。

### 主要改进

- **干净的仓库结构**：生成的内容存储在单独的 `content-branch` 中，保持主分支干净并专注于代码
- **改进的工作流**：添加了清理工作流，防止主分支中出现数千个不必要的提交
- **重构的代码库**：完全重写，具有更好的代码组织、类型提示和错误处理
- **增强的性能**：并行处理 RSS 订阅源，提高执行速度
- **更好的日志系统**：全面的日志系统，便于调试和监控

![RSS-GPT 示例](https://i.imgur.com/7darABv.jpg)

## 功能

- 使用 AI 模型（支持最新的 GPT-4o 模型）总结 RSS 订阅源，将摘要附加到原始文章中
- 支持自定义摘要长度和目标语言
- 聚合多个 RSS 订阅源，去除重复文章，用单一地址订阅
- 为 RSS 订阅源添加基于包含/排除规则和正则表达式的过滤器
- 在 GitHub Pages 上托管 RSS 订阅源，保持仓库历史干净

## 快速设置指南

1. Fork 这个仓库
2. 添加仓库 Secrets
   - `U_NAME`：你的 GitHub 用户名
   - `U_EMAIL`：你的 GitHub 邮箱
   - `WORK_TOKEN`：你的 GitHub 个人访问令牌，需要有 `repo` 和 `workflow` 权限
   - `OPENAI_API_KEY`：（可选）仅在使用 AI 摘要功能时需要
3. 在仓库设置中启用 GitHub Pages：
   - 选择从分支部署
   - 选择 `content-branch`（不是 main）
   - 设置目录为 `/docs`
4. 在 `config.ini` 中配置你的 RSS 订阅源

## 配置

编辑 `config.ini` 文件添加你的 RSS 订阅源：

```ini
[cfg]
base = "docs/"
language = "zh"  # 摘要的目标语言
keyword_length = "5"
summary_length = "200"

[source001]
name = "example-feed"
url = "https://example.com/feed.xml"
max_items = "10"
filter_apply = "title"  # 可选：应用过滤器到标题
filter_type = "exclude"  # 可选：排除或包含
filter_rule = "keyword1|keyword2"  # 可选：正则表达式模式
```

## 高级功能

### 自定义 OpenAI 模型

你可以通过在 GitHub 仓库 secrets 中设置 `CUSTOM_MODEL` 环境变量来指定你偏好的 OpenAI 模型。

### 过滤选项

- `filter_apply`：应用过滤器的位置（标题、描述或两者）
- `filter_type`：是包含还是排除匹配的条目
- `filter_rule`：用于匹配的正则表达式模式

## 贡献

欢迎贡献！随时提交问题和拉取请求。

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件。
