#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立测试知识库检索管理器（不依赖 nonebot）
"""

import sys
import os

# 添加插件路径
sys.path.insert(0, os.path.dirname(__file__))


def test_knowledge_base_retriever():
    """测试知识库检索管理器"""

    print("=" * 50)
    print("🧪 测试知识库检索管理器")
    print("=" * 50)

    # 导入模块
    print("\n1️⃣  导入知识库检索管理器...")
    try:
        from plugins.openclaw_chat import knowledge_base_retriever
        print("✅ 导入成功")
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return

    # 创建检索管理器
    print("\n2️⃣  创建知识库检索管理器...")
    try:
        retriever = knowledge_base_retriever.KnowledgeBaseRetriever(
            cache_ttl=300,
            cache_size=1000
        )
        print("✅ 检索管理器创建成功")
        print(f"   缓存 TTL: 300 秒")
        print(f"   缓存大小: 1000")
    except Exception as e:
        print(f"❌ 检索管理器创建失败: {e}")
        return

    # 测试检索上下文
    print("\n3️⃣  测试检索上下文...")
    try:
        context = knowledge_base_retriever.SearchContext(
            query="血腥僵尸掉落什么？",
            kb_id="game_terraria",
            top_k=3,
            min_score=0.0,
            filters=None,
            sort_by="score",
            use_cache=True
        )

        print("✅ 检索上下文创建成功")
        print(f"   查询: {context.query}")
        print(f"   知识库 ID: {context.kb_id}")
        print(f"   返回数量: {context.top_k}")
        print(f"   排序方式: {context.sort_by}")
    except Exception as e:
        print(f"❌ 检索上下文创建失败: {e}")
        return

    # 测试缓存
    print("\n4️⃣  测试缓存功能...")
    try:
        # 模拟检索结果
        mock_results = [
            {
                "chunk_id": "chunk_001",
                "text": "血腥僵尸是困难模式的敌人，掉落鲨牙项链",
                "metadata": {"page_name": "Bloody_Zombie"},
                "score": 0.1234
            },
            {
                "chunk_id": "chunk_002",
                "text": "鲨牙项链增加5%的近战伤害",
                "metadata": {"page_name": "Shark_Tooth_Necklace"},
                "score": 0.2345
            }
        ]

        # 添加到缓存
        retriever._add_to_cache(
            query="血腥僵尸掉落什么？",
            kb_id="game_terraria",
            results=mock_results,
            top_k=3
        )

        print("✅ 添加到缓存成功")

        # 从缓存获取
        cached_results = retriever._get_from_cache(
            query="血腥僵尸掉落什么？",
            kb_id="game_terraria",
            top_k=3
        )

        if cached_results:
            print("✅ 从缓存获取成功")
            print(f"   缓存结果数量: {len(cached_results)}")
        else:
            print("❌ 从缓存获取失败")

    except Exception as e:
        print(f"❌ 缓存测试失败: {e}")

    # 测试缓存统计
    print("\n5️⃣  测试缓存统计...")
    try:
        stats = retriever.get_cache_stats()

        print("✅ 缓存统计获取成功")
        print(f"   缓存大小: {stats['size']}/{stats['max_size']}")
        print(f"   命中次数: {stats['hits']}")
        print(f"   未命中次数: {stats['misses']}")
        print(f"   命中率: {stats['hit_rate']:.2%}")
    except Exception as e:
        print(f"❌ 缓存统计测试失败: {e}")

    # 测试打印缓存统计
    print("\n6️⃣  测试打印缓存统计...")
    try:
        stats_text = retriever.print_cache_stats()
        print("\n" + stats_text)
    except Exception as e:
        print(f"❌ 打印缓存统计失败: {e}")

    # 测试后处理
    print("\n7️⃣  测试后处理...")
    try:
        # 模拟检索结果
        raw_results = [
            {
                "chunk_id": "chunk_001",
                "text": "血腥僵尸是困难模式的敌人，掉落鲨牙项链",
                "metadata": {"page_name": "Bloody_Zombie"},
                "score": 0.1234
            },
            {
                "chunk_id": "chunk_002",
                "text": "血腥僵尸是困难模式的敌人，掉落鲨牙项链",  # 重复
                "metadata": {"page_name": "Bloody_Zombie"},
                "score": 0.2345
            },
            {
                "chunk_id": "chunk_003",
                "text": "鲨牙项链增加5%的近战伤害",
                "metadata": {"page_name": "Shark_Tooth_Necklace"},
                "score": 0.3456
            },
            {
                "chunk_id": "chunk_004",
                "text": "其他内容",
                "metadata": {"page_name": "Other"},
                "score": 0.9999  # 低相关性
            }
        ]

        # 后处理
        processed_results = retriever.post_process_results(
            results=raw_results,
            context=context
        )

        print("✅ 后处理成功")
        print(f"   原始结果: {len(raw_results)}")
        print(f"   处理后结果: {len(processed_results)}")

        for i, result in enumerate(processed_results, 1):
            print(f"\n   结果 {i}:")
            print(f"   - 文本: {result['text'][:50]}...")
            print(f"   - 分数: {result['score']:.4f}")

    except Exception as e:
        print(f"❌ 后处理测试失败: {e}")
        import traceback
        traceback.print_exc()

    # 测试过滤
    print("\n8️⃣  测试过滤功能...")
    try:
        # 创建带有过滤条件的上下文
        filter_context = knowledge_base_retriever.SearchContext(
            query="血腥僵尸掉落什么？",
            kb_id="game_terraria",
            top_k=10,
            min_score=0.0,
            filters={"page_name": "Bloody_Zombie"},  # 只返回指定页面的结果
            sort_by="score",
            use_cache=False
        )

        # 模拟检索结果
        raw_results = [
            {
                "chunk_id": "chunk_001",
                "text": "血腥僵尸是困难模式的敌人",
                "metadata": {"page_name": "Bloody_Zombie"},
                "score": 0.1234
            },
            {
                "chunk_id": "chunk_002",
                "text": "鲨牙项链增加5%的近战伤害",
                "metadata": {"page_name": "Shark_Tooth_Necklace"},
                "score": 0.2345
            }
        ]

        # 过滤
        filtered_results = retriever._filter_results(raw_results, filter_context)

        print("✅ 过滤成功")
        print(f"   原始结果: {len(raw_results)}")
        print(f"   过滤后结果: {len(filtered_results)}")

        for result in filtered_results:
            print(f"   - {result['metadata']['page_name']}: {result['text'][:40]}...")

    except Exception as e:
        print(f"❌ 过滤测试失败: {e}")

    # 测试排序
    print("\n9️⃣  测试排序功能...")
    try:
        # 测试分数排序
        score_context = knowledge_base_retriever.SearchContext(
            query="测试",
            kb_id="test_kb",
            top_k=10,
            sort_by="score"
        )

        raw_results = [
            {"chunk_id": "chunk_001", "text": "文本1", "score": 0.5},
            {"chunk_id": "chunk_002", "text": "文本2", "score": 0.3},
            {"chunk_id": "chunk_003", "text": "文本3", "score": 0.7}
        ]

        sorted_results = retriever._sort_results(raw_results, score_context)

        print("✅ 排序成功（按分数）")
        print(f"   排序前: {[r['score'] for r in raw_results]}")
        print(f"   排序后: {[r['score'] for r in sorted_results]}")

    except Exception as e:
        print(f"❌ 排序测试失败: {e}")

    # 测试去重
    print("\n🔟 测试去重功能...")
    try:
        raw_results = [
            {"chunk_id": "chunk_001", "text": "重复文本", "score": 0.1},
            {"chunk_id": "chunk_002", "text": "重复文本", "score": 0.2},
            {"chunk_id": "chunk_003", "text": "不重复文本", "score": 0.3}
        ]

        deduplicated_results = retriever._deduplicate_results(raw_results)

        print("✅ 去重成功")
        print(f"   原始结果: {len(raw_results)}")
        print(f"   去重后结果: {len(deduplicated_results)}")

    except Exception as e:
        print(f"❌ 去重测试失败: {e}")

    # 测试清空缓存
    print("\n1️⃣ 1️⃣  测试清空缓存...")
    try:
        # 清空指定知识库的缓存
        retriever.clear_cache(kb_id="game_terraria")

        print("✅ 清空缓存成功")

        # 检查缓存
        stats = retriever.get_cache_stats()
        print(f"   缓存大小: {stats['size']}")

    except Exception as e:
        print(f"❌ 清空缓存失败: {e}")

    # 测试清空所有缓存
    print("\n1️⃣ 2️⃣  测试清空所有缓存...")
    try:
        # 先添加一些缓存
        retriever._add_to_cache(
            query="测试1",
            kb_id="test_kb1",
            results=[{"text": "测试"}]
        )

        retriever._add_to_cache(
            query="测试2",
            kb_id="test_kb2",
            results=[{"text": "测试"}]
        )

        # 清空所有缓存
        retriever.clear_cache()

        print("✅ 清空所有缓存成功")

        # 检查缓存
        stats = retriever.get_cache_stats()
        print(f"   缓存大小: {stats['size']}")

    except Exception as e:
        print(f"❌ 清空所有缓存失败: {e}")

    # 完成
    print("\n" + "=" * 50)
    print("✅ 测试完成")
    print("=" * 50)


if __name__ == "__main__":
    test_knowledge_base_retriever()
