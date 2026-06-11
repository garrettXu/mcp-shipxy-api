import requests
import os

from dotenv import load_dotenv
from typing import Optional, Dict, List, Any, Tuple
import requests
import time
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, ValidationError


DEFAULT_TIMEOUT = 30


class ShipxyAPIError(Exception):
    def __init__(self, message: str, status: int | float | None = None):
        super().__init__(message)
        self.status = status


class SearchShipResult(BaseModel):
    match_type: int
    mmsi: int
    imo: int
    call_sign: str
    ship_name: str
    data_source: int
    last_time: str
    last_time_utc: int

class SearchShipResponse(BaseModel):
    status: int
    msg: str
    total: int
    data: List[SearchShipResult]

class ShipPosition(BaseModel):
    mmsi: int
    imo: int
    call_sign: str
    ship_name: str
    ship_cnname: str
    data_source: int
    ship_type: int
    length: float
    width: float
    left: float
    trail: float
    draught: float
    dest: str
    destcode: str
    eta: str
    eta_utc: int = 0  # 有些接口可能没有此字段
    navistat: int
    lat: float
    lng: float
    sog: float
    cog: float
    hdg: float
    rot: float
    last_time: str
    last_time_utc: int

class SingleShipResponse(BaseModel):
    status: int
    msg: str
    data: ShipPosition

class ManyShipResponse(BaseModel):
    status: int
    msg: str
    data: list[ShipPosition]

class FleetShipResponse(BaseModel):
    status: int
    msg: str
    data: list[ShipPosition]

class SurRoundingShipResponse(BaseModel):
    status: int
    msg: str
    total: int
    data: list[ShipPosition]

class AreaShipData(BaseModel):
    total: int
    scode: int
    continue_: int = Field(0, alias="continue")  # 'continue'为Python关键字，改为continue_
    ship_list: list[ShipPosition]

class AreaShipResponse(BaseModel):
    status: int
    msg: str
    data: AreaShipData

class ShipRegistryData(BaseModel):
    mmsi: int
    registry: str

class ShipRegistryResponse(BaseModel):
    status: int
    msg: str
    data: ShipRegistryData

class EngineInfo(BaseModel):
    designer: str
    powerKW: int

class ShipParticularData(BaseModel):
    mmsi: int
    imo: int
    call_sign: str
    ship_name: str
    length: float
    mould_width: float
    flag_country_code: str
    flag_country: str
    build_country: str
    build_date: str
    class_name: str
    pandi_club: str
    ship_type: str
    ship_type_level5_subgroup: str
    ship_type_group: str
    ship_status: str
    gross_tonnage: float
    net_tonnage: float
    deadweight: float
    teu: int
    speed_max: float
    speed_service: float
    draught: float
    port_of_registry: str
    group_code: str
    group_company: str
    group_country_code: str
    group_country: str
    shipmanager_code: str
    shipmanager_company: str
    shipmanager_country_code: str
    shipManager_country: str
    operator_code: str
    operator_company: str
    operator_country_code: str
    operator_country: str
    doc_code: str
    doc_company: str
    doc_country_code: str
    doc_country: str
    registered_code: str
    registered_owner: str
    registered_country_code: str
    registered_country: str
    technical_code: str
    technical_manager: str
    technical_country_code: str
    technical_country: str
    builder_code: str
    builder_company: str
    builder_country_code: str
    builder_country: str
    update_time: str
    main_engine_list: list[EngineInfo]
    aux_engine_list: list[EngineInfo]

class SearchShipParticularResponse(BaseModel):
    status: int
    msg: str
    data: list[ShipParticularData]

class PortData(BaseModel):
    port_code: str
    port_name: str
    port_cnname: str
    port_time_zone: str
    port_country_name: str = ""
    port_country_cnname: str = ""
    port_country_code: str = ""

class SearchPortResponse(BaseModel):
    status: int
    msg: str
    total: int
    data: list[PortData]

class BerthShipData(BaseModel):
    mmsi: int
    imo: int
    call_sign: str
    ship_name: str
    ship_type: int
    length: float
    width: float
    left: float
    trail: float
    draught: float
    arrival_time: str
    arrival_time_utc: int
    stay_time: float
    navistat: int = 0  # 有些数据可能没有该字段

class GetBerthShipsResponse(BaseModel):
    status: int
    msg: str
    total: int
    data: list[BerthShipData]

class AnchorShipData(BaseModel):
    mmsi: int
    imo: int
    call_sign: str
    ship_name: str
    ship_type: int
    length: float
    width: float
    left: float
    trail: float
    draught: float
    arrival_time: str
    arrival_time_utc: int
    stay_time: float
    navistat: int = 0  # 有些数据可能没有该字段

class GetAnchorShipsResponse(BaseModel):
    status: int
    msg: str
    total: int = 0
    data: list[AnchorShipData] = []

class ETAShipData(BaseModel):
    mmsi: int
    ship_name: str
    imo: int
    dwt: float
    ship_type: str | int
    length: float
    width: float
    draught: float
    preport_cnname: str
    last_time: str
    last_time_utc: int
    eta: str
    eta_utc: int
    dest: str
    ship_flag: str = ""
    registry: str = ""

class GetETAShipsResponse(BaseModel):
    status: int
    msg: str
    total: int
    data: list[ETAShipData]

class ShipTrackPoint(BaseModel):
    data_source: int
    utc: int
    lng: float
    lat: float
    sog: float
    cog: float

class GetShipTrackResponse(BaseModel):
    status: int
    msg: str
    data: list[ShipTrackPoint]

