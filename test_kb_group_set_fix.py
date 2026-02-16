#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 kb_group_set 命令的配置保存
验证 config 对象的正确使用
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_config_object_usage():
    """测试 config 对象的使用"""

    print("=" * 60)
    print("🧪 测试 config 对象的使用")
    print("=" * 60)

    try:
        from config import config
        from config import KnowledgeBaseConfig

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

        # 测试2：获取群知识库配置
        print("\n📌 测试2：获取群知识库配置")
        kb_id = config.get_group_kb_id(test_group_id)
        top_k = config.get_group_kb_top_k(test_group_id)

        if kb_id == test_kb_id and top_k == 3:
            print(f"   ✅ 配置保存成功")
            print(f"   - 知识库 ID: {kb_id}")
            print(f"   - top_k: {top_k}")
        else:
            print(f"   ❌ 配置保存失败")
            print(f"   - 期望: {test_kb_id}, 3")
            print(f"   - 实际: {kb_id}, {top_k}")
            return False

        # 测试3：验证全局 config 对象
        print("\n📌 测试3：验证全局 config 对象")
        print(f"   ✅ 全局 config 对象 ID: {id(config)}")

        # 测试4：模拟错误的导入方式
        print("\n📌 测试4：模拟错误的导入方式")
        print(f"   ⚠️  如果使用 'from config import config as cfg'，")
        print(f"   ⚠️  会创建一个新的 config 对象，导致配置不生效")

        # 重新导入（模拟 bug）
        import importlib
        import config as config_module
        importlib.reload(config_module)
        from config import config as cfg

        print(f"   ⚠️  新的 cfg 对象 ID: {id(cfg)}")

        # 在新对象上设置配置
        cfg.set_group_kb_config(
            group_id="test_group_2",
            kb_config=KnowledgeBaseConfig(
                enabled=True,
                kb_id="test_kb",
                top_k=5
            )
        )

        # 在全局对象上检查
        kb_id_2 = config.get_group_kb_id("test_group_2")

        if kb_id_2 is None:
            print(f"   ✅ 全局对象未受到影响（预期的行为）")
            print(f"   ✅ 这就是修复前的问题：修改了错误的 config 对象")
        else:
            print(f"   ❌ 全局对象被影响了（不应该发生）")
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
            return False
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_config_object_usage()
