#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
从环境变量加载配置（支持多模型）
"""

import os
from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Config(BaseModel):
    """机器人配置"""
    
    # AI 模型配置
    ai_model: str = os.getenv("AI_MODEL", "zhipu")  # zhipu/deepseek/siliconflow/ollama/moonshot/ohmygpt
    model_name: str = os.getenv("MODEL_NAME", "")  # 指定具体模型（可选）
    
    # 智谱 AI 配置
    openclaw_api_key: str = os.getenv("OPENCLAW_API_KEY", "")  # 兼容旧配置
    zhipu_api_key: str = os.getenv("ZHIPU_API_KEY", "") or os.getenv("OPENCLAW_API_KEY", "")
    
    # DeepSeek 配置
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    
    # 硅基流动配置
    siliconflow_api_key: str = os.getenv("SILICONFLOW_API_KEY", "")
    
    # Moonshot 配置
    moonshot_api_key: str = os.getenv("MOONSHOT_API_KEY", "")
    
    # OhMyGPT 配置
    ohmygpt_api_key: str = os.getenv("OHMYGPT_API_KEY", "")
    
    # Ollama 配置
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2")
    
    # API 配置（已废弃，但保留兼容）
    openclaw_api_url: str = os.getenv("OPENCLAW_API_URL", "http://localhost:8000/api/openclaw/chat")
    openclaw_api_timeout: int = int(os.getenv("OPENCLAW_API_TIMEOUT", "30"))
    
    # 机器人配置
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8080"))
    superusers: List[str] = eval(os.getenv("SUPERUSERS", "[]"))
    nickname: List[str] = eval(os.getenv("NICKNAME", "[\"OpenClaw\"]"))
    
    # NapCat 配置
    napcat_ws_url: str = os.getenv("NAPCAT_WS_URL", "ws://127.0.0.1:3001")
    
    # 日志配置
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "")
    
    # 高级配置
    command_start: List[str] = eval(os.getenv("COMMAND_START", '["/", ""]'))
    command_sep: List[str] = eval(os.getenv("COMMAND_SEP", '[\".\"]'))
    session_expire_timeout: int = int(os.getenv("SESSION_EXPIRE_TIMEOUT", "120"))
    
    @property
    def bot_name(self) -> str:
        """机器人名称"""
        return self.nickname[0] if self.nickname else "OpenClaw"
    
    @property
    def current_api_key(self) -> Optional[str]:
        """获取当前模型的 API Key"""
        if self.ai_model == "zhipu":
            return self.zhipu_api_key
        elif self.ai_model == "deepseek":
            return self.deepseek_api_key
        elif self.ai_model == "siliconflow":
            return self.siliconflow_api_key
        elif self.ai_model == "moonshot":
            return self.moonshot_api_key
        elif self.ai_model == "ohmygpt":
            return self.ohmygpt_api_key
        elif self.ai_model == "ollama":
            return None  # Ollama 不需要 API Key
        return None
    
    def validate_config(self) -> bool:
        """验证配置是否完整"""
        # 检查是否有任何 API Key 配置
        has_key = any([
            self.zhipu_api_key,
            self.deepseek_api_key,
            self.siliconflow_api_key,
            self.moonshot_api_key,
            self.ai_model == "ollama"  # Ollama 不需要 Key
        ])
        
        if not has_key:
            print("⚠️  警告: 未配置任何 AI API Key")
            print("   将使用简单回复模式")
            print("\n支持的模型：")
            print("  - zhipu: 智谱 AI（需要 API Key）")
            print("  - deepseek: DeepSeek（需要 API Key，有免费额度）")
            print("  - siliconflow: 硅基流动（需要 API Key，完全免费）")
            print("  - moonshot: Moonshot Kimi（需要 API Key，有免费额度）")
            print("  - ollama: Ollama 本地模型（无需 API Key，完全免费）")
        
        if not self.superusers:
            print("⚠️  警告: 未配置超级管理员")
        
        return True  # 允许没有配置的情况下使用回退模式


# 创建全局配置实例
config = Config()

# 验证配置
config.validate_config()
