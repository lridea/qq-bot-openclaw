#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向量数据库管理器
基于 Chroma 实现向量存储和检索
"""

import os
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from nonebot.log import logger


@dataclass
class DocumentChunk:
    """文档块"""

    chunk_id: str  # 文本块 ID（唯一）
    kb_id: str  # 所属知识库 ID
    text: str  # 文本内容
    source: str  # 来源（Wiki URL、文件路径等）
    metadata: Optional[Dict[str, Any]] = None  # 元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "chunk_id": self.chunk_id,
            "kb_id": self.kb_id,
            "text": self.text,
            "source": self.source,
            "metadata": self.metadata or {}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentChunk":
        """从字典创建"""
        return cls(
            chunk_id=data["chunk_id"],
            kb_id=data["kb_id"],
            text=data["text"],
            source=data["source"],
            metadata=data.get("metadata", {})
        )


class VectorDatabaseManager:
    """向量数据库管理器"""

    def __init__(self, kb_dir: str = "data/knowledge_bases"):
        """
        初始化向量数据库管理器

        Args:
            kb_dir: 知识库存储目录
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB 未安装，请安装：pip install chromadb\n"
                "或安装项目依赖：pip install -r requirements.txt"
            )

        self.kb_dir = kb_dir
        self.chroma_dir = os.path.join(kb_dir, "chroma_db")

        # 确保目录存在
        os.makedirs(self.chroma_dir, exist_ok=True)

        # 初始化 Chroma 客户端
        self._init_chroma_client()

        # 集合缓存
        self._collections: Dict[str, chromadb.Collection] = {}

        logger.info("✅ 向量数据库管理器初始化成功")

    def _init_chroma_client(self):
        """初始化 Chroma 客户端"""
        try:
            # 使用持久化客户端
            self.client = chromadb.PersistentClient(
                path=self.chroma_dir,
                settings=Settings(
                    anonymized_telemetry=False,  # 禁用遥测
                    allow_reset=True  # 允许重置
                )
            )

            logger.info(f"✅ Chroma 客户端初始化成功，存储路径: {self.chroma_dir}")

        except Exception as e:
            logger.error(f"❌ Chroma 客户端初始化失败: {e}")
            raise

    def _get_collection_name(self, kb_id: str) -> str:
        """
        获取集合名称

        Args:
            kb_id: 知识库 ID

        Returns:
            str: 集合名称
        """
        # 将知识库 ID 转换为有效的集合名称
        # Chroma 的集合名称要求：只能包含字母、数字、下划线和连字符
        return f"kb_{kb_id.replace('-', '_').replace('.', '_')}"

    def _get_or_create_collection(self, kb_id: str) -> chromadb.Collection:
        """
        获取或创建集合

        Args:
            kb_id: 知识库 ID

        Returns:
            chromadb.Collection: 集合对象
        """
        # 检查缓存
        if kb_id in self._collections:
            return self._collections[kb_id]

        # 获取或创建集合
        collection_name = self._get_collection_name(kb_id)

        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"kb_id": kb_id}
            )

            # 缓存集合
            self._collections[kb_id] = collection

            logger.info(f"✅ 获取集合成功: {collection_name}")

            return collection

        except Exception as e:
            logger.error(f"❌ 获取集合失败 {collection_name}: {e}")
            raise

    # ========== 向量存储 ==========

    def add_documents(
        self,
        kb_id: str,
        chunks: List[DocumentChunk],
        embeddings: Optional[List[List[float]]] = None
    ) -> bool:
        """
        添加文档块到向量数据库

        Args:
            kb_id: 知识库 ID
            chunks: 文档块列表
            embeddings: 向量列表（可选，如果不提供则自动生成）

        Returns:
            bool: 是否添加成功
        """
        if not chunks:
            logger.warning("⚠️  文档块列表为空")
            return False

        try:
            # 获取集合
            collection = self._get_or_create_collection(kb_id)

            # 准备数据
            ids = [chunk.chunk_id for chunk in chunks]
            documents = [chunk.text for chunk in chunks]
            metadatas = [chunk.to_dict() for chunk in chunks]

            # 添加文档
            if embeddings:
                # 使用提供的向量
                collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas
                )
            else:
                # 自动生成向量
                collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )

            logger.info(f"✅ 添加文档块成功: {len(chunks)} 个 (kb_id: {kb_id})")

            return True

        except Exception as e:
            logger.error(f"❌ 添加文档块失败 (kb_id: {kb_id}): {e}")
            return False

    def update_documents(
        self,
        kb_id: str,
        chunks: List[DocumentChunk],
        embeddings: Optional[List[List[float]]] = None
    ) -> bool:
        """
        更新文档块

        Args:
            kb_id: 知识库 ID
            chunks: 文档块列表
            embeddings: 向量列表（可选）

        Returns:
            bool: 是否更新成功
        """
        if not chunks:
            logger.warning("⚠️  文档块列表为空")
            return False

        try:
            # 获取集合
            collection = self._get_or_create_collection(kb_id)

            # 准备数据
            ids = [chunk.chunk_id for chunk in chunks]
            documents = [chunk.text for chunk in chunks]
            metadatas = [chunk.to_dict() for chunk in chunks]

            # 更新文档
            if embeddings:
                collection.update(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents,
                    metadatas=metadatas
                )
            else:
                collection.update(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )

            logger.info(f"✅ 更新文档块成功: {len(chunks)} 个 (kb_id: {kb_id})")

            return True

        except Exception as e:
            logger.error(f"❌ 更新文档块失败 (kb_id: {kb_id}): {e}")
            return False

    def delete_documents(
        self,
        kb_id: str,
        chunk_ids: List[str]
    ) -> bool:
        """
        删除文档块

        Args:
            kb_id: 知识库 ID
            chunk_ids: 文档块 ID 列表

        Returns:
            bool: 是否删除成功
        """
        if not chunk_ids:
            logger.warning("⚠️  文档块 ID 列表为空")
            return False

        try:
            # 获取集合
            collection = self._get_or_create_collection(kb_id)

            # 删除文档
            collection.delete(ids=chunk_ids)

            logger.info(f"✅ 删除文档块成功: {len(chunk_ids)} 个 (kb_id: {kb_id})")

            return True

        except Exception as e:
            logger.error(f"❌ 删除文档块失败 (kb_id: {kb_id}): {e}")
            return False

    # ========== 向量检索 ==========

    def search(
        self,
        kb_id: str,
        query: str,
        top_k: int = 3,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        相似度搜索

        Args:
            kb_id: 知识库 ID
            query: 查询文本
            top_k: 返回结果数量
            where: 元数据过滤条件

        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        try:
            # 获取集合
            collection = self._get_or_create_collection(kb_id)

            # 搜索
            results = collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where
            )

            # 处理结果
            search_results = []

            if results and results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    search_results.append({
                        "chunk_id": results['ids'][0][i],
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "score": results['distances'][0][i] if 'distances' in results else None
                    })

            logger.info(f"✅ 搜索成功: {len(search_results)} 个结果 (kb_id: {kb_id})")

            return search_results

        except Exception as e:
            logger.error(f"❌ 搜索失败 (kb_id: {kb_id}): {e}")
            return []

    # ========== 集合管理 ==========

    def delete_collection(self, kb_id: str) -> bool:
        """
        删除集合

        Args:
            kb_id: 知识库 ID

        Returns:
            bool: 是否删除成功
        """
        try:
            collection_name = self._get_collection_name(kb_id)

            # 删除集合
            self.client.delete_collection(name=collection_name)

            # 清除缓存
            if kb_id in self._collections:
                del self._collections[kb_id]

            logger.info(f"✅ 删除集合成功: {collection_name}")

            return True

        except Exception as e:
            logger.error(f"❌ 删除集合失败 {collection_name}: {e}")
            return False

    def collection_exists(self, kb_id: str) -> bool:
        """
        检查集合是否存在

        Args:
            kb_id: 知识库 ID

        Returns:
            bool: 是否存在
        """
        try:
            collection_name = self._get_collection_name(kb_id)
            collection = self.client.get_collection(name=collection_name)
            return collection is not None

        except Exception:
            return False

    def get_collection_info(self, kb_id: str) -> Optional[Dict[str, Any]]:
        """
        获取集合信息

        Args:
            kb_id: 知识库 ID

        Returns:
            Dict[str, Any]: 集合信息（不存在则返回 None）
        """
        try:
            collection = self._get_or_create_collection(kb_id)
            count = collection.count()

            return {
                "kb_id": kb_id,
                "collection_name": self._get_collection_name(kb_id),
                "count": count
            }

        except Exception as e:
            logger.error(f"❌ 获取集合信息失败 (kb_id: {kb_id}): {e}")
            return None

    # ========== 批量操作 ==========

    def clear_collection(self, kb_id: str) -> bool:
        """
        清空集合（删除所有文档）

        Args:
            kb_id: 知识库 ID

        Returns:
            bool: 是否清空成功
        """
        try:
            # 删除集合
            self.delete_collection(kb_id)

            # 重新创建集合
            self._get_or_create_collection(kb_id)

            logger.info(f"✅ 清空集合成功: {kb_id}")

            return True

        except Exception as e:
            logger.error(f"❌ 清空集合失败 (kb_id: {kb_id}): {e}")
            return False
