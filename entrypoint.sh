#!/usr/bin/env sh

echo "                                                 ";
echo "______                   _                     _ ";
echo "|  ___|                 | |                   | |";
echo "| |_ __ _ _ __ _ __ ___ | |__   __ _ _ __   __| |";
echo "|  _/ _\` | '__| '_ \` _ \| '_ \ / _\` | '_ \ / _\` |";
echo "| || (_| | |  | | | | | | | | | (_| | | | | (_| |";
echo "\_| \__,_|_|  |_| |_| |_|_| |_|\__,_|_| |_|\__,_|";
echo "                                                 ";

echo "=========== Running Alembic Migrations =========="
uv run alembic upgrade head

echo "=========== Farmhand service started ============"
uv run uvicorn main:app --host 0.0.0.0 --port 8000
