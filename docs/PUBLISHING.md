# Publishing

This project is distributed in two layers:

- PyPI package: `mcp-shipxy-api`
- MCP Registry server name: `io.github.garrettxu/mcp-shipxy-api`

The package exposes two console scripts:

- `shipxy`
- `mcp-shipxy-api`

The second script exists so package runners can execute the PyPI package name directly.

## Prerequisites

Create and activate a local virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U build twine
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U build twine
```

## Build

```bash
rm -rf dist build *.egg-info
python -m build
twine check dist/*
```

## TestPyPI

```bash
twine upload --repository testpypi dist/*
```

Install from TestPyPI in a clean environment:

```bash
python -m venv /tmp/shipxy-testpypi
source /tmp/shipxy-testpypi/bin/activate
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mcp-shipxy-api
shipxy doctor
```

## PyPI

```bash
twine upload dist/*
```

After upload, verify:

```bash
pipx install mcp-shipxy-api
shipxy --version
shipxy doctor
```

## MCP Registry

The package README contains the ownership marker required by the MCP Registry:

```text
mcp-name: io.github.garrettxu/mcp-shipxy-api
```

Publish `.mcp/server.json` after the matching package version exists on PyPI:

```bash
mcp-publisher login github
mcp-publisher publish .mcp/server.json
```

The server declares `SHIPXY_API_KEY` as a required secret environment variable.
