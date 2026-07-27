from __future__ import annotations

import argparse
import logging
import time

from .db import SessionLocal
from .notifications import process_outbox
from .observability import configure_logging, configure_sentry
from .privacy import purge_due_data

logger = logging.getLogger(__name__)


def email_once(limit: int) -> dict[str, int]:
    with SessionLocal() as db:
        result = process_outbox(db, limit=limit)
    logger.info("email_outbox_processed %s", result)
    return result


def retention_once() -> dict[str, int]:
    with SessionLocal() as db:
        result = purge_due_data(db)
    logger.info("retention_processed %s", result)
    return result


def main() -> None:
    configure_logging()
    configure_sentry()
    parser = argparse.ArgumentParser(description="ALO186 background worker")
    parser.add_argument("command", choices=["email-once", "email-loop", "retention-once"])
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--interval", type=int, default=15)
    args = parser.parse_args()

    if args.command == "email-once":
        email_once(args.limit)
        return
    if args.command == "retention-once":
        retention_once()
        return
    while True:
        email_once(args.limit)
        time.sleep(max(2, args.interval))


if __name__ == "__main__":
    main()
