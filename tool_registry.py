from dataclasses import dataclass, field
from typing import Any, Callable

from domain_catalog import error_fix, tool_response_metadata
from ship_service import ShipxyAPI


@dataclass(frozen=True)
class ParamSpec:
    name: str
    type: str
    help: str
    required: bool = False
    positional: bool = False
    default: Any = None
    cli_name: str | None = None
    aliases: tuple[str, ...] = ()

    @property
    def option_name(self) -> str:
        return self.cli_name or self.name.replace("_", "-")


@dataclass(frozen=True)
class ToolSpec:
    name: str
    method: str
    summary: str
    params: tuple[ParamSpec, ...] = field(default_factory=tuple)

    @property
    def cli_name(self) -> str:
        return self.name.replace("_", "-")

    def schema(self) -> dict[str, Any]:
        response_metadata = tool_response_metadata(self.name)
        return {
            "name": self.name,
            "cli_name": self.cli_name,
            "method": self.method,
            "summary": self.summary,
            "returns": response_metadata["returns"],
            "capability_ref": response_metadata["capability_ref"],
            "object_refs": response_metadata["object_refs"],
            "parameters": [
                {
                    "name": param.name,
                    "cli_name": param.option_name,
                    "type": param.type,
                    "required": param.required,
                    "positional": param.positional,
                    "default": param.default,
                    "help": param.help,
                }
                for param in self.params
            ],
        }


def p(
    name: str,
    type_: str,
    help_text: str,
    *,
    required: bool = False,
    positional: bool = False,
    default: Any = None,
    cli_name: str | None = None,
    aliases: tuple[str, ...] = (),
) -> ParamSpec:
    return ParamSpec(
        name=name,
        type=type_,
        help=help_text,
        required=required,
        positional=positional,
        default=default,
        cli_name=cli_name,
        aliases=aliases,
    )


