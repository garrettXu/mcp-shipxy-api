import requests
import os

from dotenv import load_dotenv
from typing import Optional, Dict, List, Any, Tuple
import requests
import time
from datetime import datetime
from pydantic import BaseModel



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
    continue_: int = 0  # 'continue'为Python关键字，改为continue_
    ship_list: list[ShipPosition]
    
    class Config:
        fields = {'continue_': 'continue'}

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
    port_country_name: str
    port_country_cnname: str
    port_country_code: str

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
    ship_type: str
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
    code: int
    message: str
    data: list[ShipApproachData]

class PortOfCallData(BaseModel):
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
    sea_area_code: str = ""

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
    waveheight: str
    visibility: float

class GetWeatherResponse(BaseModel):
    status: int
    msg: str
    total: int
    data: list[WeatherData]

class TyphoonListItem(BaseModel):
    typhoon_id: int
    typhoon_code: int
    typhoon_cncode: str
    typhoon_cnname: str
    typhoon_name: str
    current_year: int
    dataMark: str

class GetAllTyphoonResponse(BaseModel):
    status: int
    msg: str
    total: int
    data: list[TyphoonListItem]

class TyphoonDetailItem(BaseModel):
    typhoon_id: int
    typhoon_time: int
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
    radius7_s: float
    radius10_s: float
    radius12_s: float

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
    tidetype: str

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

