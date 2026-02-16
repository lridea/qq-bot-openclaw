#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能触发检测模块
检测消息是否满足触发条件（疑问句、求助词等）
"""

import re
from typing import List, Optional
from nonebot.log import logger


class IntelligentTrigger:
    """智能触发检测器"""
    
    def __init__(self, patterns: List[str]):
        """
        初始化触发检测器
        
        Args:
            patterns: 触发模式列表（正则表达式）
        """
        self.patterns = patterns
        self.compiled_patterns = []
        
        # 预编译正则表达式
        for pattern in patterns:
            try:
                self.compiled_patterns.append(re.compile(pattern))
            except re.error as e:
                logger.warning(f"无效的正则表达式: {pattern}, 错误: {e}")
    
    def check_trigger(self, message: str) -> bool:
        """
        检查消息是否触发
        
        Args:
            message: 消息内容
        
        Returns:
            是否触发（True/False）
        """
        if not message:
            return False
        
        message = message.strip()
        
        # 检查所有触发模式
        for pattern in self.compiled_patterns:
            if pattern.search(message):
                logger.info(f"🎯 消息触发智能检测: 模式={pattern.pattern}, 消息={message[:30]}")
                return True
        
        return False
    
    def get_triggered_pattern(self, message: str) -> Optional[str]:
        """
        获取触发消息的模式（用于日志）
        
        Args:
            message: 消息内容
        
        Returns:
            触发的模式文本，未触发则返回 None
        """
        if not message:
            return None
        
        message = message.strip()
        
        for pattern in self.compiled_patterns:
            if pattern.search(message):
                return pattern.pattern
        
        return None


# 创建默认的触发检测器实例
_default_trigger = None


def get_default_trigger() -> IntelligentTrigger:
    """获取默认触发检测器（使用默认模式）"""
    global _default_trigger
    
    if _default_trigger is None:
        default_patterns = [
            "[？?]",  # 包含问号
            "(有人|谁|怎么|如何|为什么|求|帮|解答|请教)",  # 疑问/求助词
            "(@机器人|@[Aa][Uu][Tt][Oo]|@[Bb][Oo][Tt])"  # 显式触发
        ]
        _default_trigger = IntelligentTrigger(default_patterns)
    
    return _default_trigger


def create_trigger_from_config(config) -> IntelligentTrigger:
    """
    从配置创建触发检测器
    
    Args:
        config: 配置对象（包含 mention_patterns）
    
    Returns:
        触发检测器实例
    """
    patterns = getattr(config, 'mention_patterns', [])
    
    if not patterns:
        # 如果没有配置，使用默认
        return get_default_trigger()
    
    return IntelligentTrigger(patterns)