TOOLS: tuple[ToolSpec, ...] = (
    ToolSpec(
        "search_ship",
        "search_ship",
        "按 MMSI、IMO、船名或呼号模糊查询船舶。",
        (
            p("keywords", "str", "船舶查询关键字。", required=True, positional=True),
            p("max_results", "int", "最大返回数量。", default=None, cli_name="max", aliases=("--max-results",)),
        ),
    ),
    ToolSpec("get_single_ship", "get_single_ship", "查询单船实时位置和基础信息。", (p("mmsi", "int", "船舶 MMSI。", required=True, positional=True),)),
    ToolSpec("get_many_ship", "get_many_ship", "查询多艘船舶的实时位置和基础信息。", (p("mmsis", "list[int]", "逗号分隔的 MMSI 列表。", required=True, positional=True),)),
    ToolSpec("get_fleet_ship", "get_fleet_ship", "查询一个船队下的全部船舶。", (p("fleet_id", "str", "船队 ID。", required=True, positional=True),)),
    ToolSpec("get_surrounding_ship", "get_surrounding_ship", "查询指定船舶 10 海里范围内的周边船舶。", (p("mmsi", "int", "船舶 MMSI。", required=True, positional=True),)),
    ToolSpec(
        "get_area_ship",
        "get_area_ship",
        "查询多边形区域内的船舶。",
        (
            p("region", "str", "区域字符串，格式如 lng,lat-lng,lat。", required=True, positional=True),
            p("output", "int", "输出格式：1 表示 JSON，0 表示 base64。", default=1),
            p("scode", "int", "分页或会话令牌。", default=None),
        ),
    ),
    ToolSpec("get_ship_registry", "get_ship_registry", "查询船舶船籍或国家地区信息。", (p("mmsi", "int", "船舶 MMSI。", required=True, positional=True),)),
    ToolSpec(
        "search_ship_particular",
        "search_ship_particular",
        "按 MMSI、IMO、呼号或船名查询船舶档案。",
        (
            p("mmsi", "int", "船舶 MMSI。", default=None),
            p("imo", "int", "船舶 IMO。", default=None),
            p("call_sign", "str", "船舶呼号。", default=None),
            p("ship_name", "str", "船舶英文名。", default=None),
        ),
    ),
    ToolSpec(
        "search_port",
        "search_port",
        "按港口名称或港口代码模糊查询港口。",
        (
            p("keywords", "str", "港口查询关键字。", required=True, positional=True),
            p("max_results", "int", "最大返回数量。", default=None, cli_name="max", aliases=("--max-results",)),
        ),
    ),
    ToolSpec(
        "get_berth_ships",
        "get_berth_ships",
        "查询港口当前靠泊船舶。",
        (
            p("port_code", "str", "港口五位码。", required=True, positional=True),
            p("ship_type", "int", "船舶类型。", default=None),
        ),
    ),
    ToolSpec(
        "get_anchor_ships",
        "get_anchor_ships",
        "查询港口当前锚地船舶。",
        (
            p("port_code", "str", "港口五位码。", required=True, positional=True),
            p("ship_type", "int", "船舶类型。", default=None),
        ),
    ),
    ToolSpec(
        "get_eta_ships",
        "get_eta_ships",
        "查询预计到达港口的船舶。",
        (
            p("port_code", "str", "港口五位码。", required=True, positional=True),
            p("start_time", "int", "开始 UTC 时间戳。", required=True, positional=True),
            p("end_time", "int", "结束 UTC 时间戳。", required=True, positional=True),
            p("ship_type", "int", "船舶类型。", default=None),
        ),
    ),
    ToolSpec(
        "get_ship_track",
        "get_ship_track",
        "查询船舶历史轨迹点。",
        (
            p("mmsi", "int", "船舶 MMSI。", required=True, positional=True),
            p("start_time", "int", "开始 UTC 时间戳。", required=True, positional=True),
            p("end_time", "int", "结束 UTC 时间戳。", required=True, positional=True),
            p("output", "int", "输出格式：1 表示 JSON，0 表示 base64。", default=1),
        ),
    ),
    ToolSpec(
        "search_ship_approach",
        "search_ship_approach",
        "查询船舶搭靠或接近事件。",
        (
            p("mmsi", "int", "船舶 MMSI。", required=True, positional=True),
            p("start_time", "int", "开始 UTC 时间戳。", required=True, positional=True),
            p("end_time", "int", "结束 UTC 时间戳。", required=True, positional=True),
            p("approach_zone", "int", "搭靠区域代码。", default=None),
        ),
    ),
    ToolSpec(
        "get_port_of_call_by_ship",
        "get_port_of_call_by_ship",
        "查询一艘船的历史靠港记录。",
        (
            p("mmsi", "int", "船舶 MMSI。", required=True, positional=True),
            p("start_time", "int", "开始 UTC 时间戳。", required=True, positional=True),
            p("end_time", "int", "结束 UTC 时间戳。", required=True, positional=True),
            p("imo", "int", "船舶 IMO。", default=None),
            p("ship_name", "str", "船舶英文名。", default=None),
            p("call_sign", "str", "船舶呼号。", default=None),
            p("time_zone", "int", "时区模式。", default=2),
        ),
    ),
    ToolSpec(
        "get_port_of_call_by_ship_port",
        "get_port_of_call_by_ship_port",
        "查询一艘船在指定港口的靠港记录。",
        (
            p("mmsi", "int", "船舶 MMSI。", required=True, positional=True),
            p("port_code", "str", "港口五位码。", required=True, positional=True),
            p("start_time", "int", "开始 UTC 时间戳。", required=True, positional=True),
            p("end_time", "int", "结束 UTC 时间戳。", required=True, positional=True),
            p("imo", "int", "船舶 IMO。", default=None),
            p("ship_name", "str", "船舶英文名。", default=None),
            p("call_sign", "str", "船舶呼号。", default=None),
            p("time_zone", "int", "时区模式。", default=2),
        ),
    ),
    ToolSpec(
        "get_ship_status",
        "get_ship_status",
        "查询船舶当前挂靠状态。",
        (
            p("mmsi", "int", "船舶 MMSI。", required=True, positional=True),
            p("imo", "int", "船舶 IMO。", default=None),
            p("ship_name", "str", "船舶英文名。", default=None),
            p("call_sign", "str", "船舶呼号。", default=None),
            p("time_zone", "int", "时区模式。", default=2),
        ),
    ),
    ToolSpec(
        "get_port_of_call_by_port",
        "get_port_of_call_by_port",
        "查询指定港口的历史靠港船舶记录。",
        (
            p("port_code", "str", "港口五位码。", required=True, positional=True),
            p("start_time", "int", "开始 UTC 时间戳。", required=True, positional=True),
            p("end_time", "int", "结束 UTC 时间戳。", required=True, positional=True),
            p("type_", "int", "查询类型：1 表示 ATA，2 表示 ATD。", default=1, cli_name="type"),
            p("time_zone", "int", "时区模式。", default=2),
        ),
    ),
    ToolSpec(
        "plan_route_by_point",
        "plan_route_by_point",
        "规划从一个坐标到另一个坐标或目的港的航线。",
        (
            p("start_point", "str", "起点坐标，格式 lng,lat。", required=True, positional=True),
            p("end_point", "str", "终点坐标，格式 lng,lat；未提供 end_port_code 时必填。", default=None),
            p("end_port_code", "str", "目的港五位码；未提供 end_point 时必填。", default=None),
            p("avoid", "str", "避让节点。", default=None),
            p("through", "str", "途经节点。", default=None),
        ),
    ),
    ToolSpec(
        "plan_route_by_port",
        "plan_route_by_port",
        "规划两个港口之间的航线。",
        (
            p("start_port_code", "str", "起始港五位码。", required=True, positional=True),
            p("end_port_code", "str", "目的港五位码。", required=True, positional=True),
            p("avoid", "str", "避让节点。", default=None),
            p("through", "str", "途经节点。", default=None),
        ),
    ),
    ToolSpec(
        "get_single_eta_precise",
        "get_single_eta_precise",
        "查询单船精准 ETA 和航程信息。",
        (
            p("mmsi", "int", "船舶 MMSI。", required=True, positional=True),
            p("port_code", "str", "目的港五位码。", default=None),
            p("speed", "float", "指定航速。", default=None),
        ),
    ),
    ToolSpec("get_weather", "get_weather", "按海区类型查询海洋气象。", (p("weather_type", "int", "海区类型：0 全部，1 沿岸，2 近海，3 远海。", required=True, positional=True),)),
    ToolSpec(
        "get_weather_by_point",
        "get_weather_by_point",
        "按坐标查询海洋气象。",
        (
            p("lng", "float", "经度。", required=True),
            p("lat", "float", "纬度。", required=True),
            p("weather_time", "int", "气象 UTC 时间戳。", default=None),
        ),
    ),
    ToolSpec("get_all_typhoon", "get_all_typhoon", "查询近年全球台风列表。"),
    ToolSpec("get_single_typhoon", "get_single_typhoon", "按台风 ID 查询单个台风详情。", (p("typhoon_id", "int", "台风 ID。", required=True, positional=True),)),
    ToolSpec("get_tides", "get_tides", "查询国内潮汐观测站列表。"),
    ToolSpec(
        "get_tide_data",
        "get_tide_data",
        "查询一个国内潮汐观测站的潮汐数据。",
        (
            p("port_code", "int", "潮汐观测站 ID。", required=True, positional=True),
            p("start_date", "str", "开始日期 yyyy-MM-dd。", required=True, positional=True),
            p("end_date", "str", "结束日期 yyyy-MM-dd。", required=True, positional=True),
        ),
    ),
    ToolSpec("get_global_tides", "get_global_tides", "查询全球潮汐观测站列表。"),
    ToolSpec(
        "get_global_tide_data",
        "get_global_tide_data",
        "查询一个全球潮汐观测站的潮汐数据。",
        (
            p("port_code", "int", "get_global_tides 返回的全球潮汐观测站 ID，不是港口五位码。", required=True, positional=True),
            p("start_date", "str", "开始日期 yyyy-MM-dd。", required=True, positional=True),
            p("end_date", "str", "结束日期 yyyy-MM-dd。", required=True, positional=True),
        ),
    ),
    ToolSpec(
        "current_weather",
        "current_weather",
        "按坐标查询全球实时大气和海洋气象。",
        (
            p("lng", "float", "WGS84 十进制度经度。", required=True),
            p("lat", "float", "WGS84 十进制度纬度。", required=True),
        ),
    ),
    ToolSpec(
        "future_weather",
        "future_weather",
        "按坐标查询全球未来大气和海洋气象预报。",
        (
            p("lng", "float", "WGS84 十进制度经度。", required=True),
            p("lat", "float", "WGS84 十进制度纬度。", required=True),
        ),
    ),
    ToolSpec(
        "history_weather",
        "history_weather",
        "按坐标和日期查询全球历史气象。",
        (
            p("lng", "float", "WGS84 十进制度经度。", required=True),
            p("lat", "float", "WGS84 十进制度纬度。", required=True),
            p("start_time", "str", "历史气象开始时间 yyyy-MM-dd HH:mm:ss。", required=True),
            p("end_time", "str", "历史气象结束时间 yyyy-MM-dd HH:mm:ss。", required=True),
        ),
    ),
    ToolSpec(
        "get_nav_warning",
        "get_nav_warning",
        "按时间范围查询中国海事局航行警告。",
        (
            p("start_time", "str", "开始时间 yyyy-MM-dd HH:mm。", required=True),
            p("end_time", "str", "结束时间 yyyy-MM-dd HH:mm。", required=True),
        ),
    ),
)

