from dataclasses import dataclass, field
from typing import Any, Callable

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
        return {
            "name": self.name,
            "cli_name": self.cli_name,
            "method": self.method,
            "summary": self.summary,
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
        "Fuzzy search ships by MMSI, IMO, name, or call sign.",
        (
            p("keywords", "str", "Ship keyword.", required=True, positional=True),
            p("max_results", "int", "Maximum result count.", default=None, cli_name="max", aliases=("--max-results",)),
        ),
    ),
    ToolSpec("get_single_ship", "get_single_ship", "Get realtime information for one ship.", (p("mmsi", "int", "Ship MMSI.", required=True, positional=True),)),
    ToolSpec("get_many_ship", "get_many_ship", "Get realtime information for multiple ships.", (p("mmsis", "list[int]", "Comma-separated MMSI list.", required=True, positional=True),)),
    ToolSpec("get_fleet_ship", "get_fleet_ship", "Get all ships in a fleet.", (p("fleet_id", "str", "Fleet ID.", required=True, positional=True),)),
    ToolSpec("get_surrounding_ship", "get_surrounding_ship", "Get ships within 10 nautical miles of a ship.", (p("mmsi", "int", "Ship MMSI.", required=True, positional=True),)),
    ToolSpec(
        "get_area_ship",
        "get_area_ship",
        "Get ships in a polygon area.",
        (
            p("region", "str", "Region string, such as lng,lat-lng,lat.", required=True, positional=True),
            p("output", "int", "Output format: 1 JSON, 0 base64.", default=1),
            p("scode", "int", "Session token.", default=None),
        ),
    ),
    ToolSpec("get_ship_registry", "get_ship_registry", "Get ship registry/country information.", (p("mmsi", "int", "Ship MMSI.", required=True, positional=True),)),
    ToolSpec(
        "search_ship_particular",
        "search_ship_particular",
        "Search ship particulars by MMSI, IMO, call sign, or ship name.",
        (
            p("mmsi", "int", "Ship MMSI.", default=None),
            p("imo", "int", "Ship IMO.", default=None),
            p("call_sign", "str", "Ship call sign.", default=None),
            p("ship_name", "str", "Ship English name.", default=None),
        ),
    ),
    ToolSpec(
        "search_port",
        "search_port",
        "Fuzzy search ports by name or port code.",
        (
            p("keywords", "str", "Port keyword.", required=True, positional=True),
            p("max_results", "int", "Maximum result count.", default=None, cli_name="max", aliases=("--max-results",)),
        ),
    ),
    ToolSpec(
        "get_berth_ships",
        "get_berth_ships",
        "Get ships currently berthed at a port.",
        (
            p("port_code", "str", "Port code.", required=True, positional=True),
            p("ship_type", "int", "Ship type.", default=None),
        ),
    ),
    ToolSpec(
        "get_anchor_ships",
        "get_anchor_ships",
        "Get ships currently anchored at a port.",
        (
            p("port_code", "str", "Port code.", required=True, positional=True),
            p("ship_type", "int", "Ship type.", default=None),
        ),
    ),
    ToolSpec(
        "get_eta_ships",
        "get_eta_ships",
        "Get ships expected to arrive at a port.",
        (
            p("port_code", "str", "Port code.", required=True, positional=True),
            p("start_time", "int", "Start UTC timestamp.", required=True, positional=True),
            p("end_time", "int", "End UTC timestamp.", required=True, positional=True),
            p("ship_type", "int", "Ship type.", default=None),
        ),
    ),
    ToolSpec(
        "get_ship_track",
        "get_ship_track",
        "Get historical track points for a ship.",
        (
            p("mmsi", "int", "Ship MMSI.", required=True, positional=True),
            p("start_time", "int", "Start UTC timestamp.", required=True, positional=True),
            p("end_time", "int", "End UTC timestamp.", required=True, positional=True),
            p("output", "int", "Output format: 1 JSON, 0 base64.", default=1),
        ),
    ),
    ToolSpec(
        "search_ship_approach",
        "search_ship_approach",
        "Search ship-to-ship approach events.",
        (
            p("mmsi", "int", "Ship MMSI.", required=True, positional=True),
            p("start_time", "int", "Start UTC timestamp.", required=True, positional=True),
            p("end_time", "int", "End UTC timestamp.", required=True, positional=True),
            p("approach_zone", "int", "Approach zone.", default=None),
        ),
    ),
    ToolSpec(
        "get_port_of_call_by_ship",
        "get_port_of_call_by_ship",
        "Get port call records for a ship.",
        (
            p("mmsi", "int", "Ship MMSI.", required=True, positional=True),
            p("start_time", "int", "Start UTC timestamp.", required=True, positional=True),
            p("end_time", "int", "End UTC timestamp.", required=True, positional=True),
            p("imo", "int", "Ship IMO.", default=None),
            p("ship_name", "str", "Ship English name.", default=None),
            p("call_sign", "str", "Ship call sign.", default=None),
            p("time_zone", "int", "Timezone mode.", default=2),
        ),
    ),
    ToolSpec(
        "get_port_of_call_by_ship_port",
        "get_port_of_call_by_ship_port",
        "Get port call records for a ship at one port.",
        (
            p("mmsi", "int", "Ship MMSI.", required=True, positional=True),
            p("port_code", "str", "Port code.", required=True, positional=True),
            p("start_time", "int", "Start UTC timestamp.", required=True, positional=True),
            p("end_time", "int", "End UTC timestamp.", required=True, positional=True),
            p("imo", "int", "Ship IMO.", default=None),
            p("ship_name", "str", "Ship English name.", default=None),
            p("call_sign", "str", "Ship call sign.", default=None),
            p("time_zone", "int", "Timezone mode.", default=2),
        ),
    ),
    ToolSpec(
        "get_ship_status",
        "get_ship_status",
        "Get current ship port-call status.",
        (
            p("mmsi", "int", "Ship MMSI.", required=True, positional=True),
            p("imo", "int", "Ship IMO.", default=None),
            p("ship_name", "str", "Ship English name.", default=None),
            p("call_sign", "str", "Ship call sign.", default=None),
            p("time_zone", "int", "Timezone mode.", default=2),
        ),
    ),
    ToolSpec(
        "get_port_of_call_by_port",
        "get_port_of_call_by_port",
        "Get port call records for a port.",
        (
            p("port_code", "str", "Port code.", required=True, positional=True),
            p("start_time", "int", "Start UTC timestamp.", required=True, positional=True),
            p("end_time", "int", "End UTC timestamp.", required=True, positional=True),
            p("type_", "int", "Query type: 1 ATA, 2 ATD.", default=1, cli_name="type"),
            p("time_zone", "int", "Timezone mode.", default=2),
        ),
    ),
    ToolSpec(
        "plan_route_by_point",
        "plan_route_by_point",
        "Plan a route between two coordinates.",
        (
            p("start_point", "str", "Start point lng,lat.", required=True, positional=True),
            p("end_point", "str", "End point lng,lat.", required=True, positional=True),
            p("avoid", "str", "Avoid nodes.", default=None),
            p("through", "str", "Through nodes.", default=None),
        ),
    ),
    ToolSpec(
        "plan_route_by_port",
        "plan_route_by_port",
        "Plan a route between two ports.",
        (
            p("start_port_code", "str", "Start port code.", required=True, positional=True),
            p("end_port_code", "str", "End port code.", required=True, positional=True),
            p("avoid", "str", "Avoid nodes.", default=None),
            p("through", "str", "Through nodes.", default=None),
        ),
    ),
    ToolSpec(
        "get_single_eta_precise",
        "get_single_eta_precise",
        "Get precise ETA and voyage information for one ship.",
        (
            p("mmsi", "int", "Ship MMSI.", required=True, positional=True),
            p("port_code", "str", "Port code.", default=None),
            p("speed", "float", "Specified speed.", default=None),
        ),
    ),
    ToolSpec("get_weather", "get_weather", "Get marine weather by area type.", (p("weather_type", "int", "Area type: 0 all, 1 coast, 2 offshore, 3 ocean.", required=True, positional=True),)),
    ToolSpec(
        "get_weather_by_point",
        "get_weather_by_point",
        "Get marine weather by coordinate.",
        (
            p("lng", "float", "Longitude.", required=True),
            p("lat", "float", "Latitude.", required=True),
            p("weather_time", "int", "Weather UTC timestamp.", default=None),
        ),
    ),
    ToolSpec("get_all_typhoon", "get_all_typhoon", "List recent typhoons."),
    ToolSpec("get_single_typhoon", "get_single_typhoon", "Get one typhoon by ID.", (p("typhoon_id", "int", "Typhoon ID.", required=True, positional=True),)),
    ToolSpec("get_tides", "get_tides", "List tide stations."),
    ToolSpec(
        "get_tide_data",
        "get_tide_data",
        "Get tide data for one tide station.",
        (
            p("port_code", "int", "Tide station ID.", required=True, positional=True),
            p("start_date", "str", "Start date yyyy-MM-dd.", required=True, positional=True),
            p("end_date", "str", "End date yyyy-MM-dd.", required=True, positional=True),
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
    raise KeyError(f"Unknown tool: {name}")


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


def invoke_tool(api: ShipxyAPI, tool_name: str, values: dict[str, Any]) -> Any:
    tool = get_tool(tool_name)
    kwargs: dict[str, Any] = {}
    for param in tool.params:
        value = values.get(param.name, param.default)
        if value is not None:
            kwargs[param.name] = parse_value(value, param.type)
    method: Callable[..., Any] = getattr(api, tool.method)
    return method(**kwargs)


def model_to_data(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", by_alias=True)
    if hasattr(value, "dict"):
        return value.dict(by_alias=True)
    return value


def all_schemas() -> list[dict[str, Any]]:
    return [tool.schema() for tool in TOOLS]
