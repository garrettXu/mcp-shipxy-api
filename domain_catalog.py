from __future__ import annotations

from copy import deepcopy
from typing import Any

from ship_service import (
    AnchorShipData,
    ApproachDataItem,
    BerthShipData,
    ETAShipData,
    GetSingleETAPreciseData,
    GetTideDataData,
    GetWeatherByPointData,
    GlobalTideStationInfo,
    NavWarningData,
    NewWeatherData,
    PortData,
    PortOfCallByPortData,
    PortOfCallByShipPortData,
    PortOfCallData,
    SearchShipResult,
    ShipParticularData,
    ShipPosition,
    ShipRegistryData,
    ShipStatusData,
    ShipTrackPoint,
    TideStationInfo,
    TyphoonDetailItem,
    TyphoonListItem,
    WeatherData,
    PlanRouteByPointData,
)


CAPABILITY_PREFIX = "capability://shipxy/"
OBJECT_PREFIX = "object://shipxy/"


FIELD_GLOSSARY: dict[str, str] = {
    "ok": "MCP 适配层调用是否完成。业务错误会以 ok=false 和结构化 error 返回。",
    "status": "Shipxy 业务状态码，0 表示成功。",
    "msg": "Shipxy 业务返回消息。",
    "total": "列表接口返回的匹配记录总数。",
    "data": "接口载荷，具体结构由 returns 和 object_refs 描述。",
    "raw": "当本地 schema 未完全匹配时保留的 Shipxy 原始响应。",
    "warning": "非致命适配层警告；数据已返回，但本地 schema 未完全匹配。",
    "mmsi": "水上移动业务标识码，9 位船舶识别码。",
    "imo": "国际海事组织船舶编号，通常为 7 位数字。",
    "call_sign": "船舶无线电呼号。",
    "ship_name": "船舶英文名。",
    "ship_cnname": "船舶中文名。",
    "match_type": "查询关键字命中船舶的匹配方式。",
    "data_source": "Shipxy 数据源代码。",
    "last_time": "最新 AIS 更新时间，格式化文本。",
    "last_time_utc": "最新 AIS 更新时间，Unix 时间戳。",
    "ship_type": "船舶类型代码或名称，具体取决于接口。",
    "length": "船长，单位米。",
    "width": "船宽，单位米。",
    "left": "AIS 天线到左舷距离，单位米。",
    "trail": "AIS 天线到船尾距离，单位米。",
    "draught": "船舶吃水，单位米。",
    "dest": "AIS 上报或 Shipxy 解析的目的地。",
    "destcode": "可用时返回的目的港代码。",
    "eta": "预计到达时间，格式化文本。",
    "eta_utc": "预计到达时间，Unix 时间戳。",
    "navistat": "AIS 航行状态代码。",
    "lat": "纬度，十进制度，有效范围 -90 到 90。",
    "lng": "经度，十进制度，有效范围 -180 到 180。",
    "sog": "对地航速，通常单位为节。",
    "cog": "对地航向，单位度。",
    "hdg": "船首向，单位度。",
    "rot": "转向率。",
    "region": "多边形区域字符串，格式为 lng,lat-lng,lat。",
    "scode": "区域查询返回的分页或会话令牌。",
    "registry": "船舶船籍或船旗信息。",
    "flag_country_code": "船旗国家或地区代码。",
    "flag_country": "船旗国家或地区名称。",
    "build_country": "船舶建造国家或地区。",
    "build_date": "船舶建造日期。",
    "class_name": "船级社名称。",
    "pandi_club": "保赔协会名称。",
    "gross_tonnage": "总吨。",
    "net_tonnage": "净吨。",
    "deadweight": "载重吨。",
    "teu": "集装箱容量，单位 TEU。",
    "speed_max": "最大航速。",
    "speed_service": "服务航速。",
    "port_code": "Shipxy 港口代码。港口类接口通常使用标准五位码，潮汐类接口使用观测站 ID。",
    "port_name": "港口英文名。",
    "port_cnname": "港口中文名。",
    "port_time_zone": "港口所在时区。",
    "port_country_name": "港口所在国家英文名。",
    "port_country_cnname": "港口所在国家中文名。",
    "port_country_code": "港口所在国家或地区代码。",
    "arrival_time": "到达时间，格式化文本。",
    "arrival_time_utc": "到达时间，Unix 时间戳。",
    "stay_time": "在港口、锚地或泊位停留时长。",
    "preport_cnname": "上一港中文名。",
    "ship_flag": "船旗国家或地区。",
    "utc": "Unix 时间戳。",
    "approach_zone": "Shipxy 搭靠区域代码。",
    "position": "事件位置文本描述。",
    "approach_time": "搭靠开始时间，格式化文本。",
    "approach_time_utc": "搭靠开始时间，Unix 时间戳。",
    "separation_time": "搭靠分离时间，格式化文本。",
    "separation_time_utc": "搭靠分离时间，Unix 时间戳。",
    "duration": "事件持续时长。",
    "terminal_name": "码头名称。",
    "berth_name": "泊位名称。",
    "arrival_anchorage": "到达锚地时间。",
    "arriveanchorage": "到达锚地时间；部分 Shipxy 接口使用该字段拼写。",
    "ata": "实际到港时间。",
    "atb": "实际靠泊时间。",
    "atd": "实际离港时间。",
    "arrival_draught": "到港吃水。",
    "departure_draught": "离港吃水。",
    "stay_terminal_time": "在码头停留时长。",
    "currentport": "当前靠港信息。",
    "previousport": "上一港信息。",
    "nextport": "下一港信息。",
    "current_sea_area": "当前海区名称。",
    "sea_area_code": "当前海区代码。",
    "current_city": "当前城市名称。",
    "current_city_code": "当前城市代码。",
    "distance": "航线距离，除非 Shipxy 文档另有说明，通常单位为海里。",
    "route": "按顺序排列的航线点。",
    "speed": "指定或计算的航速。",
    "sailed_distance": "已航行距离。",
    "sailed_time": "已航行时间。",
    "ais_speed": "根据 AIS 推断的航速。",
    "remaining_distance": "剩余航程距离。",
    "weather_type": "海区气象类型：0 全部，1 沿岸，2 近海，3 远海。",
    "sea_area": "海区名称。",
    "publish_time": "预报发布时间。",
    "center_lat": "预报区域中心纬度。",
    "center_lng": "预报区域中心经度。",
    "forecastaging": "预报时效或预报范围文本。",
    "meteorological": "天气现象文本。",
    "winddirection": "风向文本。",
    "windpower": "风力文本。",
    "waveheight": "浪高。",
    "visibility": "能见度。",
    "pressure": "气压。",
    "temperature": "温度。",
    "humidity": "湿度。",
    "winddir": "风向，单位度。",
    "windspeed": "风速。",
    "oceandir": "海流方向。",
    "oceanspeed": "海流速度。",
    "swelldir": "涌向。",
    "swellheight": "涌高。",
    "swellperiod": "涌浪周期。",
    "typhoon_id": "Shipxy 台风 ID。",
    "typhoon_code": "台风代码。",
    "typhoon_cncode": "台风中文代码。",
    "typhoon_cnname": "台风中文名。",
    "typhoon_name": "台风英文名。",
    "current_year": "台风年份。",
    "dataMark": "Shipxy 台风数据标记。",
    "typhoon_time": "台风观测时间。",
    "forecast": "预报机构或预报标签。",
    "fhour": "预报小时数。",
    "grade": "台风等级。",
    "mspeed": "最大风速。",
    "kspeed": "移动速度。",
    "direction": "移动方向。",
    "radius7": "7 级风圈半径。",
    "radius10": "10 级风圈半径。",
    "radius7_s": "7 级风圈半径详情。",
    "radius10_s": "10 级风圈半径详情。",
    "radius12_s": "12 级风圈半径详情。",
    "datumn": "观测站潮汐基准面。",
    "tide_type": "潮汐类型。",
    "tide_date": "潮汐日期。",
    "tide_time1": "第 1 个高潮或低潮时间。",
    "tide_time2": "第 2 个高潮或低潮时间。",
    "tide_time3": "第 3 个高潮或低潮时间。",
    "tide_time4": "第 4 个高潮或低潮时间。",
    "tide_height1": "第 1 个潮高。",
    "tide_height2": "第 2 个潮高。",
    "tide_height3": "第 3 个潮高。",
    "tide_height4": "第 4 个潮高。",
    "tide_lowhigh1": "第 1 个潮汐高低潮标记。",
    "tide_lowhigh2": "第 2 个潮汐高低潮标记。",
    "tide_lowhigh3": "第 3 个潮汐高低潮标记。",
    "tide_lowhigh4": "第 4 个潮汐高低潮标记。",
    "forecast_time": "气象记录的预报时间或观测时间。",
    "weather": "天气现象代码或标签。",
    "weather_desc": "天气现象的人类可读描述。",
    "precipitation": "降水量。",
    "winddir_10m": "10 米高度风向，单位度。",
    "windspeed_10m": "10 米高度风速。",
    "winddir_100m": "100 米高度风向，单位度。",
    "windspeed_100m": "100 米高度风速。",
    "wavedir": "浪向，单位度。",
    "waveperiod": "浪周期。",
    "windwaveheight": "风浪高度。",
    "windwavedir": "风浪方向，单位度。",
    "windwaveperiod": "风浪周期。",
    "sea_height": "海面高度。",
    "sea_temperature": "海面温度。",
    "sea_level_pressure": "海平面气压。",
    "warning_type": "航行警告类型代码。",
    "source": "警告发布来源。",
    "title": "航行警告标题。",
    "range_type": "警告影响范围类型。",
    "range_points": "警告影响范围坐标或几何文本。",
    "expire_time": "警告过期时间。",
    "pub_time": "警告发布时间。",
    "content": "航行警告正文。",
}


