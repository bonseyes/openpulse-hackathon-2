# AGENTS.md — Agent & Maintainer Guide (Python CLI skeleton)

Last updated: 2025-11-25

This guide standardizes how to work in **openpulse-hackathon-2**, a barebones Python CLI stub. Follow these guardrails to keep changes predictable and easy to review.

## 1) Codebase tour
- `README.md`: brief project overview and goals.
- `LICENSE`: Apache 2.0 license.
- `src/reproai/main.py`: empty entry point placeholder for future CLI logic. `PYTHONPATH=src` is needed to import `reproai` without installing.

## 2) Dev environment
- Python: target 3.11 (assumed; no version pin present). Use `pyenv` if you need to switch versions.
- Package manager: none configured; use `pip` inside a virtual environment.
- Dependencies: none declared yet.
- Optional tooling: `pre-commit`, `ruff`, `black`, and `mypy` are good defaults if you add code.

### 2.1 Bootstrap
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
# No dependencies yet; add a requirements file or pyproject.toml when the code grows.
```

## 3) Running the code
The entry file is currently empty. After adding logic, run it directly with the source tree on `PYTHONPATH`:
```bash
PYTHONPATH=src python -m reproai.main --help
```

## 4) Tests and quality checks
No automated tests or linters are defined. If you introduce them, prefer:
- Tests: `pytest`
- Lint: `ruff check .`
- Format: `black .`
- Types: `mypy src`

Set coverage thresholds in CI once tests exist.

## 5) Security and secrets
- Do not commit secrets, tokens, or `.env` files. Provide samples via `.env.example` if needed.
- Add dependency audits (e.g., `pip-audit`) once dependencies are introduced.

## 6) Git hygiene
- Keep changes minimal; avoid wholesale reformatting unrelated files.
- Do not commit build artifacts, virtualenvs, or cache directories (e.g., `.venv/`, `dist/`, `.pytest_cache/`).
- Conventional Commit titles are preferred for PRs when adding features (e.g., `feat: add CLI options`).

## 7) CI/CD expectations
No CI configuration exists yet. When adding one, ensure it covers install, tests, lint, and packaging steps consistent with the commands above.

## 8) Assumptions
- Python 3.11 chosen as the default runtime due to lack of explicit versioning.
- Package and CLI wiring are not defined; commands above assume the module will gain executable content.