class ApproachShipInfo(BaseModel):
    mmsi: int
    imo: int
    call_sign: str
    ship_name: str
    ship_type: int

class ApproachEventInfo(BaseModel):
    approach_zone: int
    lat: float
    lng: float
    port_code: str
    position: str
    approach_time: str
    approach_time_utc: int
    separation_time: str
    separation_time_utc: int
    duration: float
    sog: float

class ApproachDataItem(BaseModel):
    approach_ship: ApproachShipInfo
    approach_event: ApproachEventInfo

class ShipApproachData(BaseModel):
    ship_data: ApproachShipInfo
    approach_data: list[ApproachDataItem]

class SearchShipApproachResponse(BaseModel):
    status: int
    msg: str
    data: ShipApproachData

class PortOfCallData(BaseModel):
    ship_name: str
    call_sign: str
    imo: int
    mmsi: int
    ship_type: int
    port_cnname: str
    port_name: str
    port_time_zone: str
    port_code: str
    terminal_name: str
    berth_name: str
    port_country_cnname: str
    port_country_name: str
    port_country_code: str
    arrival_anchorage: str = ""
    ata: str = ""
    atb: str = ""
    atd: str = ""
    arrival_draught: float = 0.0
    departure_draught: float = 0.0
    stay_time: float = 0.0
    stay_terminal_time: float = 0.0

class GetPortOfCallByShipResponse(BaseModel):
    status: int
    msg: str
    data: list[PortOfCallData]

class PortOfCallByShipPortData(BaseModel):
    ship_name: str
    call_sign: str
    imo: int
    mmsi: int
    ship_type: str
    port_cnname: str
    port_name: str
    port_time_zone: str
    port_code: str
    terminal_name: str
    berth_name: str
    port_country_cnname: str
    port_country_name: str
    port_country_code: str
    arriveanchorage: str = ""
    ata: str = ""
    atb: str = ""
    atd: str = ""
    arrival_draught: float = 0.0
    departure_draught: float = 0.0
    stay_time: float = 0.0
    stay_terminal_time: float = 0.0

class GetPortOfCallByShipPortResponse(BaseModel):
    status: int
    msg: str
    total: int
    data: list[PortOfCallByShipPortData]

class PortInfo(BaseModel):
    port_code: str = ""
    port_name: str = ""
    port_cnname: str = ""
    port_time_zone: str = ""
    port_country_name: str = ""
    port_country_cnname: str = ""
    port_country_code: str = ""
    arrive_anchorage: str = ""
    ata: str = ""
    atb: str = ""
    atd: str = ""
    # currentport 可能有 country_en、country_code、arriveanchorage
    country_en: str = ""
    country_code: str = ""
    arriveanchorage: str = ""

class ShipStatusData(BaseModel):
    ship_name: str
    call_sign: str
    imo: int
    mmsi: int
    ship_type: str
    current_sea_area: str = ""
    sea_area_code: str = ""
    current_city: str = ""
    current_city_code: str = ""
    lng: float = 0.0
    lat: float = 0.0
    previousport: PortInfo = None
    currentport: PortInfo = None

class GetShipStatusResponse(BaseModel):
    status: int
    msg: str
    total: int
    data: list[ShipStatusData]

class PortCallPortInfo(BaseModel):
    port_code: str = ""
    port_cnname: str = ""
    port_name: str = ""
    port_time_zone: str = ""
    terminal_name: str = ""
    berth_name: str = ""
    arrival_anchorage: str = ""
    ata: str = ""
    atb: str = ""
    atd: str = ""
    arrival_draught: float = 0.0
    departure_draught: float = 0.0
    stay_time: float = 0.0
    stay_terminal_time: float = 0.0

class PortOfCallByPortData(BaseModel):
    imo: int
    mmsi: int
    ship_type: str
    ship_name: str
    call_sign: str
    currentport: PortCallPortInfo = None
    previousport: PortCallPortInfo = None
    nextport: PortCallPortInfo = None

class GetPortOfCallByPortResponse(BaseModel):
    status: int
    msg: str
    total: int
    data: list[PortOfCallByPortData]

class RoutePoint(BaseModel):
    lng: float
    lat: float

class PlanRouteByPointData(BaseModel):
    distance: float
    route: list[RoutePoint]

class PlanRouteByPointResponse(BaseModel):
    status: int
    msg: str
    data: PlanRouteByPointData

class PlanRouteByPortData(BaseModel):
    distance: float
    route: list[RoutePoint]

class PlanRouteByPortResponse(BaseModel):
    status: int
    msg: str
    data: PlanRouteByPortData

class SingleETAShipInfo(BaseModel):
    mmsi: int
    imo: int
    ship_name: str
    call_sign: str
    ship_type: int

class SingleETALocationInfo(BaseModel):
    lng: float
    lat: float
    speed: float = 0.0
    sog: float = 0.0
    sea_area: str = ""
    sea_area_code: str | int = ""

class SingleETAPortInfo(BaseModel):
    port_code: str = ""
    port_cnname: str = ""
    port_name: str = ""
    time_zone: int = 0
    port_country_code: str = ""
    port_country_name: str = ""
    port_country_cnname: str = ""
    ata: float = 0.0
    atb: float = 0.0
    atd: float = 0.0

class SingleETANextPortInfo(BaseModel):
    port_code: str = ""
    port_cnname: str = ""
    port_name: str = ""
    time_zone: int = 0
    port_country_code: str = ""
    port_country_name: str = ""
    port_country_cnname: str = ""
    sailed_distance: float = 0.0
    sailed_time: float = 0.0
    ais_speed: float = 0.0
    speed: float = 0.0
    eta: str = ""
    eta_utc: int = 0
    remaining_distance: float = 0.0
    distance: float = 0.0

