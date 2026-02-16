#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wiki 解析器
解析泰拉瑞亚 Wiki 页面，提取游戏相关内容
"""

import re
import httpx
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse
from nonebot.log import logger


class WikiParser:
    """Wiki 解析器"""

    def __init__(
        self,
        base_url: str = "https://terraria.wiki.gg/zh/wiki/",
        timeout: int = 30
    ):
        """
        初始化 Wiki 解析器

        Args:
            base_url: Wiki 基础 URL
            timeout: 超时时间（秒）
        """
        self.base_url = base_url
        self.timeout = timeout
        self.client = None

    def _get_client(self) -> httpx.AsyncClient:
        """
        获取 HTTP 客户端

        Returns:
            httpx.AsyncClient: HTTP 客户端
        """
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=self.timeout)
        return self.client

    async def close(self):
        """关闭 HTTP 客户端"""
        if self.client is not None:
            await self.client.aclose()
            self.client = None

    # ========== 页面获取 ==========

    async def fetch_page(self, page_name: str) -> Optional[str]:
        """
        获取 Wiki 页面内容

        Args:
            page_name: 页面名称

        Returns:
            str: 页面 HTML 内容（失败则返回 None）
        """
        try:
            client = self._get_client()
            url = urljoin(self.base_url, page_name)

            response = await client.get(url)
            response.raise_for_status()

            logger.info(f"✅ 获取 Wiki 页面成功: {page_name}")

            return response.text

        except httpx.HTTPError as e:
            logger.error(f"❌ 获取 Wiki 页面失败 {page_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ 获取 Wiki 页面失败 {page_name}: {e}")
            return None

    async def fetch_multiple_pages(self, page_names: List[str]) -> Dict[str, str]:
        """
        批量获取 Wiki 页面内容

        Args:
            page_names: 页面名称列表

        Returns:
            Dict[str, str]: 页面名称 -> HTML 内容
        """
        results = {}

        for page_name in page_names:
            html = await self.fetch_page(page_name)

            if html is not None:
                results[page_name] = html

        return results

    # ========== 内容提取 ==========

    def extract_title(self, html: str) -> Optional[str]:
        """
        提取页面标题

        Args:
            html: HTML 内容

        Returns:
            str: 页面标题（失败则返回 None）
        """
        try:
            # 尝试多种方式提取标题
            patterns = [
                r'<h1[^>]*>(.*?)</h1>',
                r'<title>(.*?)</title>',
                r'id="firstHeading"[^>]*>(.*?)</'
            ]

            for pattern in patterns:
                match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)

                if match:
                    title = match.group(1)
                    # 清理 HTML 标签
                    title = re.sub(r'<[^>]+>', '', title)
                    # 清理多余空格
                    title = re.sub(r'\s+', ' ', title).strip()
                    return title

            return None

        except Exception as e:
            logger.error(f"❌ 提取标题失败: {e}")
            return None

    def extract_content(self, html: str) -> str:
        """
        提取页面主要内容

        Args:
            html: HTML 内容

        Returns:
            str: 页面主要内容
        """
        try:
            # 尝试提取主要内容区域
            # MediaWiki 通常使用以下结构
            content_patterns = [
                r'<div[^>]*class="[^"]*mw-parser-output[^"]*"[^>]*>(.*?)</div>',
                r'<div[^>]*id="content"[^>]*>(.*?)</div>',
                r'<div[^>]*class="[^"]*mw-content-text[^"]*"[^>]*>(.*?)</div>',
            ]

            content = ""

            for pattern in content_patterns:
                match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)

                if match:
                    content = match.group(1)
                    break

            # 如果没有匹配到主要内容，使用整个 HTML
            if not content:
                content = html

            # 清理 HTML 标签
            content = self._clean_html(content)

            return content

        except Exception as e:
            logger.error(f"❌ 提取内容失败: {e}")
            return ""

    def _clean_html(self, html: str) -> str:
        """
        清理 HTML 标签，提取纯文本

        Args:
            html: HTML 内容

        Returns:
            str: 纯文本内容
        """
        # 移除脚本和样式
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        html = re.sub(r'<noscript[^>]*>.*?</noscript>', '', html, flags=re.DOTALL)

        # 移除注释
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)

        # 移除 HTML 标签（保留文本）
        html = re.sub(r'<[^>]+>', ' ', html)

        # 清理多余空格和换行
        html = re.sub(r'\n+', '\n', html)
        html = re.sub(r'[ \t]+', ' ', html)
        html = re.sub(r'\n[ \t]+\n', '\n\n', html)

        # 去除首尾空格
        html = html.strip()

        return html

    def extract_infobox(self, html: str) -> Dict[str, str]:
        """
        提取信息框（Infobox）内容

        Args:
            html: HTML 内容

        Returns:
            Dict[str, str]: 信息框字段
        """
        try:
            infobox = {}

            # 匹配信息框表格
            pattern = r'<table[^>]*class="[^"]*infobox[^"]*"[^>]*>(.*?)</table>'
            match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)

            if not match:
                return infobox

            table = match.group(1)

            # 提取表格行
            row_pattern = r'<tr[^>]*>(.*?)</tr>'
            rows = re.findall(row_pattern, table, re.DOTALL)

            for row in rows:
                # 提取单元格
                cell_pattern = r'<t[dh][^>]*>(.*?)</t[dh]>'
                cells = re.findall(cell_pattern, row, re.DOTALL)

                if len(cells) >= 2:
                    key = self._clean_html(cells[0]).strip()
                    value = self._clean_html(cells[1]).strip()

                    if key and value:
                        infobox[key] = value

            return infobox

        except Exception as e:
            logger.error(f"❌ 提取信息框失败: {e}")
            return {}

    def extract_sections(self, html: str) -> List[Dict[str, Any]]:
        """
        提取页面章节

        Args:
            html: HTML 内容

        Returns:
            List[Dict[str, Any]]: 章节列表
        """
        try:
            sections = []

            # 匹配章节标题（h2, h3）
            pattern = r'<h([23])[^>]*>(.*?)</h\1>'
            matches = list(re.finditer(pattern, html, re.DOTALL))

            for i, match in enumerate(matches):
                level = int(match.group(1))
                title = self._clean_html(match.group(2)).strip()

                # 获取章节内容（从当前章节到下一个章节）
                start = match.end()

                if i + 1 < len(matches):
                    end = matches[i + 1].start()
                else:
                    end = len(html)

                content = html[start:end]
                content = self._clean_html(content)

                # 添加章节
                sections.append({
                    "level": level,
                    "title": title,
                    "content": content
                })

            return sections

        except Exception as e:
            logger.error(f"❌ 提取章节失败: {e}")
            return []

    def extract_links(self, html: str) -> List[str]:
        """
        提取页面链接

        Args:
            html: HTML 内容

        Returns:
            List[str]: 链接列表
        """
        try:
            links = []

            # 匹配内部链接
            pattern = r'href="(/wiki/([^"#]+))"'
            matches = re.findall(pattern, html)

            for url, page_name in matches:
                # 过滤特殊页面
                if not any(prefix in page_name for prefix in [':', '#', 'File:', 'Category:']):
                    links.append(page_name)

            # 去重
            links = list(set(links))

            return links

        except Exception as e:
            logger.error(f"❌ 提取链接失败: {e}")
            return []

    # ========== 文本分割 ==========

    def split_into_chunks(
        self,
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> List[Dict[str, Any]]:
        """
        将文本分割为小块

        Args:
            text: 原始文本
            chunk_size: 每块大小（字符数）
            chunk_overlap: 块之间重叠字符数

        Returns:
            List[Dict[str, Any]]: 文本块列表
        """
        chunks = []

        # 按段落分割
        paragraphs = re.split(r'\n\n+', text)

        current_chunk = ""
        current_index = 0

        for para in paragraphs:
            para = para.strip()

            if not para:
                continue

            # 如果当前块加上新段落超过大小限制
            if len(current_chunk) + len(para) + 1 > chunk_size and current_chunk:
                # 添加当前块
                chunk_text = current_chunk.strip()

                if chunk_text:
                    chunks.append({
                        "index": current_index,
                        "text": chunk_text,
                        "char_count": len(chunk_text)
                    })
                    current_index += 1

                # 重置当前块（保留重叠部分）
                if chunk_overlap > 0:
                    words = current_chunk.split()
                    overlap_words = words[-chunk_overlap:] if len(words) > chunk_overlap else words
                    current_chunk = " ".join(overlap_words) + " "
                else:
                    current_chunk = ""

            # 添加段落
            current_chunk += para + " "

        # 添加最后一个块
        if current_chunk.strip():
            chunk_text = current_chunk.strip()

            if chunk_text:
                chunks.append({
                    "index": current_index,
                    "text": chunk_text,
                    "char_count": len(chunk_text)
                })

        logger.info(f"✅ 文本分割完成: {len(chunks)} 个块")

        return chunks

    # ========== 页面解析 ==========

    async def parse_page(self, page_name: str) -> Optional[Dict[str, Any]]:
        """
        完整解析 Wiki 页面

        Args:
            page_name: 页面名称

        Returns:
            Dict[str, Any]: 页面解析结果
        """
        # 获取页面 HTML
        html = await self.fetch_page(page_name)

        if html is None:
            return None

        # 提取内容
        title = self.extract_title(html)
        content = self._clean_html(html)
        infobox = self.extract_infobox(html)
        sections = self.extract_sections(html)
        links = self.extract_links(html)

        # 分割文本为块
        chunks = self.split_into_chunks(content)

        return {
            "page_name": page_name,
            "url": urljoin(self.base_url, page_name),
            "title": title,
            "content": content,
            "infobox": infobox,
            "sections": sections,
            "links": links,
            "chunks": chunks
        }
