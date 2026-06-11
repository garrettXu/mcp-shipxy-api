# server.py
import argparse
import contextvars
import logging
import os
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Mount, Route

from domain_catalog import describe_capabilities as catalog_describe_capabilities
from domain_catalog import describe_object as catalog_describe_object
from ship_service import ShipxyAPI
from tool_registry import all_schemas, invoke_tool
from validation import validate_tool_input as validate_shipxy_tool_input

load_dotenv()
# Create an MCP server
api_key = os.getenv('SHIPXY_API_KEY')
logger = logging.getLogger(__name__)
current_api_key: contextvars.ContextVar[str | None] = contextvars.ContextVar("shipxy_api_key", default=None)

MCP_INSTRUCTIONS = """
Shipxy MCP 是面向海事场景的 Shipxy API 工具服务，适合给大模型、Agent、自动化工作流和 MCP 客户端调用。

这个 MCP 可以查询和分析以下数据：
1. 船舶：船舶模糊查询、单船位置、多船位置、周边船舶、船籍、船舶档案、船舶轨迹、船舶会遇、船舶状态、精准 ETA、船队船舶。
2. 港口：港口查询、港口靠泊船舶、港口锚地船舶、预抵港船舶、按船舶/港口查询挂靠记录、按港口查询到离港记录。
3. 航线：按经纬度到港口规划航线、按港口到港口规划航线。
4. 气象：海洋气象区域、点位气象、当前天气、未来天气、历史天气。
5. 台风：台风列表、单个台风路径详情。
6. 潮汐：中国沿海潮汐站、潮汐数据、全球潮汐站、全球潮汐数据。
7. 航行安全：指定时间范围内的航行警告。

推荐调用流程：
1. 如果不确定应该调用哪个工具，先调用 describe_capabilities；不传 tool_name 时返回全部能力目录，传入 tool_name 时返回该工具的适用范围、参数要求、返回对象、常见错误和后续建议。
2. 如果不确定参数格式，先调用 validate_tool_input，在真正请求 Shipxy 前获取字段级错误和修复建议。
3. 如果不理解返回 JSON 字段含义，调用 describe_object 查看返回对象 schema 和中文字段解释。
4. 如果用户只给了船名、港口名等模糊信息，先调用搜索类工具获取 MMSI、IMO、port_code 或 tide station id，再调用详情类工具。
5. 对时间范围、区域范围、港口范围较大的查询，应尽量缩小范围，避免 Shipxy 请求超时或返回过大。

统一返回约定：
1. 成功时返回 ok=true，并包含 tool、capability_ref、returns、object_refs 和 data；部分列表接口还会返回 total。
2. 失败时返回 ok=false，并包含 error.type、error.message、endpoint、shipxy_status 和可用时的 fix 修复建议。
3. 常见 error.type 包括 invalid_request、permission_denied、not_found、response_validation_failed、http_error、network_error、timeout、shipxy_error。
4. response_validation_failed 表示 Shipxy 实际返回和本地 schema 不完全一致；raw/data 仍会尽量保留原始数据，Agent 应优先向用户说明 schema 漂移，而不是直接丢弃结果。

使用要求：
1. 运行 MCP 前必须通过环境变量 SHIPXY_API_KEY 提供 Shipxy API Key。
2. 不要在对话、日志或报告中明文输出 API Key。
3. 用户没有对应接口或港口范围权限时，工具会返回 permission_denied 或 Shipxy 业务错误；应提示用户检查 API Key 和 Shipxy 控制台权限。
4. 船队类接口需要用户账号下真实 fleet_id；占位值通常会返回船队不存在。

面向 Agent 的原则：
1. 优先使用结构化工具结果，不要猜测字段含义。
2. 需要解释字段时，先查 describe_object。
3. 入参错误时，把 validate_tool_input 或 error.fix 中的中文修复建议直接反馈给用户。
4. 业务无数据时，明确说明没有查到结果，并建议用户更换 MMSI、港口、时间范围或先使用搜索工具确认实体。
"""

mcp = FastMCP(
    "ship_xy_mcp",
    instructions=MCP_INSTRUCTIONS,
    website_url="https://github.com/garrettXu/mcp-shipxy-api",
)


def create_shipxy_api() -> ShipxyAPI:
    """创建ShipxyAPI实例"""
    return ShipxyAPI(api_key=current_api_key.get() or api_key)


