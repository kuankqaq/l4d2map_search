# 最终版 - 基于 NoneBot2 框架
import json
import requests

# 核心功能全部从 nonebot 导入，这是正确的路径
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg

# 定义地图数据源的URL
MAPS_JSON_URL = "https://maps.kuank.top/maps.json"

# 使用 on_command 创建一个命令处理器
l4d2map = on_command("地图", aliases={"map", "l4d2map"}, priority=5, block=True)

# 使用 @<command>.handle() 来定义命令的实际处理逻辑
@l4d2map.handle()
async def handle_map_search(args: Message = CommandArg()):
    """
    处理地图搜索命令
    """
    # 从参数中提取用户输入的文本
    query = args.extract_plain_text().strip()

    # 如果用户没有输入关键词，提示并结束
    if not query:
        await l4d2map.finish("请输入要搜索的地图名称，例如：地图 洞穴之旅")
        return

    try:
        # GET 请求获取地图数据
        response = requests.get(MAPS_JSON_URL)
        response.raise_for_status()
        maps_data = response.json()

        # 模糊搜索逻辑（关键词包含）
        found_maps = [
            a_map for a_map in maps_data
            if query.lower() in a_map.get("name", "").lower()
        ]

        # 未找到结果则提示并结束
        if not found_maps:
            await l4d2map.finish(f"未找到与“{query}”相关的地图。")
            return

        # 格式化回复消息
        reply_messages = []
        for a_map in found_maps:
            name = a_map.get("name", "未知名称")
            steam_url = a_map.get("steamUrl", "无")
            description = a_map.get("description", "无")
            download_url = a_map.get("downloadUrl")

            message = (
                f"名称：{name}\n"
                f"工坊地址：{steam_url}\n"
            )
            if download_url:
                message += f"下载地址：{download_url}\n"
            message += f"简介：{description}"
            reply_messages.append(message)

        # 发送最终结果，使用 .send()
        await l4d2map.send("\n\n---\n\n".join(reply_messages))

    except requests.exceptions.RequestException as e:
        await l4d2map.finish(f"获取地图数据时发生网络错误：{e}")
    except json.JSONDecodeError:
        await l4d2map.finish("无法解析地图数据，数据源可能已损坏。")
    except Exception as e:
        await l4d2map.finish(f"处理您的请求时发生未知错误：{e}")
