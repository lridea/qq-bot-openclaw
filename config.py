#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
从环境变量加载配置（支持多模型 + 智能触发）
"""

import os
import json
from typing import List, Optional, Dict
from pydantic import BaseModel
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class IntelligentTriggerConfig(BaseModel):
    """智能触发配置"""
    enabled: bool = True  # 是否启用智能触发
    require_mention: bool = False  # 是否强制要求@
    mention_patterns: List[str] = [  # 触发模式（正则表达式）
        "[？?]",  # 包含问号
        "(有人|谁|怎么|如何|为什么|求|帮|解答|请教)",  # 疑问/求助词
        "(@机器人|@[Aa][Uu][Tt][Oo]|@[Bb][Oo][Tt])"  # 显式触发
    ]
    history_limit: int = 20  # 查看最近多少条消息作为上下文


class GroupConfig(BaseModel):
    """群组配置"""
    trigger_config: Optional[IntelligentTriggerConfig] = None  # 该群的智能触发配置（覆盖默认）


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
    
    # ========== 智能触发配置 ==========
    intelligent_trigger_enabled: bool = os.getenv("INTELLIGENT_TRIGGER_ENABLED", "true").lower() == "true"
    intelligent_trigger_require_mention: bool = os.getenv("INTELLIGENT_TRIGGER_REQUIRE_MENTION", "false").lower() == "true"
    intelligent_trigger_patterns: List[str] = eval(os.getenv("INTELLIGENT_TRIGGER_PATTERNS", '["[？?]", "(有人|谁|怎么|如何|为什么|求|帮|解答|请教)", "(@机器人|@[Aa][Uu][Tt][Oo]|@[Bb][Oo][Tt])"]'))
    intelligent_trigger_history_limit: int = int(os.getenv("INTELLIGENT_TRIGGER_HISTORY_LIMIT", "20"))
    
    # 群组配置文件路径
    group_config_file: str = os.getenv("GROUP_CONFIG_FILE", "group_configs.json")
    
    # ========== 简洁模式配置 ==========
    reply_mode: str = os.getenv("REPLY_MODE", "normal")  # normal/concise/detailed
    reply_max_length: int = int(os.getenv("REPLY_MAX_LENGTH", "500"))  # 回复最大字符数
    concise_mode_patterns: List[str] = eval(os.getenv("CONCISE_MODE_PATTERNS", '["[？?]", "(怎么|如何|为什么)"]'))  # 简洁模式触发模式
    
    # 群组配置（运行时加载）
    _group_configs: Dict[str, GroupConfig] = {}
    
    def load_group_configs(self):
        """从文件加载群组配置"""
        try:
            if os.path.exists(self.group_config_file):
                with open(self.group_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._group_configs = {
                        group_id: GroupConfig(**config_data)
                        for group_id, config_data in data.items()
                    }
        except Exception as e:
            print(f"⚠️  加载群组配置失败: {e}")
            self._group_configs = {}
    
    def save_group_configs(self):
        """保存群组配置到文件"""
        try:
            with open(self.group_config_file, 'w', encoding='utf-8') as f:
                data = {
                    group_id: config.dict()
                    for group_id, config in self._group_configs.items()
                }
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  保存群组配置失败: {e}")
    
    def get_group_trigger_config(self, group_id: str) -> IntelligentTriggerConfig:
        """获取群组的智能触发配置（如果未配置则使用默认配置）"""
        if group_id in self._group_configs and self._group_configs[group_id].trigger_config:
            return self._group_configs[group_id].trigger_config
        
        # 返回默认配置
        return IntelligentTriggerConfig(
            enabled=self.intelligent_trigger_enabled,
            require_mention=self.intelligent_trigger_require_mention,
            mention_patterns=self.intelligent_trigger_patterns,
            history_limit=self.intelligent_trigger_history_limit
        )
    
    def set_group_trigger_config(self, group_id: str, trigger_config: IntelligentTriggerConfig):
        """设置群组的智能触发配置"""
        if group_id not in self._group_configs:
            self._group_configs[group_id] = GroupConfig()
        self._group_configs[group_id].trigger_config = trigger_config
        self.save_group_configs()
    
    def remove_group_config(self, group_id: str):
        """移除群组配置（恢复默认）"""
        if group_id in self._group_configs:
            del self._group_configs[group_id]
            self.save_group_configs()
    
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
        
        # 加载群组配置
        self.load_group_configs()
        
        # 打印智能触发配置
        if self.intelligent_trigger_enabled:
            print("✅ 智能触发模式已启用")
            print(f"   • 触发模式: {', '.join(self.intelligent_trigger_patterns[:2])}...")
            print(f"   • 历史上下文: {self.intelligent_trigger_history_limit} 条消息")
        else:
            print("⚠️  智能触发模式已禁用")
        
        return True  # 允许没有配置的情况下使用回退模式


# 创建全局配置实例
config = Config()

# 验证配置
config.validate_config()
