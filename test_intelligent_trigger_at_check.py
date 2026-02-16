#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智能触发的@检查功能
验证机器人不会误触发电@其他人的消息
"""


class MessageSegment:
    """模拟 MessageSegment"""

    def __init__(self, type, data=None):
        self.type = type
        self.data = data or {}

    def __repr__(self):
        return f"MessageSegment(type={self.type}, data={self.data})"


class Message:
    """模拟 Message"""

    def __init__(self, segments=None):
        self.segments = segments or []

    def __iter__(self):
        return iter(self.segments)

    def __str__(self):
        text_parts = []
        for seg in self.segments:
            if seg.type == 'text':
                data = seg.data
                if isinstance(data, dict):
                    text_parts.append(data.get('text', ''))
                else:
                    text_parts.append(str(data))
        return "".join(text_parts)


def test_at_check():
    """测试@检查逻辑"""

    print("=" * 60)
    print("🧪 测试智能触发的@检查功能")
    print("=" * 60)

    # 模拟机器人
    class MockBot:
        def __init__(self, self_id):
            self.self_id = self_id

    bot = MockBot(self_id=123456789)

    # 测试场景1：@机器人 + 疑问 → 应该触发
    print("\n📌 场景1：@机器人 + 疑问 → 应该触发")
    message_obj = Message([
        MessageSegment(type='at', data={'qq': '123456789'}),
        MessageSegment(type='text', data='你觉得这个游戏怎么样？')
    ])

    print(f"   消息: {message_obj}")

    has_at_other = False
    bot_self_id = str(bot.self_id) if hasattr(bot, 'self_id') else None

    for segment in message_obj:
        if segment.type == 'at':
            at_qq = segment.data.get('qq')
            if at_qq and bot_self_id and at_qq != bot_self_id:
                has_at_other = True
                break

    result = "✅ 不应该阻止（可以触发）" if not has_at_other else "❌ 应该阻止"
    print(f"   结果: {result}")
    print(f"   预期: ✅ 不应该阻止（可以触发）")
    print(f"   测试: {'✅ 通过' if not has_at_other else '❌ 失败'}")

    # 测试场景2：@其他人 + 疑问 → 不应该触发
    print("\n📌 场景2：@其他人 + 疑问 → 不应该触发")
    message_obj = Message([
        MessageSegment(type='at', data={'qq': '987654321'}),
        MessageSegment(type='text', data='你觉得这个游戏怎么样？')
    ])

    print(f"   消息: {message_obj}")

    has_at_other = False
    bot_self_id = str(bot.self_id) if hasattr(bot, 'self_id') else None

    for segment in message_obj:
        if segment.type == 'at':
            at_qq = segment.data.get('qq')
            if at_qq and bot_self_id and at_qq != bot_self_id:
                has_at_other = True
                break

    result = "✅ 应该阻止（不触发）" if has_at_other else "❌ 不应该阻止"
    print(f"   结果: {result}")
    print(f"   预期: ✅ 应该阻止（不触发）")
    print(f"   测试: {'✅ 通过' if has_at_other else '❌ 失败'}")

    # 测试场景3：直接问问题（无@）→ 应该触发
    print("\n📌 场景3：直接问问题（无@）→ 应该触发")
    message_obj = Message([
        MessageSegment(type='text', data='你觉得这个游戏怎么样？')
    ])

    print(f"   消息: {message_obj}")

    has_at_other = False
    bot_self_id = str(bot.self_id) if hasattr(bot, 'self_id') else None

    for segment in message_obj:
        if segment.type == 'at':
            at_qq = segment.data.get('qq')
            if at_qq and bot_self_id and at_qq != bot_self_id:
                has_at_other = True
                break

    result = "✅ 不应该阻止（可以触发）" if not has_at_other else "❌ 应该阻止"
    print(f"   结果: {result}")
    print(f"   预期: ✅ 不应该阻止（可以触发）")
    print(f"   测试: {'✅ 通过' if not has_at_other else '❌ 失败'}")

    # 测试场景4：多个@（包含机器人和其他人）→ 不应该触发
    print("\n📌 场景4：多个@（包含机器人和其他人）→ 不应该触发")
    message_obj = Message([
        MessageSegment(type='at', data={'qq': '123456789'}),
        MessageSegment(type='at', data={'qq': '987654321'}),
        MessageSegment(type='text', data='你们觉得这个游戏怎么样？')
    ])

    print(f"   消息: {message_obj}")

    has_at_other = False
    bot_self_id = str(bot.self_id) if hasattr(bot, 'self_id') else None

    for segment in message_obj:
        if segment.type == 'at':
            at_qq = segment.data.get('qq')
            if at_qq and bot_self_id and at_qq != bot_self_id:
                has_at_other = True
                break

    result = "✅ 应该阻止（不触发）" if has_at_other else "❌ 不应该阻止"
    print(f"   结果: {result}")
    print(f"   预期: ✅ 应该阻止（不触发）")
    print(f"   测试: {'✅ 通过' if has_at_other else '❌ 失败'}")

    print("\n" + "=" * 60)
    print("🎯 测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_at_check()
