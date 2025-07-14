# server.py
from mcp.server.fastmcp import FastMCP
from ship_service import (
    ShipxyAPI,
    SearchShipResponse,
    SingleShipResponse,
    ManyShipResponse,
    FleetShipResponse,
    SurRoundingShipResponse,
    AreaShipResponse,
    ShipRegistryResponse,
    SearchShipParticularResponse,
    SearchPortResponse,
    GetBerthShipsResponse,
    GetAnchorShipsResponse,
    GetETAShipsResponse,
    GetShipTrackResponse,
    SearchShipApproachResponse,
    GetPortOfCallByShipResponse,
    GetPortOfCallByShipPortResponse,
    GetShipStatusResponse,
    GetPortOfCallByPortResponse,
    PlanRouteByPointResponse,
    PlanRouteByPortResponse,
    GetSingleETAPreciseResponse,
    GetWeatherByPointResponse,
    GetWeatherResponse,
    GetAllTyphoonResponse,
    GetSingleTyphoonResponse,
    GetTidesResponse,
    GetTideDataResponse
)
import contextvars
import argparse
import logging
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.responses import PlainTextResponse
from mcp.server.sse import SseServerTransport
from mcp.server import Server
from dotenv import load_dotenv
import os
load_dotenv()
# Create an MCP server
api_key = os.getenv('SHIPXY_API_KEY')
mcp = FastMCP("ship_xy_mcp")


def create_shipxy_api() -> ShipxyAPI:
    """创建ShipxyAPI实例"""
    global api_key
    return ShipxyAPI(api_key=api_key)

# ShipxyAPI工具封装
@mcp.tool()
def search_ship(keywords: str, max_results: int = None) -> SearchShipResponse:
    """
    船舶模糊查询服务，是使用关键字（mmsi、imo、船名、呼号等）作为查询条件，模糊查询出所有符合条件的船舶静态信息；当使用imo作为输入时，可以查询该imo编号下，曾经使用的所有mmsi记录；当使用船名作为查询输入时，可以查询该船名所有历史使用船舶的信息。
    注：mmsi（Maritime Mobile Service Identity）‌，中文称为水上移动业务标识码，是一种九位数字码，用于船舶无线电通信系统中，能够独特识别各类台站和成组呼叫台站。MMSI具有唯一性，每条船都有一个对应的MMSI码，通常被称为“一船一码”或“九位码”‌，同一条船舶mmsi编号有可能在售卖后变更，mmsi前三位代表国家和地区。
    imo（International Maritime Organization），是国际海事组织为每一条船分配的唯一识别码,由七位数字组成,用于全球范围内对船舶身份、技术信息及安全记录的追踪与管理。
    Args:
        keywords: 查询关键字（船名、呼号、MMSI、IMO等）
        max_results: 最大返回数量（可选，最大100）
    Returns:
        SearchShipResponse: 查询结果，强类型返回
    Raises:
        Exception: 请求失败或返回错误码
    """
    return create_shipxy_api().search_ship(keywords, max_results)

@mcp.tool()
def get_single_ship(mmsi: int) -> SingleShipResponse:
    """
    单船位置查询
    根据船舶mmsi编码查询船舶的基础静态信息以及船舶的实时动态信息，包括船舶imo编号、呼号、船舶中英文名称、船舶类型、长度宽度以及AIS最新更新上报的船舶实时位置、航行状态、船舶目的港口、船舶实时速度、预计到达目的港的时间、航首向航迹向等。
    Args:
        mmsi: 船舶mmsi编号
    Returns:
        SingleShipResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_single_ship(mmsi)

@mcp.tool()
def get_many_ship(mmsis: list[int]) -> ManyShipResponse:
    """
    多船位置查询
    根据多个船舶船舶mmsi编码查询船舶的基础静态信息以及船舶的实时动态信息，包括船舶imo编号、呼号、船舶中英文名称、船舶类型、长度宽度以及AIS最新更新上报的船舶实时位置、航行状态、船舶目的港口、船舶实时速度、预计到达目的港的时间、航首向航迹向等。
    Args:
        mmsis: 船舶mmsi编号列表（最多100个）
    Returns:
        ManyShipResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_many_ship(mmsis)

@mcp.tool()
def get_fleet_ship(fleet_id: str) -> FleetShipResponse:
    """
    船队船位置查询
    控制台中维护的船队id，查询船队下所有船舶数据。
    Args:
        fleet_id: 船队编号
    Returns:
        FleetShipResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_fleet_ship(fleet_id)

@mcp.tool()
def get_surrounding_ship(mmsi: int) -> SurRoundingShipResponse:
    """
    周边船舶查询
    通过船舶的 MMSI进行查询，获取以当前船舶位置为圆心以 10 海里为半径的圆形区域内的船舶数据。返回的船舶数据列表按照由近及远进行排序，返回的数据包括船舶imo编号、呼号、船舶中英文名称、船舶类型、长度宽度以及AIS最新更新上报的船舶实时位置、航行状态、船舶目的港口、船舶实时速度、预计到达目的港的时间、航首向航迹向等。 
    Args:
        mmsi: 船舶mmsi编号
    Returns:
        SurRoundingShipResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_surrounding_ship(mmsi)

