#!/bin/bash

# 配置变量
CONFIG_FILE="config.ini"
ENCRYPTED_FILE="${CONFIG_FILE}.enc"
PASSWORD_ENV="CONFIG_ENCRYPT_PASSWORD"  # 从环境变量获取密码

# 检查密码是否设置
if [ -z "${!PASSWORD_ENV}" ]; then
    echo "错误: 请设置环境变量 $PASSWORD_ENV 用于加密"
    echo "例如: export $PASSWORD_ENV='your_secret_password'"
    exit 1
fi

# 检查 config.ini 是否有修改
if git diff --cached --name-only | grep -q "$CONFIG_FILE"; then
    echo "检测到 $CONFIG_FILE 更改，正在加密..."
    
    # 使用密码加密文件
    python crypto_utils.py "$CONFIG_FILE" -op encrypt -p "${!PASSWORD_ENV}"
    
    if [ $? -ne 0 ]; then
        echo "加密失败，提交已中止"
        exit 1
    fi
    
    # 将加密文件添加到暂存区
    git add "$ENCRYPTED_FILE"
    
    echo "已自动加密 $CONFIG_FILE 并将 $ENCRYPTED_FILE 添加到提交"
    
    # 可选：防止提交原始配置文件
    # 取消下面的注释以阻止原始配置文件被提交
    # git reset "$CONFIG_FILE"
    # echo "已从暂存区移除 $CONFIG_FILE"
fi

exit 0 