class GetSingleETAPreciseData(BaseModel):
    ship: SingleETAShipInfo
    location: SingleETALocationInfo
    preport: SingleETAPortInfo
    nextport: SingleETANextPortInfo

class GetSingleETAPreciseResponse(BaseModel):
    status: int
    msg: str
    data: GetSingleETAPreciseData

class WeatherData(BaseModel):
    weather_type: int
    sea_area: str
    publish_time: str
    center_lat: float
    center_lng: float
    forecastaging: str
    meteorological: str
    winddirection: str
    windpower: str
    waveheight: str = None
    visibility: float

class GetWeatherResponse(BaseModel):
    status: int
    msg: str
    total: int
    data: list[WeatherData]

class TyphoonListItem(BaseModel):
    typhoon_id: int | str
    typhoon_code: int | str
    typhoon_cncode: str
    typhoon_cnname: str
    typhoon_name: str
    current_year: int | str
    dataMark: str

class GetAllTyphoonResponse(BaseModel):
    status: int
    msg: str
    total: int
    data: list[TyphoonListItem]

class TyphoonDetailItem(BaseModel):
    typhoon_id: int | str
    typhoon_time: int | str
    forecast: str
    fhour: str
    lat: float
    lng: float
    grade: int
    mspeed: float
    pressure: float
    kspeed: float
    direction: str
    radius7: float
    radius10: float
    radius7_s: float | str
    radius10_s: float | str
    radius12_s: float | str

class GetSingleTyphoonResponse(BaseModel):
    status: int
    msg: str
    total: int
    data: list[TyphoonDetailItem]

class TideStationInfo(BaseModel):
    port_code: int
    port_cnname: str
    port_name: str
    port_country_cnname: str
    port_country_name: str
    lat: float
    lng: float
    port_time_zone: str
    datumn: str
    tide_type: str

class GetTidesResponse(BaseModel):
    status: int
    msg: str
    total: int
    data: list[TideStationInfo]

class TideOverviewItem(BaseModel):
    tide_date: str
    tide_time1: str
    tide_time2: str
    tide_time3: str
    tide_time4: str
    tide_height1: float
    tide_height2: float
    tide_height3: float
    tide_height4: float
    tide_lowhigh1: str
    tide_lowhigh2: str
    tide_lowhigh3: str
    tide_lowhigh4: str

class TideDetailItem(BaseModel):
    tide_date: str
    h0: float = 0.0
    h1: float = 0.0
    h2: float = 0.0
    h3: float = 0.0
    h4: float = 0.0
    h5: float = 0.0
    h6: float = 0.0
    h7: float = 0.0
    h8: float = 0.0
    h9: float = 0.0
    h10: float = 0.0
    h11: float = 0.0
    h12: float = 0.0
    h13: float = 0.0
    h14: float = 0.0
    h15: float = 0.0
    h16: float = 0.0
    h17: float = 0.0
    h18: float = 0.0
    h19: float = 0.0
    h20: float = 0.0
    h21: float = 0.0
    h22: float = 0.0
    h23: float = 0.0

class GetTideDataData(BaseModel):
    overview: list[TideOverviewItem]
    detail: list[TideDetailItem]

class GetTideDataResponse(BaseModel):
    status: int
    msg: str
    data: GetTideDataData

class GetWeatherByPointData(BaseModel):
    bm500: float
    humidity: float
    oceandir: float
    oceanspeed: float
    pressure: float
    swelldir: float
    swellheight: float
    swellperiod: float
    temperature: float
    visibility: float
    waveheight: float
    winddir: float
    windspeed: float
    publish_time: str
    lng: float
    lat: float

class GetWeatherByPointResponse(BaseModel):
    status: float
    msg: str
    data: GetWeatherByPointData


class FlexibleModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class GlobalTideStationInfo(FlexibleModel):
    port_code: int | str | None = None
    port_cnname: str | None = None
    port_name: str | None = None
    port_country_cnname: str | None = None
    port_country_name: str | None = None
    lat: float | None = None
    lng: float | None = None
    port_time_zone: str | None = None
    datumn: str | None = None
    tide_type: str | None = None


class GetGlobalTidesResponse(BaseModel):
    status: int
    msg: str
    total: int = 0
    data: list[GlobalTideStationInfo] = []


class GetGlobalTideDataResponse(BaseModel):
    status: int
    msg: str
    data: Any


class NewWeatherData(FlexibleModel):
    lng: float | None = None
    lat: float | None = None
    forecast_time: str | int | None = None
    publish_time: str | int | None = None
    temperature: float | None = None
    visibility: float | None = None
    pressure: float | None = None
    precipitation: float | None = None
    weather: str | None = None
    weather_desc: str | None = None
    winddir_10m: float | None = None
    windspeed_10m: float | None = None
    winddir_100m: float | None = None
    windspeed_100m: float | None = None
    waveheight: float | None = None
    wavedir: float | None = None
    waveperiod: float | None = None
    swellheight: float | None = None
    swelldir: float | None = None
    swellperiod: float | None = None
    windwaveheight: float | None = None
    windwavedir: float | None = None
    windwaveperiod: float | None = None
    oceandir: float | None = None
    oceanspeed: float | None = None
    sea_height: float | None = None
    sea_temperature: float | None = None
    sea_level_pressure: float | None = None


class WeatherFlexibleResponse(BaseModel):
    status: int | float
    msg: str
    data: Any


