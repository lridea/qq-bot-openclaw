#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立测试知识库构建器（不依赖 nonebot）
"""

import sys
import os
import asyncio

# 添加插件路径
sys.path.insert(0, os.path.dirname(__file__))


async def test_wiki_parser():
    """测试 Wiki 解析器"""

    print("=" * 50)
    print("🧪 测试 Wiki 解析器")
    print("=" * 50)

    # 检查 httpx 是否安装
    print("\n1️⃣  检查依赖...")
    try:
        import httpx
        print("✅ httpx 已安装")
    except ImportError:
        print("❌ httpx 未安装")
        print("   请运行: pip install httpx")
        return

    # 导入模块
    print("\n2️⃣  导入 Wiki 解析器...")
    try:
        from plugins.openclaw_chat import wiki_parser
        print("✅ 导入成功")
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return

    # 创建解析器
    print("\n3️⃣  创建 Wiki 解析器...")
    try:
        parser = wiki_parser.WikiParser(
            base_url="https://terraria.wiki.gg/zh/wiki/"
        )
        print("✅ 解析器创建成功")
    except Exception as e:
        print(f"❌ 解析器创建失败: {e}")
        return

    # 测试获取页面
    print("\n4️⃣  测试获取页面...")
    try:
        print("   正在获取: Terraria_Wiki")
        html = await parser.fetch_page("Terraria_Wiki")

        if html:
            print("✅ 页面获取成功")
            print(f"   HTML 大小: {len(html)} 字符")
        else:
            print("❌ 页面获取失败")
            return

    except Exception as e:
        print(f"❌ 页面获取失败: {e}")
        return

    # 测试提取标题
    print("\n5️⃣  测试提取标题...")
    try:
        title = parser.extract_title(html)

        if title:
            print("✅ 标题提取成功")
            print(f"   标题: {title}")
        else:
            print("⚠️  标题提取失败（可能是页面结构不同）")

    except Exception as e:
        print(f"❌ 标题提取失败: {e}")

    # 测试提取内容
    print("\n6️⃣  测试提取内容...")
    try:
        content = parser.extract_content(html)

        if content:
            print("✅ 内容提取成功")
            print(f"   内容大小: {len(content)} 字符")
            print(f"   前 100 字符: {content[:100]}...")
        else:
            print("❌ 内容提取失败")

    except Exception as e:
        print(f"❌ 内容提取失败: {e}")

    # 测试提取章节
    print("\n7️⃣  测试提取章节...")
    try:
        sections = parser.extract_sections(html)

        if sections:
            print("✅ 章节提取成功")
            print(f"   章节数量: {len(sections)}")

            for i, section in enumerate(sections[:3], 1):
                print(f"\n   章节 {i}:")
                print(f"   - 标题: {section['title']}")
                print(f"   - 层级: {section['level']}")
                print(f"   - 内容: {section['content'][:50]}...")
        else:
            print("⚠️  章节提取失败（可能是页面结构不同）")

    except Exception as e:
        print(f"❌ 章节提取失败: {e}")

    # 测试提取链接
    print("\n8️⃣  测试提取链接...")
    try:
        links = parser.extract_links(html)

        if links:
            print("✅ 链接提取成功")
            print(f"   链接数量: {len(links)}")
            print(f"   前 10 个链接: {links[:10]}")
        else:
            print("⚠️  链接提取失败（可能是页面结构不同）")

    except Exception as e:
        print(f"❌ 链接提取失败: {e}")

    # 测试文本分割
    print("\n9️⃣  测试文本分割...")
    try:
        test_text = """
泰拉瑞亚是一款2D沙盒游戏，由Re-Logic开发。

玩家可以探索、建造、战斗，与其他玩家互动。

