# Home-network deployment

Fork of pranaychandekar/mlflow-server; imports the previously uncommitted server-local
Dockerfile/start script. The runtime is now MLflow 3.17.2. Build via the sibling
home-automation/compose.server-local.yml, which supplies the existing paths and args.
New standalone installs default to SQLite; the existing deployment explicitly keeps
its file store with MLFLOW_ALLOW_FILE_STORE=true. This is a compatibility bridge,
not a database migration. Keep both mlruns and mlartifacts, including files inside
mlruns: experiment artifact locations can refer there too. Preserve absolute paths.

Before upgrading: stop the tracking server, archive both directories and save the
old image ID plus Compose file. Start an isolated copy on loopback port 18080 and
compare experiment/run IDs and artifact reads, then activate the new image. Keep
nginx/Authelia and the host backend firewall; do not expose port 8080 publicly.
Backups must include all file-store metadata and artifacts; with SQLite use its
online backup API or stop the server. Restore into empty directories with original
ownership and paths before starting the same pinned version. Roll back using the
saved image and pre-upgrade data, not a newer database opened with an old runtime.

A future SQLite migration should use mlflow migrate-filestore against a copy and
compare IDs/timestamps before switching. It is deliberately separate from this update.

Validation on 2026-10-30: isolated snapshot matched all 12 experiments and 311 runs,
ignoring only the newly added default workspace field. A sampled 1618-byte artifact
matched exactly. The running server was upgraded to 3.17.2 with the original file
store explicitly retained, then its metadata was compared again. Backup/image rollback
are under /home/balint/backups/mlflow-before-3.17.2-20261030 on server-local.
Use python3 docs/verify_metadata.py OLD_BASE NEW_BASE for a read-only comparison.
