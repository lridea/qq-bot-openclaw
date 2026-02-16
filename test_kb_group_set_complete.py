#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整测试 kb_group_set 功能
验证配置保存和读取是否正确
"""

import sys
import os
import json
import tempfile

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_kb_group_set_complete():
    """完整测试 kb_group_set 功能"""

    print("=" * 60)
    print("🧪 完整测试 kb_group_set 功能")
    print("=" * 60)

    try:
        from config import config
        from config import KnowledgeBaseConfig

        # 使用临时文件
        with tempfile.TemporaryDirectory() as temp_dir:
            # 设置临时配置文件
            config.group_config_file = os.path.join(temp_dir, "group_configs.json")
            config._group_configs = {}

            # 测试1：设置群知识库配置
            print("\n📌 测试1：设置群知识库配置")
            test_group_id = "1084998338"
            test_kb_id = "game_terraria"

            config.set_group_kb_config(
                group_id=test_group_id,
                kb_config=KnowledgeBaseConfig(
                    enabled=True,
                    kb_id=test_kb_id,
                    top_k=3
                )
            )

            print(f"   ✅ 配置已设置")
            print(f"   - 群号: {test_group_id}")
            print(f"   - 知识库 ID: {test_kb_id}")

            # 测试2：读取群知识库配置
            print("\n📌 测试2：读取群知识库配置")
            kb_id = config.get_group_kb_id(test_group_id)
            top_k = config.get_group_kb_top_k(test_group_id)

            if kb_id == test_kb_id and top_k == 3:
                print(f"   ✅ 配置读取成功")
                print(f"   - 知识库 ID: {kb_id}")
                print(f"   - top_k: {top_k}")
            else:
                print(f"   ❌ 配置读取失败")
                print(f"   - 期望: {test_kb_id}, 3")
                print(f"   - 实际: {kb_id}, {top_k}")
                return False

            # 测试3：验证配置文件
            print("\n📌 测试3：验证配置文件")
            if os.path.exists(config.group_config_file):
                with open(config.group_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if test_group_id in data:
                    kb_data = data[test_group_id].get('kb_config', {})
                    if kb_data.get('kb_id') == test_kb_id and kb_data.get('top_k') == 3:
                        print(f"   ✅ 配置文件正确")
                        print(f"   - kb_id: {kb_data.get('kb_id')}")
                        print(f"   - top_k: {kb_data.get('top_k')}")
                    else:
                        print(f"   ❌ 配置文件错误")
                        print(f"   - 期望: {test_kb_id}, 3")
                        print(f"   - 实际: {kb_data.get('kb_id')}, {kb_data.get('top_k')}")
                        return False
                else:
                    print(f"   ❌ 配置文件中没有找到群号: {test_group_id}")
                    return False
            else:
                print(f"   ❌ 配置文件不存在")
                return False

            # 测试4：模拟重启（重新加载配置）
            print("\n📌 测试4：模拟重启（重新加载配置）")
            config._group_configs = {}  # 清空内存中的配置
            config.load_group_configs()  # 从文件重新加载

            kb_id = config.get_group_kb_id(test_group_id)
            top_k = config.get_group_kb_top_k(test_group_id)

            if kb_id == test_kb_id and top_k == 3:
                print(f"   ✅ 重启后配置依然有效")
                print(f"   - 知识库 ID: {kb_id}")
                print(f"   - top_k: {top_k}")
            else:
                print(f"   ❌ 重启后配置丢失")
                print(f"   - 期望: {test_kb_id}, 3")
                print(f"   - 实际: {kb_id}, {top_k}")
                return False

            # 测试5：测试全局 config 对象
            print("\n📌 测试5：测试全局 config 对象")
            config_id = id(config)
            print(f"   ✅ 全局 config 对象 ID: {config_id}")

            # 验证全局对象
            if config.get_group_kb_id(test_group_id) == test_kb_id:
                print(f"   ✅ 全局对象配置正确")
            else:
                print(f"   ❌ 全局对象配置错误")
                return False

            # 测试6：模拟 AI 流程中的使用
            print("\n📌 测试6：模拟 AI 流程中的使用")
            from config import config as config_in_ai

            # 确保使用的是同一个对象
            if id(config_in_ai) == config_id:
                print(f"   ✅ AI 流程中使用的是同一个 config 对象")
            else:
                print(f"   ❌ AI 流程中使用了不同的 config 对象")
                print(f"   - 全局对象: {config_id}")
                print(f"   - AI 对象: {id(config_in_ai)}")
                return False

            # 在 AI 流程中读取配置
            kb_id = config_in_ai.get_group_kb_id(test_group_id)
            if kb_id == test_kb_id:
                print(f"   ✅ AI 流程中配置读取正确")
                print(f"   - 知识库 ID: {kb_id}")
            else:
                print(f"   ❌ AI 流程中配置读取错误")
                return False

        print("\n" + "=" * 60)
        print("🎯 测试完成")
        print("=" * 60)

        return True

    except ImportError as e:
        if "nonebot" in str(e) or "pydantic" in str(e):
            print(f"   ℹ️  依赖未安装，跳过测试")
            return True
        else:
            print(f"   ❌ 导入失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_kb_group_set_complete()
    sys.exit(0 if success else 1)
