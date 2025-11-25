# AGENTS.md — Agent & Maintainer Guide (Python 3 CLI)

This document describes how automated agents (and helpful humans) should interact with the repository for {{REPO_NAME}}. It standardizes installs, tests, releases, and guardrails so tasks are repeatable, auditable, and gloriously boring—in the good way.

## 0) Placeholder Legend
Replace these everywhere (including examples and YAML):

{{ORG_NAME}} – Organization or GitHub owner
{{REPO_NAME}} – Repository name
{{PACKAGE_NAME}} – Python package/import name (e.g., reproai_cli)
{{CLI_NAME}} – CLI entry point command (e.g., main.py)
{{DEFAULT_BRANCH}} – Default branch (e.g., main)
{{PYTHON_VERSION}} – Target Python (e.g., 3.12)
{{PY_MGR}} – Environment/packager: uv, pip, poetry, or hatch
{{TEST_RUNNER}} – pytest
{{LINTER}} – ruff
{{FORMATTER}} – black
{{TYPE_CHECKER}} – mypy
{{SECURITY_TOOL}} – pip-audit or safety (and bandit for code)
{{CI_PROVIDER}} – e.g., github-actions, gitlab-ci
{{CD_TARGET}} – e.g., pypi, gh-releases
{{RELEASE_TOOL}} – python-semantic-release or release-please
{{COVERAGE_THRESHOLD}} – e.g., 85
{{ENV_PREFIX}} – env var prefix used in CI (e.g., AGENT_)
{{HTTP_LIB}} – httpx or requests

## 1) Codebase Tour
1.1 Layout
Path	Purpose
/	Repo root: pyproject.toml, README.md, .editorconfig, .pre-commit-config.yaml
src/main.py	CLI entry

## 2) Dev Environment
2.1 Prereqs
Python {{PYTHON_VERSION}} (use pyenv if needed)
Package tool: {{PY_MGR}}
Optional: pre-commit for hooks

2.2 Bootstrap
```bash
# Create & activate env
# pip
python -m venv .venv && source .venv/bin/activate
python -m pip install -U pip build
pip install -e ".[dev]"

# pre-commit hooks
pre-commit install
```

2.3 Run (Dev)
```bash
# Show help
{{CLI_NAME}} --help

# Run
{{CLI_NAME}} run --paper_id paper123 --github_id github123
```

2.4 Build (Package)
```bash
python -m build  # produces dist/*.whl and dist/*.tar.gz
```

2.5 Test
```bash
# Unit + integration
pytest

# Coverage (CI-friendly)
pytest --cov={{PACKAGE_NAME}} --cov-report=term-missing --cov-fail-under={{COVERAGE_THRESHOLD}}
```

2.6 Lint, Format, Type Check
```bash
ruff check .
black --check .
mypy src
```

2.7 Security
```bash
pip-audit           # dependency CVEs
bandit -r src       # code smells
```

## 3) Scripts (Single Source of Truth)
Prefer Makefile or Nox. Example Makefile:

```
.PHONY: install fmt lint type test cov build release

install:
\tuv pip install -e ".[dev]" || pip install -e ".[dev]"

fmt:
\tblack .
\truff check --fix

lint:
\truff check .
\tbandit -r src

type:
\tmypy src

test:
\tpytest

cov:
\tpytest --cov={{PACKAGE_NAME}} --cov-report=xml --cov-fail-under={{COVERAGE_THRESHOLD}}

build:
\tpython -m build

release:
\tpython -m semantic_release version && python -m build && semantic-release publish
```

## 4) Quality Gates (CI = merge gatekeeper)
Builds: python -m build succeeds
Lint: ruff check . clean; Format: black --check .
Types: mypy src passes
Tests: coverage >= {{COVERAGE_THRESHOLD}}%
Security: pip-audit (no high CVEs) and bandit -r src clean
Conventional Commits: enforced on PR titles / commits

## 5) Conventions & Style
5.1 Python Style
PEP 8 via ruff + black; docstrings in Google style
Modules and files lowercase_with_underscores
Public API in __init__.py; avoid wild from x import * (chaos vibes)

5.2 Python Coding Rules
MUST provide clean, production-grade, high quality code.
ASSUME the user is using python version 3.10+
USE well-known python design patterns and object-oriented programming approaches
MUST provide code blocks with proper google style docstrings
MUST provide code blocks with input and return value type hinting.
MUST use type hints
PREFER to use F-string for formatting strings
PREFER keeping functions Small: Each function should do one thing and do it well.
USE @property: For getter and setter methods. - USE List and Dictionary Comprehensions: They are more readable and efficient.
USE generators for large datasets to save memory.
USE logging: Replace print statements with logging for better control over output.
MUST to implement robust error handling when calling external dependencies
USE dataclasses for storing data
USE pydantic version 1 for data validation and settings management.
Ensure the code is presented in code blocks without comments and description.
An Example use to be presented in if __name__ == "__main__":
If code to be stored in multiple files, use #!filepath to signal that in the same code block.

