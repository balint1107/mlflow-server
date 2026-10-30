#!/usr/bin/env bash
# Forward explicit server arguments, or use durable SQLite defaults for new installs.
set -euo pipefail
if [ "$#" -eq 0 ]; then
    set -- --host 0.0.0.0 --port 8080 --backend-store-uri sqlite:////mlruns/mlflow.db --artifacts-destination /mlartifacts
fi
exec mlflow server "$@"
