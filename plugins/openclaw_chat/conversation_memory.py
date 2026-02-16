#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话记忆模块
支持：短期记忆（内存）+ 长期记忆（JSON 文件）
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pathlib import Path
from nonebot.log import logger


class ConversationMemory:
    """对话记忆管理器"""

    def __init__(
        self,
        memory_dir: str = "data/conversations",
        short_term_length: int = 10,
        long_term_expire_days: int = 30,
        auto_clean: bool = True
    ):
        """
        初始化对话记忆管理器

        Args:
            memory_dir: 记忆存储目录
            short_term_length: 短期记忆长度（消息数量）
            long_term_expire_days: 长期记忆过期时间（天），0 表示永不过期
            auto_clean: 是否自动清理过期记忆
        """
        self.memory_dir = Path(memory_dir)
        self.short_term_length = short_term_length
        self.long_term_expire_days = long_term_expire_days
        self.auto_clean = auto_clean

        # 短期记忆（内存）
        self._short_term_memory: Dict[str, List[Dict[str, Any]]] = {}

        # 创建存储目录
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # 自动清理过期记忆
        if self.auto_clean:
            self._clean_expired_memory()

        logger.info(f"✅ 对话记忆已初始化: {self.memory_dir}")

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        添加消息到对话记忆

        Args:
            session_id: 会话 ID（用户 ID 或群组 ID）
            role: 角色（user/assistant/system）
            content: 消息内容
            metadata: 元数据（可选）
        """
        timestamp = time.time()

        # 创建消息对象
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat(),
            "metadata": metadata or {}
        }

        # 添加到短期记忆
        if session_id not in self._short_term_memory:
            self._short_term_memory[session_id] = []

        self._short_term_memory[session_id].append(message)

        # 限制短期记忆长度
        if len(self._short_term_memory[session_id]) > self.short_term_length:
            self._short_term_memory[session_id] = self._short_term_memory[session_id][-self.short_term_length:]

        # 保存到长期记忆
        self._save_to_long_term_memory(session_id, message)

        logger.debug(f"💾 已保存消息到记忆: session={session_id}, role={role}")

    def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取对话历史

        Args:
            session_id: 会话 ID
            limit: 最多返回的消息数量，None 表示全部

        Returns:
            消息列表
        """
        # 优先从短期记忆获取
        if session_id in self._short_term_memory:
            history = self._short_term_memory[session_id]
        else:
            # 如果短期记忆没有，尝试从长期记忆加载
            history = self._load_from_long_term_memory(session_id)
            if history:
                self._short_term_memory[session_id] = history
                history = history

        # 限制返回数量
        if limit is not None:
            history = history[-limit:]

        return history

    def get_conversation_context(
        self,
        session_id: str,
        max_tokens: int = 2000
    ) -> List[Dict[str, str]]:
        """
        获取对话上下文（用于 AI 调用）

        Args:
            session_id: 会话 ID
            max_tokens: 最大 Token 数（估算）

        Returns:
            上下文消息列表（只包含 role 和 content）
        """
        history = self.get_conversation_history(session_id)

        # 按时间排序（从旧到新）
        history = sorted(history, key=lambda x: x["timestamp"])

        # 转换为 AI 格式
        context = []
        current_tokens = 0

        # 从最新的消息开始
        for message in reversed(history):
            tokens = len(message["content"]) // 2  # 粗略估算：1 中文字符 ≈ 0.5 Token

            if current_tokens + tokens > max_tokens:
                break

            context.insert(0, {
                "role": message["role"],
                "content": message["content"]
            })

            current_tokens += tokens

        logger.debug(f"📚 已加载对话上下文: session={session_id}, messages={len(context)}")

        return context

    def clear_conversation(self, session_id: str) -> None:
        """
        清除对话记忆

        Args:
            session_id: 会话 ID
        """
        # 清除短期记忆
        if session_id in self._short_term_memory:
            del self._short_term_memory[session_id]

        # 清除长期记忆
        long_term_file = self.memory_dir / f"{session_id}.json"
        if long_term_file.exists():
            long_term_file.unlink()

        logger.info(f"🗑️ 已清除对话记忆: session={session_id}")

    def get_all_sessions(self) -> List[str]:
        """
        获取所有会话 ID

        Returns:
            会话 ID 列表
        """
        return [f.stem for f in self.memory_dir.glob("*.json")]

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话信息

        Args:
            session_id: 会话 ID

        Returns:
            会话信息字典
        """
        history = self.get_conversation_history(session_id)

        if not history:
            return None

        first_message = history[0]
        last_message = history[-1]

        return {
            "session_id": session_id,
            "message_count": len(history),
            "first_message_time": datetime.fromtimestamp(first_message["timestamp"]).isoformat(),
            "last_message_time": datetime.fromtimestamp(last_message["timestamp"]).isoformat(),
            "duration_seconds": last_message["timestamp"] - first_message["timestamp"]
        }

    def _save_to_long_term_memory(
        self,
        session_id: str,
        message: Dict[str, Any]
    ) -> None:
        """
        保存消息到长期记忆

        Args:
            session_id: 会话 ID
            message: 消息对象
        """
        long_term_file = self.memory_dir / f"{session_id}.json"

        # 读取现有历史
        if long_term_file.exists():
            try:
                with open(long_term_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception as e:
                logger.error(f"❌ 读取长期记忆失败: {e}")
                history = []
        else:
            history = []

        # 添加新消息
        history.append(message)

        # 保存回文件
        try:
            with open(long_term_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ 保存长期记忆失败: {e}")

    def _load_from_long_term_memory(self, session_id: str) -> List[Dict[str, Any]]:
        """
        从长期记忆加载对话历史

        Args:
            session_id: 会话 ID

        Returns:
            消息列表
        """
        long_term_file = self.memory_dir / f"{session_id}.json"

        if not long_term_file.exists():
            return []

        try:
            with open(long_term_file, "r", encoding="utf-8") as f:
                history = json.load(f)

            # 检查是否过期
            if self.long_term_expire_days > 0:
                expire_time = time.time() - (self.long_term_expire_days * 24 * 60 * 60)

                # 过滤过期消息
                history = [msg for msg in history if msg["timestamp"] > expire_time]

                # 如果有过期消息，更新文件
                with open(long_term_file, "r", encoding="utf-8") as f:
                    original_length = len(json.load(f))

                if len(history) < original_length:
                    with open(long_term_file, "w", encoding="utf-8") as f:
                        json.dump(history, f, ensure_ascii=False, indent=2)

            return history
        except Exception as e:
            logger.error(f"❌ 加载长期记忆失败: {e}")
            return []

    def _clean_expired_memory(self) -> None:
        """清理过期记忆"""
        if self.long_term_expire_days <= 0:
            return

        expire_time = time.time() - (self.long_term_expire_days * 24 * 60 * 60)
        cleaned_count = 0

        for file in self.memory_dir.glob("*.json"):
            try:
                # 检查文件修改时间
                if file.stat().st_mtime < expire_time:
                    file.unlink()
                    cleaned_count += 1
                    logger.info(f"🗑️ 已清理过期记忆: {file.name}")
            except Exception as e:
                logger.error(f"❌ 清理过期记忆失败: {file.name}, 错误: {e}")

        if cleaned_count > 0:
            logger.info(f"✅ 已清理 {cleaned_count} 个过期会话")

    def export_conversation(
        self,
        session_id: str,
        output_file: Optional[str] = None
    ) -> str:
        """
        导出对话记录

        Args:
            session_id: 会话 ID
            output_file: 输出文件路径（可选）

        Returns:
            导出文件路径
        """
        history = self.get_conversation_history(session_id)

        if not history:
            raise ValueError(f"会话 {session_id} 不存在")

        # 默认输出文件
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"data/export/{session_id}_{timestamp}.json"

        # 创建输出目录
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 保存到文件
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        logger.info(f"📤 已导出对话记录: {output_path}")

        return str(output_path)


# 创建全局记忆管理器实例
_memory_manager: Optional[ConversationMemory] = None


def get_memory_manager() -> ConversationMemory:
    """获取全局记忆管理器实例"""
    global _memory_manager

    if _memory_manager is None:
        raise RuntimeError("记忆管理器未初始化，请先调用 init_memory_manager()")

    return _memory_manager


def init_memory_manager(
    memory_dir: str = "data/conversations",
    short_term_length: int = 10,
    long_term_expire_days: int = 30,
    auto_clean: bool = True
) -> ConversationMemory:
    """
    初始化全局记忆管理器

    Args:
        memory_dir: 记忆存储目录
        short_term_length: 短期记忆长度
        long_term_expire_days: 长期记忆过期时间
        auto_clean: 是否自动清理过期记忆

    Returns:
        记忆管理器实例
    """
    global _memory_manager

    _memory_manager = ConversationMemory(
        memory_dir=memory_dir,
        short_term_length=short_term_length,
        long_term_expire_days=long_term_expire_days,
        auto_clean=auto_clean
    )

    logger.info("✅ 全局记忆管理器已初始化")

    return _memory_manager
