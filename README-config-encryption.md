# 配置文件加密说明

为了更好地保护敏感配置信息，本项目提供了一套基于密码的配置文件加密解密方案。这样可以安全地将加密后的配置文件提交到代码仓库，同时在GitHub Actions中使用密钥进行解密。

## 工具说明

项目包含以下与配置加密相关的文件：

1. `crypto_utils.py` - 配置文件加密解密工具
2. `pre-commit-hook.sh` - Git pre-commit钩子，自动加密配置文件
3. `install-hooks.sh` - 安装Git钩子的脚本

## 本地使用指南

### 安装步骤

1. 首先安装依赖：
   ```bash
   pip install cryptography
   ```

2. 执行钩子安装脚本：
   ```bash
   chmod +x install-hooks.sh
   ./install-hooks.sh
   ```

3. 设置加密密码环境变量：
   ```bash
   export CONFIG_ENCRYPT_PASSWORD='your_secret_password'
   ```

### 日常使用

安装钩子后，每当修改并提交 `config.ini` 文件时：

1. 系统自动加密 `config.ini` 生成 `config.ini.enc`
2. 自动将 `config.ini.enc` 添加到提交
3. 原始的 `config.ini` 文件不会被提交（已在 `.gitignore` 中设置）

### 手动加密/解密

如果需要手动加密或解密配置文件，可以使用命令：

- 加密：
  ```bash
  python crypto_utils.py config.ini -op encrypt -p your_password
  ```

- 解密：
  ```bash
  python crypto_utils.py config.ini.enc -op decrypt -p your_password
  ```

## GitHub Actions 配置

在GitHub仓库中，需要设置以下密钥：

1. 在仓库的Settings > Secrets > Actions中添加 `CONFIG_PASSWORD` 密钥
2. 设置值为与本地加密使用的相同密码

这样，GitHub Actions 工作流将能够在运行时解密配置文件：

```yaml
- name: Decrypt configuration file
  run: |
    python crypto_utils.py config.ini.enc -op decrypt -p ${{ secrets.CONFIG_PASSWORD }}
  env:
    CONFIG_PASSWORD: ${{ secrets.CONFIG_PASSWORD }}
```

## 注意事项

1. 请妥善保管加密密码，一旦丢失将无法恢复加密的配置
2. 为了安全起见，不要在任何公开场合分享密码
3. 考虑使用密码管理工具存储密码
4. 确保团队成员都知道正确的密码 