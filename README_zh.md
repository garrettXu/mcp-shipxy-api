# shipxy-api-mcp

<!-- mcp-name: io.github.garrettxu/mcp-shipxy-api -->

**Shipxy MCP Server** 是一个完全兼容 MCP 协议的开源海事场景位置服务（LBS）解决方案，为开发者和 AI 智能体提供全面的船舶与港口 API 及工具。它可无缝集成实时船舶数据、航线规划、气象、潮汐等多种能力到您的应用中。

## 🚀 项目简介

**Shipxy MCP Server** 让您的应用、LLM 和智能体具备先进的海事数据与地理空间智能，包括：

- **船舶信息与跟踪：** 实时船舶位置、静态信息、船队与区域查询。
- **港口与泊位数据：** 全球港口检索、靠泊/锚地/ETA 查询、靠港记录。
- **航线规划：** 点到点、港到港航线规划。
- **气象与潮汐：** 海洋气象、台风、潮汐站数据。
- **丰富的海事API：** 船籍、档案、搭靠事件等。

所有 API 均遵循 MCP 协议，可被任何 MCP 兼容的客户端、LLM 或智能体平台调用。

## 🛠️ 主要特性

- **完整 MCP 协议支持：** 可无缝集成到任何 MCP 兼容的智能体、LLM 或平台。
- **全面的海事数据：** 船舶、港口、航线、气象、潮汐等。
- **实时与历史数据：** 实时船舶跟踪、航次历史、事件记录。
- **开源易扩展：** MIT 协议，便于自定义和扩展。

## ⚡ 快速开始

### 1. 获取 API Key

