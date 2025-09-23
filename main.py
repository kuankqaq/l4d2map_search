import json
import requests
# 修正为新版AstrBot的正确导入路径
from astrbot.plugin import on_command
from astrbot.session import CommandSession

# 定义地图数据源的URL为常量，方便后续维护
MAPS_JSON_URL = "https://maps.kuank.top/maps.json"

@on_command("地图", aliases=("map", "l4d2map"))
async def search_l4d2_map(session: CommandSession):
    """
    根据用户输入的关键词，从指定的JSON数据源中搜索求生之路2地图信息。
    """
    # 获取用户输入的查询参数
    query = session.current_arg_text.strip()
    if not query:
        await session.send("请输入要搜索的地图名称，例如：地图 洞穴之旅")
        return

    try:
        # 通过requests库获取在线地图数据
        response = requests.get(MAPS_JSON_URL)
        response.raise_for_status() # 如果请求失败则抛出异常
        maps_data = response.json()

        # 在地图名称中搜索包含查询关键词的地图，不区分大小写
        found_maps = [
            a_map for a_map in maps_data
            if query.lower() in a_map.get("name", "").lower()
        ]

        # 如果未找到任何匹配的地图
        if not found_maps:
            await session.send(f"未找到与“{query}”相关的地图。")
            return

        # 格式化并准备发送回复消息
        reply_messages = []
        for a_map in found_maps:
            # 提取地图信息，提供默认值以避免因缺少字段而出错
            name = a_map.get("name", "未知名称")
            steam_url = a_map.get("steamUrl", "无")
            description = a_map.get("description", "无")
            download_url = a_map.get("downloadUrl")

            # 构建单张地图的回复文本
            message = (
                f"名称：{name}\n"
                f"工坊地址：{steam_url}\n"
            )
            # 仅当下载地址存在时才加入回复
            if download_url:
                message += f"下载地址：{download_url}\n"
            message += f"简介：{description}"

            reply_messages.append(message)

        # 使用分隔符将多张地图的信息拼接成一条消息发送
        await session.send("\n\n---\n\n".join(reply_messages))

    except requests.exceptions.RequestException as e:
        # 处理网络请求相关的异常
        await session.send(f"获取地图数据时发生网络错误：{e}")
    except json.JSONDecodeError:
        # 处理JSON解析失败的异常
        await session.send("无法解析地图数据，数据源可能已损坏。")
    except Exception as e:
        # 捕获其他未知异常，增加插件的健壮性
        await session.send(f"处理您的请求时发生未知错误：{e}")
