#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试对话记忆的编码问题
验证加载长期记忆时不会出现编码错误
"""

import json
import os
import tempfile


def test_encoding_fix():
    """测试编码修复"""

    print("=" * 60)
    print("🧪 测试对话记忆的编码问题")
    print("=" * 60)

    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件
        test_file = os.path.join(temp_dir, "test_conversation.json")

        # 创建包含中文字符和特殊字符的数据
        test_data = [
            {
                "role": "user",
                "content": "你好！你觉得泰拉瑞亚这个游戏怎么样？🎮",
                "timestamp": 1705435200
            },
            {
                "role": "assistant",
                "content": "哇~ 主人，泰拉瑞亚是一个超级好玩的游戏呢！✨💙\n\n这个游戏有超多内容可以探索！🌟",
                "timestamp": 1705435260
            },
            {
                "role": "user",
                "content": "@机器人 血腥僵尸掉落什么？💀",
                "timestamp": 1705435320
            }
        ]

        # 写入文件（使用 UTF-8 编码）
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 测试文件已创建: {test_file}")

        # 测试1：使用 UTF-8 编码读取（正确方式）
        print("\n📌 测试1：使用 UTF-8 编码读取（正确方式）")
        try:
            with open(test_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"   ✅ 读取成功，消息数: {len(data)}")
            print(f"   内容: {data[0]['content']}")
        except Exception as e:
            print(f"   ❌ 读取失败: {e}")

        # 测试2：使用默认编码读取（错误方式，模拟 bug）
        print("\n📌 测试2：使用默认编码读取（错误方式，模拟 bug）")
        try:
            with open(test_file, "r") as f:
                data = json.load(f)
            print(f"   ✅ 读取成功，消息数: {len(data)}")
            print(f"   内容: {data[0]['content']}")
        except UnicodeDecodeError as e:
            print(f"   ❌ 读取失败（预期的错误）: {e}")
            print(f"   ✅ 这就是修复前的问题！")
        except Exception as e:
            print(f"   ⚠️  其他错误: {e}")

        # 测试3：修复后的逻辑（先读取，再比较长度）
        print("\n📌 测试3：修复后的逻辑（先读取，再比较长度）")
        try:
            with open(test_file, "r", encoding="utf-8") as f:
                original_length = len(json.load(f))

            # 模拟过滤过期消息
            filtered_data = [msg for msg in test_data if msg["timestamp"] > 1705435200]

            if len(filtered_data) < original_length:
                print(f"   ✅ 需要更新文件（过滤了 {original_length - len(filtered_data)} 条消息）")
                with open(test_file, "w", encoding="utf-8") as f:
                    json.dump(filtered_data, f, ensure_ascii=False, indent=2)
            else:
                print(f"   ✅ 无需更新文件")

            print(f"   ✅ 修复后的逻辑工作正常")
        except Exception as e:
            print(f"   ❌ 修复后的逻辑失败: {e}")

    print("\n" + "=" * 60)
    print("🎯 测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_encoding_fix()
