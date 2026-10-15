"""CLI entrypoint: python -m app.scripts.seed [--force]"""

from __future__ import annotations

import argparse
import logging
import sys

from app.core.database import SessionLocal
from app.core.logging import configure_logging
from app.services.seed import seed_all


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed Bharat Yatra demo data")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Attempt to create any missing seed rows even if states exist",
    )
    args = parser.parse_args(argv)
    configure_logging(debug=True)
    logger = logging.getLogger("seed")

    session = SessionLocal()
    try:
        counts = seed_all(session, force=args.force)
        logger.info("Seed finished: %s", counts)
        return 0
    except Exception:
        session.rollback()
        logger.exception("Seed failed")
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
