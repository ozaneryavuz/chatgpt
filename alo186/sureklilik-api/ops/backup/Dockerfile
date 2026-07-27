FROM postgres:16-alpine

RUN apk add --no-cache bash ca-certificates restic tzdata

COPY ops/backup/backup_to_r2.sh /usr/local/bin/backup-to-r2
COPY ops/backup/verify_restore.sh /usr/local/bin/verify-restore
RUN chmod 0755 /usr/local/bin/backup-to-r2 /usr/local/bin/verify-restore

USER postgres
ENTRYPOINT []
CMD ["/usr/local/bin/backup-to-r2"]