def _mask_api_key(value: str) -> str:
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def _extract_api_key_from_request(request: Request) -> str | None:
    ak = request.query_params.get("ak")
    if ak:
        return ak

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:].strip()

    return None


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """创建支持 /sse?ak=... 和 Authorization Bearer 的 SSE MCP 应用。"""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request):
        connection_api_key = _extract_api_key_from_request(request)
        if not connection_api_key:
            return JSONResponse(
                {
                    "error": "Missing authentication. Please provide 'ak' query parameter or 'Authorization: Bearer <token>' header."
                },
                status_code=401,
            )

        logger.info("SSE connection authenticated with Shipxy API key %s", _mask_api_key(connection_api_key))
        token = current_api_key.set(connection_api_key)
        try:
            async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
            ) as (read_stream, write_stream):
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp_server.create_initialization_options(),
                )
            return PlainTextResponse("")
        except Exception as exc:
            logger.exception("SSE connection failed: %s", exc)
            return JSONResponse({"error": f"Internal server error: {exc}"}, status_code=500)
        finally:
            current_api_key.reset(token)

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


def run_sse_server(host: str = "0.0.0.0", port: int = 18081, *, debug: bool = False) -> None:
    import uvicorn

    logging.basicConfig(level=logging.INFO)
    starlette_app = create_starlette_app(mcp._mcp_server, debug=debug)
    logger.info("Shipxy MCP SSE server listening on http://%s:%s/sse", host, port)
    logger.info("Authentication: http://%s:%s/sse?ak=your_api_key", host, port)
    logger.info("Authentication: Authorization: Bearer your_api_key")
    uvicorn.run(starlette_app, host=host, port=port)


@mcp.tool()
def describe_capabilities(tool_name: str = None) -> dict[str, Any]:
    """
    描述 Shipxy MCP 能力、入参、返回对象、常见错误和推荐调用流程。
    参数：
        tool_name: 可选工具名；不传则返回全部能力目录。
    """
    return catalog_describe_capabilities(all_schemas(), tool_name)


@mcp.tool()
def describe_object(object_name: str = None) -> dict[str, Any]:
    """
    描述 Shipxy 返回对象 schema 和字段含义。
    参数：
        object_name: 可选对象名；不传则返回全部对象列表。
    """
    return catalog_describe_object(object_name)


