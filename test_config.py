#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试配置模块
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("1. 开始测试配置模块...")

try:
    from config import Config
    print("2. 成功导入 Config 类")
except Exception as e:
    print(f"2. 导入 Config 类失败: {e}")
    sys.exit(1)

try:
    config = Config()
    print("3. 成功创建 Config 实例")
except Exception as e:
    print(f"3. 创建 Config 实例失败: {e}")
    sys.exit(1)

try:
    result = config.validate_config()
    print(f"4. 成功验证配置，结果: {result}")
except Exception as e:
    print(f"4. 验证配置失败: {e}")
    sys.exit(1)

print("5. 测试完成，配置模块正常")
print(f"   API URL: {config.openclaw_api_url}")
print(f"   API Key: {config.openclaw_api_key}")
print(f"   超级管理员: {config.superusers}")
print(f"   机器人名称: {config.bot_name}")
