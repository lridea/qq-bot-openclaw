#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试知识库管理器
"""

import sys
import os

# 添加插件路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from plugins.openclaw_chat.knowledge_base_manager import KnowledgeBaseManager


def test_knowledge_base_manager():
    """测试知识库管理器"""

    print("=" * 50)
    print("🧪 测试知识库管理器")
    print("=" * 50)

    # 创建管理器
    print("\n1️⃣  创建知识库管理器...")
    manager = KnowledgeBaseManager(kb_dir="data/knowledge_bases")
    print("✅ 管理器创建成功")

    # 创建知识库
    print("\n2️⃣  创建知识库...")
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

    # 获取知识库
    print("\n3️⃣  获取知识库...")
    kb_info = manager.get_knowledge_base("game_terraria")

    if kb_info:
        print("✅ 知识库获取成功")
        print(f"   ID: {kb_info.kb_id}")
        print(f"   名称: {kb_info.kb_name}")
        print(f"   类型: {kb_info.kb_type}")
        print(f"   状态: {kb_info.status}")
    else:
        print("❌ 知识库获取失败")
        return

    # 更新知识库
    print("\n4️⃣  更新知识库...")
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

    # 检查状态
    print("\n5️⃣  检查知识库状态...")
    is_ready = manager.is_ready("game_terraria")
    status = manager.get_status("game_terraria")

    print(f"   准备就绪: {is_ready}")
    print(f"   状态: {status}")

    # 列出所有知识库
    print("\n6️⃣  列出所有知识库...")
    kb_list = manager.list_knowledge_bases()
    print(f"   知识库数量: {len(kb_list)}")

    for kb in kb_list:
        print(f"   - {kb.kb_id}: {kb.kb_name} ({kb.status})")

    # 打印状态
    print("\n7️⃣  打印知识库状态...")
    print("\n" + manager.print_status("game_terraria"))

    # 测试删除
    print("\n8️⃣  测试删除...")
    print("   （仅演示，不实际删除）")

    # print("\n9️⃣  删除知识库...")
    # result = manager.delete_knowledge_base("game_terraria")
    # if result:
    #     print("✅ 知识库删除成功")
    # else:
    #     print("❌ 知识库删除失败")

    # 完成
    print("\n" + "=" * 50)
    print("✅ 测试完成")
    print("=" * 50)


if __name__ == "__main__":
    test_knowledge_base_manager()
