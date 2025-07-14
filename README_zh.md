# shipxy-api-mcp

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

```bash
pip install -r requirements.txt
```

### 3. 配置

在项目根目录创建 `.env` 文件：

```
SHIPXY_API_KEY=你的_api_key
```

### 4. 启动服务

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

## 🧩 支持的API

| 工具名称                  | 说明                                   |
|--------------------------|----------------------------------------|
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
| get_port_of_call_by_port | 查询港口靠港记录                       |
| plan_route_by_point      | 点到点航线规划                         |
| plan_route_by_port       | 港到港航线规划                         |
| get_single_eta_precise   | 查询船舶ETA及航程信息                  |
| get_weather_by_point     | 按坐标查询海洋气象                     |
| get_weather              | 按区域查询海洋气象                     |
| get_all_typhoon          | 查询近年台风列表                       |
| get_single_typhoon       | 查询指定台风详情                       |
| get_tides                | 查询潮汐观测站列表                     |
| get_tide_data            | 查询指定潮汐站潮汐数据                 |

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
├── requirements.txt    # Python依赖
├── pyproject.toml      # 项目元数据
└── README_zh.md        # 本文件
```

## 📄 许可证

MIT © shipxy-api-mcp 贡献者

## 📞 联系方式

如需了解更多或商务合作，请联系：

**电话：** 400-010-8558 / 010-8286 8599 