@mcp.tool()
def validate_tool_input(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """
    在真正请求 Shipxy 前校验工具入参，并返回字段级修复建议。
    参数：
        tool_name: Shipxy 工具名。
        arguments: 将要传给该工具的参数 JSON。
    """
    return validate_shipxy_tool_input(tool_name, arguments)

# ShipxyAPI工具封装
@mcp.tool()
def search_ship(keywords: str, max_results: int = None) -> dict[str, Any]:
    """
    船舶模糊查询服务，是使用关键字（mmsi、imo、船名、呼号等）作为查询条件，模糊查询出所有符合条件的船舶静态信息；当使用imo作为输入时，可以查询该imo编号下，曾经使用的所有mmsi记录；当使用船名作为查询输入时，可以查询该船名所有历史使用船舶的信息。
    注：MMSI 中文称为水上移动业务标识码，是一种九位数字码，用于船舶无线电通信系统中，能够独特识别各类台站和成组呼叫台站。MMSI具有唯一性，每条船都有一个对应的MMSI码，通常被称为“一船一码”或“九位码”‌，同一条船舶mmsi编号有可能在售卖后变更，mmsi前三位代表国家和地区。
    IMO 是国际海事组织为每一条船分配的唯一识别码,由七位数字组成,用于全球范围内对船舶身份、技术信息及安全记录的追踪与管理。
    参数：
        keywords: 查询关键字（船名、呼号、MMSI、IMO等）
        max_results: 最大返回数量（可选，最大100）
    返回：
        SearchShipResponse: 查询结果，强类型返回
    异常：
        请求失败或返回错误码。
    """
    return invoke_tool(create_shipxy_api(), "search_ship", locals())

@mcp.tool()
def get_single_ship(mmsi: int) -> dict[str, Any]:
    """
    单船位置查询
    根据船舶mmsi编码查询船舶的基础静态信息以及船舶的实时动态信息，包括船舶imo编号、呼号、船舶中英文名称、船舶类型、长度宽度以及AIS最新更新上报的船舶实时位置、航行状态、船舶目的港口、船舶实时速度、预计到达目的港的时间、航首向航迹向等。
    参数：
        mmsi: 船舶mmsi编号
    返回：
        SingleShipResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_single_ship", locals())

@mcp.tool()
def get_many_ship(mmsis: list[int]) -> dict[str, Any]:
    """
    多船位置查询
    根据多个船舶船舶mmsi编码查询船舶的基础静态信息以及船舶的实时动态信息，包括船舶imo编号、呼号、船舶中英文名称、船舶类型、长度宽度以及AIS最新更新上报的船舶实时位置、航行状态、船舶目的港口、船舶实时速度、预计到达目的港的时间、航首向航迹向等。
    参数：
        mmsis: 船舶mmsi编号列表（最多100个）
    返回：
        ManyShipResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_many_ship", locals())

@mcp.tool()
def get_fleet_ship(fleet_id: str) -> dict[str, Any]:
    """
    船队船位置查询
    控制台中维护的船队id，查询船队下所有船舶数据。
    参数：
        fleet_id: 船队编号
    返回：
        FleetShipResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_fleet_ship", locals())

@mcp.tool()
def get_surrounding_ship(mmsi: int) -> dict[str, Any]:
    """
    周边船舶查询
    通过船舶的 MMSI进行查询，获取以当前船舶位置为圆心以 10 海里为半径的圆形区域内的船舶数据。返回的船舶数据列表按照由近及远进行排序，返回的数据包括船舶imo编号、呼号、船舶中英文名称、船舶类型、长度宽度以及AIS最新更新上报的船舶实时位置、航行状态、船舶目的港口、船舶实时速度、预计到达目的港的时间、航首向航迹向等。 
    参数：
        mmsi: 船舶mmsi编号
    返回：
        SurRoundingShipResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_surrounding_ship", locals())

@mcp.tool()
def get_area_ship(region: str, output: int = 1, scode: int = None) -> dict[str, Any]:
    """
    区域船舶查询
    通过船舶的 MMSI进行查询，获取以当前船舶位置为圆心以 10 海里为半径的圆形区域内的船舶数据。返回的船舶数据列表按照由近及远进行排序，返回的数据包括船舶imo编号、呼号、船舶中英文名称、船舶类型、长度宽度以及AIS最新更新上报的船舶实时位置、航行状态、船舶目的港口、船舶实时速度、预计到达目的港的时间、航首向航迹向等。 
    参数：
        region: 区域字符串（lng,lat-lng,lat-...）
        output: 输出格式，1为json，0为base64
        scode: 会话令牌（可选）
    返回：
        AreaShipResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_area_ship", locals())

@mcp.tool()
def get_ship_registry(mmsi: int) -> dict[str, Any]:
    """
    船籍信息查询
    通过船舶的mmsi编号来查询匹配船舶的船籍国家或地区信息。
    参数：
        mmsi: 船舶mmsi编号
    返回：
        ShipRegistryResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_ship_registry", locals())

@mcp.tool()
def search_ship_particular(mmsi: int = None, imo: int = None, call_sign: str = None, ship_name: str = None) -> dict[str, Any]:
    """
    船舶档案查询
    通过船舶的mmsi编号、imo编号、呼号或者船舶的英文名称来查询船舶的劳式档案数据。注：只有具备imo编号的船舶有档案记录
    参数：
        mmsi: 船舶mmsi编号（可选）
        imo: imo编号（可选）
        call_sign: 呼号（可选）
        ship_name: 船名（可选）
    返回：
        SearchShipParticularResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "search_ship_particular", locals())

@mcp.tool()
def search_port(keywords: str, max_results: int = None) -> dict[str, Any]:
    """
    港口查询
    对全球港口数据进行模糊查询，支持通过港口的中英文名称和五位码模糊检索获取港口的基本信息，包括港口中英文名称、港口五位码、港口所在时区等。返回结果中获取的五位码是船讯网以港口维度查询数据的唯一标识。
    参数：
        keywords: 港口关键字（中文/英文/五位码）
        max_results: 最大返回数量（可选，最大100）
    返回：
        SearchPortResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "search_port", locals())

@mcp.tool()
def get_berth_ships(port_code: str, ship_type: int = None) -> dict[str, Any]:
    """
    港口靠泊船舶查询
    使用港口五位码查询当前港口正在靠泊的全部船舶信息，包括当前靠泊船的总数量、船舶类型、船舶基础信息、船舶到达港口时间和停留时间。
    参数：
        port_code: 港口标准五位码
        ship_type: 船舶类型（可选）
    返回：
        GetBerthShipsResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_berth_ships", locals())

@mcp.tool()
def get_anchor_ships(port_code: str, ship_type: int = None) -> dict[str, Any]:
    """
    港口锚地船舶查询
    使用港口五位码查询当前港口正在锚地的全部船舶信息，包括当前港口锚地等待船舶的总数量、船舶类型、船舶基础信息、船舶到达港口时间和停留时间。
    参数：
        port_code: 港口标准五位码
        ship_type: 船舶类型（可选）
    返回：
        GetAnchorShipsResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_anchor_ships", locals())

