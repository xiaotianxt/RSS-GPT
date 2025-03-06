#!/bin/bash

HOOKS_DIR=".git/hooks"
PRE_COMMIT_HOOK="${HOOKS_DIR}/pre-commit"

# 确保钩子目录存在
mkdir -p "$HOOKS_DIR"

# 复制钩子并设置执行权限
cp pre-commit-hook.sh "$PRE_COMMIT_HOOK"
chmod +x "$PRE_COMMIT_HOOK"

echo "Git pre-commit 钩子已安装，它将自动加密 config.ini 文件"
echo "请设置环境变量 CONFIG_ENCRYPT_PASSWORD 以提供加密密码:"
echo "export CONFIG_ENCRYPT_PASSWORD='your_secret_password'" 