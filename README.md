uv run uvicorn web_app:app --reload

psql postgres -c "CREATE USER bloguser WITH PASSWORD 'blogpass';"
createdb blog -O bloguser
psql blog -U bloguser
\dt 查看表格
\d 表格

scripts/alembic.sh upgrade head
scripts/alembic.sh current
scripts/alembic.sh revision --autogenerate -m "add column"