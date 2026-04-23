"""Dokumentu API galapunkti."""
from __future__ import annotations

from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Document, DocumentTopic, DocumentRelation, DocumentSection, DocType, DocStatus
from ..schemas import (
    DocumentOut, DocumentListOut, DocumentDetailOut, RelatedDocOut,
    TopicSiblingOut, TopicSiblingsGroupOut,
)

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _to_out(doc: Document) -> DocumentOut:
    return DocumentOut(
        id=doc.id,
        external_id=doc.external_id,
        source=doc.source,
        doc_type=doc.doc_type,
        title=doc.title,
        number=doc.number,
        issuer=doc.issuer,
        adopted_date=doc.adopted_date,
        effective_date=doc.effective_date,
        status=doc.status,
        official_url=doc.official_url,
        summary=doc.summary,
        license=doc.license,
        last_imported=doc.last_imported,
        topics=[t.topic for t in doc.topics],
    )


def _topic_siblings(
    db: Session, doc_id: int, topics: List[str], per_topic_limit: int = 8
) -> List[TopicSiblingsGroupOut]:
    """Atgriež citus dokumentus, kas pieder tām pašām tēmām, grupētus pēc tēmas."""
    out: List[TopicSiblingsGroupOut] = []
    seen_ids: set[int] = {doc_id}
    for topic in topics:
        ids_sub = select(DocumentTopic.document_id).where(DocumentTopic.topic == topic)
        total = db.execute(
            select(func.count(Document.id)).where(
                Document.id.in_(ids_sub), Document.id != doc_id
            )
        ).scalar_one()
        stmt = (
            select(Document)
            .where(Document.id.in_(ids_sub), Document.id != doc_id)
            .order_by(Document.adopted_date.desc().nullslast(), Document.last_imported.desc())
            .limit(per_topic_limit)
        )
        rows = db.execute(stmt).scalars().all()
        items: List[TopicSiblingOut] = []
        for d in rows:
            if d.id in seen_ids:
                continue
            seen_ids.add(d.id)
            items.append(TopicSiblingOut(
                id=d.id,
                doc_type=d.doc_type,
                title=d.title,
                number=d.number,
                issuer=d.issuer,
                status=d.status,
            ))
        if items:
            out.append(TopicSiblingsGroupOut(topic=topic, total=total, items=items))
    return out


def _related_for(db: Session, doc_id: int) -> List[RelatedDocOut]:
    out: List[RelatedDocOut] = []
    stmt = select(DocumentRelation).where(
        or_(DocumentRelation.from_id == doc_id, DocumentRelation.to_id == doc_id)
    )
    for rel in db.execute(stmt).scalars().all():
        other_id = rel.to_id if rel.from_id == doc_id else rel.from_id
        target = db.get(Document, other_id)
        if target is not None:
            out.append(RelatedDocOut(
                id=target.id,
                title=target.title,
                doc_type=target.doc_type,
                relation_type=rel.relation_type,
                official_url=target.official_url,
            ))
    return out


@router.get("", response_model=DocumentListOut)
def list_documents(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Meklēšanas vaicājums"),
    source: Optional[str] = None,
    doc_type: Optional[DocType] = None,
    status: Optional[DocStatus] = None,
    topic: Optional[str] = None,
    issuer: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Atgriež dokumentu sarakstu ar filtriem."""
    stmt = select(Document).options(selectinload(Document.topics))
    count_stmt = select(func.count(Document.id))

    conditions = []
    if q:
        like = f"%{q}%"
        conditions.append(or_(
            Document.title.ilike(like),
            Document.number.ilike(like),
            Document.issuer.ilike(like),
            Document.summary.ilike(like),
        ))
    if source:
        conditions.append(Document.source == source)
    if doc_type:
        conditions.append(Document.doc_type == doc_type)
    if status:
        conditions.append(Document.status == status)
    if issuer:
        conditions.append(Document.issuer.ilike(f"%{issuer}%"))
    if date_from:
        conditions.append(Document.adopted_date >= date_from)
    if date_to:
        conditions.append(Document.adopted_date <= date_to)
    if topic:
        sub = select(DocumentTopic.document_id).where(DocumentTopic.topic == topic)
        conditions.append(Document.id.in_(sub))

    if conditions:
        stmt = stmt.where(*conditions)
        count_stmt = count_stmt.where(*conditions)

    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(Document.last_imported.desc()).limit(limit).offset(offset)
    items = db.execute(stmt).scalars().all()

    return DocumentListOut(total=total, items=[_to_out(d) for d in items])


@router.get("/{doc_id}", response_model=DocumentDetailOut)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    """Atgriež viena dokumenta pilnu kartīti ar saistītajiem dokumentiem."""
    doc = db.get(Document, doc_id, options=[selectinload(Document.topics)])
    if not doc:
        raise HTTPException(status_code=404, detail="Dokuments nav atrasts")

    base = _to_out(doc)
    related = _related_for(db, doc_id)
    section_count = db.execute(
        select(func.count(DocumentSection.id)).where(DocumentSection.document_id == doc_id)
    ).scalar_one()
    topic_siblings = _topic_siblings(db, doc_id, [t.topic for t in doc.topics])
    return DocumentDetailOut(
        **base.model_dump(),
        related=related,
        section_count=section_count,
        topic_siblings=topic_siblings,
    )
