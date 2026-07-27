FROM postgres:16-alpine

RUN apk add --no-cache ca-certificates restic tzdata \
    && addgroup -S backup \
    && adduser -S -G backup -h /home/backup backup \
    && mkdir -p /opt/alo186 /work /home/backup/.cache/restic \
    && chown -R backup:backup /opt/alo186 /work /home/backup

COPY --chown=backup:backup ops/backup/backup_to_r2.sh /opt/alo186/backup_to_r2.sh
COPY --chown=backup:backup ops/backup/restore_verify.sh /opt/alo186/restore_verify.sh
RUN chmod 0755 /opt/alo186/*.sh

USER backup
WORKDIR /work

ENTRYPOINT ["/opt/alo186/backup_to_r2.sh"]
