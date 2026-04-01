# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Support for Google Search Console URL Testing Tools API
- Enhanced filtering in search analytics
- Batch URL inspection support

## [0.1.0] - 2026-04-01

### Added
- Initial release with 7 MCP tools:
  - `get_sites` — List all Search Console sites
  - `query_search_analytics` — Query search performance data
  - `get_sitemap` — Get sitemap metadata
  - `list_sitemaps` — List all sitemaps
  - `submit_sitemap` — Submit new sitemaps
  - `delete_sitemap` — Remove sitemaps
  - `inspect_url` — Check URL indexing status
- Application Default Credentials (ADC) support
- Automatic token refresh with 401 retry
- Async HTTP via httpx
- MCP 2024-11-05 protocol compliance

### Technical
- Python 3.10+ requirement
- Minimal dependencies: google-auth, httpx, mcp
- Apache 2.0 license

[Unreleased]: https://github.com/harisnadeem/searchconsole-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/harisnadeem/searchconsole-mcp/releases/tag/v0.1.0