@mcp.tool()
def get_area_ship(region: str, output: int = 1, scode: int = None) -> AreaShipResponse:
    """
    区域船舶查询
    通过船舶的 MMSI进行查询，获取以当前船舶位置为圆心以 10 海里为半径的圆形区域内的船舶数据。返回的船舶数据列表按照由近及远进行排序，返回的数据包括船舶imo编号、呼号、船舶中英文名称、船舶类型、长度宽度以及AIS最新更新上报的船舶实时位置、航行状态、船舶目的港口、船舶实时速度、预计到达目的港的时间、航首向航迹向等。 
    Args:
        region: 区域字符串（lng,lat-lng,lat-...）
        output: 输出格式，1为json，0为base64
        scode: 会话令牌（可选）
    Returns:
        AreaShipResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_area_ship(region, output, scode)

@mcp.tool()
def get_ship_registry(mmsi: int) -> ShipRegistryResponse:
    """
    船籍信息查询
    通过船舶的mmsi编号来查询匹配船舶的船籍国家或地区信息。
    Args:
        mmsi: 船舶mmsi编号
    Returns:
        ShipRegistryResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_ship_registry(mmsi)

@mcp.tool()
def search_ship_particular(mmsi: int = None, imo: int = None, call_sign: str = None, ship_name: str = None) -> SearchShipParticularResponse:
    """
    船舶档案查询
    通过船舶的mmsi编号、imo编号、呼号或者船舶的英文名称来查询船舶的劳式档案数据。注：只有具备imo编号的船舶有档案记录
    Args:
        mmsi: 船舶mmsi编号（可选）
        imo: imo编号（可选）
        call_sign: 呼号（可选）
        ship_name: 船名（可选）
    Returns:
        SearchShipParticularResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().search_ship_particular(mmsi, imo, call_sign, ship_name)

@mcp.tool()
def search_port(keywords: str, max_results: int = None) -> SearchPortResponse:
    """
    港口查询
    对全球港口数据进行模糊查询，支持通过港口的中英文名称和五位码模糊检索获取港口的基本信息，包括港口中英文名称、港口五位码、港口所在时区等。返回结果中获取的五位码是船讯网以港口维度查询数据的唯一标识。
    Args:
        keywords: 港口关键字（中文/英文/五位码）
        max_results: 最大返回数量（可选，最大100）
    Returns:
        SearchPortResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().search_port(keywords, max_results)

@mcp.tool()
def get_berth_ships(port_code: str, ship_type: int = None) -> GetBerthShipsResponse:
    """
    港口靠泊船舶查询
    使用港口五位码查询当前港口正在靠泊的全部船舶信息，包括当前靠泊船的总数量、船舶类型、船舶基础信息、船舶到达港口时间和停留时间。
    Args:
        port_code: 港口标准五位码
        ship_type: 船舶类型（可选）
    Returns:
        GetBerthShipsResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_berth_ships(port_code, ship_type)

@mcp.tool()
def get_anchor_ships(port_code: str, ship_type: int = None) -> GetAnchorShipsResponse:
    """
    港口锚地船舶查询
    使用港口五位码查询当前港口正在锚地的全部船舶信息，包括当前港口锚地等待船舶的总数量、船舶类型、船舶基础信息、船舶到达港口时间和停留时间。
    Args:
        port_code: 港口标准五位码
        ship_type: 船舶类型（可选）
    Returns:
        GetAnchorShipsResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_anchor_ships(port_code, ship_type)

@mcp.tool()
def get_eta_ships(port_code: str, start_time: int, end_time: int, ship_type: int = None) -> GetETAShipsResponse:
    """
    预抵港船舶查询
    使用港口五位码和时间周期查询在未来某一时间段预计到达该港口的船舶列表和船舶信息。
    Args:
        port_code: 港口标准五位码
        start_time: 开始时间（UTC时间戳）
        end_time: 结束时间（UTC时间戳）
        ship_type: 船舶类型（可选）
    Returns:
        GetETAShipsResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_eta_ships(port_code, start_time, end_time, ship_type)

@mcp.tool()
def get_ship_track(mmsi: int, start_time: int, end_time: int, output: int = 1) -> GetShipTrackResponse:
    """
    船舶轨迹查询
    通过船舶的mmsi编号和时间段，查询船舶历史经过的轨迹点。
    Args:
        mmsi: 船舶mmsi编号
        start_time: 查询的开始时间，unix时间戳
        end_time: 查询的截止时间，unix时间戳
        output: 输出格式，1为json，0为base64，默认为1
    Returns:
        GetShipTrackResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_ship_track(mmsi, start_time, end_time, output)