class NavWarningData(FlexibleModel):
    warning_type: int | str | None = None
    source: str | None = None
    title: str | None = None
    range_type: int | str | None = None
    range_points: Any = None
    expire_time: str | None = None
    pub_time: str | None = None
    content: str | None = None


class GetNavWarningResponse(BaseModel):
    status: int
    msg: str
    total: int = 0
    data: list[NavWarningData] = []

class ShipxyAPI:
    """船讯网API封装"""
    def __init__(self, api_key: str, base_url: str = "http://api.shipxy.com/apicall"):
        """
        初始化船讯网API客户端
        
        参数：
            api_key: 船讯网提供的API key
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        
        # 船舶类型映射字典
        self.ship_types = {
            50: "引航船",
            51: "搜救船",
            52: "拖轮",
            53: "港口供应船",
            54: "载有防污染装置和设备的船舶",
            55: "执法艇",
            56: "备用-用于当地船舶的任务分配",
            57: "备用-用于当地船舶的任务分配",
            58: "医疗船",
            59: "符合18号决议的船舶",
            30: "捕捞",
            31: "拖引",
            32: "拖引(船长>200m或船宽>25m)",
            33: "疏浚或水下作业",
            34: "潜水作业",
            35: "参与军事行动",
            36: "帆船航行",
            37: "娱乐船"
        }
        
        # 船舶类型范围映射
        self.ship_type_ranges = {
            (20, 29): "地效应船",
            (40, 49): "高速船",
            (60, 69): "客船",
            (70, 79): "货船",
            (80, 89): "油轮",
            (90, 99): "其他类型船舶"
        }
        
        # 特殊类型
        self.special_types = {
            100: "集装箱"
        }

    def _classify_error(self, message: str) -> str:
        """将 Shipxy 或客户端错误消息映射成稳定的错误类型。"""
        lowered = (message or "").lower()
        if any(token in lowered for token in ["permission", "unauthorized", "forbidden", "无权限", "权限", "未授权", "key", "ak", "超出限定", "限定"]):
            return "permission_denied"
        if any(token in lowered for token in ["不存在", "未找到", "搜索不到", "无结果", "not found"]):
            return "not_found"
        if any(token in lowered for token in ["参数", "param", "invalid", "必须", "缺少", "missing"]):
            return "invalid_request"
        if any(token in lowered for token in ["timeout", "timed out", "超时"]):
            return "timeout"
        return "shipxy_error"

    def _error_result(
        self,
        error_type: str,
        message: str,
        *,
        endpoint: str | None = None,
        status_code: int | None = None,
        shipxy_status: int | float | None = None,
        details: Any = None,
    ) -> dict[str, Any]:
        error: dict[str, Any] = {
            "type": error_type,
            "message": message,
        }
        if endpoint is not None:
            error["endpoint"] = endpoint
        if status_code is not None:
            error["status_code"] = status_code
        if shipxy_status is not None:
            error["shipxy_status"] = shipxy_status
        if details is not None:
            error["details"] = details
        return {"ok": False, "error": error}

    def _validation_details(self, exc: ValidationError) -> list[dict[str, Any]]:
        details = []
        for error in exc.errors():
            details.append(
                {
                    "field": ".".join(str(part) for part in error.get("loc", ())),
                    "message": error.get("msg", ""),
                    "type": error.get("type", ""),
                }
            )
        return details

    def _success_result(self, endpoint: str, resp_json: dict[str, Any], model_cls: type[BaseModel]) -> dict[str, Any]:
        """优先返回解析后的数据；解析失败时回退到 Shipxy 原始数据。"""
        try:
            parsed = model_cls(**resp_json).model_dump(mode="json", by_alias=True)
            return {"ok": True, "endpoint": endpoint, **parsed}
        except ValidationError as exc:
            result: dict[str, Any] = {
                "ok": True,
                "endpoint": endpoint,
                "status": resp_json.get("status"),
                "msg": resp_json.get("msg", ""),
                "data": resp_json.get("data"),
                "raw": resp_json,
                "warning": {
                    "type": "response_validation_failed",
                    "message": "Shipxy 返回数据与本地 Pydantic 模型不完全匹配，已返回原始响应数据。",
                    "details": self._validation_details(exc),
                },
            }
            if "total" in resp_json:
                result["total"] = resp_json.get("total")
            return result

    def _exception_result(self, operation: str, exc: Exception) -> dict[str, Any]:
        if isinstance(exc, ValidationError):
            return self._error_result(
                "response_validation_failed",
                "Shipxy 返回数据与本地 Pydantic 模型不完全匹配。",
                endpoint=operation,
                details=self._validation_details(exc),
            )

        if isinstance(exc, ShipxyAPIError):
            message = str(exc)
            return self._error_result(
                self._classify_error(message),
                message,
                endpoint=operation,
                shipxy_status=exc.status,
            )

        message = str(exc)
        if message.startswith("HTTP请求失败:"):
            status_text = message.split(":", 1)[1].strip()
            status_code = int(status_text) if status_text.isdigit() else None
            return self._error_result("http_error", message, endpoint=operation, status_code=status_code)

        if message.startswith("请求船讯网失败:"):
            return self._error_result("network_error", message, endpoint=operation)

        if message.startswith("船讯网返回错误:"):
            clean_message = message.split(":", 1)[1].strip()
            return self._error_result(self._classify_error(clean_message), clean_message, endpoint=operation)

        return self._error_result(self._classify_error(message), message, endpoint=operation)

    def _get_ship_type_name(self, type_code: int) -> str:
        """获取船舶类型名称
        
        参数：
            type_code: 船舶类型代码
            
        返回：
            船舶类型名称
        """
        # 首先检查精确匹配
        if type_code in self.ship_types:
            return self.ship_types[type_code]
            
        # 检查特殊类型
        if type_code in self.special_types:
            return self.special_types[type_code]
            
        # 检查范围匹配
        for range_tuple, type_name in self.ship_type_ranges.items():
            if range_tuple[0] <= type_code <= range_tuple[1]:
                return type_name
                
        return "未知类型"

    def search_ship(self, keywords: str, max_results: Optional[int] = None) -> SearchShipResponse:
        """
        查询船舶信息（SearchShip接口）
        参数：
            keywords: 查询关键字（船名、呼号、MMSI、IMO等）
            max_results: 最大返回数量（可选，最大100）
        返回：
            SearchShipResponse: 查询结果，强类型返回
        异常：
            请求失败或返回错误码
        """
        url = f"{self.base_url}/v3/SearchShip"
        params = {
            "key": self.api_key,
            "keywords": keywords
        }
        if max_results is not None:
            params["max"] = max_results
        
        # 优先GET请求，若参数过长则自动切换POST
        try:
            response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
            if response.status_code == 414:  # URI Too Long
                response = requests.post(url, data=params, timeout=DEFAULT_TIMEOUT)
        except Exception as e:
            raise Exception(f"请求船讯网失败: {e}")
        
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        
        # 强类型化返回
        return self._success_result("SearchShip", resp_json, SearchShipResponse)

    def get_single_ship(self, mmsi: int) -> SingleShipResponse:
        """
        单船位置查询
        参数：
            mmsi: 船舶mmsi编号
        返回：
            SingleShipResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetSingleShip"
        params = {
            "key": self.api_key,
            "mmsi": mmsi
        }
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetSingleShip", resp_json, SingleShipResponse)

    def get_many_ship(self, mmsis: list[int]) -> ManyShipResponse:
        """
        多船位置查询
        参数：
            mmsis: 船舶mmsi编号列表（最多100个）
        返回：
            ManyShipResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetManyShip"
        mmsis_str = ','.join(str(m) for m in mmsis)
        params = {
            "key": self.api_key,
            "mmsis": mmsis_str
        }
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetManyShip", resp_json, ManyShipResponse)

    def get_fleet_ship(self, fleet_id: str) -> FleetShipResponse:
        """
        船队船位置查询
        参数：
            fleet_id: 船队编号
        返回：
            FleetShipResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetFleetShip"
        params = {
            "key": self.api_key,
            "fleet_id": fleet_id
        }
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetFleetShip", resp_json, FleetShipResponse)

    def get_surrounding_ship(self, mmsi: int) -> SurRoundingShipResponse:
        """
        周边船舶查询
        参数：
            mmsi: 船舶mmsi编号
        返回：
            SurRoundingShipResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetSurRoundingShip"
        params = {
            "key": self.api_key,
            "mmsi": mmsi
        }
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetSurRoundingShip", resp_json, SurRoundingShipResponse)

    def get_area_ship(self, region: str, output: int = 1, scode: int = None) -> AreaShipResponse:
        """
        区域船舶查询
        参数：
            region: 区域字符串（lng,lat-lng,lat-...）
            output: 输出格式，1为json，0为base64
            scode: 会话令牌（可选）
        返回：
            AreaShipResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetAreaShip"
        params = {
            "key": self.api_key,
            "region": region,
            "output": output
        }
        if scode is not None:
            params["scode"] = scode
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetAreaShip", resp_json, AreaShipResponse)

    def get_ship_registry(self, mmsi: int) -> ShipRegistryResponse:
        """
        船籍信息查询
        参数：
            mmsi: 船舶mmsi编号
        返回：
            ShipRegistryResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetShipRegistry"
        params = {
            "key": self.api_key,
            "mmsi": mmsi
        }
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetShipRegistry", resp_json, ShipRegistryResponse)

    def search_ship_particular(self, mmsi: int = None, imo: int = None, call_sign: str = None, ship_name: str = None) -> SearchShipParticularResponse:
        """
        船舶档案查询
        参数：
            mmsi: 船舶mmsi编号（可选）
            imo: imo编号（可选）
            call_sign: 呼号（可选）
            ship_name: 船名（可选）
        返回：
            SearchShipParticularResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/SearchShipParticular"
        params = {"key": self.api_key}
        if mmsi is not None:
            params["mmsi"] = mmsi
        if imo is not None:
            params["imo"] = imo
        if call_sign is not None:
            params["call_sign"] = call_sign
        if ship_name is not None:
            params["ship_name"] = ship_name
        if len(params) == 1:
            raise Exception("必须至少提供mmsi、imo、call_sign、ship_name中的一个")
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("SearchShipParticular", resp_json, SearchShipParticularResponse)

    def search_port(self, keywords: str, max_results: int = None) -> SearchPortResponse:
        """
        港口查询
        参数：
            keywords: 港口关键字（中文/英文/五位码）
            max_results: 最大返回数量（可选，最大100）
        返回：
            SearchPortResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/SearchPort"
        params = {
            "key": self.api_key,
            "keywords": keywords
        }
        if max_results is not None:
            params["max"] = max_results
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("SearchPort", resp_json, SearchPortResponse)

    def get_berth_ships(self, port_code: str, ship_type: int = None) -> GetBerthShipsResponse:
        """
        港口靠泊船舶查询
        参数：
            port_code: 港口标准五位码
            ship_type: 船舶类型（可选）
        返回：
            GetBerthShipsResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetBerthShips"
        params = {
            "key": self.api_key,
            "port_code": port_code
        }
        if ship_type is not None:
            params["ship_type"] = ship_type
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetBerthShips", resp_json, GetBerthShipsResponse)

    def get_anchor_ships(self, port_code: str, ship_type: int = None) -> GetAnchorShipsResponse:
        """
        港口锚地船舶查询
        参数：
            port_code: 港口标准五位码
            ship_type: 船舶类型（可选）
        返回：
            GetAnchorShipsResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetAnchorShips"
        params = {
            "key": self.api_key,
            "port_code": port_code
        }
        if ship_type is not None:
            params["ship_type"] = ship_type
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        # 兼容返回结构为list或dict
        if isinstance(resp_json.get("data"), dict):
            return self._success_result("GetAnchorShips", {**resp_json, "total": 1, "data": [resp_json["data"]]}, GetAnchorShipsResponse)
        return self._success_result("GetAnchorShips", resp_json, GetAnchorShipsResponse)

    def get_eta_ships(self, port_code: str, start_time: int, end_time: int, ship_type: int = None) -> GetETAShipsResponse:
        """
        预抵港船舶查询
        参数：
            port_code: 港口标准五位码
            start_time: 开始时间（UTC时间戳）
            end_time: 结束时间（UTC时间戳）
            ship_type: 船舶类型（可选）
        返回：
            GetETAShipsResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetETAShips"
        params = {
            "key": self.api_key,
            "port_code": port_code,
            "start_time": start_time,
            "end_time": end_time
        }
        if ship_type is not None:
            params["ship_type"] = ship_type
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetETAShips", resp_json, GetETAShipsResponse)

    def get_ship_track(self, mmsi: int, start_time: int, end_time: int, output: int = 1) -> GetShipTrackResponse:
        """
        船舶轨迹查询
        参数：
            mmsi: 船舶mmsi编号
            start_time: 查询的开始时间，unix时间戳
            end_time: 查询的截止时间，unix时间戳
            output: 输出格式，1为json，0为base64，默认为1
        返回：
            GetShipTrackResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetShipTrack"
        params = {
            "key": self.api_key,
            "mmsi": mmsi,
            "start_time": start_time,
            "end_time": end_time,
            "output": output
        }
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetShipTrack", resp_json, GetShipTrackResponse)

    def search_ship_approach(self, mmsi: int, start_time: int, end_time: int, approach_zone: int = None) -> SearchShipApproachResponse:
        """
        船舶搭靠事件查询
        参数：
            mmsi: 船舶mmsi编号
            start_time: 开始时间（UTC时间戳）
            end_time: 结束时间（UTC时间戳）
            approach_zone: 搭靠地区（可选）
        返回：
            SearchShipApproachResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/SearchshipApproach"
        params = {
            "key": self.api_key,
            "mmsi": mmsi,
            "start_time": start_time,
            "end_time": end_time
        }
        if approach_zone is not None:
            params["approach_zone"] = approach_zone
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg") or resp_json.get("message", "未知错误"), resp_json.get("status"))
        return self._success_result("SearchshipApproach", resp_json, SearchShipApproachResponse)

    def get_port_of_call_by_ship(self, mmsi: int, start_time: int, end_time: int, imo: int = None, ship_name: str = None, call_sign: str = None, time_zone: int = 2) -> GetPortOfCallByShipResponse:
        """
        船舶靠港记录查询
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
        url = f"{self.base_url}/v3/GetPortofCallByShip"
        params = {
            "key": self.api_key,
            "mmsi": mmsi,
            "start_time": start_time,
            "end_time": end_time,
            "time_zone": time_zone
        }
        if imo is not None:
            params["imo"] = imo
        if ship_name is not None:
            params["ship_name"] = ship_name
        if call_sign is not None:
            params["call_sign"] = call_sign
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetPortofCallByShip", resp_json, GetPortOfCallByShipResponse)

    def get_port_of_call_by_ship_port(self, mmsi: int, port_code: str, start_time: int, end_time: int, imo: int = None, ship_name: str = None, call_sign: str = None, time_zone: int = 2) -> GetPortOfCallByShipPortResponse:
        """
        船舶在指定港口的靠港记录查询
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
        url = f"{self.base_url}/v3/GetPortofCallByShipPort"
        params = {
            "key": self.api_key,
            "mmsi": mmsi,
            "port_code": port_code,
            "start_time": start_time,
            "end_time": end_time,
            "time_zone": time_zone
        }
        if imo is not None:
            params["imo"] = imo
        if ship_name is not None:
            params["ship_name"] = ship_name
        if call_sign is not None:
            params["call_sign"] = call_sign
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetPortofCallByShipPort", resp_json, GetPortOfCallByShipPortResponse)

    def get_ship_status(self, mmsi: int, imo: int = None, ship_name: str = None, call_sign: str = None, time_zone: int = 2) -> GetShipStatusResponse:
        """
        船舶状态查询
        参数：
            mmsi: 船舶mmsi编号
            imo: IMO编号（可选）
            ship_name: 船舶英文名称（可选）
            call_sign: 船舶呼号（可选）
            time_zone: 时区（默认2，北京时区）
        返回：
            GetShipStatusResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetShipStatus"
        params = {
            "key": self.api_key,
            "mmsi": mmsi,
            "time_zone": time_zone
        }
        if imo is not None:
            params["imo"] = imo
        if ship_name is not None:
            params["ship_name"] = ship_name
        if call_sign is not None:
            params["call_sign"] = call_sign
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetShipStatus", resp_json, GetShipStatusResponse)

    def get_port_of_call_by_port(self, port_code: str, start_time: int, end_time: int, type_: int = 1, time_zone: int = 2) -> GetPortOfCallByPortResponse:
        """
        港口靠港记录查询
        参数：
            port_code: 港口五位码
            start_time: 开始时间（UTC时间戳）
            end_time: 结束时间（UTC时间戳）
            type_: 查询类型（1:ATA，2:ATD，默认1）
            time_zone: 时区（默认2，北京时区）
        返回：
            GetPortOfCallByPortResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetPortofCallByPort"
        params = {
            "key": self.api_key,
            "port_code": port_code,
            "start_time": start_time,
            "end_time": end_time,
            "type": type_,
            "time_zone": time_zone
        }
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetPortofCallByPort", resp_json, GetPortOfCallByPortResponse)

    def plan_route_by_point(self, start_point: str, end_point: str = None, end_port_code: str = None, avoid: str = None, through: str = None) -> PlanRouteByPointResponse:
        """
        航线规划（经纬度点）
        参数：
            start_point: 起始点（lng,lat）
            end_point: 结束点（lng,lat）
            end_port_code: 结束港口五位码
            avoid: 绕航节点（可选）
            through: 途经点（可选）
        返回：
            PlanRouteByPointResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/PlanRouteByPoint"
        params = {
            "key": self.api_key,
            "start_point": start_point,
        }
        if end_point is not None:
            params["end_point"] = end_point
        if end_port_code is not None:
            params["end_port_code"] = end_port_code
        if avoid is not None:
            params["avoid"] = avoid
        if through is not None:
            params["through"] = through
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("PlanRouteByPoint", resp_json, PlanRouteByPointResponse)

    def plan_route_by_port(self, start_port_code: str, end_port_code: str, avoid: str = None, through: str = None) -> PlanRouteByPortResponse:
        """
        航线规划（港口）
        参数：
            start_port_code: 出发港标准五位码
            end_port_code: 到达港标准五位码
            avoid: 绕航节点（可选）
            through: 途经点（可选）
        返回：
            PlanRouteByPortResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/PlanRouteByPort"
        params = {
            "key": self.api_key,
            "start_port_code": start_port_code,
            "end_port_code": end_port_code
        }
        if avoid is not None:
            params["avoid"] = avoid
        if through is not None:
            params["through"] = through
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("PlanRouteByPort", resp_json, PlanRouteByPortResponse)

    def get_single_eta_precise(self, mmsi: int, port_code: str = None, speed: float = None) -> GetSingleETAPreciseResponse:
        """
        单船精确ETA查询
        参数：
            mmsi: 船舶mmsi编号
            port_code: 港口五位码（可选）
            speed: 设定船速（可选）
        返回：
            GetSingleETAPreciseResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetSingleETAPrecise"
        params = {
            "key": self.api_key,
            "mmsi": mmsi
        }
        if port_code is not None:
            params["port_code"] = port_code
        if speed is not None:
            params["speed"] = speed
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetSingleETAPrecise", resp_json, GetSingleETAPreciseResponse)

    def get_weather(self, weather_type: int) -> GetWeatherResponse:
        """
        区域气象查询
        参数：
            weather_type: 区域类型（0：全部；1：沿岸；2：近海；3：远海）
        返回：
            GetWeatherResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetWeather"
        params = {
            "key": self.api_key,
            "weather_type": weather_type
        }
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetWeather", resp_json, GetWeatherResponse)

    def get_all_typhoon(self) -> GetAllTyphoonResponse:
        """
        获取全球台风列表
        返回：
            GetAllTyphoonResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetAllTyphoon"
        params = {"key": self.api_key}
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetAllTyphoon", resp_json, GetAllTyphoonResponse)

    def get_single_typhoon(self, typhoon_id: int) -> GetSingleTyphoonResponse:
        """
        获取单个台风信息
        参数：
            typhoon_id: 台风序号
        返回：
            GetSingleTyphoonResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetSingleTyphoon"
        params = {"key": self.api_key, "typhoon_id": typhoon_id}
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetSingleTyphoon", resp_json, GetSingleTyphoonResponse)

    def get_tides(self) -> GetTidesResponse:
        """
        查询国内潮汐观测站列表
        返回：
            GetTidesResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetTides"
        params = {"key": self.api_key}
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetTides", resp_json, GetTidesResponse)

    def get_tide_data(self, port_code: int, start_date: str, end_date: str) -> GetTideDataResponse:
        """
        查询单个港口潮汐观测站详情
        参数：
            port_code: 潮汐观测站id
            start_date: 起始日期（yyyy-MM-dd）
            end_date: 结束日期（yyyy-MM-dd）
        返回：
            GetTideDataResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetTideData"
        params = {
            "key": self.api_key,
            "port_code": port_code,
            "start_date": start_date,
            "end_date": end_date
        }
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetTideData", resp_json, GetTideDataResponse)

    def get_weather_by_point(self, lng: float, lat: float, weather_time: int = None) -> GetWeatherByPointResponse:
        """
        单点海洋气象查询
        请求地址: https://api.shipxy.com/apicall/v3/GetWeatherByPoint
        请求方式: GET
        请求调用示例:
            https://api.shipxy.com/apicall/v3/GetWeatherByPoint?key=你的key&lng=123.58414&lat=27.37979
        参数：
            lng: 经度，WGS84坐标系，格式为lng=155.2134
            lat: 纬度，WGS84坐标系，格式为lat=20.2134
            weather_time: 查询时间（可选，UTC时间戳），不填写则查询最近时间的气象数据
        返回：
            GetWeatherByPointResponse: 查询结果，强类型返回
        异常：
            请求失败或返回错误码
        """
        url = f"{self.base_url}/v3/GetWeatherByPoint"
        params = {
            "key": self.api_key,
            "lng": lng,
            "lat": lat
        }
        if weather_time is not None:
            params["weather_time"] = weather_time
        try:
            response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        except Exception as e:
            raise Exception(f"请求船讯网失败: {e}")
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetWeatherByPoint", resp_json, GetWeatherByPointResponse)

    def get_global_tides(self) -> GetGlobalTidesResponse:
        """
        查询全球潮汐观测站列表。
        返回：
            GetGlobalTidesResponse: 全球潮汐观测站列表。
        """
        url = f"{self.base_url}/v3/GetGlobalTides"
        params = {"key": self.api_key}
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetGlobalTides", resp_json, GetGlobalTidesResponse)

    def get_global_tide_data(self, port_code: int, start_date: str, end_date: str) -> GetGlobalTideDataResponse:
        """
        查询单个全球潮汐观测站详情。
        参数：
            port_code: 全球潮汐观测站 id，不是港口五位码。
            start_date: 起始日期 yyyy-MM-dd。
            end_date: 结束日期 yyyy-MM-dd。
        返回：
            GetGlobalTideDataResponse: 潮汐概览和小时潮高数据。
        """
        url = f"{self.base_url}/v3/GetGlobalTideData"
        params = {
            "key": self.api_key,
            "port_code": port_code,
            "start_date": start_date,
            "end_date": end_date,
        }
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetGlobalTideData", resp_json, GetGlobalTideDataResponse)

    def current_weather(self, lng: float, lat: float) -> WeatherFlexibleResponse:
        """
        新全球实时气象查询。
        参数：
            lng: 经度。
            lat: 纬度。
        返回：
            WeatherFlexibleResponse: 实时大气气象和海洋气象数据。
        """
        url = f"{self.base_url}/v3/CurrentWeather"
        params = {"key": self.api_key, "lng": lng, "lat": lat}
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("CurrentWeather", resp_json, WeatherFlexibleResponse)

    def future_weather(self, lng: float, lat: float) -> WeatherFlexibleResponse:
        """
        新全球未来气象预报查询。
        参数：
            lng: 经度。
            lat: 纬度。
        返回：
            WeatherFlexibleResponse: 未来 7 天大气气象和海洋气象预报数据。
        """
        url = f"{self.base_url}/v3/FutureWeather"
        params = {"key": self.api_key, "lng": lng, "lat": lat}
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("FutureWeather", resp_json, WeatherFlexibleResponse)

    def history_weather(self, lng: float, lat: float, start_time: str, end_time: str) -> WeatherFlexibleResponse:
        """
        历史气象记录查询。
        参数：
            lng: 经度。
            lat: 纬度。
            start_time: 查询开始时间 yyyy-MM-dd HH:mm:ss，支持历史三年内数据。
            end_time: 查询结束时间 yyyy-MM-dd HH:mm:ss。
        返回：
            WeatherFlexibleResponse: 历史大气气象和海洋气象数据。
        """
        url = f"{self.base_url}/v3/HistoryWeather"
        params = {"key": self.api_key, "lng": lng, "lat": lat, "start_time": start_time, "end_time": end_time}
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("HistoryWeather", resp_json, WeatherFlexibleResponse)

    def get_nav_warning(self, start_time: str, end_time: str) -> GetNavWarningResponse:
        """
        航行警告查询。
        参数：
            start_time: 开始时间 yyyy-MM-dd HH:mm。
            end_time: 结束时间 yyyy-MM-dd HH:mm。
        返回：
            GetNavWarningResponse: 中国海事局航行警告列表。
        """
        url = f"{self.base_url}/v3/GetNavWarning"
        params = {"key": self.api_key, "start_time": start_time, "end_time": end_time}
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise ShipxyAPIError(resp_json.get("msg", "未知错误"), resp_json.get("status"))
        return self._success_result("GetNavWarning", resp_json, GetNavWarningResponse)


