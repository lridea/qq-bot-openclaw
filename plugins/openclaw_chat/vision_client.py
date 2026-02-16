#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vision AI 调用客户端
调用支持视觉的 AI 模型识别图片
"""

import httpx
import base64
import os
from typing import Optional, Dict, Any
from .image_processor import ImageData, check_vision_support
from nonebot.log import logger


class VisionAIClient:
    """Vision AI 调用客户端"""
    
    def __init__(self, api_key: str, provider: str = "openai", base_url: Optional[str] = None):
        """
        初始化 Vision AI 客户端
        
        Args:
            api_key: API Key
            provider: 供应商（openai/anthropic/google/zhipu/siliconflow）
            base_url: API 基础 URL（可选）
        """
        self.api_key = api_key
        self.provider = provider
        self.base_url = base_url or self._get_default_url(provider)
    
    def _get_default_url(self, provider: str) -> str:
        """获取默认 API URL"""
        urls = {
            "openai": "https://api.openai.com/v1/chat/completions",
            "anthropic": "https://api.anthropic.com/v1/messages",
            "google": "https://generativelanguage.googleapis.com/v1beta/models",
            "zhipu": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            "siliconflow": "https://api.siliconflow.cn/v1/chat/completions",
            "ohmygpt": "https://api.ohmygpt.com/v1/chat/completions"
        }
        return urls.get(provider, urls["openai"])
    
    async def recognize_image(
        self,
        image_data: ImageData,
        prompt: str = "请描述这张图片",
        model: str = "gpt-4o-mini"
    ) -> str:
        """
        识别图片
        
        Args:
            image_data: 图片数据（ImageData 对象）
            prompt: 提示词
            model: 模型名称
        
        Returns:
            str: AI 的识别结果
        """
        
        # 检查模型是否支持 Vision
        if not check_vision_support(model):
            logger.warning(f"⚠️ 模型 {model} 不支持 Vision 能力")
            return f"抱歉，模型 {model} 不支持图片识别功能。\n\n支持图片识别的模型：\n• GPT-4o / GPT-4o-mini\n• GLM-4V\n• Claude 3 系列\n• Gemini Pro Vision\n• Qwen-VL"
        
        # 准备图片数据
        image_url = await self._prepare_image_url(image_data)
        if not image_url:
            logger.error("❌ 无法获取图片数据")
            return "抱歉，无法获取图片数据。"
        
        # 调用对应的 API
        try:
            if self.provider == "anthropic":
                return await self._call_anthropic(prompt, image_url, model)
            elif self.provider == "google":
                return await self._call_google(prompt, image_url, model)
            else:
                # OpenAI 兼容 API（包括智谱、硅基流动等）
                return await self._call_openai_compatible(prompt, image_url, model)
                
        except httpx.TimeoutException:
            logger.error(f"❌ {self.provider} Vision API 超时")
            return f"抱歉，图片识别超时，请稍后再试。"
        except Exception as e:
            logger.error(f"❌ Vision API 调用失败: {e}")
            return f"抱歉，图片识别失败：{str(e)}"
    
    async def _prepare_image_url(self, image_data: ImageData) -> Optional[str]:
        """准备图片 URL（统一格式）"""
        
        if image_data.url:
            # 如果是 http/https URL，直接使用
            if image_data.url.startswith(("http://", "https://")):
                return image_data.url
            # 如果已经是 data URL，直接使用
            elif image_data.url.startswith("data:"):
                return image_data.url
        
        elif image_data.base64:
            # Base64 格式，添加 data URL 前缀
            return f"data:image/jpeg;base64,{image_data.base64}"
        
        elif image_data.file_path:
            # 本地文件，读取并转换为 base64
            try:
                with open(image_data.file_path, "rb") as f:
                    image_base64 = base64.b64encode(f.read()).decode('utf-8')
                    return f"data:image/jpeg;base64,{image_base64}"
            except Exception as e:
                logger.error(f"❌ 读取本地图片失败: {e}")
                return None
        
        return None
    
    async def _call_openai_compatible(self, prompt: str, image_url: str, model: str) -> str:
        """调用 OpenAI 兼容 API"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            "max_tokens": 1000
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.base_url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                reply = result["choices"][0]["message"]["content"]
                logger.info(f"✅ {self.provider} Vision 回复成功: {reply[:50]}...")
                return reply
            else:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_msg = error_data.get("error", {}).get("message", response.text)
                logger.error(f"❌ {self.provider} Vision API 错误: {response.status_code} - {error_msg}")
                return f"抱歉，{self.provider} Vision 服务出错（{response.status_code}）"
    
    async def _call_anthropic(self, prompt: str, image_url: str, model: str) -> str:
        """调用 Anthropic Claude API"""
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # 提取 base64 数据
        if image_url.startswith("data:"):
            image_base64 = image_url.split(",")[1]
        else:
            # 如果是 URL，需要下载
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    image_bytes = await resp.read()
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        data = {
            "model": model,
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.base_url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                reply = result["content"][0]["text"]
                logger.info(f"✅ Claude Vision 回复成功: {reply[:50]}...")
                return reply
            else:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_msg = error_data.get("error", {}).get("message", response.text)
                logger.error(f"❌ Claude Vision API 错误: {response.status_code} - {error_msg}")
                return f"抱歉，Claude Vision 服务出错（{response.status_code}）"
    
    async def _call_google(self, prompt: str, image_url: str, model: str) -> str:
        """调用 Google Gemini API"""
        
        # 提取 base64 数据
        if image_url.startswith("data:"):
            image_base64 = image_url.split(",")[1]
        else:
            # 如果是 URL，需要下载
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    image_bytes = await resp.read()
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        url = f"{self.base_url}/{model}:generateContent?key={self.api_key}"
        
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                reply = result["candidates"][0]["content"]["parts"][0]["text"]
                logger.info(f"✅ Google Vision 回复成功: {reply[:50]}...")
                return reply
            else:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_msg = error_data.get("error", {}).get("message", response.text)
                logger.error(f"❌ Google Vision API 错误: {response.status_code} - {error_msg}")
                return f"抱歉，Google Vision 服务出错（{response.status_code}）"
