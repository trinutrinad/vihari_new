"""Bootstrap a local SQLite database (no Docker/Postgres required).

Usage (from backend/ with venv active):

    python -m app.scripts.init_local

Requires DATABASE_URL to start with sqlite, e.g. in repo-root .env:

    DATABASE_URL=sqlite:///./bharatyatra.db
"""

from __future__ import annotations

import logging
import sys

from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine, init_models
from app.core.logging import configure_logging
from app.services.seed import seed_all


def main() -> int:
    configure_logging(debug=True)
    logger = logging.getLogger("init_local")
    settings = get_settings()

    if not settings.database_url.startswith("sqlite"):
        logger.error(
            "DATABASE_URL is not sqlite (%s). "
            "For Docker-free local mode set:\n"
            "  DATABASE_URL=sqlite:///./bharatyatra.db",
            settings.database_url,
        )
        return 1

    init_models()
    Base.metadata.create_all(bind=engine)
    logger.info("Created tables in %s", settings.database_url)

    session = SessionLocal()
    try:
        counts = seed_all(session, force=True)
        logger.info("Seed finished: %s", counts)
        return 0
    except Exception:
        session.rollback()
        logger.exception("Local init failed")
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