@mcp.tool()
def get_eta_ships(port_code: str, start_time: int, end_time: int, ship_type: int = None) -> dict[str, Any]:
    """
    预抵港船舶查询
    使用港口五位码和时间周期查询在未来某一时间段预计到达该港口的船舶列表和船舶信息。
    参数：
        port_code: 港口标准五位码
        start_time: 开始时间（UTC时间戳）
        end_time: 结束时间（UTC时间戳）
        ship_type: 船舶类型（可选）
    返回：
        GetETAShipsResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_eta_ships", locals())

@mcp.tool()
def get_ship_track(mmsi: int, start_time: int, end_time: int, output: int = 1) -> dict[str, Any]:
    """
    船舶轨迹查询
    通过船舶的mmsi编号和时间段，查询船舶历史经过的轨迹点。
    参数：
        mmsi: 船舶mmsi编号
        start_time: 查询的开始时间，unix时间戳
        end_time: 查询的截止时间，unix时间戳
        output: 输出格式，1为json，0为base64，默认为1
    返回：
        GetShipTrackResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_ship_track", locals())

@mcp.tool()
def search_ship_approach(mmsi: int, start_time: int, end_time: int, approach_zone: int = None) -> dict[str, Any]:
    """
    船舶搭靠事件查询
    查询指定船舶在一段时间内是否有搭靠行为，如果有搭靠行为则列出搭靠的船舶详细信息以及搭靠的位置、坐标、搭靠开始时间、结束时间等。根据全球船舶实时位置监控，测算两船贴近停靠或并排行驶超过5分钟，则判定为船舶搭靠。
    参数：
        mmsi: 船舶mmsi编号
        start_time: 开始时间（UTC时间戳）
        end_time: 结束时间（UTC时间戳）
        approach_zone: 搭靠地区（可选）
    返回：
        SearchShipApproachResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "search_ship_approach", locals())

@mcp.tool()
def get_port_of_call_by_ship(mmsi: int, start_time: int, end_time: int, imo: int = None, ship_name: str = None, call_sign: str = None, time_zone: int = 2) -> dict[str, Any]:
    """
    船舶靠港记录查询
    查询船舶在一段时间以内的历史靠港记录，可以获得船舶到达锚地的时间、到达港口范围以及停靠到泊位的时间，以及船舶在港口停留的时长，进出港的吃水情况等。
    参数：
        mmsi: 船舶mmsi编号
        start_time: 开始时间（UTC时间戳）
        end_time: 结束时间（UTC时间戳）
        imo: IMO编号（可选）
        ship_name: 船舶英文名称（可选）
        call_sign: 船舶呼号（可选）
        time_zone: 时区（默认2，北京时区）
    返回：
        GetPortOfCallByShipResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_port_of_call_by_ship", locals())

@mcp.tool()
def get_port_of_call_by_ship_port(mmsi: int, port_code: str, start_time: int, end_time: int, imo: int = None, ship_name: str = None, call_sign: str = None, time_zone: int = 2) -> dict[str, Any]:
    """
    船舶在指定港口的靠港记录查询
    查询船舶在一段时间以内的在某一具体港口靠港的记录，可以获得船舶到达锚地的时间、到达港口范围以及停靠到泊位的时间，以及船舶在港口停留的时长，进出港的吃水情况等。
    参数：
        mmsi: 船舶mmsi编号
        port_code: 港口五位码
        start_time: 开始时间（UTC时间戳）
        end_time: 结束时间（UTC时间戳）
        imo: IMO编号（可选）
        ship_name: 船舶英文名称（可选）
        call_sign: 船舶呼号（可选）
        time_zone: 时区（默认2，北京时区）
    返回：
        GetPortOfCallByShipPortResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_port_of_call_by_ship_port", locals())

@mcp.tool()
def get_ship_status(mmsi: int, imo: int = None, ship_name: str = None, call_sign: str = None, time_zone: int = 2) -> dict[str, Any]:
    """
    船舶当前挂靠信息查询
    查询船舶当前时间点是否挂靠了港口，如果当前正在某一港口挂靠，则可以获得当前挂靠港口的信息以及入港时间。
    参数：
        mmsi: 船舶mmsi编号
        imo: IMO编号（可选）
        ship_name: 船舶英文名称（可选）
        call_sign: 船舶呼号（可选）
        time_zone: 时区（默认2，北京时区）
    返回：
        GetShipStatusResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_ship_status", locals())

