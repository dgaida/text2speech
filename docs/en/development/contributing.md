# Contributing

Thank you for your interest in contributing to the `text2speech` project!

## Development Setup

1. Clone the repository
2. Create a virtual environment
3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```

## Pull Request Process

1. Create a new branch for your feature or bugfix.
2. Write tests for your changes.
3. Ensure all tests pass (`pytest`).
4. Check code quality (`black`, `ruff`, `mypy`).
5. Ensure complete documentation for new APIs (Google style).
6. Submit your pull request.

## Conventional Commits

We use [Conventional Commits](https://www.conventionalcommits.org/) to generate automated changelogs.

Examples:
- `feat: add support for new language`
- `fix: fix memory leak in queue`
- `docs: update API reference`