@mcp.tool()
def search_ship_approach(mmsi: int, start_time: int, end_time: int, approach_zone: int = None) -> SearchShipApproachResponse:
    """
    船舶搭靠事件查询
    查询指定船舶在一段时间内是否有搭靠行为，如果有搭靠行为则列出搭靠的船舶详细信息以及搭靠的位置、坐标、搭靠开始时间、结束时间等。根据全球船舶实时位置监控，测算两船贴近停靠或并排行驶超过5分钟，则判定为船舶搭靠。
    Args:
        mmsi: 船舶mmsi编号
        start_time: 开始时间（UTC时间戳）
        end_time: 结束时间（UTC时间戳）
        approach_zone: 搭靠地区（可选）
    Returns:
        SearchShipApproachResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().search_ship_approach(mmsi, start_time, end_time, approach_zone)

@mcp.tool()
def get_port_of_call_by_ship(mmsi: int, start_time: int, end_time: int, imo: int = None, ship_name: str = None, call_sign: str = None, time_zone: int = 2) -> GetPortOfCallByShipResponse:
    """
    船舶靠港记录查询
    查询船舶在一段时间以内的历史靠港记录，可以获得船舶到达锚地的时间、到达港口范围以及停靠到泊位的时间，以及船舶在港口停留的时长，进出港的吃水情况等。
    Args:
        mmsi: 船舶mmsi编号
        start_time: 开始时间（UTC时间戳）
        end_time: 结束时间（UTC时间戳）
        imo: IMO编号（可选）
        ship_name: 船舶英文名称（可选）
        call_sign: 船舶呼号（可选）
        time_zone: 时区（默认2，北京时区）
    Returns:
        GetPortOfCallByShipResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_port_of_call_by_ship(mmsi, start_time, end_time, imo, ship_name, call_sign, time_zone)

@mcp.tool()
def get_port_of_call_by_ship_port(mmsi: int, port_code: str, start_time: int, end_time: int, imo: int = None, ship_name: str = None, call_sign: str = None, time_zone: int = 2) -> GetPortOfCallByShipPortResponse:
    """
    船舶在指定港口的靠港记录查询
    查询船舶在一段时间以内的在某一具体港口靠港的记录，可以获得船舶到达锚地的时间、到达港口范围以及停靠到泊位的时间，以及船舶在港口停留的时长，进出港的吃水情况等。
    Args:
        mmsi: 船舶mmsi编号
        port_code: 港口五位码
        start_time: 开始时间（UTC时间戳）
        end_time: 结束时间（UTC时间戳）
        imo: IMO编号（可选）
        ship_name: 船舶英文名称（可选）
        call_sign: 船舶呼号（可选）
        time_zone: 时区（默认2，北京时区）
    Returns:
        GetPortOfCallByShipPortResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_port_of_call_by_ship_port(mmsi, port_code, start_time, end_time, imo, ship_name, call_sign, time_zone)

@mcp.tool()
def get_ship_status(mmsi: int, imo: int = None, ship_name: str = None, call_sign: str = None, time_zone: int = 2) -> GetShipStatusResponse:
    """
    船舶当前挂靠信息查询
    查询船舶当前时间点是否挂靠了港口，如果当前正在某一港口挂靠，则可以获得当前挂靠港口的信息以及入港时间。
    Args:
        mmsi: 船舶mmsi编号
        imo: IMO编号（可选）
        ship_name: 船舶英文名称（可选）
        call_sign: 船舶呼号（可选）
        time_zone: 时区（默认2，北京时区）
    Returns:
        GetShipStatusResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_ship_status(mmsi, imo, ship_name, call_sign, time_zone)

@mcp.tool()
def get_port_of_call_by_port(port_code: str, start_time: int, end_time: int, type_: int = 1, time_zone: int = 2) -> GetPortOfCallByPortResponse:
    """
    港口靠港记录查询
    使用港口五位码查询港口在某一时间周期内历史靠泊的所有船舶信息。包括船舶基础信息、船舶在该港口的靠港记录以及船舶在上一个港口和下一个港口的靠港记录信息。
    Args:
        port_code: 港口五位码
        start_time: 开始时间（UTC时间戳）
        end_time: 结束时间（UTC时间戳）
        type_: 查询类型（1:ATA，2:ATD，默认1）
        time_zone: 时区（默认2，北京时区）
    Returns:
        GetPortOfCallByPortResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_port_of_call_by_port(port_code, start_time, end_time, type_, time_zone)

@mcp.tool()
def plan_route_by_point(start_point: str, end_point: str, avoid: str = None, through: str = None) -> PlanRouteByPointResponse:
    """
    点到点航线规划
    查询两个坐标点之间的航线规划，获取航线的总里程以及航线经过的点位坐标经纬度。
    Args:
        start_point: 起始点（lng,lat）
        end_point: 结束点（lng,lat）
        avoid: 绕航节点（可选）
        through: 途经点（可选）
    Returns:
        PlanRouteByPointResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().plan_route_by_point(start_point, end_point, avoid, through)