@mcp.tool()
def get_port_of_call_by_port(port_code: str, start_time: int, end_time: int, type_: int = 1, time_zone: int = 2) -> dict[str, Any]:
    """
    港口靠港记录查询
    使用港口五位码查询港口在某一时间周期内历史靠泊的所有船舶信息。包括船舶基础信息、船舶在该港口的靠港记录以及船舶在上一个港口和下一个港口的靠港记录信息。
    参数：
        port_code: 港口五位码
        start_time: 开始时间（UTC时间戳）
        end_time: 结束时间（UTC时间戳）
        type_: 查询类型（1:ATA，2:ATD，默认1）
        time_zone: 时区（默认2，北京时区）
    返回：
        GetPortOfCallByPortResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_port_of_call_by_port", locals())

@mcp.tool()
def plan_route_by_point(start_point: str, end_point: str = None, end_port_code: str = None, avoid: str = None, through: str = None) -> dict[str, Any]:
    """
    点到点/点到港航线规划
    查询起点坐标到终点坐标或终点港口之间的航线规划，获取航线的总里程以及航线经过的点位坐标经纬度。
    参数：
        start_point: 起始点（lng,lat）
        end_point: 结束点（lng,lat），与 end_port_code 二选一
        end_port_code: 结束港口五位码，与 end_point 二选一
        avoid: 绕航节点（可选）
        through: 途经点（可选）
    返回：
        PlanRouteByPointResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "plan_route_by_point", locals())

@mcp.tool()
def plan_route_by_port(start_port_code: str, end_port_code: str, avoid: str = None, through: str = None) -> dict[str, Any]:
    """
    港口到港口航线规划
    查询两个港口之间的航线规划，获取航线的总里程以及航线经过的点位坐标经纬度。
    参数：
        start_port_code: 出发港标准五位码
        end_port_code: 到达港标准五位码
        avoid: 绕航节点（可选）
        through: 途经点（可选）
    返回：
        PlanRouteByPortResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "plan_route_by_port", locals())

@mcp.tool()
def get_single_eta_precise(mmsi: int, port_code: str = None, speed: float = None) -> dict[str, Any]:
    """
    预计到达时间(ETA)查询
    查询船舶在出发港的靠泊信息实际离港时间以及去往下一个目的港的总航程、已行驶航程和预计到达时间的预估。
    参数：
        mmsi: 船舶mmsi编号
        port_code: 港口五位码（可选）
        speed: 设定船速（可选）
    返回：
        GetSingleETAPreciseResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_single_eta_precise", locals())

@mcp.tool()
def get_weather_by_point(lng: float, lat: float, weather_time: int = None) -> dict[str, Any]:
    """
    单点海洋气象查询
    根据位置坐标查询全球的海洋气象数据，包括气压、气压流向、风向、风速、浪高、可见度等航海场景常用的气象信息。
    参数：
        lng: 经度
        lat: 纬度
        weather_time: 查询时间（可选，UTC时间戳）
    返回：
        GetWeatherByPointResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_weather_by_point", locals())

@mcp.tool()
def get_weather(weather_type: int) -> dict[str, Any]:
    """
    海区气象查询
    获取全球海区未来72小时以内的气象数据，以整个海区范围作为预报维度，数据不如单点海洋气象精准。
    参数：
        weather_type: 区域类型（0：全部；1：沿岸；2：近海；3：远海）
    返回：
        GetWeatherResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_weather", locals())

@mcp.tool()
def get_all_typhoon() -> dict[str, Any]:
    """
    获取全球台风列表
    查询近三年全球的台风数据，包括台风的位置、走向、风速、风级、半径等信息。请求数据时，需要先获取全球台风列表，再根据返回的台风信息中的台风id，查询单个台风的数据详情。
    返回：
        GetAllTyphoonResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_all_typhoon", locals())

@mcp.tool()
def get_single_typhoon(typhoon_id: int) -> dict[str, Any]:
    """
    获取单个台风信息，包括台风的位置、走向、风速、风级、半径等信息。请求数据时，需要先获取全球台风列表，再根据返回的台风信息中的台风id，查询单个台风的数据详情。
    
    参数：
        typhoon_id: 台风序号
    返回：
        GetSingleTyphoonResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_single_typhoon", locals())