OBJECT_MODELS = {
    "SearchShipResult": SearchShipResult,
    "VesselPosition": ShipPosition,
    "ShipRegistry": ShipRegistryData,
    "ShipParticular": ShipParticularData,
    "Port": PortData,
    "BerthShip": BerthShipData,
    "AnchorShip": AnchorShipData,
    "ETAShip": ETAShipData,
    "ShipTrackPoint": ShipTrackPoint,
    "ShipApproach": ApproachDataItem,
    "PortCall": PortOfCallData,
    "PortCallByShipPort": PortOfCallByShipPortData,
    "ShipStatus": ShipStatusData,
    "PortCallByPort": PortOfCallByPortData,
    "Route": PlanRouteByPointData,
    "SingleETAPrecise": GetSingleETAPreciseData,
    "WeatherArea": WeatherData,
    "WeatherPoint": GetWeatherByPointData,
    "TyphoonListItem": TyphoonListItem,
    "TyphoonDetail": TyphoonDetailItem,
    "TideStation": TideStationInfo,
    "TideData": GetTideDataData,
    "GlobalTideStation": GlobalTideStationInfo,
    "NewWeather": NewWeatherData,
    "NavWarning": NavWarningData,
}


CAPABILITY_CATALOG: dict[str, dict[str, Any]] = {
    "search_ship": {
        "category": "船舶",
        "returns": "list[SearchShipResult]",
        "object_refs": ["SearchShipResult"],
        "when_to_use": "当用户只有船名、MMSI、IMO 或呼号时，用于先检索候选船舶。",
        "next_steps": ["选定 MMSI 后调用 get_single_ship 查询实时位置。", "需要 IMO 级别档案数据时调用 search_ship_particular。"],
    },
    "get_single_ship": {
        "category": "船舶",
        "returns": "VesselPosition",
        "object_refs": ["VesselPosition"],
        "when_to_use": "按一个 MMSI 查询最新 AIS 位置和核心船舶身份信息。",
        "next_steps": ["需要周边交通态势时调用 get_surrounding_ship。", "需要历史轨迹时调用 get_ship_track。"],
    },
    "get_many_ship": {
        "category": "船舶",
        "returns": "list[VesselPosition]",
        "object_refs": ["VesselPosition"],
        "when_to_use": "按已知 MMSI 列表批量查询最新 AIS 位置。",
    },
    "get_fleet_ship": {
        "category": "船舶",
        "returns": "list[VesselPosition]",
        "object_refs": ["VesselPosition"],
        "when_to_use": "查询 Shipxy 控制台中已配置船队下的船舶。",
    },
    "get_surrounding_ship": {
        "category": "船舶",
        "returns": "list[VesselPosition]",
        "object_refs": ["VesselPosition"],
        "when_to_use": "按已知 MMSI 查询该船 10 海里范围内的周边船舶。",
    },
    "get_area_ship": {
        "category": "船舶",
        "returns": "list[VesselPosition]",
        "object_refs": ["VesselPosition"],
        "when_to_use": "查询多边形区域内的船舶。",
    },
    "get_ship_registry": {
        "category": "船舶",
        "returns": "ShipRegistry",
        "object_refs": ["ShipRegistry"],
        "when_to_use": "按 MMSI 查询船籍或船旗信息。",
    },
    "search_ship_particular": {
        "category": "船舶",
        "returns": "list[ShipParticular]",
        "object_refs": ["ShipParticular"],
        "when_to_use": "查询船舶档案信息。至少需要 MMSI、IMO、呼号或船名中的一个。",
    },
    "search_port": {
        "category": "港口",
        "returns": "list[Port]",
        "object_refs": ["Port"],
        "when_to_use": "在调用港口、航线、靠泊、锚地、ETA 或靠港记录工具前，先查询 Shipxy 港口五位码。",
    },
    "get_berth_ships": {
        "category": "港口",
        "returns": "list[BerthShip]",
        "object_refs": ["BerthShip"],
        "when_to_use": "按已知港口五位码查询当前靠泊船舶。",
    },
    "get_anchor_ships": {
        "category": "港口",
        "returns": "list[AnchorShip]",
        "object_refs": ["AnchorShip"],
        "when_to_use": "按已知港口五位码查询当前锚地等待船舶。",
    },
    "get_eta_ships": {
        "category": "港口",
        "returns": "list[ETAShip]",
        "object_refs": ["ETAShip"],
        "when_to_use": "按港口五位码和 Unix 时间戳范围查询预计到港船舶。",
    },
    "get_ship_track": {
        "category": "轨迹",
        "returns": "list[ShipTrackPoint]",
        "object_refs": ["ShipTrackPoint"],
        "when_to_use": "按 MMSI 和时间范围查询历史 AIS 轨迹点。",
    },
    "search_ship_approach": {
        "category": "风险",
        "returns": "ShipApproach",
        "object_refs": ["ShipApproach"],
        "when_to_use": "查询指定 MMSI 在时间范围内的接近、贴靠或并排行驶事件。",
    },
    "get_port_of_call_by_ship": {
        "category": "靠港记录",
        "returns": "list[PortCall]",
        "object_refs": ["PortCall"],
        "when_to_use": "查询一艘船的历史靠港记录。",
    },
    "get_port_of_call_by_ship_port": {
        "category": "靠港记录",
        "returns": "list[PortCallByShipPort]",
        "object_refs": ["PortCallByShipPort"],
        "when_to_use": "查询一艘船在某个指定港口的靠港记录。",
    },
    "get_ship_status": {
        "category": "靠港记录",
        "returns": "list[ShipStatus]",
        "object_refs": ["ShipStatus"],
        "when_to_use": "查询船舶当前是否正在某个港口挂靠。",
    },
    "get_port_of_call_by_port": {
        "category": "靠港记录",
        "returns": "list[PortCallByPort]",
        "object_refs": ["PortCallByPort"],
        "when_to_use": "查询某个港口在时间范围内的历史靠港船舶。",
    },
    "plan_route_by_point": {
        "category": "航线",
        "returns": "Route",
        "object_refs": ["Route"],
        "when_to_use": "从一个经纬度点规划到另一个经纬度点或目的港五位码的海上航线。",
    },
    "plan_route_by_port": {
        "category": "航线",
        "returns": "Route",
        "object_refs": ["Route"],
        "when_to_use": "按两个 Shipxy 港口五位码规划港到港海上航线。",
    },
    "get_single_eta_precise": {
        "category": "ETA",
        "returns": "SingleETAPrecise",
        "object_refs": ["SingleETAPrecise"],
        "when_to_use": "查询一艘船的精准航程 ETA，可选指定目的港或航速。",
    },
    "get_weather_by_point": {
        "category": "气象",
        "returns": "WeatherPoint",
        "object_refs": ["WeatherPoint"],
        "when_to_use": "按坐标查询该点海洋气象。",
    },
    "get_weather": {
        "category": "气象",
        "returns": "list[WeatherArea]",
        "object_refs": ["WeatherArea"],
        "when_to_use": "按海区类型查询未来海洋气象。",
    },
    "get_all_typhoon": {
        "category": "台风",
        "returns": "list[TyphoonListItem]",
        "object_refs": ["TyphoonListItem"],
        "when_to_use": "查询台风列表，通常在调用 get_single_typhoon 前先使用。",
    },
    "get_single_typhoon": {
        "category": "台风",
        "returns": "list[TyphoonDetail]",
        "object_refs": ["TyphoonDetail"],
        "when_to_use": "按 typhoon_id 查询单个台风的详细轨迹和预报点。",
    },
    "get_tides": {
        "category": "潮汐",
        "returns": "list[TideStation]",
        "object_refs": ["TideStation"],
        "when_to_use": "查询国内潮汐观测站 ID，通常在调用 get_tide_data 前先使用。",
    },
    "get_tide_data": {
        "category": "潮汐",
        "returns": "TideData",
        "object_refs": ["TideData"],
        "when_to_use": "按国内潮汐观测站 ID 查询每日潮汐概览和逐小时潮高。",
        "parameter_notes": {
            "port_code": "使用 get_tides 返回的数字观测站 ID，不要使用港口五位码。",
            "start_date": "使用 yyyy-MM-dd 格式。",
            "end_date": "使用 yyyy-MM-dd 格式，且不能早于 start_date。",
        },
        "return_description": "返回国内潮汐观测站的每日高潮/低潮概览和逐小时潮高。",
    },
    "get_global_tides": {
        "category": "潮汐",
        "returns": "list[GlobalTideStation]",
        "object_refs": ["GlobalTideStation"],
        "when_to_use": "查询全球潮汐观测站 ID，通常在调用 get_global_tide_data 前先使用。",
        "next_steps": ["使用返回的数字 port_code 观测站 ID 调用 get_global_tide_data。"],
        "return_description": "返回全球潮汐观测站列表；其中 port_code 是观测站 ID，不是普通 Shipxy 港口五位码。",
    },
    "get_global_tide_data": {
        "category": "潮汐",
        "returns": "TideData",
        "object_refs": ["TideData"],
        "when_to_use": "按全球潮汐观测站 ID 查询每日潮汐概览和逐小时潮高。",
        "parameter_notes": {
            "port_code": "使用 get_global_tides 返回的数字观测站 ID，不要使用港口五位码。",
            "start_date": "使用 yyyy-MM-dd 格式。",
            "end_date": "使用 yyyy-MM-dd 格式，且不能早于 start_date。",
        },
        "return_description": "返回全球潮汐观测站的每日高潮/低潮概览和逐小时潮高。",
    },
    "current_weather": {
        "category": "气象",
        "returns": "NewWeather",
        "object_refs": ["NewWeather"],
        "when_to_use": "按坐标查询当前全球大气和海洋气象。",
        "parameter_notes": {
            "lng": "WGS84 十进制度经度，范围 -180 到 180。",
            "lat": "WGS84 十进制度纬度，范围 -90 到 90。",
        },
        "return_description": "返回当前温度、能见度、气压、风、浪、涌、流、海况等可用气象字段。",
    },
    "future_weather": {
        "category": "气象",
        "returns": "list[NewWeather]",
        "object_refs": ["NewWeather"],
        "when_to_use": "按坐标查询未来全球大气和海洋气象预报。",
        "parameter_notes": {
            "lng": "WGS84 十进制度经度，范围 -180 到 180。",
            "lat": "WGS84 十进制度纬度，范围 -90 到 90。",
        },
        "return_description": "返回包含预报时间及大气/海洋指标的未来气象记录。",
    },
    "history_weather": {
        "category": "气象",
        "returns": "list[NewWeather]",
        "object_refs": ["NewWeather"],
        "when_to_use": "按坐标和时间范围查询全球历史大气和海洋气象。",
        "parameter_notes": {
            "lng": "WGS84 十进制度经度，范围 -180 到 180。",
            "lat": "WGS84 十进制度纬度，范围 -90 到 90。",
            "start_time": "使用 yyyy-MM-dd HH:mm:ss 格式；这是秒级日期时间，不是 Unix 时间戳。",
            "end_time": "使用 yyyy-MM-dd HH:mm:ss 格式，且必须晚于 start_time。",
        },
        "return_description": "返回所选时间范围内的历史气象记录，具体字段随 Shipxy 数据可用性变化。",
    },
    "get_nav_warning": {
        "category": "海事数据",
        "returns": "list[NavWarning]",
        "object_refs": ["NavWarning"],
        "when_to_use": "按时间范围查询中国海事局发布的航行警告。",
        "parameter_notes": {
            "start_time": "使用 yyyy-MM-dd HH:mm 格式；这不是 Unix 时间戳。",
            "end_time": "使用 yyyy-MM-dd HH:mm 格式，且必须晚于 start_time。",
        },
        "return_description": "返回航行警告记录，包括标题、来源、影响范围、发布时间、过期时间和正文等可用信息。",
    },
}


