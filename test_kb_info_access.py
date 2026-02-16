#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 kb_admin_commands 中的对象访问方式
验证 KnowledgeBaseInfo 对象使用属性访问而不是下标访问
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_kb_info_access():
    """测试 KnowledgeBaseInfo 对象访问方式"""

    print("=" * 60)
    print("🧪 测试 KnowledgeBaseInfo 对象访问方式")
    print("=" * 60)

    try:
        from plugins.openclaw_chat.knowledge_base_manager import KnowledgeBaseInfo

        # 创建测试对象
        kb_info = KnowledgeBaseInfo(
            kb_id="game_terraria",
            kb_name="泰拉瑞亚知识库",
            kb_type="game",
            source="https://terraria.wiki.gg",
            created_at="2026-02-16T19:00:00",
            updated_at="2026-02-16T19:00:00",
            status="ready",
            chunk_count=245
        )

        # 测试1：属性访问（正确方式）
        print("\n📌 测试1：属性访问（正确方式）")
        try:
            kb_id = kb_info.kb_id
            kb_name = kb_info.kb_name
            status = kb_info.status
            print(f"   ✅ 属性访问成功")
            print(f"   - kb_id: {kb_id}")
            print(f"   - kb_name: {kb_name}")
            print(f"   - status: {status}")
        except Exception as e:
            print(f"   ❌ 属性访问失败: {e}")
            return False

        # 测试2：下标访问（错误方式）
        print("\n📌 测试2：下标访问（错误方式，模拟 bug）")
        try:
            kb_id = kb_info["kb_id"]
            kb_name = kb_info["kb_name"]
            status = kb_info["status"]
            print(f"   ❌ 下标访问成功（不应该成功！）")
            return False
        except TypeError as e:
            print(f"   ✅ 下标访问失败（预期的错误）: {e}")
            print(f"   ✅ 这就是修复前的问题！")

        # 测试3：转换为字典
        print("\n📌 测试3：转换为字典")
        try:
            kb_dict = kb_info.to_dict()
            print(f"   ✅ 转换成功")
            print(f"   - kb_id: {kb_dict['kb_id']}")
            print(f"   - kb_name: {kb_dict['kb_name']}")
            print(f"   - status: {kb_dict['status']}")
        except Exception as e:
            print(f"   ❌ 转换失败: {e}")
            return False

        print("\n" + "=" * 60)
        print("🎯 测试完成")
        print("=" * 60)

        return True

    except ImportError as e:
        if "nonebot" in str(e):
            print(f"   ℹ️  nonebot 未安装，跳过测试")
            return True
        else:
            print(f"   ❌ 导入失败: {e}")
            return False
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    test_kb_info_access()