def _wrap_shipxy_api_methods() -> None:
    method_names = [
        "search_ship",
        "get_single_ship",
        "get_many_ship",
        "get_fleet_ship",
        "get_surrounding_ship",
        "get_area_ship",
        "get_ship_registry",
        "search_ship_particular",
        "search_port",
        "get_berth_ships",
        "get_anchor_ships",
        "get_eta_ships",
        "get_ship_track",
        "search_ship_approach",
        "get_port_of_call_by_ship",
        "get_port_of_call_by_ship_port",
        "get_ship_status",
        "get_port_of_call_by_port",
        "plan_route_by_point",
        "plan_route_by_port",
        "get_single_eta_precise",
        "get_weather",
        "get_all_typhoon",
        "get_single_typhoon",
        "get_tides",
        "get_tide_data",
        "get_weather_by_point",
        "get_global_tides",
        "get_global_tide_data",
        "current_weather",
        "future_weather",
        "history_weather",
        "get_nav_warning",
    ]

    for method_name in method_names:
        original = getattr(ShipxyAPI, method_name)

        def wrapped(self, *args, __original=original, __method_name=method_name, **kwargs):
            try:
                return __original(self, *args, **kwargs)
            except Exception as exc:
                return self._exception_result(__method_name, exc)

        wrapped.__name__ = original.__name__
        wrapped.__doc__ = original.__doc__
        setattr(ShipxyAPI, method_name, wrapped)


_wrap_shipxy_api_methods()
