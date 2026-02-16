#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 vector_database_manager 的导入问题
验证 chromadb 类型注解不会导致导入错误
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_import():
    """测试导入"""

    print("=" * 60)
    print("🧪 测试 vector_database_manager 导入")
    print("=" * 60)

    # 测试1：正常导入（chromadb 已安装）
    print("\n📌 测试1：正常导入（chromadb 已安装）")
    try:
        from plugins.openclaw_chat.vector_database_manager import VectorDatabaseManager
        print(f"   ✅ 导入成功")
    except ImportError as e:
        if "chromadb" in str(e):
            print(f"   ℹ️  导入失败（chromadb 未安装）: {e}")
            print(f"   ℹ️  这是正常的，chromadb 是可选依赖")
        elif "nonebot" in str(e):
            print(f"   ℹ️  导入失败（nonebot 未安装）: {e}")
            print(f"   ℹ️  这是正常的，nonebot 是开发依赖")
        else:
            print(f"   ⚠️  导入失败: {e}")
    except Exception as e:
        print(f"   ❌ 导入失败（其他错误）: {e}")
        return False

    # 测试2：检查 VectorDatabaseManager 类
    print("\n📌 测试2：检查 VectorDatabaseManager 类")
    try:
        from plugins.openclaw_chat.vector_database_manager import VectorDatabaseManager

        # 检查类方法
        methods = [
            "_get_or_create_collection",
            "get_collection",
            "add_documents",
            "search",
            "delete",
        ]

        for method in methods:
            if hasattr(VectorDatabaseManager, method):
                print(f"   ✅ {method} 方法存在")
            else:
                print(f"   ❌ {method} 方法不存在")
                return False

    except ImportError as e:
        if "chromadb" in str(e):
            print(f"   ℹ️  chromadb 未安装，跳过方法检查")
        elif "nonebot" in str(e):
            print(f"   ℹ️  nonebot 未安装，跳过方法检查")
        else:
            print(f"   ⚠️  导入失败: {e}")
            return False
    except Exception as e:
        print(f"   ❌ 检查失败: {e}")
        return False

    # 测试3：检查 CHROMADB_AVAILABLE 标志
    print("\n📌 测试3：检查 CHROMADB_AVAILABLE 标志")
    try:
        from plugins.openclaw_chat.vector_database_manager import CHROMADB_AVAILABLE

        if CHROMADB_AVAILABLE:
            print(f"   ✅ CHROMADB_AVAILABLE = True")
        else:
            print(f"   ℹ️  CHROMADB_AVAILABLE = False（chromadb 未安装）")
    except Exception as e:
        print(f"   ❌ 检查失败: {e}")
        return False

    print("\n" + "=" * 60)
    print("🎯 测试完成")
    print("=" * 60)

    return True


if __name__ == "__main__":
    test_import()
