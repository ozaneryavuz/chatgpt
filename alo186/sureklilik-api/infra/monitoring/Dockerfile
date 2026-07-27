FROM grafana/alloy:v1.16.1

COPY infra/monitoring/config.alloy /etc/alloy/config.alloy

ENTRYPOINT ["/bin/alloy"]
CMD ["run", "/etc/alloy/config.alloy", "--storage.path=/tmp/alloy"]
