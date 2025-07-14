# shipxy-api-mcp

**Shipxy MCP Server** is a fully MCP-compliant, open-source Location-Based Service (LBS) solution for maritime scenarios, providing a comprehensive suite of ship and port APIs and tools for developers and AI agents. It enables seamless integration of real-time vessel data, route planning, weather, tides, and more into your applications.

## 🚀 Introduction

**Shipxy MCP Server** empowers your applications, LLMs, and agents with advanced maritime data and geospatial intelligence, including:

- **Ship Information & Tracking:** Real-time vessel position, static info, fleet, and area queries.
- **Port & Berth Data:** Global port search, berth/anchor/ETA queries, port call records.
- **Route Planning:** Point-to-point and port-to-port route planning.
- **Weather & Tides:** Marine weather, typhoon, and tide station data.
- **Rich Maritime APIs:** Ship registry, particulars, approach events, and more.

All APIs follow the MCP protocol and can be called from any MCP-compliant client, LLM, or agent platform.

## 🛠️ Key Features

- **Full MCP Protocol Support:** Seamless integration with any MCP-compliant agent, LLM, or platform.
- **Comprehensive Maritime Data:** Ships, ports, routes, weather, tides, and more.
- **Real-Time & Historical Data:** Live vessel tracking, voyage history, and event records.
- **Open Source & Extensible:** MIT licensed, easy to customize and extend.

## ⚡ Quick Start

### 1. Get Your API Key

Register and create a server-side API Key at [Shipxy Open Platform](https://api.shipxy.com/v3/console/overview).  
**Note:** The API key is required for all requests.

### 2. Installation

```bash
pip install -r requirements.txt
```


### 3. Configuration

Create a `.env` file in your project root:

```
SHIPXY_API_KEY=your_api_key_here
```

### 4. Start the Server

Recommended: Use an `mcp.json` configuration file for easy integration with MCP CLI and agent platforms. Example:

```json
{
  "mcpServers": {
    "shipxy-api-mcp": {
      "command": "python",
      "args": ["/path/to/your/server.py"],
      "env": {
        "SHIPXY_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## 🧩 Supported APIs

| Tool Name                | Description                                                      |
|--------------------------|------------------------------------------------------------------|
| search_ship              | Fuzzy search for ships by MMSI, IMO, name, or call sign          |
| get_single_ship          | Query real-time info for a single ship by MMSI                   |
| get_many_ship            | Query real-time info for multiple ships by MMSI list             |
| get_fleet_ship           | Query all ships in a fleet                                       |
| get_surrounding_ship     | Query ships within 10nm of a given ship                          |
| get_area_ship            | Query ships in a specified area                                  |
| get_ship_registry        | Query ship registry/country info                                 |
| search_ship_particular   | Query ship particulars by MMSI/IMO/call sign/name                |
| search_port              | Fuzzy search for ports by name or code                           |
| get_berth_ships          | Query ships currently berthed at a port                          |
| get_anchor_ships         | Query ships at anchor at a port                                  |
| get_eta_ships            | Query ships with ETA to a port                                   |
| get_ship_track           | Query historical track points for a ship                         |
| search_ship_approach     | Query ship-to-ship approach events                               |
| get_port_of_call_by_ship | Query port call records for a ship                               |
| get_port_of_call_by_port | Query port call records for a port                               |
| plan_route_by_point      | Plan route between two coordinates                               |
| plan_route_by_port       | Plan route between two ports                                     |
| get_single_eta_precise   | Get ETA and voyage info for a ship                               |
| get_weather_by_point     | Query marine weather by coordinates                              |
| get_weather              | Query marine weather by area                                     |
| get_all_typhoon          | List recent typhoons                                             |
| get_single_typhoon       | Query details for a specific typhoon                             |
| get_tides                | List tide stations                                               |
| get_tide_data            | Query tide data for a station                                    |

## 🌍 Application Scenarios

- **Maritime Logistics & Fleet Management**
- **Vessel Tracking & Monitoring**
- **Port Operations & ETA Prediction**
- **Smart Shipping & Route Optimization**
- **Marine Weather & Safety Applications**

## 📦 Project Structure

```
.
├── server.py           # MCP server entry point
├── ship_service.py     # Shipxy API integration and business logic
├── requirements.txt    # Python dependencies
├── pyproject.toml      # Project metadata
└── README.md           # This file
```

## 📄 License

MIT © shipxy-api-mcp contributors

## 📞 Contact

For more information or business inquiries, please contact:

**Phone:** 400-010-8558 / 010-8286 8599