ERROR_CATALOG: dict[str, dict[str, Any]] = {
    "invalid_request": {
        "meaning": "入参缺失、格式错误或超出允许范围。",
        "fix": "读取 error.details，修正对应字段后重试；如果返回 recommended_tool，优先按推荐工具补全前置信息。",
    },
    "permission_denied": {
        "meaning": "API Key 无效、已过期，或没有对应 Shipxy 服务/港口范围权限。",
        "fix": "请用户确认 SHIPXY_API_KEY，并在 Shipxy 控制台开通对应 API 权限或港口范围。",
    },
    "not_found": {
        "meaning": "请求的 Shipxy 实体不存在，或当前 API Key 无权查看。",
        "fix": "先使用搜索类工具查询实体，再用返回的 id/code 重试。",
    },
    "response_validation_failed": {
        "meaning": "Shipxy 返回数据与本地 Pydantic 模型不完全一致。",
        "fix": "raw/data 字段仍会返回原始数据；可以先读取 raw/data，并反馈 schema 漂移以便更新模型。",
    },
    "http_error": {
        "meaning": "Shipxy 返回了非 200 HTTP 响应。",
        "fix": "稍后重试或检查 status_code；持续失败可能表示接口地址或网络异常。",
    },
    "network_error": {
        "meaning": "当前服务无法连接 Shipxy。",
        "fix": "检查网络连通性后重试。",
    },
    "timeout": {
        "meaning": "Shipxy 请求超时。",
        "fix": "缩小查询范围或缩短时间窗口后重试。",
    },
    "shipxy_error": {
        "meaning": "Shipxy 返回了尚未映射到更具体类型的业务错误。",
        "fix": "读取 Shipxy 返回消息，并据此调整入参或服务权限。",
    },
}


