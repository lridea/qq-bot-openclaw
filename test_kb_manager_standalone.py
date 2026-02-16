#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立测试知识库管理器（不依赖 nonebot）
"""

import sys
import os
import json
from datetime import datetime

# 添加插件路径
sys.path.insert(0, os.path.dirname(__file__))


def test_knowledge_base_manager():
    """测试知识库管理器"""

    print("=" * 50)
    print("🧪 测试知识库管理器")
    print("=" * 50)

    # 创建测试目录
    test_dir = "data/knowledge_bases_test"

    # 清理旧测试数据
    if os.path.exists(test_dir):
        import shutil
        shutil.rmtree(test_dir)

    # 导入模块
    print("\n1️⃣  导入知识库管理器...")
    try:
        # 直接导入，不经过 __init__.py
        from plugins.openclaw_chat import knowledge_base_manager
        print("✅ 导入成功")
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return

    # 创建管理器
    print("\n2️⃣  创建知识库管理器...")
    try:
        manager = knowledge_base_manager.KnowledgeBaseManager(kb_dir=test_dir)
        print("✅ 管理器创建成功")
    except Exception as e:
        print(f"❌ 管理器创建失败: {e}")
        return

    # 创建知识库
    print("\n3️⃣  创建知识库...")
    try:
        result = manager.create_knowledge_base(
            kb_id="game_terraria",
            kb_name="泰拉瑞亚知识库",
            kb_type="game",
            source="https://terraria.wiki.gg/",
            metadata={"game": "Terraria", "language": "zh"}
        )

        if result:
            print("✅ 知识库创建成功")
        else:
            print("❌ 知识库创建失败")
            return

    except Exception as e:
        print(f"❌ 知识库创建失败: {e}")
        return

    # 检查文件是否创建
    print("\n4️⃣  检查文件...")
    metadata_file = os.path.join(test_dir, "metadata", "game_terraria.json")
    index_dir = os.path.join(test_dir, "indices", "game_terraria")

    if os.path.exists(metadata_file):
        print("✅ 元数据文件创建成功")

        # 读取并打印内容
        with open(metadata_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"   内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
    else:
        print("❌ 元数据文件未创建")

    if os.path.exists(index_dir):
        print("✅ 索引目录创建成功")
    else:
        print("❌ 索引目录未创建")

    # 获取知识库
    print("\n5️⃣  获取知识库...")
    try:
        kb_info = manager.get_knowledge_base("game_terraria")

        if kb_info:
            print("✅ 知识库获取成功")
            print(f"   ID: {kb_info.kb_id}")
            print(f"   名称: {kb_info.kb_name}")
            print(f"   类型: {kb_info.kb_type}")
            print(f"   状态: {kb_info.status}")
            print(f"   创建时间: {kb_info.created_at}")
        else:
            print("❌ 知识库获取失败")
            return

    except Exception as e:
        print(f"❌ 知识库获取失败: {e}")
        return

    # 更新知识库
    print("\n6️⃣  更新知识库...")
    try:
        result = manager.update_knowledge_base(
            kb_id="game_terraria",
            status="ready",
            chunk_count=100
        )

        if result:
            print("✅ 知识库更新成功")
        else:
            print("❌ 知识库更新失败")
            return

    except Exception as e:
        print(f"❌ 知识库更新失败: {e}")
        return

    # 检查状态
    print("\n7️⃣  检查知识库状态...")
    try:
        is_ready = manager.is_ready("game_terraria")
        status = manager.get_status("game_terraria")

        print(f"   准备就绪: {is_ready}")
        print(f"   状态: {status}")
    except Exception as e:
        print(f"❌ 检查状态失败: {e}")
        return

    # 列出所有知识库
    print("\n8️⃣  列出所有知识库...")
    try:
        kb_list = manager.list_knowledge_bases()
        print(f"   知识库数量: {len(kb_list)}")

        for kb in kb_list:
            print(f"   - {kb.kb_id}: {kb.kb_name} ({kb.status})")
    except Exception as e:
        print(f"❌ 列出知识库失败: {e}")
        return

    # 创建第二个知识库
    print("\n9️⃣  创建第二个知识库...")
    try:
        result = manager.create_knowledge_base(
            kb_id="tech_programming",
            kb_name="编程知识库",
            kb_type="tech",
            source="data/programming_docs",
            metadata={"language": ["python", "javascript"]}
        )

        if result:
            print("✅ 第二个知识库创建成功")
        else:
            print("❌ 第二个知识库创建失败")

    except Exception as e:
        print(f"❌ 第二个知识库创建失败: {e}")

    # 再次列出所有知识库
    print("\n🔟 再次列出所有知识库...")
    try:
        kb_list = manager.list_knowledge_bases()
        print(f"   知识库数量: {len(kb_list)}")

        for kb in kb_list:
            print(f"   - {kb.kb_id}: {kb.kb_name} ({kb.status})")
    except Exception as e:
        print(f"❌ 列出知识库失败: {e}")

    # 打印状态
    print("\n1️⃣ 1️⃣  打印知识库状态...")
    try:
        status_text = manager.print_status()
        print("\n" + status_text)
    except Exception as e:
        print(f"❌ 打印状态失败: {e}")

    # 测试删除
    print("\n1️⃣ 2️⃣  测试删除...")
    try:
        print("   删除第二个知识库...")
        result = manager.delete_knowledge_base("tech_programming")

        if result:
            print("✅ 知识库删除成功")

            # 验证删除
            kb_list = manager.list_knowledge_bases()
            print(f"   剩余知识库数量: {len(kb_list)}")
        else:
            print("❌ 知识库删除失败")
    except Exception as e:
        print(f"❌ 知识库删除失败: {e}")

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
    test_knowledge_base_manager()
