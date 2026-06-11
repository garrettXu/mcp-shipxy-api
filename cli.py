import argparse
import importlib.metadata
import json
import os
import sys
from collections.abc import Sequence
from typing import Any

from dotenv import dotenv_values, load_dotenv

from ship_service import ShipxyAPI
from tool_registry import TOOLS, all_schemas, get_tool, invoke_tool, model_to_data, parse_value


EXIT_USAGE = 1
EXIT_MISSING_API_KEY = 2
EXIT_API_ERROR = 3


class CliError(Exception):
    error_type = "cli_error"
    exit_code = EXIT_USAGE


class MissingAPIKeyError(CliError):
    error_type = "missing_api_key"
    exit_code = EXIT_MISSING_API_KEY


def json_print(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def compact_json_print(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def get_api_key(args: argparse.Namespace | None = None) -> str:
    load_dotenv()
    api_key = getattr(args, "api_key", None) if args else None
    api_key = api_key or os.getenv("SHIPXY_API_KEY")
    if not api_key:
        raise MissingAPIKeyError("缺少 SHIPXY_API_KEY。请在 .env、环境变量中设置，或通过 --api-key 传入。")
    return api_key


def create_api(args: argparse.Namespace) -> ShipxyAPI:
    return ShipxyAPI(api_key=get_api_key(args))


def format_error(error: Exception) -> dict[str, Any]:
    error_type = getattr(error, "error_type", error.__class__.__name__)
    return {"ok": False, "error_type": error_type, "message": str(error)}


def render_table(payload: Any) -> None:
    rows = payload
    if isinstance(payload, dict):
        if isinstance(payload.get("tools"), list):
            rows = payload["tools"]
        elif isinstance(payload.get("schema"), dict):
            rows = payload["schema"].get("parameters", payload["schema"])
        else:
            rows = payload.get("data", payload)
        if isinstance(rows, dict) and isinstance(rows.get("data"), list):
            rows = rows["data"]
    if isinstance(rows, dict):
        rows = [rows]
    if not isinstance(rows, list) or not rows:
        print("")
        return
    if not all(isinstance(row, dict) for row in rows):
        for item in rows:
            print(item)
        return

    keys: list[str] = []
    for row in rows:
        for key, value in row.items():
            if isinstance(value, (dict, list)):
                continue
            if key not in keys:
                keys.append(key)
            if len(keys) >= 8:
                break
        if len(keys) >= 8:
            break

    widths = {
        key: min(
            40,
            max(len(key), *(len(str(row.get(key, ""))) for row in rows[:50])),
        )
        for key in keys
    }
    print("  ".join(key.ljust(widths[key]) for key in keys))
    print("  ".join("-" * widths[key] for key in keys))
    for row in rows:
        print("  ".join(str(row.get(key, ""))[: widths[key]].ljust(widths[key]) for key in keys))


def render_result(payload: Any, output_format: str) -> None:
    if output_format == "json":
        json_print(payload)
    elif output_format == "pretty":
        json_print(payload)
    elif output_format == "ndjson":
        data = payload.get("data") if isinstance(payload, dict) else payload
        rows = data.get("data") if isinstance(data, dict) else data
        if isinstance(rows, list):
            for row in rows:
                compact_json_print(row)
        else:
            compact_json_print(payload)
    elif output_format == "table":
        render_table(payload)


def collect_values(args: argparse.Namespace, tool_name: str) -> dict[str, Any]:
    tool = get_tool(tool_name)
    values: dict[str, Any] = {}
    for param in tool.params:
        value = getattr(args, param.name, param.default)
        if value is not None:
            values[param.name] = parse_value(value, param.type)
    return values


def run_tool(args: argparse.Namespace) -> int:
    api = create_api(args)
    result = invoke_tool(api, args.tool_name, collect_values(args, args.tool_name))
    data = model_to_data(result)
    if isinstance(data, dict) and "ok" in data:
        payload = {"tool": args.tool_name, **data}
    else:
        payload = {"ok": True, "tool": args.tool_name, "data": data}
    render_result(payload, args.format)
    if payload.get("ok") is False:
        error_type = payload.get("error", {}).get("type")
        return EXIT_USAGE if error_type == "invalid_request" else EXIT_API_ERROR
    return 0


def command_tools(args: argparse.Namespace) -> int:
    payload = {"ok": True, "tools": all_schemas()}
    render_result(payload, args.format)
    return 0


def command_schema(args: argparse.Namespace) -> int:
    if args.name:
        payload = {"ok": True, "schema": get_tool(args.name).schema()}
    else:
        payload = {"ok": True, "tools": all_schemas()}
    render_result(payload, args.format)
    return 0


def key_source(args: argparse.Namespace) -> str | None:
    if getattr(args, "api_key", None):
        return "flag"
    env_values = dotenv_values(".env")
    env_file_value = env_values.get("SHIPXY_API_KEY")
    env_value = os.getenv("SHIPXY_API_KEY")
    if env_file_value and env_value == env_file_value:
        return ".env"
    if env_value:
        return "environment"
    if env_file_value:
        return ".env"
    return None


def command_auth_status(args: argparse.Namespace) -> int:
    load_dotenv()
    source = key_source(args)
    payload = {
        "ok": True,
        "authenticated": source is not None,
        "source": source,
    }
    render_result(payload, args.format)
    return 0


def installed_version(package: str) -> str | None:
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return None


def command_doctor(args: argparse.Namespace) -> int:
    load_dotenv()
    deps = {
        "httpx": installed_version("httpx"),
        "requests": installed_version("requests"),
        "python-dotenv": installed_version("python-dotenv"),
        "mcp": installed_version("mcp"),
        "pydantic": installed_version("pydantic"),
        "starlette": installed_version("starlette"),
        "uvicorn": installed_version("uvicorn"),
    }
    missing = [name for name, version in deps.items() if version is None]
    payload = {
        "ok": not missing,
        "python": sys.version.split()[0],
        "api_key_present": key_source(args) is not None,
        "dependency_versions": deps,
        "missing_dependencies": missing,
        "tool_count": len(TOOLS),
    }
    render_result(payload, args.format)
    return 0 if not missing else EXIT_USAGE


def command_mcp_start(args: argparse.Namespace) -> int:
    import server

    if args.transport == "sse":
        server.run_sse_server(args.host, args.port, debug=args.debug)
        return 0

    server.mcp.settings.host = args.host
    server.mcp.settings.port = args.port
    server.mcp.run(transport=args.transport, mount_path=args.mount_path)
    return 0


def add_global_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--api-key", help="Shipxy API Key。会覆盖 SHIPXY_API_KEY。")
    parser.add_argument(
        "--format",
        choices=("json", "pretty", "table", "ndjson"),
        default="json",
        help="输出格式。默认 json，便于 Agent 调用。",
    )


def add_tool_parser(subparsers: argparse._SubParsersAction, tool) -> None:
    parser = subparsers.add_parser(tool.cli_name, help=tool.summary, description=tool.summary)
    add_global_options(parser)
    for param in tool.params:
        arg_type = str
        if param.type == "int":
            arg_type = int
        elif param.type == "float":
            arg_type = float

        if param.positional:
            parser.add_argument(param.name, type=arg_type, help=param.help)
            continue

        flags = [f"--{param.option_name}", *param.aliases]
        parser.add_argument(
            *flags,
            dest=param.name,
            type=arg_type,
            required=param.required,
            default=None,
            help=param.help,
        )
    parser.set_defaults(func=run_tool, tool_name=tool.name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="shipxy", description="Shipxy API 命令行工具。")
    parser.add_argument("--version", action="version", version="shipxy 0.1.0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    tools_parser = subparsers.add_parser("tools", help="列出可用工具。")
    add_global_options(tools_parser)
    tools_parser.set_defaults(func=command_tools)

    schema_parser = subparsers.add_parser("schema", help="查看工具 schema。")
    add_global_options(schema_parser)
    schema_parser.add_argument("name", nargs="?", help="工具名，例如 search-ship。")
    schema_parser.set_defaults(func=command_schema)

    auth_parser = subparsers.add_parser("auth", help="认证相关辅助命令。")
    auth_subparsers = auth_parser.add_subparsers(dest="auth_command", required=True)
    auth_status_parser = auth_subparsers.add_parser("status", help="查看 API Key 状态。")
    add_global_options(auth_status_parser)
    auth_status_parser.set_defaults(func=command_auth_status)

    doctor_parser = subparsers.add_parser("doctor", help="检查本地 CLI 配置。")
    add_global_options(doctor_parser)
    doctor_parser.set_defaults(func=command_doctor)

    mcp_parser = subparsers.add_parser("mcp", help="MCP 服务相关辅助命令。")
    mcp_subparsers = mcp_parser.add_subparsers(dest="mcp_command", required=True)
    mcp_start_parser = mcp_subparsers.add_parser("start", help="启动 MCP 服务。")
    mcp_start_parser.add_argument("--transport", choices=("stdio", "sse", "streamable-http"), default="stdio")
    mcp_start_parser.add_argument("--host", default="127.0.0.1")
    mcp_start_parser.add_argument("--port", type=int, default=8000)
    mcp_start_parser.add_argument("--mount-path", default=None)
    mcp_start_parser.add_argument("--debug", action="store_true")
    mcp_start_parser.set_defaults(func=command_mcp_start)

    for tool in TOOLS:
        add_tool_parser(subparsers, tool)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except CliError as error:
        render_result(format_error(error), getattr(args, "format", "json"))
        return error.exit_code
    except Exception as error:
        render_result(format_error(error), getattr(args, "format", "json"))
        return EXIT_API_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