5.3 Error Handling & Logging
Centralize exceptions in exceptions.py
Use logging with structured fields; no print()-driven observability
Redact API keys, tokens, PII in logs (we like secrets secret)

5.4 Testing
Unit test the agent’s decision logic and tool adapters
Mock model calls (pytest-mock, respx/responses, or vcrpy)
No live network in unit tests; integration tests may target Test endpoints

## 6) Architecture
CLI → src/{{PACKAGE_NAME}}/main.py

## 7) Release Management
Versioning: Semantic Versioning (SemVer)
Commits: Conventional Commits (feat:, fix:, chore:…)
Changelog: auto-generated by {{RELEASE_TOOL}}
Tags: vX.Y.Z on {{DEFAULT_BRANCH}}
Artifacts: wheels + source tarball; optional single-binary (pyinstaller) for {{CD_TARGET}}

## 9) Agent Operating Procedures

TL;DR: be predictable, idempotent, and drama-free.

9.1 Allowed Commands (safe)
make install|lint|type|test|cov|build
{{CLI_NAME}} run [...] with documented flags
Editing prompts under prompts/ with ADR note

9.2 Caution / Approval Needed
Changing provider defaults or safety thresholds
Rotating secrets / adding new scopes
Introducing new external tools with side effects
Modifying CI/CD workflows

9.3 Git Hygiene
Branch from {{DEFAULT_BRANCH}}
PR titles follow Conventional Commits
Keep diffs minimal; don’t reformat the world mid-feature
Never commit dist/, .env*, .pytest_cache/, or virtualenvs

## 10) Security & Compliance
Secrets loaded only from env/CI; .env.example for docs
Dependency audit ({{SECURITY_TOOL}}) on PRs
Code scan (bandit) on PRs
License policy via pip-licenses (block disallowed)
Optional: CSP/egress allowlists if the agent calls remote tools

## 11) Example Files (snippets)
11.1 pyproject.toml (minimal)
```
[project]
name = "{{PACKAGE_NAME}}"
version = "0.1.0"
description = "A Python CLI script."
readme = "README.md"
requires-python = ">={{PYTHON_VERSION}}"
authors = [{ name = "Your Team", email = "team@example.com" }]
dependencies = [
  "{{HTTP_LIB}}",
  "pydantic>=2",
  "typer[all]",
]
[project.optional-dependencies]
dev = ["pytest", "pytest-cov", "black", "ruff", "mypy", "pip-audit", "bandit", "build", "vcrpy"]

[project.scripts]
{{CLI_NAME}} = "{{PACKAGE_NAME}}.cli:app"

[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
lint.select = ["E","F","I","B","UP","S","BLE"]
lint.ignore = ["E501"]

[tool.mypy]
python_version = "{{PYTHON_VERSION}}"
strict = true
packages = ["{{PACKAGE_NAME}}"]
```

11.2 src/{{PACKAGE_NAME}}/main.py (Typer)
```
import typer

app = typer.Typer(help="{{CLI_NAME}} — Python CLI")

@app.command()
def run(paper_id: str = typer.Argument(..., help="Paper ID"),
        github_id: str = typer.Argument(..., help="Github ID"),
        log_level: str = typer.Option("INFO", help="DEBUG/INFO/WARN/ERROR")):

    """Run script."""
    result = "dummy"
    typer.echo(result.output)

if __name__ == "__main__":
    app()
```

11.3 .pre-commit-config.yaml
```
repos:
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.6.9
    hooks: [ { id: ruff, args: [ "--fix" ] } ]
  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks: [ { id: black } ]
```

## 12) One-Liners (handy incantations)
```
# Clean env, install, test
rm -rf .venv && uv venv -p {{PYTHON_VERSION}} && source .venv/bin/activate && make install test

# Full CI locally
make lint type cov build

# Publish to TestPyPI (manual)
python -m build && twine upload --repository testpypi dist/*

# Run with explicit model
{{CLI_NAME}} run --paper_id paper123 --github_id github123
```

## 13) Appendix: CLI Commands (must stay in sync)
{{CLI_NAME}} run — single-shot agent or scripted run
{{CLI_NAME}} tools — list available tools & schemas
{{CLI_NAME}} config — print effective config (redacted)
{{CLI_NAME}} version — print version/build info
