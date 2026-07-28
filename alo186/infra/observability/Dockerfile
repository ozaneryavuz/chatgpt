FROM grafana/alloy:v1.18.0

COPY render.config.alloy /etc/alloy/config.alloy

ENTRYPOINT ["/bin/alloy"]
CMD ["run", "/etc/alloy/config.alloy", "--storage.path=/tmp/alloy"]
