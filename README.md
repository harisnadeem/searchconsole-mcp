# Google Search Console MCP Server (by Haris Nadeem)

Package name: `searchconsole-mcp`

A lightweight, fast MCP server for Google Search Console. Query search analytics, manage sitemaps, and inspect URLs directly from your AI assistant.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)

## Features

- **7 Powerful Tools**: List sites, query search analytics, manage sitemaps, inspect URLs
- **Fast & Lightweight**: Built with `httpx` and `google-auth` — minimal dependencies
- **Standard MCP**: Works with Claude Desktop, Cursor, Windsurf, and any MCP-compatible client
- **Full Analytics**: Query clicks, impressions, CTR, and position with flexible dimensions and filters
- **URL Inspection**: Check indexing status and coverage for any URL
- **Sitemap Management**: Submit, list, and delete sitemaps

## Installation

### From PyPI (recommended)

```bash
pip install searchconsole-mcp
```

### From source

```bash
git clone https://github.com/harisnadeem/searchconsole-mcp.git
cd searchconsole-mcp
pip install -e .
```

## Quick Start

### 1. Enable the Search Console API

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/library/searchconsole.googleapis.com)
2. Select or create a project
3. Click **Enable**

### 2. Authenticate

**Option A: User Account (OAuth)** — recommended for personal use

```bash
gcloud auth application-default login
```

**Option B: Service Account** — recommended for team/agency use

1. Create a service account: [Google Cloud Console → IAM → Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Download the JSON key
3. Set the environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
   ```

### 3. Configure your MCP client

#### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "searchconsole": {
      "command": "searchconsole-mcp",
      "env": {}
    }
  }
}
```

#### Cursor

In Cursor Settings → Features → MCP, add:

- **Name**: `searchconsole`
- **Type**: `command`
- **Command**: `searchconsole-mcp`

#### Windsurf

Edit `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "searchconsole": {
      "command": "searchconsole-mcp"
    }
  }
}
```

## Usage Examples

Once connected, ask your AI assistant:

- *"List all sites in my Search Console account"*
- *"Show me search analytics for example.com for the last 30 days"*
- *"Get the top queries with highest impressions but low CTR"*
- *"Check if https://example.com/page is indexed"*
- *"Submit the sitemap at https://example.com/sitemap.xml"*

## Available Tools

| Tool | Description |
|------|-------------|
| `get_sites` | List all verified sites in your Search Console account |
| `query_search_analytics` | Query clicks, impressions, CTR, position by dimensions |
| `get_sitemap` | Get metadata for a specific sitemap |
| `list_sitemaps` | List all sitemaps for a site |
| `submit_sitemap` | Submit/add a new sitemap URL |
| `delete_sitemap` | Remove a sitemap from Search Console |
| `inspect_url` | Inspect indexing status, coverage, and robots.txt state |

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account key JSON | Only if using service account |

### Google Cloud Project

The server uses [Application Default Credentials (ADC)](https://cloud.google.com/docs/authentication/application-default-credentials). Ensure the Google Cloud project has the **Search Console API** enabled.

## API Rate Limits

The Search Console API enforces per-user quotas:
- Default: ~25,000 queries per day
- URL Inspection: Limited (~10 per minute)

The server does not implement additional rate limiting; respect the API quotas.

## Requirements

- Python 3.10+
- Google Cloud project with Search Console API enabled
- Authenticated Google account with Search Console access

## Development

```bash
# Clone and setup
git clone https://github.com/harisnadeem/searchconsole-mcp.git
cd searchconsole-mcp
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
python -m pytest tests/

# Format code
black searchconsole_mcp/
ruff check searchconsole_mcp/
```

## Publishing a Release

This repository is configured for GitHub Actions + PyPI Trusted Publishing.

1. In PyPI, create the project `searchconsole-mcp` (or use the existing one).
2. In PyPI project settings, add a Trusted Publisher:
   - Owner: `harisnadeem`
   - Repository: `searchconsole-mcp`
   - Workflow: `publish.yml`
   - Environment: `pypi`
3. Create and push a version tag:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
4. Create a GitHub Release for that tag.
5. The `Publish to PyPI` workflow publishes the package automatically.

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.

## Acknowledgments

Built with:
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Google Search Console API](https://developers.google.com/search)
- [httpx](https://www.python-httpx.org/)

---

**Not officially affiliated with Google.** This is an unofficial, community-maintained MCP server for Google Search Console.