def object_ref(name: str) -> str:
    return f"{OBJECT_PREFIX}{name}"


def capability_ref(tool_name: str) -> str:
    return f"{CAPABILITY_PREFIX}{tool_name}"


def _with_field_descriptions(schema: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(schema)

    def visit(node: Any) -> None:
        if not isinstance(node, dict):
            return
        node.pop("title", None)
        properties = node.get("properties")
        if isinstance(properties, dict):
            for field_name, field_schema in properties.items():
                if isinstance(field_schema, dict) and field_name in FIELD_GLOSSARY:
                    field_schema.setdefault("description", FIELD_GLOSSARY[field_name])
                visit(field_schema)
        for child_key in ("items", "additionalProperties"):
            visit(node.get(child_key))
        defs = node.get("$defs")
        if isinstance(defs, dict):
            for item in defs.values():
                visit(item)

    visit(result)
    return result


def describe_object(object_name: str | None = None) -> dict[str, Any]:
    if object_name:
        model = OBJECT_MODELS.get(object_name)
        if model is None:
            return {
                "ok": False,
                "error": {
                    "type": "not_found",
                    "message": f"未知 Shipxy 返回对象：{object_name}",
                    "available_objects": sorted(OBJECT_MODELS),
                },
            }
        return {
            "ok": True,
            "object": object_name,
            "object_ref": object_ref(object_name),
            "schema": _with_field_descriptions(model.model_json_schema()),
        }

    return {
        "ok": True,
        "objects": [
            {
                "name": name,
                "object_ref": object_ref(name),
                "fields": sorted(model.model_json_schema().get("properties", {}).keys()),
            }
            for name, model in sorted(OBJECT_MODELS.items())
        ],
    }


def tool_response_metadata(tool_name: str) -> dict[str, Any]:
    capability = CAPABILITY_CATALOG.get(tool_name, {})
    object_names = capability.get("object_refs", [])
    return {
        "returns": capability.get("returns", "未知"),
        "capability_ref": capability_ref(tool_name),
        "object_refs": [object_ref(name) for name in object_names],
    }


def describe_capability(tool_schema: dict[str, Any]) -> dict[str, Any]:
    name = tool_schema["name"]
    capability = CAPABILITY_CATALOG.get(name, {})
    metadata = tool_response_metadata(name)
    parameter_notes = capability.get("parameter_notes", {})
    parameter_requirements = [
        {
            "name": param["name"],
            "type": param["type"],
            "required": param["required"],
            "positional": param["positional"],
            "default": param["default"],
            "description": param["help"],
            "note": parameter_notes.get(param["name"], ""),
        }
        for param in tool_schema.get("parameters", [])
    ]
    return {
        **tool_schema,
        **metadata,
        "category": capability.get("category", "其他"),
        "usage_scope": capability.get("usage_scope", capability.get("when_to_use", tool_schema.get("summary", ""))),
        "when_to_use": capability.get("when_to_use", tool_schema.get("summary", "")),
        "parameter_requirements": parameter_requirements,
        "return_description": capability.get("return_description", f"返回 {metadata['returns']}。字段定义请调用 describe_object 查看。"),
        "next_steps": capability.get("next_steps", []),
        "common_errors": ERROR_CATALOG,
        "result_contract": {
            "success": {
                "ok": True,
                "tool": name,
                "returns": metadata["returns"],
                "capability_ref": metadata["capability_ref"],
                "object_refs": metadata["object_refs"],
                "data": "与 returns/object_refs 对应的业务数据。",
            },
            "error": {
                "ok": False,
                "tool": name,
                "capability_ref": metadata["capability_ref"],
                "error": {
                    "type": "invalid_request | permission_denied | not_found | response_validation_failed | http_error | network_error | timeout | shipxy_error",
                    "message": "中文错误说明。",
                    "details": "可用时返回字段级错误详情。",
                    "fix": "可用时返回可执行的修复建议。",
                },
            },
        },
    }


def describe_capabilities(tool_schemas: list[dict[str, Any]], tool_name: str | None = None) -> dict[str, Any]:
    if tool_name:
        normalized = tool_name.replace("-", "_")
        for tool_schema in tool_schemas:
            if tool_schema["name"] == normalized:
                return {"ok": True, "capability": describe_capability(tool_schema)}
        return {
            "ok": False,
            "error": {
                "type": "not_found",
                "message": f"未知 Shipxy 工具：{tool_name}",
                "available_tools": [tool["name"] for tool in tool_schemas],
            },
        }

    return {
        "ok": True,
        "capabilities": [describe_capability(tool_schema) for tool_schema in tool_schemas],
    }


def error_fix(error_type: str | None) -> dict[str, Any] | None:
    if not error_type:
        return None
    entry = ERROR_CATALOG.get(error_type)
    if not entry:
        return None
    return {"meaning": entry["meaning"], "strategy": entry["fix"]}
