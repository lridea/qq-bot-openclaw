#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 OpenClaw API 连接
"""

import httpx
import asyncio

async def test_api():
    """测试 OpenClaw API 连接"""
    api_url = "http://8.149.57.30:8000/api/openclaw/chat"
    api_key = "openclaw_qqbot_2026_key"
    
    print(f"测试 API 连接: {api_url}")
    
    try:
        # 测试网络连接
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "prompt": "你好",
                    "user_id": "test",
                    "group_id": "test"
                }
            )
            
            print(f"HTTP 状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                print("✅ API 连接成功！")
            else:
                print("❌ API 连接失败！")
                
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        
if __name__ == "__main__":
    asyncio.run(test_api())
