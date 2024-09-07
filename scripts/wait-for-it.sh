#!/usr/bin/env bash

# Use this to wait for a service to be available.
# Usage: wait-for-it.sh host:port [-t timeout] [-- command args]
# Example: wait-for-it.sh db:5432 -- python my_app.py

TIMEOUT=15
WAIT_FOR=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -t)
      TIMEOUT="$2"
      shift 2
      ;;
    *)
      WAIT_FOR="$1"
      shift
      ;;
  esac
done

if [[ -z "$WAIT_FOR" ]]; then
  echo "Usage: wait-for-it.sh host:port [-t timeout] [-- command args]"
  exit 1
fi

HOST=$(echo "$WAIT_FOR" | cut -d: -f1)
PORT=$(echo "$WAIT_FOR" | cut -d: -f2)

# Wait for the host:port to be available
echo "Waiting for $WAIT_FOR..."
for ((i=0; i<TIMEOUT; i++)); do
  nc -z "$HOST" "$PORT" && break
  sleep 1
done

# Check if the service is up
if ! nc -z "$HOST" "$PORT"; then
  echo "Timeout waiting for $WAIT_FOR"
  exit 1
fi

echo "$WAIT_FOR is up!"
