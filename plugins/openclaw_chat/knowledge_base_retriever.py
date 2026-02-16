#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库检索管理器
优化检索结果，实现结果排序和过滤，添加检索缓存
"""

import time
import hashlib
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
from nonebot.log import logger


@dataclass
class SearchCacheItem:
    """检索缓存项"""

    query: str  # 查询文本
    kb_id: str  # 知识库 ID
    results: List[Dict[str, Any]]  # 检索结果
    timestamp: float  # 时间戳
    ttl: int = 300  # 缓存过期时间（秒）

    def is_expired(self) -> bool:
        """
        检查是否过期

        Returns:
            bool: 是否过期
        """
        return time.time() - self.timestamp > self.ttl


@dataclass
class SearchContext:
    """检索上下文"""

    query: str  # 查询文本
    kb_id: str  # 知识库 ID
    top_k: int = 3  # 返回结果数量
    min_score: float = 0.0  # 最小相似度分数
    filters: Optional[Dict[str, Any]] = None  # 过滤条件
    sort_by: str = "score"  # 排序方式（score/relevance/time）
    use_cache: bool = True  # 是否使用缓存


class KnowledgeBaseRetriever:
    """知识库检索管理器"""

    def __init__(
        self,
        cache_ttl: int = 300,
        cache_size: int = 1000
    ):
        """
        初始化知识库检索管理器

        Args:
            cache_ttl: 缓存过期时间（秒，默认 5 分钟）
            cache_size: 缓存大小（默认 1000）
        """
        self.cache_ttl = cache_ttl
        self.cache_size = cache_size

        # 缓存：key -> SearchCacheItem
        self._cache: Dict[str, SearchCacheItem] = {}

        # 缓存访问时间（用于 LRU）
        self._cache_access_time: Dict[str, float] = {}

        # 缓存命中统计
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }

        logger.info(f"✅ 知识库检索管理器初始化成功（TTL: {cache_ttl}s, Size: {cache_size}）")

    def _generate_cache_key(
        self,
        query: str,
        kb_id: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        生成缓存键

        Args:
            query: 查询文本
            kb_id: 知识库 ID
            top_k: 返回结果数量
            filters: 过滤条件

        Returns:
            str: 缓存键
        """
        # 将参数组合成字符串
        params = f"{query}:{kb_id}:{top_k}:{str(filters)}"

        # 生成哈希
        return hashlib.md5(params.encode('utf-8')).hexdigest()

    def _get_from_cache(
        self,
        query: str,
        kb_id: str,
        top_k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        从缓存获取结果

        Args:
            query: 查询文本
            kb_id: 知识库 ID
            top_k: 返回结果数量
            filters: 过滤条件

        Returns:
            List[Dict[str, Any]]: 检索结果（缓存未命中则返回 None）
        """
        cache_key = self._generate_cache_key(query, kb_id, top_k, filters)

        if cache_key not in self._cache:
            self._cache_stats["misses"] += 1
            return None

        cache_item = self._cache[cache_key]

        # 检查是否过期
        if cache_item.is_expired():
            # 移除过期项
            del self._cache[cache_key]
            self._cache_stats["misses"] += 1
            return None

        # 更新访问时间
        self._cache_access_time[cache_key] = time.time()
        self._cache_stats["hits"] += 1

        logger.debug(f"✅ 缓存命中: {cache_key[:8]}...")

        return cache_item.results

    def _add_to_cache(
        self,
        query: str,
        kb_id: str,
        results: List[Dict[str, Any]],
        top_k: int = 3,
        filters: Optional[Dict[str, Any]] = None
    ):
        """
        添加结果到缓存

        Args:
            query: 查询文本
            kb_id: 知识库 ID
            results: 检索结果
            top_k: 返回结果数量
            filters: 过滤条件
        """
        # 检查缓存大小
        if len(self._cache) >= self.cache_size:
            self._evict_lru()

        cache_key = self._generate_cache_key(query, kb_id, top_k, filters)

        # 添加到缓存
        cache_item = SearchCacheItem(
            query=query,
            kb_id=kb_id,
            results=results,
            timestamp=time.time(),
            ttl=self.cache_ttl
        )

        self._cache[cache_key] = cache_item
        self._cache_access_time[cache_key] = time.time()

        logger.debug(f"✅ 添加到缓存: {cache_key[:8]}... (结果数: {len(results)})")

    def _evict_lru(self):
        """移除最久未使用的缓存项（LRU）"""
        if not self._cache:
            return

        # 找到最久未使用的缓存项
        lru_key = min(self._cache_access_time, key=self._cache_access_time.get)

        # 移除
        del self._cache[lru_key]
        del self._cache_access_time[lru_key]

        self._cache_stats["evictions"] += 1

        logger.debug(f"✅ 移除 LRU 缓存项: {lru_key[:8]}...")

    # ========== 检索优化 ==========

    def post_process_results(
        self,
        results: List[Dict[str, Any]],
        context: SearchContext
    ) -> List[Dict[str, Any]]:
        """
        后处理检索结果

        Args:
            results: 原始检索结果
            context: 检索上下文

        Returns:
            List[Dict[str, Any]]: 处理后的结果
        """
        if not results:
            return []

        # 1. 过滤
        filtered_results = self._filter_results(results, context)

        # 2. 排序
        sorted_results = self._sort_results(filtered_results, context)

        # 3. 限制数量
        limited_results = sorted_results[:context.top_k]

        # 4. 去重
        deduplicated_results = self._deduplicate_results(limited_results)

        return deduplicated_results

    def _filter_results(
        self,
        results: List[Dict[str, Any]],
        context: SearchContext
    ) -> List[Dict[str, Any]]:
        """
        过滤检索结果

        Args:
            results: 原始检索结果
            context: 检索上下文

        Returns:
            List[Dict[str, Any]]: 过滤后的结果
        """
        filtered = []

        for result in results:
            # 检查最小分数
            if result.get("score") and result["score"] < context.min_score:
                continue

            # 检查自定义过滤条件
            if context.filters:
                if not self._match_filters(result, context.filters):
                    continue

            filtered.append(result)

        logger.debug(f"✅ 过滤结果: {len(results)} -> {len(filtered)}")

        return filtered

    def _match_filters(
        self,
        result: Dict[str, Any],
        filters: Dict[str, Any]
    ) -> bool:
        """
        匹配过滤条件

        Args:
            result: 检索结果
            filters: 过滤条件

        Returns:
            bool: 是否匹配
        """
        metadata = result.get("metadata", {})

        for key, value in filters.items():
            if key not in metadata:
                return False

            if metadata[key] != value:
                return False

        return True

    def _sort_results(
        self,
        results: List[Dict[str, Any]],
        context: SearchContext
    ) -> List[Dict[str, Any]]:
        """
        排序检索结果

        Args:
            results: 检索结果
            context: 检索上下文

        Returns:
            List[Dict[str, Any]]: 排序后的结果
        """
        if context.sort_by == "score":
            # 按相似度分数排序（升序）
            return sorted(results, key=lambda x: x.get("score", float('inf')))

        elif context.sort_by == "relevance":
            # 按相关性排序（考虑多个因素）
            return sorted(
                results,
                key=lambda x: self._calculate_relevance(x, context.query)
            )

        else:
            # 默认按分数排序
            return results

    def _calculate_relevance(
        self,
        result: Dict[str, Any],
        query: str
    ) -> float:
        """
        计算相关性分数

        Args:
            result: 检索结果
            query: 查询文本

        Returns:
            float: 相关性分数（越低越相关）
        """
        # 基础分数（相似度）
        score = result.get("score", 1.0)

        # 文本长度因子（越短越相关）
        text_length = len(result.get("text", ""))
        length_factor = text_length / 1000.0  # 归一化

        # 关键词匹配因子
        keywords = query.split()
        text = result.get("text", "").lower()

        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text)
        keyword_factor = 1.0 - (keyword_matches / len(keywords)) if keywords else 0.0

        # 综合分数
        relevance = score * (1.0 + length_factor) * (1.0 + keyword_factor)

        return relevance

    def _deduplicate_results(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        去重检索结果

        Args:
            results: 检索结果

        Returns:
            List[Dict[str, Any]]: 去重后的结果
        """
        seen = set()
        deduplicated = []

        for result in results:
            # 使用文本作为去重依据
            text = result.get("text", "")

            if text not in seen:
                seen.add(text)
                deduplicated.append(result)

        logger.debug(f"✅ 去重结果: {len(results)} -> {len(deduplicated)}")

        return deduplicated

    # ========== 检索接口 ==========

    async def retrieve(
        self,
        vector_db,
        context: SearchContext
    ) -> List[Dict[str, Any]]:
        """
        检索知识库

        Args:
            vector_db: 向量数据库管理器
            context: 检索上下文

        Returns:
            List[Dict[str, Any]]: 检索结果
        """
        # 检查缓存
        if context.use_cache:
            cached_results = self._get_from_cache(
                query=context.query,
                kb_id=context.kb_id,
                top_k=context.top_k,
                filters=context.filters
            )

            if cached_results is not None:
                logger.info(f"✅ 缓存命中: {context.kb_id}")
                return cached_results

        # 执行检索
        logger.info(f"🔍 检索知识库: {context.kb_id}")

        # 构建元数据过滤条件
        where = None
        if context.filters:
            where = context.filters

        # 调用向量数据库搜索
        raw_results = vector_db.search(
            kb_id=context.kb_id,
            query=context.query,
            top_k=context.top_k * 2,  # 获取更多结果，后处理后筛选
            where=where
        )

        # 后处理
        processed_results = self.post_process_results(raw_results, context)

        # 添加到缓存
        if context.use_cache:
            self._add_to_cache(
                query=context.query,
                kb_id=context.kb_id,
                results=processed_results,
                top_k=context.top_k,
                filters=context.filters
            )

        logger.info(f"✅ 检索完成: {len(processed_results)} 个结果")

        return processed_results

    # ========== 缓存管理 ==========

    def clear_cache(self, kb_id: Optional[str] = None):
        """
        清空缓存

        Args:
            kb_id: 知识库 ID（None 则清空所有）
        """
        if kb_id is None:
            # 清空所有缓存
            self._cache.clear()
            self._cache_access_time.clear()
            logger.info("✅ 清空所有缓存")
        else:
            # 清空指定知识库的缓存
            keys_to_remove = [
                key for key, item in self._cache.items()
                if item.kb_id == kb_id
            ]

            for key in keys_to_remove:
                del self._cache[key]
                if key in self._cache_access_time:
                    del self._cache_access_time[key]

            logger.info(f"✅ 清空缓存: {kb_id} ({len(keys_to_remove)} 项)")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计

        Returns:
            Dict[str, Any]: 缓存统计
        """
        hit_rate = 0.0

        total_requests = self._cache_stats["hits"] + self._cache_stats["misses"]
        if total_requests > 0:
            hit_rate = self._cache_stats["hits"] / total_requests

        return {
            "size": len(self._cache),
            "max_size": self.cache_size,
            "hits": self._cache_stats["hits"],
            "misses": self._cache_stats["misses"],
            "evictions": self._cache_stats["evictions"],
            "hit_rate": hit_rate,
            "ttl": self.cache_ttl
        }

    def print_cache_stats(self) -> str:
        """
        打印缓存统计

        Returns:
            str: 缓存统计文本
        """
        stats = self.get_cache_stats()

        lines = [
            "📊 缓存统计",
            "=" * 30,
            f"缓存大小: {stats['size']}/{stats['max_size']}",
            f"命中次数: {stats['hits']}",
            f"未命中次数: {stats['misses']}",
            f"淘汰次数: {stats['evictions']}",
            f"命中率: {stats['hit_rate']:.2%}",
            f"TTL: {stats['ttl']}秒"
        ]

        return "\n".join(lines)
