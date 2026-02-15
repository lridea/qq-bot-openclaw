#!/bin/bash

echo "================================"
echo "  QQ Bot - OpenClaw"
echo "  正在启动机器人..."
echo "================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未检测到 Python3"
    echo "请先安装 Python 3.8 或更高版本"
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -f "venv/bin/python" ]; then
    echo "📦 未检测到虚拟环境，正在创建..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 创建虚拟环境失败"
        exit 1
    fi
    echo "✅ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 检查依赖是否安装
if ! pip show nonebot2 &> /dev/null; then
    echo "📥 正在安装依赖..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 安装依赖失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
fi

# 检查 .env 文件是否存在
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 配置文件"
    echo "正在创建默认配置..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件"
    echo ""
    echo "⚠️  请编辑 .env 文件，填写正确的配置："
    echo "   - OPENCLAW_API_URL"
    echo "   - OPENCLAW_API_KEY"
    echo "   - SUPERUSERS"
    echo ""
    exit 0
fi

# 启动机器人
echo ""
echo "================================"
echo "  正在启动机器人..."
echo "  按 Ctrl+C 停止"
echo "================================"
echo ""

python3 bot.py

# 如果机器人退出
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 机器人启动失败"
fi
