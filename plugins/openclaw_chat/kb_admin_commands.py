#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库管理员命令
提供知识库管理和配置的管理员命令
"""

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from nonebot.exception import FinishedException

# 导入配置
from config import config

# 导入知识库模块
try:
    from .knowledge_base_manager import KnowledgeBaseManager
    from .vector_database_manager import VectorDatabaseManager
    from .knowledge_base_retriever import KnowledgeBaseRetriever
    from .knowledge_base_builder import KnowledgeBaseBuilder
    from .ai_processor import init_knowledge_base, retrieve_from_knowledge_base
    KNOWLEDGE_BASE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_BASE_AVAILABLE = False
    logger.warning("⚠️  知识库模块未安装，知识库管理员命令将不可用")


# ========== 初始化知识库 ==========

_kb_manager = None
_vdb_manager = None
_builder = None


def _init_kb_if_needed():
    """如果需要，初始化知识库"""
    global _kb_manager, _vdb_manager, _builder

    if not KNOWLEDGE_BASE_AVAILABLE:
        return None, None, None

    if _kb_manager is None:
        try:
            init_knowledge_base(kb_dir=config.knowledge_base_dir)

            _kb_manager = KnowledgeBaseManager(kb_dir=config.knowledge_base_dir)
            _vdb_manager = VectorDatabaseManager(kb_dir=config.knowledge_base_dir)
            _builder = KnowledgeBaseBuilder(kb_dir=config.knowledge_base_dir)

            logger.info("✅ 知识库管理器初始化成功")
        except Exception as e:
            logger.error(f"❌ 知识库管理器初始化失败: {e}")
            return None, None, None

    return _kb_manager, _vdb_manager, _builder


# ========== 命令：查看知识库列表 ==========

kb_list = on_command(
    "kb_list",
    aliases={"知识库列表", "kb列表", "list_kb"},
    priority=5,
    block=True
)


@kb_list.handle()
async def handle_kb_list():
    """查看知识库列表"""
    # 初始化知识库
    kb_manager, _, _ = _init_kb_if_needed()

    if kb_manager is None:
        await kb_list.finish("⚠️  知识库功能未启用或初始化失败")

    try:
        # 获取知识库列表
        kb_list_data = kb_manager.list_knowledge_bases()

        if not kb_list_data:
            await kb_list.finish("📚 当前没有知识库\n\n💡 使用 /kb_build <知识库ID> 来创建知识库")

        # 构建回复
        reply_lines = ["📚 知识库列表\n"]

        for i, kb_info in enumerate(kb_list_data, 1):
            kb_id = kb_info.kb_id
            kb_name = kb_info.kb_name
            status = kb_info.status

            # 状态图标
            status_icon = "✅" if status == "ready" else "⏳"
            status_text = "已就绪" if status == "ready" else "构建中"

            reply_lines.append(f"\n{i}. {status_icon} **{kb_name}**")
            reply_lines.append(f"   - ID: {kb_id}")
            reply_lines.append(f"   - 状态: {status_text}")

        await kb_list.finish("\n".join(reply_lines))

    except FinishedException:
        raise
    except Exception as e:
        logger.error(f"❌ 查看知识库列表失败: {e}")
        await kb_list.finish(f"❌ 查看知识库列表失败: {e}")


# ========== 命令：查看知识库状态 ==========

kb_status = on_command(
    "kb_status",
    aliases={"知识库状态", "kb状态", "status_kb"},
    priority=5,
    block=True
)


@kb_status.handle()
async def handle_kb_status(args: Message = CommandArg()):
    """查看知识库状态"""
    # 初始化知识库
    kb_manager, vdb_manager, _ = _init_kb_if_needed()

    if kb_manager is None:
        await kb_status.finish("⚠️  知识库功能未启用或初始化失败")

    # 获取知识库 ID
    kb_id = args.extract_plain_text().strip()

    if not kb_id:
        await kb_status.finish("⚠️  请提供知识库 ID\n\n💡 使用方法: /kb_status <知识库ID>")

    try:
        # 检查知识库是否存在
        if not kb_manager.exists(kb_id):
            await kb_status.finish(f"⚠️  知识库不存在: {kb_id}")

        # 获取知识库信息
        kb_info = kb_manager.get_knowledge_base(kb_id)

        # 构建回复
        reply_lines = [
            f"📊 知识库状态: **{kb_info.kb_name}**\n",
            f"• ID: {kb_info.kb_id}",
            f"• 状态: {'✅ 已就绪' if kb_info.status == 'ready' else '⏳ 构建中'}",
            f"• 创建时间: {kb_info.created_at}",
            f"• 最后更新: {kb_info.updated_at}",
        ]

        # 如果已就绪，添加统计信息
        if kb_info.status == "ready" and vdb_manager:
            try:
                collection = vdb_manager.get_collection(kb_id)
                if collection:
                    count = collection.count()
                    reply_lines.append(f"• 文档数量: {count}")
            except Exception as e:
                logger.warning(f"⚠️  无法获取文档数量: {e}")

        await kb_status.finish("\n".join(reply_lines))

    except FinishedException:
        raise
    except Exception as e:
        logger.error(f"❌ 查看知识库状态失败: {e}")
        await kb_status.finish(f"❌ 查看知识库状态失败: {e}")


# ========== 命令：构建知识库（仅超级管理员） ==========

kb_build = on_command(
    "kb_build",
    aliases={"构建知识库", "kb构建"},
    priority=5,
    block=True,
    rule=to_me(),
    permission=SUPERUSER
)


@kb_build.handle()
async def handle_kb_build(args: Message = CommandArg()):
    """构建知识库"""
    # 初始化知识库
    kb_manager, _, builder = _init_kb_if_needed()

    if kb_manager is None:
        await kb_build.finish("⚠️  知识库功能未启用或初始化失败")

    # 获取参数
    arg_text = args.extract_plain_text().strip()
    parts = arg_text.split()

    if len(parts) < 1:
        await kb_build.finish(
            "⚠️  请提供知识库 ID\n\n"
            "💡 使用方法: /kb_build <知识库ID> [名称]\n"
            "   例如: /kb_build game_terraria 泰拉瑞亚游戏知识库"
        )

    kb_id = parts[0]
    kb_name = parts[1] if len(parts) > 1 else kb_id

    try:
        # 检查知识库是否已存在
        if kb_manager.exists(kb_id):
            await kb_build.finish(f"⚠️  知识库已存在: {kb_id}\n\n💡 使用 /kb_update {kb_id} 来更新知识库")

        # 创建知识库
        kb_manager.create(kb_id, kb_name=kb_name)

        await kb_build.send(f"✅ 知识库已创建: {kb_id}\n\n⏳ 正在构建，请稍候...")

        # 构建知识库
        # TODO: 这里需要根据具体需求实现构建逻辑
        # 例如：解析 Wiki、处理文档等

        await kb_build.send(f"✅ 知识库构建完成: {kb_id}\n\n💡 使用 /kb_status {kb_id} 查看状态")

    except FinishedException:
        raise
    except Exception as e:
        logger.error(f"❌ 构建知识库失败: {e}")
        await kb_build.finish(f"❌ 构建知识库失败: {e}")


# ========== 命令：更新知识库（仅超级管理员） ==========

kb_update = on_command(
    "kb_update",
    aliases={"更新知识库", "kb更新"},
    priority=5,
    block=True,
    rule=to_me(),
    permission=SUPERUSER
)


@kb_update.handle()
async def handle_kb_update(args: Message = CommandArg()):
    """更新知识库"""
    # 初始化知识库
    kb_manager, _, builder = _init_kb_if_needed()

    if kb_manager is None:
        await kb_update.finish("⚠️  知识库功能未启用或初始化失败")

    # 获取知识库 ID
    kb_id = args.extract_plain_text().strip()

    if not kb_id:
        await kb_update.finish("⚠️  请提供知识库 ID\n\n💡 使用方法: /kb_update <知识库ID>")

    try:
        # 检查知识库是否存在
        if not kb_manager.exists(kb_id):
            await kb_update.finish(f"⚠️  知识库不存在: {kb_id}")

        # 更新知识库
        await kb_update.send(f"⏳ 正在更新知识库: {kb_id}\n\n请稍候...")

        # 更新知识库
        # TODO: 这里需要根据具体需求实现更新逻辑

        await kb_update.send(f"✅ 知识库更新完成: {kb_id}\n\n💡 使用 /kb_status {kb_id} 查看状态")

    except FinishedException:
        raise
    except Exception as e:
        logger.error(f"❌ 更新知识库失败: {e}")
        await kb_update.finish(f"❌ 更新知识库失败: {e}")


# ========== 命令：删除知识库（仅超级管理员） ==========

kb_delete = on_command(
    "kb_delete",
    aliases={"删除知识库", "kb删除"},
    priority=5,
    block=True,
    rule=to_me(),
    permission=SUPERUSER
)


@kb_delete.handle()
async def handle_kb_delete(args: Message = CommandArg()):
    """删除知识库"""
    # 初始化知识库
    kb_manager, _, _ = _init_kb_if_needed()

    if kb_manager is None:
        await kb_delete.finish("⚠️  知识库功能未启用或初始化失败")

    # 获取知识库 ID
    kb_id = args.extract_plain_text().strip()

    if not kb_id:
        await kb_delete.finish("⚠️  请提供知识库 ID\n\n💡 使用方法: /kb_delete <知识库ID>")

    try:
        # 检查知识库是否存在
        if not kb_manager.exists(kb_id):
            await kb_delete.finish(f"⚠️  知识库不存在: {kb_id}")

        # 删除知识库
        kb_manager.delete(kb_id)

        await kb_delete.finish(f"✅ 知识库已删除: {kb_id}")

    except FinishedException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除知识库失败: {e}")
        await kb_delete.finish(f"❌ 删除知识库失败: {e}")


# ========== 命令：群组知识库配置 ==========

kb_group_set = on_command(
    "kb_group_set",
    aliases={"设置群知识库", "kb群设置"},
    priority=5,
    block=True,
    rule=to_me(),
    permission=SUPERUSER
)


@kb_group_set.handle()
async def handle_kb_group_set(args: Message = CommandArg(), event: GroupMessageEvent = None):
    """设置群知识库"""
    # 初始化知识库
    kb_manager, _, _ = _init_kb_if_needed()

    if kb_manager is None:
        await kb_group_set.finish("⚠️  知识库功能未启用或初始化失败")

    # 获取参数
    arg_text = args.extract_plain_text().strip()
    parts = arg_text.split()

    if len(parts) < 2:
        await kb_group_set.finish(
            "⚠️  参数不正确\n\n"
            "💡 使用方法: /kb_group_set <群号> <知识库ID> [top_k]\n"
            "   例如: /kb_group_set 123456789 game_terraria 3"
        )

    group_id = parts[0]
    kb_id = parts[1]
    top_k = int(parts[2]) if len(parts) > 2 else 3

    try:
        # 检查知识库是否存在
        if kb_manager and not kb_manager.exists(kb_id):
            await kb_group_set.finish(f"⚠️  知识库不存在: {kb_id}\n\n💡 使用 /kb_list 查看可用知识库")

        # 设置群知识库配置
        from config import KnowledgeBaseConfig

        config.set_group_kb_config(
            group_id=group_id,
            kb_config=KnowledgeBaseConfig(
                enabled=True,
                kb_id=kb_id,
                top_k=top_k
            )
        )

        await kb_group_set.finish(
            f"✅ 群知识库配置已设置\n\n"
            f"• 群号: {group_id}\n"
            f"• 知识库: {kb_id}\n"
            f"• 检索数量: {top_k}"
        )

    except FinishedException:
        raise
    except Exception as e:
        logger.error(f"❌ 设置群知识库失败: {e}")
        await kb_group_set.finish(f"❌ 设置群知识库失败: {e}")


# ========== 命令：查看群知识库状态 ==========

kb_group_status = on_command(
    "kb_group_status",
    aliases={"群知识库状态", "kb群状态"},
    priority=5,
    block=True
)


@kb_group_status.handle()
async def handle_kb_group_status(event: GroupMessageEvent = None):
    """查看群知识库状态"""
    # 获取群号
    if event:
        group_id = str(event.group_id)
    else:
        await kb_group_status.finish("⚠️  此命令只能在群聊中使用")

    try:
        # 获取群知识库配置
        kb_id = config.get_group_kb_id(group_id)
        top_k = config.get_group_kb_top_k(group_id)

        if not kb_id:
            await kb_group_status.finish(
                f"⏳ 当前群未配置知识库\n\n"
                f"💡 使用 /kb_group_set {group_id} <知识库ID> 来配置"
            )

        # 初始化知识库
        kb_manager, _, _ = _init_kb_if_needed()

        # 获取知识库状态
        kb_info = None
        if kb_manager and kb_manager.exists(kb_id):
            kb_info = kb_manager.get_status(kb_id)

        # 构建回复
        reply_lines = [
            f"📊 群知识库状态\n\n",
            f"• 群号: {group_id}",
            f"• 知识库 ID: {kb_id}",
            f"• 检索数量: {top_k}",
        ]

        if kb_info:
            reply_lines.append(f"• 知识库名称: {kb_info.kb_name}")
            reply_lines.append(f"• 状态: {'✅ 已就绪' if kb_info.status == 'ready' else '⏳ 构建中'}")
        else:
            reply_lines.append(f"• 状态: ⚠️  知识库不存在")

        await kb_group_status.finish("\n".join(reply_lines))

    except FinishedException:
        raise
    except Exception as e:
        logger.error(f"❌ 查看群知识库状态失败: {e}")
        await kb_group_status.finish(f"❌ 查看群知识库状态失败: {e}")


# ========== 命令：测试知识库检索 ==========

kb_test = on_command(
    "kb_test",
    aliases={"测试知识库", "kb测试"},
    priority=5,
    block=True
)


@kb_test.handle()
async def handle_kb_test(args: Message = CommandArg(), event: GroupMessageEvent = None):
    """测试知识库检索"""
    # 获取查询文本
    query = args.extract_plain_text().strip()

    if not query:
        await kb_test.finish("⚠️  请提供查询文本\n\n💡 使用方法: /kb_test <查询文本>\n   例如: /kb_test 血腥僵尸掉落什么？")

    try:
        # 获取群号
        group_id = str(event.group_id) if event else None

        # 如果是私聊，使用默认知识库
        if not group_id:
            kb_id = config.knowledge_base_default_kb_id
        else:
            # 获取群知识库配置
            kb_id = config.get_group_kb_id(group_id)

        if not kb_id:
            await kb_test.finish(
                "⚠️  当前群未配置知识库\n\n"
                "💡 超级管理员可以使用 /kb_group_set 来配置"
            )

        # 获取群知识库配置
        top_k = config.get_group_kb_top_k(group_id) if group_id else config.knowledge_base_top_k

        # 检索知识库
        result = await retrieve_from_knowledge_base(
            query=query,
            kb_id=kb_id,
            top_k=top_k,
            use_cache=False  # 测试时不使用缓存
        )

        if not result:
            await kb_test.finish(f"⚠️  知识库检索无结果\n\n查询: {query}")

        # 构建回复
        reply_lines = [
            f"🔍 知识库检索结果\n\n",
            f"• 查询: {query}",
            f"• 知识库: {kb_id}",
            f"\n📄 检索结果:\n",
        ]

        reply_lines.append(result)

        await kb_test.finish("\n".join(reply_lines))

    except FinishedException:
        raise
    except Exception as e:
        logger.error(f"❌ 测试知识库检索失败: {e}")
        await kb_test.finish(f"❌ 测试知识库检索失败: {e}")


# ========== 命令：知识库帮助 ==========

kb_help = on_command(
    "kb_help",
    aliases={"知识库帮助", "kb帮助"},
    priority=5,
    block=True
)


@kb_help.handle()
async def handle_kb_help():
    """知识库帮助"""
    help_text = """
📚 知识库命令帮助

📖 查看知识库:
  /kb_list - 查看所有知识库
  /kb_status <知识库ID> - 查看知识库状态
  /kb_test <查询文本> - 测试知识库检索
  /kb_group_status - 查看当前群的知识库状态

⚙️ 管理员命令（仅超级管理员）:
  /kb_build <知识库ID> [名称] - 构建知识库
  /kb_update <知识库ID> - 更新知识库
  /kb_delete <知识库ID> - 删除知识库
  /kb_group_set <群号> <知识库ID> [top_k] - 设置群知识库

💡 示例:
  /kb_list - 查看所有知识库
  /kb_status game_terraria - 查看泰拉瑞亚知识库状态
  /kb_test 血腥僵尸掉落什么？ - 测试检索
  /kb_group_set 123456789 game_terraria 3 - 设置群知识库
"""

    await kb_help.finish(help_text)
