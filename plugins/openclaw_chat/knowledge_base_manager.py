#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库管理器
管理游戏知识库的创建、读取、更新、删除
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from nonebot.log import logger


@dataclass
class KnowledgeBaseInfo:
    """知识库信息"""

    kb_id: str  # 知识库 ID（唯一标识）
    kb_name: str  # 知识库名称
    kb_type: str  # 知识库类型（game/tech/life/general）
    source: str  # 数据源（Wiki URL、文件路径等）
    created_at: str  # 创建时间（ISO 8601）
    updated_at: str  # 更新时间（ISO 8601）
    status: str  # 状态（ready/building/error）
    chunk_count: int = 0  # 文本块数量
    metadata: Optional[Dict[str, Any]] = None  # 元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeBaseInfo":
        """从字典创建"""
        return cls(**data)


class KnowledgeBaseManager:
    """知识库管理器"""

    def __init__(self, kb_dir: str = "data/knowledge_bases"):
        """
        初始化知识库管理器

        Args:
            kb_dir: 知识库存储目录
        """
        self.kb_dir = kb_dir
        self._ensure_dir()
        self._knowledge_bases: Dict[str, KnowledgeBaseInfo] = {}
        self._load_from_file()

    def _ensure_dir(self):
        """确保知识库目录存在"""
        os.makedirs(self.kb_dir, exist_ok=True)
        os.makedirs(os.path.join(self.kb_dir, "indices"), exist_ok=True)
        os.makedirs(os.path.join(self.kb_dir, "metadata"), exist_ok=True)

    def _get_metadata_file(self, kb_id: str) -> str:
        """获取知识库元数据文件路径"""
        return os.path.join(self.kb_dir, "metadata", f"{kb_id}.json")

    def _get_index_dir(self, kb_id: str) -> str:
        """获取知识库索引目录"""
        return os.path.join(self.kb_dir, "indices", kb_id)

    def _load_from_file(self):
        """从文件加载知识库元数据"""
        metadata_dir = os.path.join(self.kb_dir, "metadata")

        if not os.path.exists(metadata_dir):
            return

        for filename in os.listdir(metadata_dir):
            if not filename.endswith(".json"):
                continue

            kb_id = filename[:-5]  # 去掉 .json 后缀
            file_path = os.path.join(metadata_dir, filename)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                kb_info = KnowledgeBaseInfo.from_dict(data)
                self._knowledge_bases[kb_id] = kb_info

                logger.info(f"✅ 加载知识库元数据: {kb_id}")

            except Exception as e:
                logger.error(f"❌ 加载知识库元数据失败 {kb_id}: {e}")

    def _save_to_file(self, kb_id: str):
        """保存知识库元数据到文件"""
        if kb_id not in self._knowledge_bases:
            logger.warning(f"⚠️  知识库不存在: {kb_id}")
            return

        kb_info = self._knowledge_bases[kb_id]

        # 更新时间
        kb_info.updated_at = datetime.now().isoformat()

        file_path = self._get_metadata_file(kb_id)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(kb_info.to_dict(), f, ensure_ascii=False, indent=2)

            logger.info(f"✅ 保存知识库元数据: {kb_id}")

        except Exception as e:
            logger.error(f"❌ 保存知识库元数据失败 {kb_id}: {e}")

    # ========== CRUD 操作 ==========

    def create_knowledge_base(
        self,
        kb_id: str,
        kb_name: str,
        kb_type: str = "game",
        source: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        创建知识库

        Args:
            kb_id: 知识库 ID（唯一标识）
            kb_name: 知识库名称
            kb_type: 知识库类型（game/tech/life/general）
            source: 数据源（Wiki URL、文件路径等）
            metadata: 元数据

        Returns:
            bool: 是否创建成功
        """
        # 检查知识库是否已存在
        if kb_id in self._knowledge_bases:
            logger.warning(f"⚠️  知识库已存在: {kb_id}")
            return False

        # 创建知识库信息
        now = datetime.now().isoformat()

        kb_info = KnowledgeBaseInfo(
            kb_id=kb_id,
            kb_name=kb_name,
            kb_type=kb_type,
            source=source,
            created_at=now,
            updated_at=now,
            status="building",
            chunk_count=0,
            metadata=metadata or {}
        )

        # 保存到内存
        self._knowledge_bases[kb_id] = kb_info

        # 保存到文件
        self._save_to_file(kb_id)

        # 创建索引目录
        os.makedirs(self._get_index_dir(kb_id), exist_ok=True)

        logger.info(f"✅ 创建知识库: {kb_id}")

        return True

    def get_knowledge_base(self, kb_id: str) -> Optional[KnowledgeBaseInfo]:
        """
        获取知识库信息

        Args:
            kb_id: 知识库 ID

        Returns:
            KnowledgeBaseInfo: 知识库信息（不存在则返回 None）
        """
        return self._knowledge_bases.get(kb_id)

    def list_knowledge_bases(self) -> List[KnowledgeBaseInfo]:
        """
        列出所有知识库

        Returns:
            List[KnowledgeBaseInfo]: 知识库列表
        """
        return list(self._knowledge_bases.values())

    def update_knowledge_base(
        self,
        kb_id: str,
        status: Optional[str] = None,
        chunk_count: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新知识库

        Args:
            kb_id: 知识库 ID
            status: 状态
            chunk_count: 文本块数量
            metadata: 元数据

        Returns:
            bool: 是否更新成功
        """
        if kb_id not in self._knowledge_bases:
            logger.warning(f"⚠️  知识库不存在: {kb_id}")
            return False

        kb_info = self._knowledge_bases[kb_id]

        if status is not None:
            kb_info.status = status

        if chunk_count is not None:
            kb_info.chunk_count = chunk_count

        if metadata is not None:
            if kb_info.metadata is None:
                kb_info.metadata = {}
            kb_info.metadata.update(metadata)

        # 保存到文件
        self._save_to_file(kb_id)

        logger.info(f"✅ 更新知识库: {kb_id}")

        return True

    def delete_knowledge_base(self, kb_id: str) -> bool:
        """
        删除知识库

        Args:
            kb_id: 知识库 ID

        Returns:
            bool: 是否删除成功
        """
        if kb_id not in self._knowledge_bases:
            logger.warning(f"⚠️  知识库不存在: {kb_id}")
            return False

        # 从内存删除
        del self._knowledge_bases[kb_id]

        # 删除元数据文件
        metadata_file = self._get_metadata_file(kb_id)
        if os.path.exists(metadata_file):
            os.remove(metadata_file)

        # 删除索引目录
        index_dir = self._get_index_dir(kb_id)
        if os.path.exists(index_dir):
            import shutil
            shutil.rmtree(index_dir)

        logger.info(f"✅ 删除知识库: {kb_id}")

        return True

    # ========== 辅助方法 ==========

    def exists(self, kb_id: str) -> bool:
        """
        检查知识库是否存在

        Args:
            kb_id: 知识库 ID

        Returns:
            bool: 是否存在
        """
        return kb_id in self._knowledge_bases

    def get_index_dir(self, kb_id: str) -> Optional[str]:
        """
        获取知识库索引目录

        Args:
            kb_id: 知识库 ID

        Returns:
            str: 索引目录（不存在则返回 None）
        """
        if kb_id not in self._knowledge_bases:
            return None

        return self._get_index_dir(kb_id)

    def is_ready(self, kb_id: str) -> bool:
        """
        检查知识库是否准备就绪

        Args:
            kb_id: 知识库 ID

        Returns:
            bool: 是否准备就绪
        """
        kb_info = self.get_knowledge_base(kb_id)

        if kb_info is None:
            return False

        return kb_info.status == "ready"

    def get_status(self, kb_id: str) -> Optional[str]:
        """
        获取知识库状态

        Args:
            kb_id: 知识库 ID

        Returns:
            str: 状态（不存在则返回 None）
        """
        kb_info = self.get_knowledge_base(kb_id)

        if kb_info is None:
            return None

        return kb_info.status

    def print_status(self, kb_id: Optional[str] = None) -> str:
        """
        打印知识库状态

        Args:
            kb_id: 知识库 ID（None 则打印所有）

        Returns:
            str: 状态文本
        """
        lines = []

        if kb_id is None:
            # 打印所有知识库
            lines.append("📚 知识库列表\n")
            lines.append("=" * 50)

            kb_list = self.list_knowledge_bases()

            if not kb_list:
                lines.append("📭 暂无知识库")
            else:
                for kb_info in kb_list:
                    lines.append(f"\n📖 知识库: {kb_info.kb_id}")
                    lines.append(f"  名称: {kb_info.kb_name}")
                    lines.append(f"  类型: {kb_info.kb_type}")
                    lines.append(f"  状态: {kb_info.status}")
                    lines.append(f"  文本块: {kb_info.chunk_count}")
                    lines.append(f"  创建时间: {kb_info.created_at[:19]}")
                    lines.append(f"  更新时间: {kb_info.updated_at[:19]}")
                    lines.append(f"  数据源: {kb_info.source}")

        else:
            # 打印指定知识库
            kb_info = self.get_knowledge_base(kb_id)

            if kb_info is None:
                lines.append(f"❌ 知识库不存在: {kb_id}")
            else:
                lines.append(f"📖 知识库: {kb_info.kb_id}")
                lines.append(f"  名称: {kb_info.kb_name}")
                lines.append(f"  类型: {kb_info.kb_type}")
                lines.append(f"  状态: {kb_info.status}")
                lines.append(f"  文本块: {kb_info.chunk_count}")
                lines.append(f"  创建时间: {kb_info.created_at[:19]}")
                lines.append(f"  更新时间: {kb_info.updated_at[:19]}")
                lines.append(f"  数据源: {kb_info.source}")

                if kb_info.metadata:
                    lines.append(f"  元数据: {json.dumps(kb_info.metadata, ensure_ascii=False)}")

        return "\n".join(lines)
