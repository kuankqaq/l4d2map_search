import json
import requests

from astrbot.core.plugin import on_command
from astrbot.core.session import CommandSession

# 定义地图数据源的URL为常量
MAPS_JSON_URL = "https://maps.kuank.top/maps.json"

@on_command("地图", aliases={'map', 'l4d2map'})
async def search_l4d2_map(session: CommandSession):
    """
    根据用户输入的关键词，从指定的JSON数据源中搜索求生之路2地图信息。
    """
    # 从 session 对象中获取用户输入的参数文本
    query = session.current_arg_text.strip()
    if not query:
        await session.send("请输入要搜索的地图名称，例如：地图 洞穴之旅")
        return

    try:
        # 通过requests库获取在线地图数据
        response = requests.get(MAPS_JSON_URL)
        response.raise_for_status()
        maps_data = response.json()

        # 在地图名称中搜索包含查询关键词的地图，不区分大小写
        found_maps = [
            a_map for a_map in maps_data
            if query.lower() in a_map.get("name", "").lower()
        ]

        # 如果未找到任何匹配的地图
        if not found_maps:
            
