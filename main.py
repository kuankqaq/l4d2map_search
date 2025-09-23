# 最终修正版 - 修复了缩进错误
import json
import requests

from astrbot.core.plugin import on_command
from astrbot.core.session import CommandSession

MAPS_JSON_URL = "https://maps.kuank.top/maps.json"

@on_command("地图", aliases={'map', 'l4d2map'})
async def search_l4d2_map(session: CommandSession):
    """
    根据用户输入的关键词，从指定的JSON数据源中搜索求生之路2地图信息。
    """
    query = session.current_arg_text.strip()
    
    # --- 这是修正的地方 ---
    if not query:
        # 下面这两行必须有4个空格的缩进
        await session.send("请输入要搜索的地图名称，例如：地图 洞穴之旅")
        return

    try:
        response = requests.get(MAPS_JSON_URL)
        response.raise_for_status()
        maps_data = response.json()

        found_maps = [
            a_map for a_map in maps_data
            if query.lower() in a_map.get("name", "").lower()
        ]

        if not found_maps:
            await session.send(f"未找到与“{query}”相关的地图。")
            return

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

        await session.send("\n\n---\n\n".join(reply_messages))

    except requests.exceptions.RequestException as e:
        await session.send(f"获取地图数据时发生网络错误：{e}")
    except json.JSONDecodeError:
        await session.send("无法解析地图数据，数据源可能已损坏。")
    except Exception as e:
        await session.send(f"处理您的请求时发生未知错误：{e}")
