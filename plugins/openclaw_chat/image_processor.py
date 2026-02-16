#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片处理模块
处理 QQ 消息中的图片，并调用支持视觉的 AI 模型识别
"""

import base64
import re
import os
import logging
from typing import Optional, List, Dict, Any
from nonebot.adapters.onebot.v11 import Bot, Event

logger = logging.getLogger(__name__)


# 支持 Vision 能力的 AI 模型
VISION_MODELS = {
    "openai": {
        "models": ["gpt-4o", "gpt-4-vision-preview", "gpt-4o-mini"],
        "api_type": "openai",
        "support_vision": True
    },
    "claude": {
        "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3.5-opus"],
        "api_type": "anthropic",
        "support_vision": True
    },
    "google": {
        "models": ["gemini-pro-vision", "gemini-1.5-pro-vision"],
        "api_type": "google",
        "support_vision": True
    },
    "zhipu": {
        "models": ["glm-4v", "glm-4v-plus"],
        "api_type": "zhipu",
        "support_vision": True
    },
    "deepseek": {
        "models": ["deepseek-vl-chat"],
        "api_type": "deepseek",
        "support_vision": False  # DeepSeek 可能不支持 vision
    },
    "siliconflow": {
        "models": ["Qwen/Qwen2-VL-7B-Instruct", "Qwen/Qwen2-VL-72B-Instruct"],
        "api_type": "openai_compatible",
        "support_vision": True
    }
}


class ImageData:
    """图片数据类"""
    
    def __init__(self, url: Optional[str] = None, base64: Optional[str] = None, 
                 file_path: Optional[str] = None):
        self.url = url
        self.base64 = base64
        self.file_path = file_path
    
    def has_data(self) -> bool:
        """检查是否有图片数据"""
        return bool(self.url or self.base64 or self.file_path)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "url": self.url,
            "base64": self.base64,
            "file_path": self.file_path
        }


async def extract_image_from_message(bot: Bot, event: Event) -> Optional[ImageData]:
    """
    从 QQ 消息中提取图片数据
    
    Args:
        bot: Bot 实例
        event: Event 事件
    
    Returns:
        ImageData: 图片数据，如果没有图片则返回 None
    """
    message = event.get_message()
    
    for seg in message:
        if seg.type == "image":
            image_data = seg.data
            
            # 方式1：URL 链接
            if "url" in image_data and image_data["url"]:
                logger.info(f"✨ 提取到图片 URL: {image_data['url']}")
                return ImageData(url=image_data["url"])
            
            # 方式2：Base64 编码
            if "file" in image_data:
                file = image_data["file"]
                
                # 检查 base64:// 前缀
                if file.startswith("base64://"):
                    base64_data = file.replace("base64://", "")
                    logger.info(f"✨ 提取到 Base64 图片数据")
                    return ImageData(base64=base64_data)
                
                # 检查是否已经是 base64 格式（较长且有 == 结尾）
                if len(file) > 100 and re.search(r"==={0,2}$", file):
                    logger.info(f"✨ 检测到 Base64 图片数据")
                    return ImageData(base64=file)
                
                # 方式3：本地文件（尝试通过 OneBot API 获取）
                logger.info(f"📄 检测到本地图片文件，尝试通过 API 获取 URL...")
                try:
                    # 调用 OneBot API 获取图片信息
                    image_info = await bot.call_api("get_image", file=file)
                    
                    if image_info and "url" in image_info:
                        logger.info(f"✅ 成功获取图片 URL: {image_info['url']}")
                        return ImageData(url=image_info["url"])
                    else:
                        logger.warning(f"⚠️ 无法获取图片 URL: {image_info}")
                        return None
                        
                except Exception as e:
                    logger.error(f"❌ 获取图片 URL 失败: {e}")
                    return None
    
    logger.info("ℹ️ 消息中没有图片")
    return None


def get_base64_from_url(image_url: str) -> str:
    """
    将图片 URL 转换为 Base64 编码
    
    Args:
        image_url: 图片 URL
    
    Returns:
        str: Base64 编码的图片数据
    """
    import requests
    
    try:
        # 下载图片
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # 转换为 base64
        image_base64 = base64.b64encode(response.content).decode('utf-8')
        
        # 检测图片类型
        content_type = response.headers.get('content-type', 'image/jpeg')
        
        return f"data:{content_type};base64,{image_base64}"
        
    except Exception as e:
        logger.error(f"❌ 下载图片并转换为 Base64 失败: {e}")
        return ""


def check_vision_support(model: str) -> bool:
    """
    检查模型是否支持 Vision 能力
    
    Args:
        model: 模型名称
    
    Returns:
        bool: 是否支持 Vision
    """
    # 检查各个供应商的 vision 模型
    for provider, config in VISION_MODELS.items():
        if model in config["models"]:
            return config["support_vision"]
    
    return False


def get_vision_models() -> List[str]:
    """
    获取所有支持 Vision 的模型列表
    
    Returns:
        List[str]: 模型名称列表
    """
    models = []
    for config in VISION_MODELS.values():
        if config["support_vision"]:
            models.extend(config["models"])
    return models


async def download_image(image_url: str, save_dir: str = "temp/images") -> Optional[str]:
    """
    下载图片并保存到本地
    
    Args:
        image_url: 图片 URL
        save_dir: 保存目录
    
    Returns:
        str: 保存的文件路径，失败返回 None
    """
    import aiohttp
    import time
    
    try:
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)
        
        # 生成文件名
        filename = f"{int(time.time())}.jpg"
        filepath = os.path.join(save_dir, filename)
        
        # 下载图片
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    with open(filepath, "wb") as f:
                        f.write(await resp.read())
                    logger.info(f"✅ 图片已下载: {filepath}")
                    return filepath
                else:
                    logger.error(f"❌ 下载图片失败: HTTP {resp.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"❌ 下载图片异常: {e}")
        return None


def create_vision_message(prompt: str, image_data: ImageData) -> Dict[str, Any]:
    """
    创建 Vision API 的消息格式
    
    Args:
        prompt: 用户提示词
        image_data: 图片数据
    
    Returns:
        Dict: API 消息格式
    """
    # 构建消息
    content = [
        {"type": "text", "text": prompt}
    ]
    
    # 添加图片
    if image_data.url:
        # URL 格式
        content.append({
            "type": "image_url",
            "image_url": {"url": image_data.url}
        })
    elif image_data.base64:
        # Base64 格式
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_data.base64}"}
        })
    elif image_data.file_path:
        # 本地文件格式（需要先读取）
        try:
            with open(image_data.file_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode('utf-8')
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                })
        except Exception as e:
            logger.error(f"❌ 读取本地图片失败: {e}")
    
    return {
        "role": "user",
        "content": content
    }