@mcp.tool()
def plan_route_by_port(start_port_code: str, end_port_code: str, avoid: str = None, through: str = None) -> PlanRouteByPortResponse:
    """
    港口到港口航线规划
    查询两个港口之间的航线规划，获取航线的总里程以及航线经过的点位坐标经纬度。
    Args:
        start_port_code: 出发港PortCode港口标准五位码
        end_port_code: 到达港PortCode港口标准五位码
        avoid: 绕航节点（可选）
        through: 途经点（可选）
    Returns:
        PlanRouteByPortResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().plan_route_by_port(start_port_code, end_port_code, avoid, through)

@mcp.tool()
def get_single_eta_precise(mmsi: int, port_code: str = None, speed: float = None) -> GetSingleETAPreciseResponse:
    """
    预计到达时间(ETA)查询
    查询船舶在出发港的靠泊信息实际离港时间以及去往下一个目的港的总航程、已行驶航程和预计到达时间的预估。
    Args:
        mmsi: 船舶mmsi编号
        port_code: 港口五位码（可选）
        speed: 设定船速（可选）
    Returns:
        GetSingleETAPreciseResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_single_eta_precise(mmsi, port_code, speed)

@mcp.tool()
def get_weather_by_point(lng: float, lat: float, weather_time: int = None) -> GetWeatherByPointResponse:
    """
    单点海洋气象查询
    根据位置坐标查询全球的海洋气象数据，包括气压、气压流向、风向、风速、浪高、可见度等航海场景常用的气象信息。
    Args:
        lng: 经度
        lat: 纬度
        weather_time: 查询时间（可选，UTC时间戳）
    Returns:
        GetWeatherByPointResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_weather_by_point(lng, lat, weather_time)

@mcp.tool()
def get_weather(weather_type: int) -> GetWeatherResponse:
    """
    海区气象查询
    获取全球海区未来72小时以内的气象数据，以整个海区范围作为预报维度，数据不如单点海洋气象精准。
    Args:
        weather_type: 区域类型（0：全部；1：沿岸；2：近海；3：远海）
    Returns:
        GetWeatherResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_weather(weather_type)

@mcp.tool()
def get_all_typhoon() -> GetAllTyphoonResponse:
    """
    获取全球台风列表
    查询近三年全球的台风数据，包括台风的位置、走向、风速、风级、半径等信息。请求数据时，需要先获取全球台风列表，再根据返回的台风信息中的台风id，查询单个台风的数据详情。
    Returns:
        GetAllTyphoonResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_all_typhoon()

@mcp.tool()
def get_single_typhoon(typhoon_id: int) -> GetSingleTyphoonResponse:
    """
    获取单个台风信息，包括台风的位置、走向、风速、风级、半径等信息。请求数据时，需要先获取全球台风列表，再根据返回的台风信息中的台风id，查询单个台风的数据详情。
    
    Args:
        typhoon_id: 台风序号
    Returns:
        GetSingleTyphoonResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_single_typhoon(typhoon_id)

@mcp.tool()
def get_tides() -> GetTidesResponse:
    """
    查询国内潮汐观测站列表
    查询国内潮汐观测站每天24小时潮汐变化数据。其中潮汐高度是根据每个港口的潮汐基准面计算的高度数据，不同港口的潮汐基准面不同，需要在请求并计算数据时注意。
    Returns:
        GetTidesResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_tides()

@mcp.tool()
def get_tide_data(port_code: int, start_date: str, end_date: str) -> GetTideDataResponse:
    """
    查询单个港口潮汐观测站详情
    查询国内潮汐观测站每天24小时潮汐变化数据。其中潮汐高度是根据每个港口的潮汐基准面计算的高度数据，不同港口的潮汐基准面不同，需要在请求并计算数据时注意。
    Args:
        port_code: 潮汐观测站id
        start_date: 起始日期（yyyy-MM-dd）
        end_date: 结束日期（yyyy-MM-dd）
    Returns:
        GetTideDataResponse: 查询结果，强类型返回
    """
    return create_shipxy_api().get_tide_data(port_code, start_date, end_date)


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run()