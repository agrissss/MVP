"""API galapunkti avotiem un tēmām (metadati UI darbam)."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Source, DocumentTopic, Document, DocType, DocStatus
from ..schemas import SourceOut

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/sources", response_model=List[SourceOut])
def list_sources(db: Session = Depends(get_db)):
    """Atgriež visus reģistrētos avotus ar to audita datiem."""
    return db.execute(select(Source).order_by(Source.code)).scalars().all()


@router.get("/topics")
def list_topics(db: Session = Depends(get_db)):
    """Atgriež visu tēmu sarakstu ar dokumentu skaitiem."""
    stmt = (
        select(DocumentTopic.topic, func.count(DocumentTopic.id))
        .group_by(DocumentTopic.topic)
        .order_by(DocumentTopic.topic)
    )
    rows = db.execute(stmt).all()
    return [{"topic": t, "count": c} for t, c in rows]


@router.get("/doc-types")
def list_doc_types():
    """Visu atbalstīto dokumentu veidu saraksts."""
    return [{"value": t.value, "label": _LABELS_DOC_TYPE.get(t.value, t.value)}
            for t in DocType]


@router.get("/statuses")
def list_statuses():
    """Visu dokumentu statusu saraksts."""
    return [{"value": s.value, "label": _LABELS_STATUS.get(s.value, s.value)}
            for s in DocStatus]


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    """Dashboard statistika."""
    total = db.execute(select(func.count(Document.id))).scalar_one()
    by_source = db.execute(
        select(Document.source, func.count(Document.id)).group_by(Document.source)
    ).all()
    by_type = db.execute(
        select(Document.doc_type, func.count(Document.id)).group_by(Document.doc_type)
    ).all()
    return {
        "total": total,
        "by_source": [{"source": s, "count": c} for s, c in by_source],
        "by_type": [{"doc_type": t.value if hasattr(t, "value") else t, "count": c}
                    for t, c in by_type],
    }


_LABELS_DOC_TYPE = {
    "likums": "Likums",
    "mk_noteikumi": "MK noteikumi",
    "instrukcija": "Instrukcija",
    "vadlinijas": "Vadlīnijas",
    "datu_kopa": "Datu kopa",
    "pazinojums": "Paziņojums",
    "cits": "Cits",
}

_LABELS_STATUS = {
    "speka": "Spēkā",
    "zaudejis_speku": "Zaudējis spēku",
    "grozits": "Grozīts",
    "nezinams": "Nezināms",
}
