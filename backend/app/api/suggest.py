"""Ātrie meklēšanas ieteikumi (typeahead).

Atgriež īsu, apvienotu sarakstu ar dokumentu, sekciju un tēmu atbilstībām,
lai frontend varētu rādīt nolaižamos ieteikumus lietotājam rakstot.
"""
from __future__ import annotations

from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Document, DocumentSection, DocumentTopic

router = APIRouter(prefix="/api/suggest", tags=["suggest"])


class DocumentSuggestion(BaseModel):
    kind: str = "document"
    id: int
    title: str
    doc_type: str
    number: Optional[str] = None
    issuer: Optional[str] = None


class SectionSuggestion(BaseModel):
    kind: str = "section"
    id: int
    document_id: int
    document_title: str
    level: str
    number: str
    title: Optional[str] = None
    snippet: Optional[str] = None


class TopicSuggestion(BaseModel):
    kind: str = "topic"
    topic: str
    doc_count: int


class SuggestOut(BaseModel):
    q: str
    documents: List[DocumentSuggestion]
    sections: List[SectionSuggestion]
    topics: List[TopicSuggestion]


@router.get("", response_model=SuggestOut)
def suggest(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
):
    """Atgriež līdz `limit` ierakstiem katrā kategorijā (dokumenti / sekcijas / tēmas)."""
    q_norm = q.strip()
    if not q_norm:
        return SuggestOut(q=q, documents=[], sections=[], topics=[])

    like = f"%{q_norm}%"

    # --- Dokumenti ---
    doc_stmt = (
        select(Document)
        .where(
            or_(
                Document.title.ilike(like),
                Document.number.ilike(like),
                Document.issuer.ilike(like),
                Document.summary.ilike(like),
            )
        )
        .order_by(Document.last_imported.desc())
        .limit(limit)
    )
    doc_rows = db.execute(doc_stmt).scalars().all()
    documents = [
        DocumentSuggestion(
            id=d.id,
            title=d.title,
            doc_type=d.doc_type.value if hasattr(d.doc_type, "value") else str(d.doc_type),
            number=d.number,
            issuer=d.issuer,
        )
        for d in doc_rows
    ]

    # --- Sekcijas (panti/punkti) ---
    sec_stmt = (
        select(DocumentSection, Document.title)
        .join(Document, Document.id == DocumentSection.document_id)
        .where(
            or_(
                DocumentSection.title.ilike(like),
                DocumentSection.snippet.ilike(like),
                DocumentSection.number.ilike(like),
                DocumentSection.path.ilike(like),
            )
        )
        .order_by(DocumentSection.document_id, DocumentSection.sort_order)
        .limit(limit)
    )
    sections: List[SectionSuggestion] = []
    for sec, doc_title in db.execute(sec_stmt).all():
        sections.append(SectionSuggestion(
            id=sec.id,
            document_id=sec.document_id,
            document_title=doc_title,
            level=sec.level.value if hasattr(sec.level, "value") else str(sec.level),
            number=sec.number,
            title=sec.title,
            snippet=sec.snippet,
        ))

    # --- Tēmas ---
    # Izšķirīgās tēmas ar dokumentu skaitu; filtrē pēc tēmas koda vai cilvēkam lasāma nosaukuma
    # (LV nosaukumu atbilstību neveicam backend; frontend to atfiltrē, ja nepieciešams)
    q_lower = q_norm.lower()
    topic_stmt = (
        select(DocumentTopic.topic, func.count(DocumentTopic.document_id))
        .group_by(DocumentTopic.topic)
        .order_by(func.count(DocumentTopic.document_id).desc())
    )
    topic_rows = db.execute(topic_stmt).all()
    topics: List[TopicSuggestion] = []
    for topic, cnt in topic_rows:
        if q_lower in topic.lower():
            topics.append(TopicSuggestion(topic=topic, doc_count=int(cnt)))
        if len(topics) >= limit:
            break

    return SuggestOut(q=q_norm, documents=documents, sections=sections, topics=topics)