TOOLS_BY_NAME = {tool.name: tool for tool in TOOLS}
TOOLS_BY_CLI_NAME = {tool.cli_name: tool for tool in TOOLS}


def normalize_tool_name(name: str) -> str:
    return name.replace("-", "_")


def get_tool(name: str) -> ToolSpec:
    normalized = normalize_tool_name(name)
    if normalized in TOOLS_BY_NAME:
        return TOOLS_BY_NAME[normalized]
    raise KeyError(f"未知工具：{name}")


def parse_value(value: Any, type_name: str) -> Any:
    if value is None:
        return None
    if type_name == "int":
        return int(value)
    if type_name == "float":
        return float(value)
    if type_name == "list[int]":
        if isinstance(value, list):
            return [int(item) for item in value]
        return [int(item.strip()) for item in str(value).split(",") if item.strip()]
    return value


def _invalid_request_result(tool_name: str, errors: list[dict[str, Any]]) -> dict[str, Any]:
    metadata = tool_response_metadata(tool_name)
    return {
        "ok": False,
        "tool": tool_name,
        "capability_ref": metadata["capability_ref"],
        "returns": metadata["returns"],
        "object_refs": metadata["object_refs"],
        "error": {
            "type": "invalid_request",
            "message": "Shipxy 工具入参不合法。",
            "details": errors,
            "fix": error_fix("invalid_request"),
        },
    }


