#!/bin/sh
set -e

echo "[entrypoint] Waiting for database connection..."
python -c "
import time, pymysql, os
host = os.getenv('MYSQL_SERVER', 'mysql')
port = int(os.getenv('MYSQL_PORT', '3306'))
user = os.getenv('MYSQL_USER', 'root')
pwd = os.getenv('MYSQL_PASSWORD', 'secret')
db = os.getenv('MYSQL_DB', 'word_intelligence')

for i in range(30):
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=pwd, connect_timeout=3)
        with conn.cursor() as cur:
            cur.execute(f'CREATE DATABASE IF NOT EXISTS \`{db}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;')
        conn.close()
        print('[entrypoint] Database server is ready.')
        break
    except Exception as e:
        print(f'[entrypoint] DB connection attempt {i+1}/30 failed: {e}. Retrying in 2s...')
        time.sleep(2)
"

echo "[entrypoint] Running database schema migrations (Alembic)..."
alembic upgrade head || echo "[entrypoint] Warning: Alembic migration encountered an error or already up to date."

echo "[entrypoint] Starting Word Intelligence backend ASGI service..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