请在 [船讯网开放平台](https://api.shipxy.com/v3/console/overview) 注册并创建服务端 API Key。
**注意：** 所有请求均需 API Key。

### 2. 安装依赖

正式发布到 PyPI 后可直接安装：

```bash
pipx install mcp-shipxy-api
```

或安装到已有虚拟环境：

```bash
pip install mcp-shipxy-api
```

本地源码开发：

```bash
pip install -r requirements.txt
```

### 3. 配置

在项目根目录创建 `.env` 文件：

```
SHIPXY_API_KEY=你的_api_key
```

### 4. 启动服务

#### stdio 方式

推荐使用 `mcp.json` 配置文件，便于与 MCP CLI 及智能体平台集成。示例：

```json
{
  "mcpServers": {
    "shipxy-api-mcp": {
      "command": "python",
      "args": ["/path/to/your/server.py"],
      "env": {
        "SHIPXY_API_KEY": "你的_api_key"
      }
    }
  }
}
```

也可以直接运行：

```bash
python server.py
```

#### SSE 方式

需要把服务部署成 HTTP/SSE 时，可以这样启动：

```bash
python server.py --transport sse --host 0.0.0.0 --port 18081
```

SSE 端点：

```text
http://localhost:18081/sse
```

消息端点：

```text
http://localhost:18081/messages/
```

SSE 支持两种 API Key 传入方式：

```bash
curl 'http://localhost:18081/sse?ak=你的_api_key'
curl -H 'Authorization: Bearer 你的_api_key' http://localhost:18081/sse
```

MCP 客户端配置 SSE 时，推荐使用 Bearer Token：

```text
SSE URL: http://localhost:18081/sse
Authentication: Bearer Token
Token: 你的 Shipxy API Key
```

## CLI 使用

本项目也提供跨平台 CLI，命令保持扁平结构，直接对应 MCP tool 名称，仅把下划线改成短横线：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

shipxy auth status
shipxy tools
shipxy schema search-ship
shipxy search-ship COSCO --max 5
shipxy get-single-ship 413211000
shipxy search-port Shanghai
shipxy plan-route-by-port CNSHA SGSIN
shipxy plan-route-by-point 113.571144,22.844316 --end-port-code CNQDG
shipxy get-weather-by-point --lng 123.58414 --lat 27.37979
```

Windows PowerShell 激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

CLI 默认输出 JSON，方便大模型和其他 Agent 调用。需要人类可读输出时可指定：

```bash
shipxy search-ship COSCO --max 5 --format table
shipxy search-ship COSCO --max 5 --format pretty
shipxy search-ship COSCO --max 5 --format ndjson
```

也可以通过 CLI 启动 MCP Server：

```bash
shipxy mcp start
shipxy mcp start --transport sse --host 0.0.0.0 --port 18081
```

stdio 方式下，Agent 和 MCP 客户端应通过 `SHIPXY_API_KEY` 环境变量传入 API Key：

```json
{
  "mcpServers": {
    "shipxy": {
      "command": "shipxy",
      "args": ["mcp", "start"],
      "env": {
        "SHIPXY_API_KEY": "你的_api_key"
      }
    }
  }
}
```

## Agent 调用建议

面向大模型和其他 Agent 调用时，建议按这个顺序使用：

1. `describe_capabilities`：查看可用工具、适用场景、返回对象和常见错误。
2. `describe_object`：查看返回对象字段含义，例如 `VesselPosition`、`Port`、`Route`。
3. `validate_tool_input`：在正式调用 Shipxy 前预校验参数，获取字段级修复建议。
4. 调用具体业务工具，例如 `search_ship`、`get_single_ship`、`plan_route_by_port`。

所有业务工具返回都包含 `ok`、`tool`、`returns`、`capability_ref`、`object_refs`。失败时返回结构化 `error`，包括错误类型、消息、详情和可执行修复建议。

## 🧩 支持的API

| 工具名称                  | 说明                                   |
|--------------------------|----------------------------------------|
| describe_capabilities    | 查询工具能力、返回对象、错误和调用建议 |
| describe_object          | 查询返回对象 schema 和字段含义         |
| validate_tool_input      | 预校验工具入参并返回修复建议           |
| search_ship              | 按 MMSI、IMO、船名、呼号模糊查询船舶   |
| get_single_ship          | 查询单船实时信息（MMSI）               |
| get_many_ship            | 查询多船实时信息（MMSI列表）           |
| get_fleet_ship           | 查询船队下所有船舶                     |
| get_surrounding_ship     | 查询指定船舶10海里内的周边船舶         |
| get_area_ship            | 查询指定区域内的船舶                   |
| get_ship_registry        | 查询船舶国籍/船籍信息                  |
| search_ship_particular   | 按 MMSI/IMO/呼号/船名查船舶档案        |
| search_port              | 按名称或五位码模糊查询港口             |
| get_berth_ships          | 查询港口当前靠泊船舶                   |
| get_anchor_ships         | 查询港口当前锚地船舶                   |
| get_eta_ships            | 查询未来预计到港船舶                   |
| get_ship_track           | 查询船舶历史轨迹点                     |
| search_ship_approach     | 查询船舶搭靠事件                       |
| get_port_of_call_by_ship | 查询船舶靠港记录                       |
| get_port_of_call_by_ship_port | 查询船舶在指定港口的靠港记录      |
| get_port_of_call_by_port | 查询港口靠港记录                       |
| plan_route_by_point      | 点到点/点到港航线规划                  |
| plan_route_by_port       | 港到港航线规划                         |
| get_single_eta_precise   | 查询船舶ETA及航程信息                  |
| get_weather_by_point     | 按坐标查询海洋气象                     |
| get_weather              | 按区域查询海洋气象                     |
| get_all_typhoon          | 查询近年台风列表                       |
| get_single_typhoon       | 查询指定台风详情                       |
| get_tides                | 查询潮汐观测站列表                     |
| get_tide_data            | 查询指定潮汐站潮汐数据                 |
| get_global_tides         | 查询全球潮汐观测站列表                 |
| get_global_tide_data     | 查询指定全球潮汐站潮汐数据             |
| current_weather          | 查询全球实时大气与海洋气象             |
| future_weather           | 查询全球未来大气与海洋气象预报         |
| history_weather          | 查询指定坐标和时间范围的历史气象       |
| get_nav_warning          | 查询中国海事局航行警告                 |

## 🌍 应用场景

- **航运物流与船队管理**
- **船舶跟踪与监控**
- **港口运营与ETA预测**
- **智能航运与航线优化**
- **海洋气象与安全应用**

## 📦 项目结构

```
.
├── server.py           # MCP服务入口
├── ship_service.py     # 船讯网API集成与业务逻辑
├── tool_registry.py    # CLI/MCP工具注册表
├── domain_catalog.py   # 能力目录、返回对象schema、字段解释
├── validation.py       # 入参预校验与修复建议
├── requirements.txt    # Python依赖
├── pyproject.toml      # 项目元数据
└── README_zh.md        # 本文件
```

## 📄 许可证

MIT © shipxy-api-mcp 贡献者

## 📞 联系方式

如需了解更多或商务合作，请联系：

**电话：** 400-010-8558 / 010-8286 8599
