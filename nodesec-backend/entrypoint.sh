#!/bin/sh
# entrypoint.sh — Run Alembic migrations then start the app.
# This ensures the DB schema is always current on every container start.
set -e

echo "⟳ Waiting for database to be ready..."
python -c "
import asyncio, asyncpg, os, time

async def wait_for_db():
    url = os.environ.get('DATABASE_URL', '').replace('postgresql+asyncpg://', '')
    for attempt in range(30):
        try:
            conn = await asyncpg.connect('postgresql://' + url)
            await conn.close()
            print('✓ Database is ready')
            return
        except Exception as e:
            print(f'  Attempt {attempt+1}/30: {e}')
            time.sleep(2)
    raise RuntimeError('Database not reachable after 60s')

asyncio.run(wait_for_db())
"

echo "⟳ Running Alembic migrations..."
alembic upgrade head
echo "✓ Migrations complete"

echo "▶ Starting uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
