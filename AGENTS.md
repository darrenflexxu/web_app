# AGENTS.md

## Stack
- FastAPI + SQLAlchemy 2 + Pydantic v2 + Jinja2. SQLite at repo-root `blog.db`.
- `src` layout: package is `src/web_app/`. Installed editable via `.venv` (`web_app.pth` points at `src`), so `import web_app` works from repo root with `.venv/bin/python` — no `PYTHONPATH` needed.
- Python `>=3.14`, managed with `uv` (`uv.lock`, `.python-version`, `.venv/`).

## Entrypoints (non-obvious)
- All routes + `app` live in `src/web_app/__init__.py`. `database.py` (engine/`Base`/`get_db`), `models.py` (SQLAlchemy), `schemas.py` (Pydantic) are supporting modules only.
- `[project.scripts] web-app = "web_app:main"` is **broken** — no `main` exists. Do not use `.venv/bin/web-app`.
- Run dev server from **repo root** (paths below are CWD-relative):
  - `.venv/bin/uvicorn web_app:app --reload`
  - or `uv run uvicorn web_app:app --reload`

## CWD-relative paths — always run from repo root
- `src/web_app/__init__.py:17`: `Base.metadata.create_all(bind=engine)` runs on import, creates `./blog.db`.
- `database.py:4`: `sqlite:///./blog.db` — CWD-dependent.
- `Jinja2Templates(directory="templates")`, `StaticFiles(directory="static"/"media")` — `templates/`, `static/`, `media/` are at repo root, not under `src/`.

## Imports
- Always package-qualified: `from web_app.database import Base`, never bare `from database import ...` (breaks `import web_app`; `models.py:8` regressed this before).

## No tests / lint / CI
- No test suite, formatter, typecheck, or workflows. Verify with `import web_app` + focused `uvicorn` smoke test.

## Gotchas
- Volume `/Volumes/Backup` auto-creates macOS AppleDouble `._*` files (also inside `.git/objects`, `__pycache__`). Clean with `find . -name '._*' -delete`. Do not commit them.
- `blog.db` (`._blog.db` too) and `media/` are not in `.gitignore` — avoid committing local DB/uploads.
- `schemas.py`: `PostResponse` redefines `PostBase.author: str` as `author: UserResponse`. Keep in mind when touching post serialization.