def _with_response_metadata(tool_name: str, result: Any) -> Any:
    data = model_to_data(result)
    if not isinstance(data, dict):
        return data

    metadata = tool_response_metadata(tool_name)
    data.setdefault("tool", tool_name)
    data.setdefault("capability_ref", metadata["capability_ref"])
    data.setdefault("returns", metadata["returns"])
    data.setdefault("object_refs", metadata["object_refs"])

    if data.get("ok") is False and isinstance(data.get("error"), dict):
        error = data["error"]
        error.setdefault("fix", error_fix(error.get("type")))
    return data


def invoke_tool(api: ShipxyAPI, tool_name: str, values: dict[str, Any]) -> Any:
    tool = get_tool(tool_name)
    from validation import validate_tool_input

    validation = validate_tool_input(tool.name, values)
    if not validation["ok"]:
        return _invalid_request_result(tool.name, validation["errors"])

    kwargs: dict[str, Any] = {}
    for param in tool.params:
        value = values.get(param.name, param.default)
        if value is not None:
            try:
                kwargs[param.name] = parse_value(value, param.type)
            except (TypeError, ValueError) as exc:
                return _invalid_request_result(
                    tool.name,
                    [
                        {
                            "type": "invalid_request",
                            "field": param.name,
                            "message": f"无法将参数解析为 {param.type}: {exc}",
                            "received": value,
                            "expected": param.type,
                            "fix": {"strategy": "请按工具文档要求的参数类型传值。"},
                        }
                    ],
                )
    method: Callable[..., Any] = getattr(api, tool.method)
    return _with_response_metadata(tool.name, method(**kwargs))


def model_to_data(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", by_alias=True)
    if hasattr(value, "dict"):
        return value.dict(by_alias=True)
    return value


def all_schemas() -> list[dict[str, Any]]:
    return [tool.schema() for tool in TOOLS]
