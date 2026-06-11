from __future__ import annotations

from datetime import datetime
from typing import Any


def _is_missing(value: Any) -> bool:
    return value is None or value == ""


def _display(value: Any) -> Any:
    if isinstance(value, str) and len(value) > 120:
        return value[:117] + "..."
    return value


def _error(
    field: str,
    message: str,
    *,
    received: Any = None,
    expected: str = "",
    strategy: str = "",
    recommended_tool: str | None = None,
    example: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fix: dict[str, Any] = {"strategy": strategy or message}
    if recommended_tool:
        fix["recommended_tool"] = recommended_tool
    if example:
        fix["example"] = example
    return {
        "type": "invalid_request",
        "field": field,
        "message": message,
        "received": _display(received),
        "expected": expected,
        "fix": fix,
    }


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _digits(value: Any) -> str:
    return str(value).strip()


def _validate_mmsi(field: str, value: Any) -> list[dict[str, Any]]:
    text = _digits(value)
    if not text.isdigit() or len(text) != 9:
        return [
            _error(
                field,
                "MMSI 必须是 9 位数字。",
                received=value,
                expected="9 位数字，例如 413543265",
                strategy="如果只知道船名、IMO 或呼号，请先搜索船舶。",
                recommended_tool="search_ship",
                example={"keywords": "COSCO", "max_results": 5},
            )
        ]
    return []


def _validate_imo(field: str, value: Any) -> list[dict[str, Any]]:
    if _is_missing(value):
        return []
    text = _digits(value)
    if not text.isdigit() or len(text) != 7:
        return [
            _error(
                field,
                "IMO 应为 7 位数字。",
                received=value,
                expected="7 位数字",
                strategy="如果不确定，请先搜索船舶并使用返回的 IMO 或 MMSI。",
                recommended_tool="search_ship",
            )
        ]
    return []


def _validate_port_code(field: str, value: Any, *, tide_station: bool = False, station_tool: str = "get_tides") -> list[dict[str, Any]]:
    if tide_station:
        station_id = _as_int(value)
        if station_id is None or station_id <= 0:
            return [
                _error(
                    field,
                    "潮汐观测站 ID 必须是正整数。",
                    received=value,
                    expected=f"{station_tool} 返回的正整数。",
                    strategy=f"请先调用 {station_tool}，并使用返回的 port_code 观测站 ID。",
                    recommended_tool=station_tool,
                )
            ]
        return []

    text = str(value).strip()
    if len(text) != 5:
        return [
            _error(
                field,
                "港口类接口需要 Shipxy 标准 5 字符 port_code。",
                received=value,
                expected="5 字符 port_code，例如 CNSHG。",
                strategy="请先搜索港口，并使用返回的 port_code。",
                recommended_tool="search_port",
                example={"keywords": "Shanghai", "max_results": 5},
            )
        ]
    return []


def _validate_point(field: str, value: Any) -> list[dict[str, Any]]:
    parts = str(value).split(",")
    if len(parts) != 2:
        return [
            _error(
                field,
                "坐标点必须使用 lng,lat 格式。",
                received=value,
                expected="lng,lat，例如 121.5,31.2",
                strategy="请先填写经度，再填写纬度。",
            )
        ]
    lng = _as_float(parts[0].strip())
    lat = _as_float(parts[1].strip())
    return _validate_lng_lat(f"{field}.lng", lng, parts[0].strip()) + _validate_lng_lat(f"{field}.lat", lat, parts[1].strip())


def _validate_port_or_point_destination(args: dict[str, Any]) -> list[dict[str, Any]]:
    has_end_point = not _is_missing(args.get("end_point"))
    has_end_port = not _is_missing(args.get("end_port_code"))
    if has_end_point == has_end_port:
        return [
            _error(
                "end_point|end_port_code",
                "必须且只能提供一个目的地：end_point 或 end_port_code。",
                received={"end_point": args.get("end_point"), "end_port_code": args.get("end_port_code")},
                expected="end_point=lng,lat 或 end_port_code=5 字符港口代码二选一。",
                strategy="点到点航线使用 end_point，点到港航线使用 end_port_code。",
            )
        ]
    return []


def _validate_lng_lat(field: str, numeric: float | None, received: Any) -> list[dict[str, Any]]:
    if field.endswith(".lng") or field == "lng":
        if numeric is None or numeric < -180 or numeric > 180:
            return [_error(field, "经度必须在 -180 到 180 之间。", received=received, expected="-180 <= lng <= 180")]
    if field.endswith(".lat") or field == "lat":
        if numeric is None or numeric < -90 or numeric > 90:
            return [_error(field, "纬度必须在 -90 到 90 之间。", received=received, expected="-90 <= lat <= 90")]
    return []


def _validate_date(field: str, value: Any) -> list[dict[str, Any]]:
    try:
        datetime.strptime(str(value), "%Y-%m-%d")
    except ValueError:
        return [
            _error(
                field,
                "日期必须使用 yyyy-MM-dd 格式。",
                received=value,
                expected="yyyy-MM-dd，例如 2026-06-11",
                strategy="请使用日历日期，不要使用 Unix 时间戳。",
            )
        ]
    return []


def _validate_datetime(field: str, value: Any) -> list[dict[str, Any]]:
    try:
        datetime.strptime(str(value), "%Y-%m-%d %H:%M")
    except ValueError:
        return [
            _error(
                field,
                "日期时间必须使用 yyyy-MM-dd HH:mm 格式。",
                received=value,
                expected="yyyy-MM-dd HH:mm，例如 2026-06-11 09:30",
                strategy="请使用分钟级本地日期时间字符串，不要使用 Unix 时间戳。",
            )
        ]
    return []


def _validate_datetime_seconds(field: str, value: Any) -> list[dict[str, Any]]:
    try:
        datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return [
            _error(
                field,
                "日期时间必须使用 yyyy-MM-dd HH:mm:ss 格式。",
                received=value,
                expected="yyyy-MM-dd HH:mm:ss，例如 2026-06-10 00:00:00",
                strategy="请使用秒级本地日期时间字符串，不要只传日期或 Unix 时间戳。",
            )
        ]
    return []


def _normalize_mmsis(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [value]


def validate_tool_input(tool_name: str, arguments: dict[str, Any] | None) -> dict[str, Any]:
    from tool_registry import get_tool
    from domain_catalog import tool_response_metadata

    args = arguments or {}
    try:
        tool = get_tool(tool_name)
    except KeyError as exc:
        return {
            "ok": False,
            "tool": tool_name,
            "errors": [
                _error(
                    "tool_name",
                    f"未知工具：{tool_name}",
                    received=tool_name,
                    expected="已注册的 Shipxy 工具名。",
                    strategy="调用 describe_capabilities 查看可用工具列表。",
                    recommended_tool="describe_capabilities",
                )
            ],
        }

    errors: list[dict[str, Any]] = []
    expected_fields = {param.name for param in tool.params}
    param_types = {param.name: param.type for param in tool.params}
    extra_fields = sorted(set(args) - expected_fields)
    for field in extra_fields:
        errors.append(
            _error(
                field,
                "该工具不支持这个参数。",
                received=args.get(field),
                expected=f"可用参数：{', '.join(sorted(expected_fields)) or '无参数'}",
                strategy="请移除该字段，或选择正确的 Shipxy 工具。",
                recommended_tool="describe_capabilities",
            )
        )

    for param in tool.params:
        value = args.get(param.name, param.default)
        if param.required and _is_missing(value):
            errors.append(
                _error(
                    param.name,
                    "缺少必填参数。",
                    received=value,
                    expected=param.help,
                    strategy="调用工具前请补充该必填参数。",
                )
            )
            continue
        if _is_missing(value):
            continue

        if param.type == "int" and _as_int(value) is None:
            errors.append(_error(param.name, "参数必须是整数。", received=value, expected="整数"))
            continue
        if param.type == "float" and _as_float(value) is None:
            errors.append(_error(param.name, "参数必须是数字。", received=value, expected="数字"))
            continue
        if param.type == "list[int]":
            items = _normalize_mmsis(value)
            if len(items) > 100:
                errors.append(
                    _error(
                        param.name,
                        "MMSI 列表最多包含 100 个元素。",
                        received=f"{len(items)} 个元素",
                        expected="1 到 100 个 MMSI",
                        strategy="请将请求拆分为多次调用。",
                    )
                )
            for index, item in enumerate(items):
                errors.extend(_validate_mmsi(f"{param.name}.{index}", item))

    if "mmsi" in expected_fields and not _is_missing(args.get("mmsi")):
        errors.extend(_validate_mmsi("mmsi", args.get("mmsi")))
    if "imo" in expected_fields and not _is_missing(args.get("imo")):
        errors.extend(_validate_imo("imo", args.get("imo")))
    if tool.name == "search_ship_particular" and all(_is_missing(args.get(field)) for field in ("mmsi", "imo", "call_sign", "ship_name")):
        errors.append(
            _error(
                "mmsi|imo|call_sign|ship_name",
                "至少需要一个船舶标识。",
                received=args,
                expected="提供 mmsi、imo、call_sign 或 ship_name。",
                strategy="如果没有精确标识，请先搜索船舶。",
                recommended_tool="search_ship",
            )
        )

    for field in ("keywords", "fleet_id", "call_sign", "ship_name"):
        if field in expected_fields and not _is_missing(args.get(field)) and not str(args.get(field)).strip():
            errors.append(_error(field, "文本参数不能为空。", received=args.get(field), expected="非空文本"))

    if "max_results" in expected_fields and not _is_missing(args.get("max_results")):
        value = _as_int(args.get("max_results"))
        if value is None or value < 1 or value > 100:
            errors.append(_error("max_results", "max_results 必须在 1 到 100 之间。", received=args.get("max_results"), expected="1 <= max_results <= 100"))

    if "output" in expected_fields and not _is_missing(args.get("output")):
        value = _as_int(args.get("output"))
        if value not in (0, 1):
            errors.append(_error("output", "output 必须是 0 或 1。", received=args.get("output"), expected="0 表示 base64，1 表示 JSON"))

    if tool.name in ("get_tide_data", "get_global_tide_data") and "port_code" in expected_fields and not _is_missing(args.get("port_code")):
        station_tool = "get_global_tides" if tool.name == "get_global_tide_data" else "get_tides"
        errors.extend(_validate_port_code("port_code", args.get("port_code"), tide_station=True, station_tool=station_tool))
    else:
        for field in ("port_code", "start_port_code", "end_port_code"):
            if field in expected_fields and not _is_missing(args.get(field)):
                errors.extend(_validate_port_code(field, args.get(field)))

    for field in ("lng", "lat"):
        if field in expected_fields and not _is_missing(args.get(field)):
            errors.extend(_validate_lng_lat(field, _as_float(args.get(field)), args.get(field)))

    for field in ("start_point", "end_point"):
        if field in expected_fields and not _is_missing(args.get(field)):
            errors.extend(_validate_point(field, args.get(field)))

    if tool.name == "plan_route_by_point":
        errors.extend(_validate_port_or_point_destination(args))
        if not _is_missing(args.get("end_port_code")):
            errors.extend(_validate_port_code("end_port_code", args.get("end_port_code")))

    if "region" in expected_fields and not _is_missing(args.get("region")):
        points = [point for point in str(args.get("region")).split("-") if point]
        if len(points) < 3:
            errors.append(
                _error(
                    "region",
                    "区域必须至少包含三个 lng,lat 坐标点。",
                    received=args.get("region"),
                    expected="lng,lat-lng,lat-lng,lat",
                    strategy="请提供多边形，而不是单点或线段。",
                )
            )
        for index, point in enumerate(points):
            errors.extend(_validate_point(f"region.{index}", point))

    if "weather_type" in expected_fields and not _is_missing(args.get("weather_type")):
        value = _as_int(args.get("weather_type"))
        if value not in (0, 1, 2, 3):
            errors.append(_error("weather_type", "weather_type 必须是 0、1、2 或 3。", received=args.get("weather_type"), expected="0 全部，1 沿岸，2 近海，3 远海"))

    if "type_" in expected_fields and not _is_missing(args.get("type_")):
        value = _as_int(args.get("type_"))
        if value not in (1, 2):
            errors.append(_error("type_", "type 必须是 1 或 2。", received=args.get("type_"), expected="1 表示 ATA，2 表示 ATD"))

    integer_time_fields = ("start_time", "end_time", "weather_time", "typhoon_id")
    for field in integer_time_fields:
        if field in expected_fields and param_types.get(field) == "int" and not _is_missing(args.get(field)):
            value = _as_int(args.get(field))
            if value is None or value < 0:
                errors.append(_error(field, f"{field} 必须是非负 Unix 时间戳或 ID。", received=args.get(field), expected="非负整数"))

    if (
        "start_time" in expected_fields
        and "end_time" in expected_fields
        and param_types.get("start_time") == "int"
        and param_types.get("end_time") == "int"
        and not _is_missing(args.get("start_time"))
        and not _is_missing(args.get("end_time"))
    ):
        start = _as_int(args.get("start_time"))
        end = _as_int(args.get("end_time"))
        if start is not None and end is not None and start >= end:
            errors.append(
                _error(
                    "start_time/end_time",
                    "start_time 必须早于 end_time。",
                    received={"start_time": args.get("start_time"), "end_time": args.get("end_time")},
                    expected="start_time < end_time",
                    strategy="请使用有效的 Unix 时间戳范围。",
                )
            )

    if tool.name == "history_weather":
        for field in ("start_time", "end_time"):
            if not _is_missing(args.get(field)):
                errors.extend(_validate_datetime_seconds(field, args.get(field)))
        try:
            start = datetime.strptime(str(args.get("start_time")), "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(str(args.get("end_time")), "%Y-%m-%d %H:%M:%S")
            if start >= end:
                errors.append(
                    _error(
                        "start_time/end_time",
                        "start_time 必须早于 end_time。",
                        received={"start_time": args.get("start_time"), "end_time": args.get("end_time")},
                        expected="start_time < end_time",
                        strategy="请使用有效的 yyyy-MM-dd HH:mm:ss 时间范围。",
                    )
                )
        except ValueError:
            pass

    if tool.name == "get_nav_warning":
        for field in ("start_time", "end_time"):
            if not _is_missing(args.get(field)):
                errors.extend(_validate_datetime(field, args.get(field)))
        try:
            start = datetime.strptime(str(args.get("start_time")), "%Y-%m-%d %H:%M")
            end = datetime.strptime(str(args.get("end_time")), "%Y-%m-%d %H:%M")
            if start >= end:
                errors.append(
                    _error(
                        "start_time/end_time",
                        "start_time 必须早于 end_time。",
                        received={"start_time": args.get("start_time"), "end_time": args.get("end_time")},
                        expected="start_time < end_time",
                        strategy="请使用有效的 yyyy-MM-dd HH:mm 时间范围。",
                    )
                )
        except ValueError:
            pass

    for field in ("start_date", "end_date"):
        if field in expected_fields and not _is_missing(args.get(field)):
            errors.extend(_validate_date(field, args.get(field)))
    if "start_date" in expected_fields and "end_date" in expected_fields and not _is_missing(args.get("start_date")) and not _is_missing(args.get("end_date")):
        try:
            start_date = datetime.strptime(str(args.get("start_date")), "%Y-%m-%d")
            end_date = datetime.strptime(str(args.get("end_date")), "%Y-%m-%d")
            if start_date > end_date:
                errors.append(
                    _error(
                        "start_date/end_date",
                        "start_date 必须早于或等于 end_date。",
                        received={"start_date": args.get("start_date"), "end_date": args.get("end_date")},
                        expected="start_date <= end_date",
                    )
                )
        except ValueError:
            pass

    metadata = tool_response_metadata(tool.name)
    return {
        "ok": not errors,
        "tool": tool.name,
        "capability_ref": metadata["capability_ref"],
        "returns": metadata["returns"],
        "object_refs": metadata["object_refs"],
        "errors": errors,
    }
