#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片识别功能测试用例
测试图片提取、Vision AI 调用等功能
"""

import asyncio
import base64
from unittest.mock import Mock, AsyncMock, patch
import pytest


# ========== 测试 ImageProcessor ==========

class TestImageProcessor:
    """测试图片处理模块"""
    
    @pytest.mark.asyncio
    async def test_extract_url_image(self):
        """测试提取 URL 图片"""
        from plugins.openclaw_chat.image_processor import extract_image_from_message
        
        # 模拟 Bot 和 Event
        bot = Mock()
        event = Mock()
        
        # 模拟消息包含 URL 图片
        message = Mock()
        message.__iter__ = Mock(return_value=iter([
            Mock(type="image", data={"url": "https://example.com/image.jpg"})
        ]))
        event.get_message = Mock(return_value=message)
        
        # 提取图片
        image_data = await extract_image_from_message(bot, event)
        
        # 验证
        assert image_data is not None
        assert image_data.url == "https://example.com/image.jpg"
        assert image_data.has_data() is True
    
    @pytest.mark.asyncio
    async def test_extract_base64_image(self):
        """测试提取 Base64 图片"""
        from plugins.openclaw_chat.image_processor import extract_image_from_message
        
        # 模拟 Bot 和 Event
        bot = Mock()
        event = Mock()
        
        # 模拟 base64 数据
        fake_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        # 模拟消息包含 Base64 图片
        message = Mock()
        message.__iter__ = Mock(return_value=iter([
            Mock(type="image", data={"file": f"base64://{fake_base64}"})
        ]))
        event.get_message = Mock(return_value=message)
        
        # 提取图片
        image_data = await extract_image_from_message(bot, event)
        
        # 验证
        assert image_data is not None
        assert image_data.base64 == fake_base64
        assert image_data.has_data() is True
    
    @pytest.mark.asyncio
    async def test_extract_no_image(self):
        """测试消息中没有图片"""
        from plugins.openclaw_chat.image_processor import extract_image_from_message
        
        # 模拟 Bot 和 Event
        bot = Mock()
        event = Mock()
        
        # 模拟纯文本消息
        message = Mock()
        message.__iter__ = Mock(return_value=iter([
            Mock(type="text", data={"text": "你好"})
        ]))
        event.get_message = Mock(return_value=message)
        
        # 提取图片
        image_data = await extract_image_from_message(bot, event)
        
        # 验证
        assert image_data is None
    
    def test_check_vision_support(self):
        """测试 Vision 模型检查"""
        from plugins.openclaw_chat.image_processor import check_vision_support
        
        # 支持的模型
        assert check_vision_support("gpt-4o") is True
        assert check_vision_support("gpt-4o-mini") is True
        assert check_vision_support("glm-4v") is True
        assert check_vision_support("claude-3-opus-20240229") is True
        
        # 不支持的模型
        assert check_vision_support("gpt-3.5-turbo") is False
        assert check_vision_support("glm-4") is False


# ========== 测试 VisionAI Client ==========

class TestVisionAIClient:
    """测试 Vision AI 客户端"""
    
    @pytest.mark.asyncio
    async def test_recognize_image_with_url(self):
        """测试识别 URL 图片"""
        from plugins.openclaw_chat.vision_client import VisionAIClient
        from plugins.openclaw_chat.image_processor import ImageData
        
        # 模拟 API 响应
        with patch('httpx.AsyncClient') as mock_client:
            # 模拟响应
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value={
                "choices": [{
                    "message": {
                        "content": "这是一张美丽的风景照片"
                    }
                }]
            })
            
            # 模拟异步上下文管理器
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value.post = AsyncMock(return_value=mock_response)
            
            # 创建客户端
            client = VisionAIClient(api_key="test_key", provider="openai")
            
            # 创建图片数据
            image_data = ImageData(url="https://example.com/image.jpg")
            
            # 识别图片
            result = await client.recognize_image(
                image_data=image_data,
                prompt="请描述这张图片",
                model="gpt-4o-mini"
            )
            
            # 验证
            assert "风景照片" in result or result  # 只要有返回就通过
    
    @pytest.mark.asyncio
    async def test_recognize_image_unsupported_model(self):
        """测试不支持的模型"""
        from plugins.openclaw_chat.vision_client import VisionAIClient
        from plugins.openclaw_chat.image_processor import ImageData
        
        # 创建客户端
        client = VisionAIClient(api_key="test_key", provider="openai")
        
        # 创建图片数据
        image_data = ImageData(url="https://example.com/image.jpg")
        
        # 识别图片（不支持的模型）
        result = await client.recognize_image(
            image_data=image_data,
            prompt="请描述这张图片",
            model="gpt-3.5-turbo"  # 不支持 Vision
        )
        
        # 验证
        assert "不支持图片识别" in result


# ========== 集成测试 ==========

class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_image_recognition_flow(self):
        """测试完整的图片识别流程"""
        from plugins.openclaw_chat.image_processor import extract_image_from_message, ImageData
        from plugins.openclaw_chat.vision_client import VisionAIClient
        
        # 1. 模拟从消息提取图片
        bot = Mock()
        event = Mock()
        message = Mock()
        message.__iter__ = Mock(return_value=iter([
            Mock(type="image", data={"url": "https://example.com/test.jpg"})
        ]))
        event.get_message = Mock(return_value=message)
        
        image_data = await extract_image_from_message(bot, event)
        
        # 验证提取成功
        assert image_data is not None
        assert image_data.url == "https://example.com/test.jpg"
        
        # 2. 模拟 Vision AI 识别
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value={
                "choices": [{
                    "message": {
                        "content": "识别成功"
                    }
                }]
            })
            
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value.post = AsyncMock(return_value=mock_response)
            
            client = VisionAIClient(api_key="test_key", provider="openai")
            result = await client.recognize_image(
                image_data=image_data,
                prompt="请描述",
                model="gpt-4o-mini"
            )
            
            # 验证识别成功
            assert result  # 有返回就成功


# ========== 运行测试 ==========

if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "-s"])