游戏中有各种敌人、Boss、物品和装备。
        """.strip()

        chunks = parser.split_into_chunks(test_text, chunk_size=100, chunk_overlap=20)

        if chunks:
            print("✅ 文本分割成功")
            print(f"   块数量: {len(chunks)}")

            for i, chunk in enumerate(chunks, 1):
                print(f"\n   块 {i}:")
                print(f"   - 索引: {chunk['index']}")
                print(f"   - 字符数: {chunk['char_count']}")
                print(f"   - 内容: {chunk['text'][:50]}...")
        else:
            print("❌ 文本分割失败")

    except Exception as e:
        print(f"❌ 文本分割失败: {e}")

    # 测试完整解析
    print("\n🔟 测试完整解析...")
    try:
        print("   正在解析: Terraria_Wiki")
        page_data = await parser.parse_page("Terraria_Wiki")

        if page_data:
            print("✅ 页面解析成功")
            print(f"   页面名称: {page_data['page_name']}")
            print(f"   URL: {page_data['url']}")
            print(f"   标题: {page_data.get('title', 'N/A')}")
            print(f"   内容大小: {len(page_data['content'])} 字符")
            print(f"   信息框字段: {len(page_data['infobox'])}")
            print(f"   章节数量: {len(page_data['sections'])}")
            print(f"   链接数量: {len(page_data['links'])}")
            print(f"   文本块数量: {len(page_data['chunks'])}")
        else:
            print("❌ 页面解析失败")

    except Exception as e:
        print(f"❌ 页面解析失败: {e}")
        import traceback
        traceback.print_exc()

    # 关闭解析器
    print("\n1️⃣ 1️⃣  关闭解析器...")
    await parser.close()
    print("✅ 解析器已关闭")

    # 完成
    print("\n" + "=" * 50)
    print("✅ 测试完成")
    print("=" * 50)


async def test_knowledge_base_builder():
    """测试知识库构建器"""

    print("\n" + "=" * 50)
    print("🧪 测试知识库构建器")
    print("=" * 50)

    # 检查依赖
    print("\n1️⃣  检查依赖...")
    try:
        import chromadb
        print("✅ ChromaDB 已安装")
    except ImportError:
        print("❌ ChromaDB 未安装")
        print("   请运行: pip install chromadb")
        return

    # 导入模块
    print("\n2️⃣  导入知识库构建器...")
    try:
        from plugins.openclaw_chat import knowledge_base_builder
        print("✅ 导入成功")
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return

    # 创建构建器
    print("\n3️⃣  创建知识库构建器...")
    try:
        builder = knowledge_base_builder.KnowledgeBaseBuilder(
            kb_dir="data/knowledge_bases_test_builder",
            wiki_url="https://terraria.wiki.gg/zh/wiki/",
            chunk_size=500,
            chunk_overlap=50
        )
        print("✅ 构建器创建成功")
    except Exception as e:
        print(f"❌ 构建器创建失败: {e}")
        return

    # 构建知识库
    print("\n4️⃣  构建知识库...")
    try:
        print("   正在构建: game_terraria_test")

        result = await builder.build_knowledge_base(
            kb_id="game_terraria_test",
            kb_name="泰拉瑞亚知识库（测试）",
            kb_type="game",
            pages=["Terraria_Wiki", "游戏机制"]  # 只测试几个页面
        )

        if result:
            print("✅ 知识库构建成功")
        else:
            print("❌ 知识库构建失败")
            return

    except Exception as e:
        print(f"❌ 知识库构建失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 搜索知识库
    print("\n5️⃣  搜索知识库...")
    try:
        results = await builder.search(
            kb_id="game_terraria_test",
            query="泰拉瑞亚是什么游戏？",
            top_k=2
        )

        if results:
            print("✅ 搜索成功")
            print(f"   结果数量: {len(results)}")

            for i, result in enumerate(results, 1):
                print(f"\n   结果 {i}:")
                print(f"   - 文本: {result['text'][:80]}...")
                print(f"   - 来源: {result['metadata']['source']}")
                print(f"   - 页面: {result['metadata']['page_name']}")
                print(f"   - 相似度: {result['score']:.4f}")
        else:
            print("⚠️  搜索结果为空")

    except Exception as e:
        print(f"❌ 搜索失败: {e}")

    # 关闭构建器
    print("\n6️⃣  关闭构建器...")
    await builder.close()
    print("✅ 构建器已关闭")

    # 完成
    print("\n" + "=" * 50)
    print("✅ 测试完成")
    print("=" * 50)

    # 清理测试数据
    print("\n🧹 清理测试数据...")
    import shutil
    if os.path.exists("data/knowledge_bases_test_builder"):
        shutil.rmtree("data/knowledge_bases_test_builder")
        print("✅ 测试数据已清理")


async def main():
    """主函数"""
    print("\n🎯 开始测试\n")

    # 测试 Wiki 解析器
    await test_wiki_parser()

    # 测试知识库构建器
    await test_knowledge_base_builder()

    print("\n🎉 所有测试完成\n")


if __name__ == "__main__":
    asyncio.run(main())
