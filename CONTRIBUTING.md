# Contributing to searchconsole-mcp

Thank you for your interest in improving this project! This document provides guidelines for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/harisnadeem/searchconsole-mcp.git`
3. Create a virtual environment: `python -m venv .venv`
4. Activate it: `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows)
5. Install development dependencies: `pip install -e ".[dev]"`

## Development Workflow

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Run tests and ensure they pass: `python -m pytest`
4. Format your code: `black searchconsole_mcp/ && ruff check searchconsole_mcp/`
5. Commit your changes: `git commit -m "Add feature: description"`
6. Push to your fork: `git push origin feature/your-feature-name`
7. Open a Pull Request

## Code Style

- Follow PEP 8
- Use type hints for function signatures
- Add docstrings for all public functions
- Keep functions focused and small
- Use descriptive variable names

## Reporting Issues

When reporting issues, please include:
- Python version (`python --version`)
- Package version (`pip show searchconsole-mcp`)
- Steps to reproduce
- Expected vs actual behavior
- Any error messages

## Pull Request Guidelines

- Update documentation if needed
- Add tests for new features
- Ensure all existing tests pass
- Keep PRs focused on a single change
- Link to related issues if applicable

## Questions?

Open a [GitHub Discussion](https://github.com/harisnadeem/searchconsole-mcp/discussions) or create an issue.

Thank you for contributing!
