#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库构建器
结合 Wiki 解析器、知识库管理器、向量数据库管理器，构建游戏知识库
"""

import uuid
import asyncio
from typing import List, Dict, Optional, Any
from .wiki_parser import WikiParser
from .knowledge_base_manager import KnowledgeBaseManager
from .vector_database_manager import VectorDatabaseManager, DocumentChunk
from nonebot.log import logger


class KnowledgeBaseBuilder:
    """知识库构建器"""

    def __init__(
        self,
        kb_dir: str = "data/knowledge_bases",
        wiki_url: str = "https://terraria.wiki.gg/zh/wiki/",
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """
        初始化知识库构建器

        Args:
            kb_dir: 知识库存储目录
            wiki_url: Wiki 基础 URL
            chunk_size: 每块大小（字符数）
            chunk_overlap: 块之间重叠字符数
        """
        self.kb_dir = kb_dir
        self.wiki_url = wiki_url
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 初始化管理器
        self.kb_manager = KnowledgeBaseManager(kb_dir=kb_dir)
        self.vdb_manager = VectorDatabaseManager(kb_dir=kb_dir)
        self.wiki_parser = WikiParser(base_url=wiki_url)

        logger.info("✅ 知识库构建器初始化成功")

    async def close(self):
        """关闭资源"""
        await self.wiki_parser.close()
        logger.info("✅ 知识库构建器资源已关闭")

    # ========== 知识库构建 ==========

    async def build_knowledge_base(
        self,
        kb_id: str,
        kb_name: str,
        kb_type: str = "game",
        pages: Optional[List[str]] = None
    ) -> bool:
        """
        构建知识库

        Args:
            kb_id: 知识库 ID
            kb_name: 知识库名称
            kb_type: 知识库类型（game/tech/life/general）
            pages: 页面列表（None 则使用默认页面）

        Returns:
            bool: 是否构建成功
        """
        try:
            # 创建知识库
            logger.info(f"📚 开始构建知识库: {kb_id}")

            result = self.kb_manager.create_knowledge_base(
                kb_id=kb_id,
                kb_name=kb_name,
                kb_type=kb_type,
                source=self.wiki_url,
                metadata={"chunk_size": self.chunk_size, "chunk_overlap": self.chunk_overlap}
            )

            if not result:
                logger.error(f"❌ 创建知识库失败: {kb_id}")
                return False

            # 获取页面列表
            if pages is None:
                pages = self._get_default_pages()

            logger.info(f"📄 待处理页面数量: {len(pages)}")

            # 解析页面并添加到向量数据库
            chunks = []
            chunk_count = 0

            for page_name in pages:
                logger.info(f"📖 正在解析页面: {page_name}")

                # 解析页面
                page_data = await self.wiki_parser.parse_page(page_name)

                if page_data is None:
                    logger.warning(f"⚠️  页面解析失败: {page_name}")
                    continue

                # 提取文本块
                page_chunks = self._extract_chunks(page_data, kb_id)
                chunks.extend(page_chunks)
                chunk_count += len(page_chunks)

                logger.info(f"✅ 页面解析成功: {page_name}, 块数量: {len(page_chunks)}")

            # 添加到向量数据库
            if chunks:
                logger.info(f"💾 正在添加 {len(chunks)} 个文本块到向量数据库...")

                result = self.vdb_manager.add_documents(
                    kb_id=kb_id,
                    chunks=chunks
                )

                if result:
                    logger.info(f"✅ 文本块添加成功")
                else:
                    logger.error(f"❌ 文本块添加失败")
                    return False
            else:
                logger.warning(f"⚠️  没有可添加的文本块")

            # 更新知识库状态
            self.kb_manager.update_knowledge_base(
                kb_id=kb_id,
                status="ready",
                chunk_count=chunk_count
            )

            logger.info(f"✅ 知识库构建成功: {kb_id}, 总块数: {chunk_count}")

            return True

        except Exception as e:
            logger.error(f"❌ 构建知识库失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _extract_chunks(
        self,
        page_data: Dict[str, Any],
        kb_id: str
    ) -> List[DocumentChunk]:
        """
        从页面数据提取文本块

        Args:
            page_data: 页面数据
            kb_id: 知识库 ID

        Returns:
            List[DocumentChunk]: 文本块列表
        """
        chunks = []

        # 从页面的文本块提取
        for chunk_data in page_data.get("chunks", []):
            chunk_id = f"{page_data['page_name']}_chunk_{chunk_data['index']}"

            chunk = DocumentChunk(
                chunk_id=chunk_id,
                kb_id=kb_id,
                text=chunk_data["text"],
                source=page_data["url"],
                metadata={
                    "page_name": page_data["page_name"],
                    "page_title": page_data.get("title", ""),
                    "chunk_index": chunk_data["index"],
                    "char_count": chunk_data["char_count"]
                }
            )

            chunks.append(chunk)

        return chunks

    def _get_default_pages(self) -> List[str]:
        """
        获取默认页面列表

        Returns:
            List[str]: 页面名称列表
        """
        # 泰拉瑞亚核心页面
        pages = [
            "Terraria_Wiki",
            "游戏机制",
            "敌人",
            "Boss",
            "事件",
            "生物群落",
            "物品",
            "武器",
            "盔甲",
            "配饰",
            "消耗品",
            "方块",
            "家具",
            "NPC",
            "合成",
        ]

        return pages

    # ========== 知识库更新 ==========

    async def update_knowledge_base(
        self,
        kb_id: str,
        pages: Optional[List[str]] = None
    ) -> bool:
        """
        更新知识库

        Args:
            kb_id: 知识库 ID
            pages: 页面列表（None 则使用默认页面）

        Returns:
            bool: 是否更新成功
        """
        try:
            # 检查知识库是否存在
            if not self.kb_manager.exists(kb_id):
                logger.error(f"❌ 知识库不存在: {kb_id}")
                return False

            # 清空向量数据库
            logger.info(f"🧹 清空知识库: {kb_id}")
            self.vdb_manager.clear_collection(kb_id)

            # 重新构建
            kb_info = self.kb_manager.get_knowledge_base(kb_id)

            if kb_info is None:
                logger.error(f"❌ 获取知识库信息失败: {kb_id}")
                return False

            result = await self.build_knowledge_base(
                kb_id=kb_id,
                kb_name=kb_info.kb_name,
                kb_type=kb_info.kb_type,
                pages=pages
            )

            return result

        except Exception as e:
            logger.error(f"❌ 更新知识库失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ========== 单页面添加 ==========

    async def add_page(
        self,
        kb_id: str,
        page_name: str
    ) -> bool:
        """
        添加单个页面到知识库

        Args:
            kb_id: 知识库 ID
            page_name: 页面名称

        Returns:
            bool: 是否添加成功
        """
        try:
            # 检查知识库是否存在
            if not self.kb_manager.exists(kb_id):
                logger.error(f"❌ 知识库不存在: {kb_id}")
                return False

            logger.info(f"📖 正在添加页面: {page_name}")

            # 解析页面
            page_data = await self.wiki_parser.parse_page(page_name)

            if page_data is None:
                logger.error(f"❌ 页面解析失败: {page_name}")
                return False

            # 提取文本块
            chunks = self._extract_chunks(page_data, kb_id)

            if not chunks:
                logger.warning(f"⚠️  页面没有文本块: {page_name}")
                return False

            # 添加到向量数据库
            result = self.vdb_manager.add_documents(
                kb_id=kb_id,
                chunks=chunks
            )

            if result:
                logger.info(f"✅ 页面添加成功: {page_name}, 块数量: {len(chunks)}")

                # 更新知识库信息
                kb_info = self.kb_manager.get_knowledge_base(kb_id)
                if kb_info:
                    new_chunk_count = kb_info.chunk_count + len(chunks)
                    self.kb_manager.update_knowledge_base(
                        kb_id=kb_id,
                        chunk_count=new_chunk_count
                    )

                return True
            else:
                logger.error(f"❌ 页面添加失败: {page_name}")
                return False

        except Exception as e:
            logger.error(f"❌ 添加页面失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ========== 搜索 ==========

    async def search(
        self,
        kb_id: str,
        query: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        搜索知识库

        Args:
            kb_id: 知识库 ID
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        try:
            # 检查知识库是否存在
            if not self.kb_manager.exists(kb_id):
                logger.error(f"❌ 知识库不存在: {kb_id}")
                return []

            # 检查知识库是否准备就绪
            if not self.kb_manager.is_ready(kb_id):
                logger.warning(f"⚠️  知识库未准备就绪: {kb_id}")
                return []

            # 搜索向量数据库
            results = self.vdb_manager.search(
                kb_id=kb_id,
                query=query,
                top_k=top_k
            )

            return results

        except Exception as e:
            logger.error(f"❌ 搜索失败: {e}")
            return []
