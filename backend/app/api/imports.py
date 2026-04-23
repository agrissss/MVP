"""Importa API — palaiž avotu adapteru un saglabā rezultātu."""
from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from ..adapters import get_adapter, REGISTRY
from ..database import get_db
from ..models import (
    Document, DocumentTopic, DocumentSection, SectionLevel,
    Source, ImportRun,
)
from ..normalizer import classify_doc_type, classify_status, guess_topics
from ..schemas import ImportResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/import", tags=["import"])


@router.post("/{source}", response_model=ImportResult)
def run_import(
    source: str,
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=500),
    query: Optional[str] = None,
):
    """Palaiž importu no norādītā avota."""
    if source not in REGISTRY:
        raise HTTPException(status_code=404, detail=f"Nav reģistrēts avots: {source}")

    adapter = get_adapter(source)
    meta = adapter.get_source_meta()

    run = ImportRun(source=source, started_at=datetime.utcnow(), status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    src = db.get(Source, source)
    if not src:
        src = Source(code=meta.code, name=meta.name, base_url=meta.base_url,
                     license_notes=meta.license_notes)
        db.add(src)

    t0 = time.monotonic()
    count = 0
    error: Optional[str] = None

    try:
        for norm in adapter.fetch_batch(limit=limit, query=query):
            _upsert_document(db, norm)
            count += 1
            if count % 20 == 0:
                db.commit()
        db.commit()
        run.status = "ok"
    except Exception as e:  # noqa: BLE001
        logger.exception("Importa kļūda avotam %s", source)
        run.status = "failed"
        error = str(e)
        db.rollback()

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

    return ImportResult(
        source=source,
        status=run.status,
        doc_count=count,
        duration_sec=round(duration, 2),
        error=error,
    )


def _upsert_document(db: Session, norm) -> Document:
    """Ievieto vai atjaunina dokumentu pēc (source, external_id)."""
    existing = db.execute(
        select(Document).where(
            Document.source == norm.source,
            Document.external_id == norm.external_id,
        )
    ).scalar_one_or_none()

    doc_type_enum = classify_doc_type(norm.doc_type)
    status_enum = classify_status(norm.status)
    now = datetime.utcnow()

    if existing:
        existing.title = norm.title
        existing.number = norm.number
        existing.issuer = norm.issuer
        existing.doc_type = doc_type_enum
        existing.status = status_enum
        existing.adopted_date = norm.adopted_date
        existing.effective_date = norm.effective_date
        existing.official_url = norm.official_url
        existing.summary = norm.summary
        existing.license = norm.license
        existing.last_imported = now
        existing.updated_at = now
        doc = existing
    else:
        doc = Document(
            external_id=norm.external_id,
            source=norm.source,
            doc_type=doc_type_enum,
            title=norm.title,
            number=norm.number,
            issuer=norm.issuer,
            adopted_date=norm.adopted_date,
            effective_date=norm.effective_date,
            status=status_enum,
            official_url=norm.official_url,
            summary=norm.summary,
            license=norm.license,
            last_imported=now,
            created_at=now,
            updated_at=now,
        )
        db.add(doc)
        db.flush()

    # Topics
    guessed = set(guess_topics(norm.title, norm.issuer))
    for t in norm.topics:
        tl = (t or "").lower()
        for our_topic in (
            "nodokli", "gramatvediba", "darba_tiesibas", "logistika", "transports",
            "muita", "e_komercija", "datu_aizsardziba", "komercdarbiba", "publiskie_iepirkumi"
        ):
            if our_topic.replace("_", "") in tl.replace(" ", "").replace("_", ""):
                guessed.add(our_topic)

    doc.topics.clear()
    db.flush()
    for topic in guessed:
        db.add(DocumentTopic(document_id=doc.id, topic=topic))

    # Sections — upsert only if adapter returned any
    sections = getattr(norm, "sections", None) or []
    if sections:
        _upsert_sections(db, doc.id, sections)

    return doc


def _upsert_sections(db: Session, document_id: int, sections) -> None:
    """Pārraksta dokumenta sekcijas ar jauno komplektu.

    Stratēģija: dzēšam veco komplektu un pievienojam jauno. Tas ir
    vienkāršāk nekā katras sekcijas atrašana — strukturālas izmaiņas
    pašas par sevi ir reti, un dzēšanas izmaksas ir zemas.
    """
    db.execute(
        delete(DocumentSection).where(DocumentSection.document_id == document_id)
    )
    db.flush()

    def _add_tree(nodes, parent_id, order_offset=0):
        next_order = order_offset
        for node in nodes:
            level_val = node.level if isinstance(node.level, str) else str(node.level)
            try:
                level_enum = SectionLevel(level_val)
            except ValueError:
                level_enum = SectionLevel.PUNKTS
            row = DocumentSection(
                document_id=document_id,
                parent_id=parent_id,
                level=level_enum,
                number=str(node.number)[:50],
                path=str(node.path)[:100],
                title=(node.title or None),
                snippet=(node.snippet or None),
                anchor=(node.anchor or None),
                sort_order=next_order,
            )
            db.add(row)
            db.flush()
            next_order += 1
            if node.children:
                next_order = _add_tree(node.children, row.id, next_order)
        return next_order

    _add_tree(sections, None, 0)
