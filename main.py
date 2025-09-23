import json
import httpx  # 遵循文档建议，使用异步http库而不是requests

# 1. 遵循文档，从正确的 `astrbot.api` 路径导入所需模块
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
MAPS_JSON_URL = "https://maps.kuank.top/maps.json"

# 2. 遵循文档，使用 @register 装饰器注册一个继承自 Star 的类
@register(
    "l4d2map_search",  # 插件ID
    "kuank",  # 作者
    "一个可以根据关键词搜索L4D2地图信息的插件",  # 描述
    "1.0.9",  # 版本
    "https://github.com/kuankqaq/l4d2map_search"  # 仓库地址
)
class L4D2MapSearchPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 建议在 __init__ 中创建一个可复用的 httpx 客户端
        self.http_client = httpx.AsyncClient()

    # 3. 遵循文档，指令处理函数是类的一个方法，并使用 @filter.command 装饰器
    # 并且，使用类型提示来自动解析指令后的参数
    @filter.command("地图", alias={'map', 'l4d2map'})
    async def search_map(self, event: AstrMessageEvent, keyword: str = ""):
        """根据关键词搜索求生之路2地图信息。"""
        
        query = keyword.strip()
        if not query:
            # 4. 遵循文档，使用 yield event.plain_result() 来回复消息
            yield event.plain_result("请输入要搜索的地图名称，例如：/地图 洞穴之旅")
            return

        try:
            # 5. 遵循文档，使用异步网络请求
            response = await self.http_client.get(MAPS_JSON_URL, timeout=10.0)
            response.raise_for_status()  # 如果请求失败则抛出异常
            maps_data = response.json()

            # 模糊搜索逻辑
            found_maps = [
                a_map for a_map in maps_data
                if query.lower() in a_map.get("name", "").lower()
            ]

            if not found_maps:
                yield event.plain_result(f"未找到与“{query}”相关的地图。")
                return

            # 格式化回复消息
            reply_messages = []
            for a_map in found_maps:
                name = a_map.get("name", "未知名称")
                steam_url = a_map.get("steamUrl", "无")
                description = a_map.get("description", "无")
                download_url = a_map.get("downloadUrl")

                message = f"名称：{name}\n工坊地址：{steam_url}\n"
                if download_url:
                    message += f"下载地址：{download_url}\n"
                message += f"简介：{description}"
                reply_messages.append(message)
            
            # 发送最终拼接好的结果
            yield event.plain_result("\n\n---\n\n".join(reply_messages))

        except httpx.RequestError as e:
            logger.error(f"请求地图数据时发生网络错误: {e}")
            yield event.plain_result(f"获取地图数据时发生网络错误，请稍后再试。")
        except json.JSONDecodeError:
            logger.error("解析地图JSON数据失败")
            yield event.plain_result("无法解析地图数据，数据源可能已损坏。")
        except Exception as e:
            logger.error(f"处理地图搜索时发生未知错误: {e}")
            yield event.plain_result(f"处理您的请求时发生未知错误。")

    async def terminate(self):
        # 插件卸载时，关闭http客户端
        await self.http_client.aclose()
