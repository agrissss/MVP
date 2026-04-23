"""CLI importa palaišanas rīks.

Izmantošana:
    python import_runner.py --source data_gov_lv --limit 50
    python import_runner.py --source likumi_lv --limit 10
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime

from app.adapters import get_adapter, REGISTRY
from app.database import init_db, SessionLocal
from app.models import Source, ImportRun
from app.api.imports import _upsert_document

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description="Importē dokumentus no oficiālā avota.")
    parser.add_argument("--source", required=True, choices=sorted(REGISTRY.keys()),
                        help="Avota kods")
    parser.add_argument("--limit", type=int, default=50, help="Maksimālais dokumentu skaits")
    parser.add_argument("--query", default=None, help="Meklēšanas vaicājums (atkarīgs no avota)")
    args = parser.parse_args()

    init_db()

    adapter = get_adapter(args.source)
    meta = adapter.get_source_meta()

    db = SessionLocal()
    try:
        run = ImportRun(source=args.source, started_at=datetime.utcnow(), status="running")
        db.add(run)
        db.commit()
        db.refresh(run)

        src = db.get(Source, args.source)
        if not src:
            src = Source(code=meta.code, name=meta.name, base_url=meta.base_url,
                         license_notes=meta.license_notes)
            db.add(src)
            db.commit()

        t0 = time.monotonic()
        count = 0
        try:
            for norm in adapter.fetch_batch(limit=args.limit, query=args.query):
                _upsert_document(db, norm)
                count += 1
                if count % 20 == 0:
                    db.commit()
                    logger.info("  … saglabāti %d ieraksti", count)
            db.commit()
            run.status = "ok"
            error = None
        except Exception as e:  # noqa: BLE001
            logger.exception("Importa kļūda")
            db.rollback()
            run.status = "failed"
            error = str(e)

        duration = time.monotonic() - t0
        run.finished_at = datetime.utcnow()
        run.doc_count = count
        run.error_message = error

        src.last_import_at = run.finished_at
        src.last_import_count = count
        src.last_import_status = run.status
        src.last_import_error = error

        db.add(run)
        db.add(src)
        db.commit()

        logger.info("Pabeigts: avots=%s, count=%d, status=%s, ilgums=%.2fs",
                    args.source, count, run.status, duration)
        return 0 if run.status == "ok" else 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
