#!/bin/bash
set -e

echo "Waiting for database ready status..."
python -c "
import socket, time
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        s.connect(('${POSTGRES_HOST:-postgres}', ${POSTGRES_PORT:-5432}))
        s.close()
        break
    except Exception:
        time.sleep(1)
"

echo "Database operational. Starting application..."
exec "$@"