@mcp.tool()
def get_tides() -> dict[str, Any]:
    """
    查询国内潮汐观测站列表
    查询国内潮汐观测站每天24小时潮汐变化数据。其中潮汐高度是根据每个港口的潮汐基准面计算的高度数据，不同港口的潮汐基准面不同，需要在请求并计算数据时注意。
    返回：
        GetTidesResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_tides", locals())

@mcp.tool()
def get_tide_data(port_code: int, start_date: str, end_date: str) -> dict[str, Any]:
    """
    查询单个港口潮汐观测站详情
    查询国内潮汐观测站每天24小时潮汐变化数据。其中潮汐高度是根据每个港口的潮汐基准面计算的高度数据，不同港口的潮汐基准面不同，需要在请求并计算数据时注意。
    参数：
        port_code: 潮汐观测站id
        start_date: 起始日期（yyyy-MM-dd）
        end_date: 结束日期（yyyy-MM-dd）
    返回：
        GetTideDataResponse: 查询结果，强类型返回
    """
    return invoke_tool(create_shipxy_api(), "get_tide_data", locals())


@mcp.tool()
def get_global_tides() -> dict[str, Any]:
    """
    查询全球潮汐观测站列表。
    返回：
        全球潮汐观测站列表；返回的 port_code 是潮汐站 id，不是港口五位码。
    """
    return invoke_tool(create_shipxy_api(), "get_global_tides", locals())


@mcp.tool()
def get_global_tide_data(port_code: int, start_date: str, end_date: str) -> dict[str, Any]:
    """
    查询单个全球潮汐观测站详情。
    参数：
        port_code: 全球潮汐观测站 id，由 get_global_tides 返回
        start_date: 起始日期（yyyy-MM-dd）
        end_date: 结束日期（yyyy-MM-dd）
    返回：
        全球潮汐概览和逐小时潮高数据。
    """
    return invoke_tool(create_shipxy_api(), "get_global_tide_data", locals())


@mcp.tool()
def current_weather(lng: float, lat: float) -> dict[str, Any]:
    """
    新全球实时气象查询。
    参数：
        lng: 经度，WGS84 十进制度
        lat: 纬度，WGS84 十进制度
    返回：
        实时大气气象和海洋气象数据。
    """
    return invoke_tool(create_shipxy_api(), "current_weather", locals())


@mcp.tool()
def future_weather(lng: float, lat: float) -> dict[str, Any]:
    """
    新全球未来气象预报查询。
    参数：
        lng: 经度，WGS84 十进制度
        lat: 纬度，WGS84 十进制度
    返回：
        未来大气气象和海洋气象预报数据。
    """
    return invoke_tool(create_shipxy_api(), "future_weather", locals())


@mcp.tool()
def history_weather(lng: float, lat: float, start_time: str, end_time: str) -> dict[str, Any]:
    """
    历史气象记录查询。
    参数：
        lng: 经度，WGS84 十进制度
        lat: 纬度，WGS84 十进制度
        start_time: 查询开始时间（yyyy-MM-dd HH:mm:ss）
        end_time: 查询结束时间（yyyy-MM-dd HH:mm:ss）
    返回：
        指定日期的大气气象和海洋气象历史数据。
    """
    return invoke_tool(create_shipxy_api(), "history_weather", locals())


@mcp.tool()
def get_nav_warning(start_time: str, end_time: str) -> dict[str, Any]:
    """
    航行警告查询。
    参数：
        start_time: 开始时间（yyyy-MM-dd HH:mm）
        end_time: 结束时间（yyyy-MM-dd HH:mm）
    返回：
        中国海事局航行警告列表。
    """
    return invoke_tool(create_shipxy_api(), "get_nav_warning", locals())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="运行 Shipxy MCP 服务。")
    parser.add_argument("--transport", choices=("stdio", "sse"), default=None, help="传输方式；默认 stdio。")
    parser.add_argument("--host", help="SSE 绑定主机；传入该参数时默认启动 SSE。")
    parser.add_argument("--port", type=int, help="SSE 监听端口；传入该参数时默认启动 SSE。")
    parser.add_argument("--debug", action="store_true", help="启用 Starlette debug 模式。")
    args = parser.parse_args()

    transport = args.transport or ("sse" if args.host or args.port else "stdio")
    if transport == "sse":
        run_sse_server(host=args.host or "0.0.0.0", port=args.port or 18081, debug=args.debug)
    else:
        mcp.run()
