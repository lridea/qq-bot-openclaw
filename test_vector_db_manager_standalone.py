#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立测试向量数据库管理器（不依赖 nonebot）
"""

import sys
import os
import tempfile
import shutil

# 添加插件路径
sys.path.insert(0, os.path.dirname(__file__))


def test_vector_database_manager():
    """测试向量数据库管理器"""

    print("=" * 50)
    print("🧪 测试向量数据库管理器")
    print("=" * 50)

    # 检查 chromadb 是否安装
    print("\n1️⃣  检查依赖...")
    try:
        import chromadb
        print("✅ ChromaDB 已安装")
    except ImportError:
        print("❌ ChromaDB 未安装")
        print("   请运行: pip install chromadb")
        return

    # 导入模块
    print("\n2️⃣  导入向量数据库管理器...")
    try:
        from plugins.openclaw_chat import vector_database_manager
        print("✅ 导入成功")
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return

    # 创建测试目录
    test_dir = "data/knowledge_bases_test_vdb"
    print("\n3️⃣  创建测试目录...")

    # 清理旧测试数据
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    print(f"✅ 测试目录: {test_dir}")

    # 创建管理器
    print("\n4️⃣  创建向量数据库管理器...")
    try:
        manager = vector_database_manager.VectorDatabaseManager(kb_dir=test_dir)
        print("✅ 管理器创建成功")
    except Exception as e:
        print(f"❌ 管理器创建失败: {e}")
        return

    # 测试集合创建
    print("\n5️⃣  测试集合创建...")
    try:
        # 获取或创建集合
        collection = manager._get_or_create_collection("test_kb")
        print("✅ 集合创建成功")
        print(f"   集合名称: {manager._get_collection_name('test_kb')}")
    except Exception as e:
        print(f"❌ 集合创建失败: {e}")
        return

    # 测试添加文档
    print("\n6️⃣  测试添加文档...")
    try:
        # 创建测试文档块
        chunks = [
            vector_database_manager.DocumentChunk(
                chunk_id="chunk_001",
                kb_id="test_kb",
                text="泰拉瑞亚是一款2D沙盒游戏",
                source="https://test.example.com/terraria",
                metadata={"category": "game", "type": "intro"}
            ),
            vector_database_manager.DocumentChunk(
                chunk_id="chunk_002",
                kb_id="test_kb",
                text="血腥僵尸是困难模式的敌人，掉落鲨牙项链",
                source="https://test.example.com/bloody_zombie",
                metadata={"category": "enemy", "type": "drops"}
            ),
            vector_database_manager.DocumentChunk(
                chunk_id="chunk_003",
                kb_id="test_kb",
                text="鲨牙项链增加5%的近战伤害",
                source="https://test.example.com/shark_tooth_necklace",
                metadata={"category": "item", "type": "accessory"}
            )
        ]

        # 添加文档
        result = manager.add_documents(kb_id="test_kb", chunks=chunks)

        if result:
            print("✅ 文档添加成功")
            print(f"   添加数量: {len(chunks)}")
        else:
            print("❌ 文档添加失败")
            return

    except Exception as e:
        print(f"❌ 文档添加失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 测试集合信息
    print("\n7️⃣  测试获取集合信息...")
    try:
        info = manager.get_collection_info("test_kb")

        if info:
            print("✅ 集合信息获取成功")
            print(f"   知识库 ID: {info['kb_id']}")
            print(f"   集合名称: {info['collection_name']}")
            print(f"   文档数量: {info['count']}")
        else:
            print("❌ 集合信息获取失败")
            return

    except Exception as e:
        print(f"❌ 集合信息获取失败: {e}")
        return

    # 测试搜索
    print("\n8️⃣  测试搜索...")
    try:
        results = manager.search(
            kb_id="test_kb",
            query="血腥僵尸掉落什么？",
            top_k=2
        )

        if results:
            print("✅ 搜索成功")
            print(f"   结果数量: {len(results)}")

            for i, result in enumerate(results, 1):
                print(f"\n   结果 {i}:")
                print(f"   - 文本: {result['text'][:50]}...")
                print(f"   - 来源: {result['metadata']['source']}")
                print(f"   - 相似度: {result['score']:.4f}")
        else:
            print("⚠️  搜索结果为空")

    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 测试更新文档
    print("\n9️⃣  测试更新文档...")
    try:
        # 更新第一个文档
        updated_chunks = [
            vector_database_manager.DocumentChunk(
                chunk_id="chunk_001",
                kb_id="test_kb",
                text="泰拉瑞亚是一款2D沙盒游戏，由Re-Logic开发",
                source="https://test.example.com/terraria",
                metadata={"category": "game", "type": "intro", "developer": "Re-Logic"}
            )
        ]

        result = manager.update_documents(kb_id="test_kb", chunks=updated_chunks)

        if result:
            print("✅ 文档更新成功")
        else:
            print("❌ 文档更新失败")

    except Exception as e:
        print(f"❌ 文档更新失败: {e}")

    # 测试删除文档
    print("\n🔟 测试删除文档...")
    try:
        result = manager.delete_documents(
            kb_id="test_kb",
            chunk_ids=["chunk_003"]
        )

        if result:
            print("✅ 文档删除成功")

            # 验证删除
            info = manager.get_collection_info("test_kb")
            print(f"   剩余文档: {info['count']}")
        else:
            print("❌ 文档删除失败")

    except Exception as e:
        print(f"❌ 文档删除失败: {e}")

    # 测试清空集合
    print("\n1️⃣ 1️⃣  测试清空集合...")
    try:
        result = manager.clear_collection("test_kb")

        if result:
            print("✅ 集合清空成功")

            # 验证清空
            info = manager.get_collection_info("test_kb")
            print(f"   文档数量: {info['count']}")
        else:
            print("❌ 集合清空失败")

    except Exception as e:
        print(f"❌ 集合清空失败: {e}")

    # 测试删除集合
    print("\n1️⃣ 2️⃣  测试删除集合...")
    try:
        result = manager.delete_collection("test_kb")

        if result:
            print("✅ 集合删除成功")

            # 验证删除
            exists = manager.collection_exists("test_kb")
            print(f"   集合存在: {exists}")
        else:
            print("❌ 集合删除失败")

    except Exception as e:
        print(f"❌ 集合删除失败: {e}")

    # 完成
    print("\n" + "=" * 50)
    print("✅ 测试完成")
    print("=" * 50)

    # 清理测试数据
    print("\n🧹 清理测试数据...")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        print("✅ 测试数据已清理")


if __name__ == "__main__":
    test_vector_database_manager()
