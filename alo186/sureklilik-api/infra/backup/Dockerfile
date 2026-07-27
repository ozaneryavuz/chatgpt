FROM postgres:16-alpine

RUN apk add --no-cache \
    aws-cli \
    bash \
    ca-certificates \
    coreutils \
    curl \
    restic \
    tzdata

WORKDIR /opt/alo186
COPY infra/backup/run_backup.sh /opt/alo186/run_backup.sh
COPY infra/backup/restore_verify.sh /opt/alo186/restore_verify.sh
RUN chmod 0755 /opt/alo186/run_backup.sh /opt/alo186/restore_verify.sh \
    && chown -R postgres:postgres /opt/alo186

USER postgres
ENTRYPOINT []
CMD ["/opt/alo186/run_backup.sh"]
