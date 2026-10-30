FROM ghcr.io/mlflow/mlflow:v3.17.2@sha256:2cc40b3208991940d824d04f339833a0b69507569012aa5ec545690608602fc0
WORKDIR /opt/deployment
COPY --chmod=0755 start-server.sh ./
ENTRYPOINT ["/opt/deployment/start-server.sh"]