class ShipxyAPI:
    """船讯网API封装"""
    
    def __init__(self, api_key: str, base_url: str = "http://api.shipxy.com/apicall"):
        """
        初始化船讯网API客户端
        
        Args:
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

    def _get_ship_type_name(self, type_code: int) -> str:
        """获取船舶类型名称
        
        Args:
            type_code: 船舶类型代码
            
        Returns:
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
        Args:
            keywords: 查询关键字（船名、呼号、MMSI、IMO等）
            max_results: 最大返回数量（可选，最大100）
        Returns:
            SearchShipResponse: 查询结果，强类型返回
        Raises:
            Exception: 请求失败或返回错误码
        """
        url = f"{self.base_url}/v3/SearchShip"
        params = {
            "key": self.api_key,
            "keywords": keywords
        }
        if max_results is not None:
            params["max"] = max_results
        
        print(f'url: {url}, params: {params}')
        # 优先GET请求，若参数过长则自动切换POST
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 414:  # URI Too Long
                response = requests.post(url, data=params, timeout=10)
        except Exception as e:
            raise Exception(f"请求船讯网失败: {e}")
        
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        
        # 强类型化返回
        return SearchShipResponse(**resp_json)

    def get_single_ship(self, mmsi: int) -> SingleShipResponse:
        """
        单船位置查询
        Args:
            mmsi: 船舶mmsi编号
        Returns:
            SingleShipResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetSingleShip"
        params = {
            "key": self.api_key,
            "mmsi": mmsi
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return SingleShipResponse(**resp_json)

    def get_many_ship(self, mmsis: list[int]) -> ManyShipResponse:
        """
        多船位置查询
        Args:
            mmsis: 船舶mmsi编号列表（最多100个）
        Returns:
            ManyShipResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetManyShip"
        mmsis_str = ','.join(str(m) for m in mmsis)
        params = {
            "key": self.api_key,
            "mmsis": mmsis_str
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return ManyShipResponse(**resp_json)

    def get_fleet_ship(self, fleet_id: str) -> FleetShipResponse:
        """
        船队船位置查询
        Args:
            fleet_id: 船队编号
        Returns:
            FleetShipResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetFleetShip"
        params = {
            "key": self.api_key,
            "fleet_id": fleet_id
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return FleetShipResponse(**resp_json)

    def get_surrounding_ship(self, mmsi: int) -> SurRoundingShipResponse:
        """
        周边船舶查询
        Args:
            mmsi: 船舶mmsi编号
        Returns:
            SurRoundingShipResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetSurRoundingShip"
        params = {
            "key": self.api_key,
            "mmsi": mmsi
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return SurRoundingShipResponse(**resp_json)

    def get_area_ship(self, region: str, output: int = 1, scode: int = None) -> AreaShipResponse:
        """
        区域船舶查询
        Args:
            region: 区域字符串（lng,lat-lng,lat-...）
            output: 输出格式，1为json，0为base64
            scode: 会话令牌（可选）
        Returns:
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
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return AreaShipResponse(**resp_json)

    def get_ship_registry(self, mmsi: int) -> ShipRegistryResponse:
        """
        船籍信息查询
        Args:
            mmsi: 船舶mmsi编号
        Returns:
            ShipRegistryResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetShipRegistry"
        params = {
            "key": self.api_key,
            "mmsi": mmsi
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return ShipRegistryResponse(**resp_json)

    def search_ship_particular(self, mmsi: int = None, imo: int = None, call_sign: str = None, ship_name: str = None) -> SearchShipParticularResponse:
        """
        船舶档案查询
        Args:
            mmsi: 船舶mmsi编号（可选）
            imo: imo编号（可选）
            call_sign: 呼号（可选）
            ship_name: 船名（可选）
        Returns:
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
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return SearchShipParticularResponse(**resp_json)

    def search_port(self, keywords: str, max_results: int = None) -> SearchPortResponse:
        """
        港口查询
        Args:
            keywords: 港口关键字（中文/英文/五位码）
            max_results: 最大返回数量（可选，最大100）
        Returns:
            SearchPortResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/SearchPort"
        params = {
            "key": self.api_key,
            "keywords": keywords
        }
        if max_results is not None:
            params["max"] = max_results
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return SearchPortResponse(**resp_json)

    def get_berth_ships(self, port_code: str, ship_type: int = None) -> GetBerthShipsResponse:
        """
        港口靠泊船舶查询
        Args:
            port_code: 港口标准五位码
            ship_type: 船舶类型（可选）
        Returns:
            GetBerthShipsResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetBerthShips"
        params = {
            "key": self.api_key,
            "port_code": port_code
        }
        if ship_type is not None:
            params["ship_type"] = ship_type
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return GetBerthShipsResponse(**resp_json)

    def get_anchor_ships(self, port_code: str, ship_type: int = None) -> GetAnchorShipsResponse:
        """
        港口锚地船舶查询
        Args:
            port_code: 港口标准五位码
            ship_type: 船舶类型（可选）
        Returns:
            GetAnchorShipsResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetAnchorShips"
        params = {
            "key": self.api_key,
            "port_code": port_code
        }
        if ship_type is not None:
            params["ship_type"] = ship_type
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        # 兼容返回结构为list或dict
        if isinstance(resp_json.get("data"), dict):
            return GetAnchorShipsResponse(status=resp_json["status"], msg=resp_json["msg"], total=1, data=[AnchorShipData(**resp_json["data"])])
        return GetAnchorShipsResponse(**resp_json)

    def get_eta_ships(self, port_code: str, start_time: int, end_time: int, ship_type: int = None) -> GetETAShipsResponse:
        """
        预抵港船舶查询
        Args:
            port_code: 港口标准五位码
            start_time: 开始时间（UTC时间戳）
            end_time: 结束时间（UTC时间戳）
            ship_type: 船舶类型（可选）
        Returns:
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
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return GetETAShipsResponse(**resp_json)

    def get_ship_track(self, mmsi: int, start_time: int, end_time: int, output: int = 1) -> GetShipTrackResponse:
        """
        船舶轨迹查询
        Args:
            mmsi: 船舶mmsi编号
            start_time: 查询的开始时间，unix时间戳
            end_time: 查询的截止时间，unix时间戳
            output: 输出格式，1为json，0为base64，默认为1
        Returns:
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
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return GetShipTrackResponse(**resp_json)

    def search_ship_approach(self, mmsi: int, start_time: int, end_time: int, approach_zone: int = None) -> SearchShipApproachResponse:
        """
        船舶搭靠事件查询
        Args:
            mmsi: 船舶mmsi编号
            start_time: 开始时间（UTC时间戳）
            end_time: 结束时间（UTC时间戳）
            approach_zone: 搭靠地区（可选）
        Returns:
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
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("code") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('message', '未知错误')}")
        return SearchShipApproachResponse(**resp_json)

    def get_port_of_call_by_ship(self, mmsi: int, start_time: int, end_time: int, imo: int = None, ship_name: str = None, call_sign: str = None, time_zone: int = 2) -> GetPortOfCallByShipResponse:
        """
        船舶靠港记录查询
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
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return GetPortOfCallByShipResponse(**resp_json)

    def get_port_of_call_by_ship_port(self, mmsi: int, port_code: str, start_time: int, end_time: int, imo: int = None, ship_name: str = None, call_sign: str = None, time_zone: int = 2) -> GetPortOfCallByShipPortResponse:
        """
        船舶在指定港口的靠港记录查询
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
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return GetPortOfCallByShipPortResponse(**resp_json)

    def get_ship_status(self, mmsi: int, imo: int = None, ship_name: str = None, call_sign: str = None, time_zone: int = 2) -> GetShipStatusResponse:
        """
        船舶状态查询
        Args:
            mmsi: 船舶mmsi编号
            imo: IMO编号（可选）
            ship_name: 船舶英文名称（可选）
            call_sign: 船舶呼号（可选）
            time_zone: 时区（默认2，北京时区）
        Returns:
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
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return GetShipStatusResponse(**resp_json)

    def get_port_of_call_by_port(self, port_code: str, start_time: int, end_time: int, type_: int = 1, time_zone: int = 2) -> GetPortOfCallByPortResponse:
        """
        港口靠港记录查询
        Args:
            port_code: 港口五位码
            start_time: 开始时间（UTC时间戳）
            end_time: 结束时间（UTC时间戳）
            type_: 查询类型（1:ATA，2:ATD，默认1）
            time_zone: 时区（默认2，北京时区）
        Returns:
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
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return GetPortOfCallByPortResponse(**resp_json)

    def plan_route_by_point(self, start_point: str, end_point: str, avoid: str = None, through: str = None) -> PlanRouteByPointResponse:
        """
        航线规划（经纬度点）
        Args:
            start_point: 起始点（lng,lat）
            end_point: 结束点（lng,lat）
            avoid: 绕航节点（可选）
            through: 途经点（可选）
        Returns:
            PlanRouteByPointResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/PlanRouteByPoint"
        params = {
            "key": self.api_key,
            "start_point": start_point,
            "end_point": end_point
        }
        if avoid is not None:
            params["avoid"] = avoid
        if through is not None:
            params["through"] = through
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return PlanRouteByPointResponse(**resp_json)

    def plan_route_by_port(self, start_port_code: str, end_port_code: str, avoid: str = None, through: str = None) -> PlanRouteByPortResponse:
        """
        航线规划（港口）
        Args:
            start_port_code: 出发港PortCode港口标准五位码
            end_port_code: 到达港PortCode港口标准五位码
            avoid: 绕航节点（可选）
            through: 途经点（可选）
        Returns:
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
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return PlanRouteByPortResponse(**resp_json)

    def get_single_eta_precise(self, mmsi: int, port_code: str = None, speed: float = None) -> GetSingleETAPreciseResponse:
        """
        单船精确ETA查询
        Args:
            mmsi: 船舶mmsi编号
            port_code: 港口五位码（可选）
            speed: 设定船速（可选）
        Returns:
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
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return GetSingleETAPreciseResponse(**resp_json)

    def get_weather(self, weather_type: int) -> GetWeatherResponse:
        """
        区域气象查询
        Args:
            weather_type: 区域类型（0：全部；1：沿岸；2：近海；3：远海）
        Returns:
            GetWeatherResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetWeather"
        params = {
            "key": self.api_key,
            "weather_type": weather_type
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return GetWeatherResponse(**resp_json)

    def get_all_typhoon(self) -> GetAllTyphoonResponse:
        """
        获取全球台风列表
        Returns:
            GetAllTyphoonResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetAllTyphoon"
        params = {"key": self.api_key}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return GetAllTyphoonResponse(**resp_json)

    def get_single_typhoon(self, typhoon_id: int) -> GetSingleTyphoonResponse:
        """
        获取单个台风信息
        Args:
            typhoon_id: 台风序号
        Returns:
            GetSingleTyphoonResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetSingleTyphoon"
        params = {"key": self.api_key, "typhoon_id": typhoon_id}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return GetSingleTyphoonResponse(**resp_json)

    def get_tides(self) -> GetTidesResponse:
        """
        查询国内潮汐观测站列表
        Returns:
            GetTidesResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetTides"
        params = {"key": self.api_key}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return GetTidesResponse(**resp_json)

    def get_tide_data(self, port_code: int, start_date: str, end_date: str) -> GetTideDataResponse:
        """
        查询单个港口潮汐观测站详情
        Args:
            port_code: 潮汐观测站id
            start_date: 起始日期（yyyy-MM-dd）
            end_date: 结束日期（yyyy-MM-dd）
        Returns:
            GetTideDataResponse: 查询结果，强类型返回
        """
        url = f"{self.base_url}/v3/GetTideData"
        params = {
            "key": self.api_key,
            "port_code": port_code,
            "start_date": start_date,
            "end_date": end_date
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return GetTideDataResponse(**resp_json)

    def get_weather_by_point(self, lng: float, lat: float, weather_time: int = None) -> GetWeatherByPointResponse:
        """
        单点海洋气象查询
        请求地址: https://api.shipxy.com/apicall/v3/GetWeatherByPoint
        请求方式: GET
        请求调用示例:
            https://api.shipxy.com/apicall/v3/GetWeatherByPoint?key=你的key&lng=123.58414&lat=27.37979
        Args:
            lng: 经度，WGS84坐标系，格式为lng=155.2134
            lat: 纬度，WGS84坐标系，格式为lat=20.2134
            weather_time: 查询时间（可选，UTC时间戳），不填写则查询最近时间的气象数据
        Returns:
            GetWeatherByPointResponse: 查询结果，强类型返回
        Raises:
            Exception: 请求失败或返回错误码
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
            response = requests.get(url, params=params, timeout=10)
        except Exception as e:
            raise Exception(f"请求船讯网失败: {e}")
        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")
        resp_json = response.json()
        if resp_json.get("status") != 0:
            raise Exception(f"船讯网返回错误: {resp_json.get('msg', '未知错误')}")
        return GetWeatherByPointResponse(**resp_json)

    