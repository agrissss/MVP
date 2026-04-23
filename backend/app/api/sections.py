"""Sekciju API — pantu/punktu hierarhija un meklēšana apakšpunktu līmenī."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Document, DocumentSection, SectionLevel
from ..schemas import (
    SectionOut,
    SectionTreeOut,
    SectionHitOut,
    SectionSearchOut,
)

router = APIRouter(prefix="/api", tags=["sections"])


def _deep_link(doc: Document, section: DocumentSection) -> str:
    if section.anchor:
        return f"{doc.official_url}#{section.anchor}"
    return doc.official_url


def _section_to_out(doc: Document, s: DocumentSection) -> SectionOut:
    return SectionOut(
        id=s.id,
        document_id=s.document_id,
        parent_id=s.parent_id,
        level=s.level,
        number=s.number,
        path=s.path,
        title=s.title,
        snippet=s.snippet,
        anchor=s.anchor,
        deep_link=_deep_link(doc, s),
        sort_order=s.sort_order,
    )


@router.get("/documents/{doc_id}/sections", response_model=List[SectionTreeOut])
def list_sections(doc_id: int, db: Session = Depends(get_db)):
    """Atgriež dokumenta sekcijas hierarhiskā kokā (TOC).

    Ja dokumentam nav sekciju, atgriež tukšu sarakstu — klients tādā
    gadījumā vienkārši nerāda TOC.
    """
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Dokuments nav atrasts")

    rows = db.execute(
        select(DocumentSection)
        .where(DocumentSection.document_id == doc_id)
        .order_by(DocumentSection.sort_order)
    ).scalars().all()

    if not rows:
        return []

    # Uzbūve hierarhiju map[parent_id] = list[children]
    by_parent: dict[Optional[int], list] = {}
    for r in rows:
        by_parent.setdefault(r.parent_id, []).append(r)

    def build(parent_id: Optional[int]) -> List[SectionTreeOut]:
        out: List[SectionTreeOut] = []
        for s in by_parent.get(parent_id, []):
            base = _section_to_out(doc, s)
            out.append(SectionTreeOut(
                **base.model_dump(),
                children=build(s.id),
            ))
        return out

    return build(None)


@router.get("/sections/search", response_model=SectionSearchOut)
def search_sections(
    db: Session = Depends(get_db),
    q: str = Query(..., min_length=2, description="Meklēšanas vaicājums"),
    doc_id: Optional[int] = Query(None, description="Ierobežot viena dokumenta ietvaros"),
    level: Optional[SectionLevel] = Query(None, description="Tikai attiecīgā līmeņa sekcijas"),
    limit: int = Query(30, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Meklē sekciju līmenī — pēc virsraksta, numura un fragmenta.

    Atgriež sekcijas ar dokumenta kontekstu (breadcrumb), lai lietotājs
    saprastu, kur katrs punkts atrodas.
    """
    like = f"%{q}%"
    conditions = [
        or_(
            DocumentSection.title.ilike(like),
            DocumentSection.snippet.ilike(like),
            DocumentSection.number.ilike(like),
            DocumentSection.path.ilike(like),
        )
    ]
    if doc_id is not None:
        conditions.append(DocumentSection.document_id == doc_id)
    if level is not None:
        conditions.append(DocumentSection.level == level)

    stmt = (
        select(DocumentSection)
        .where(*conditions)
        .order_by(DocumentSection.document_id, DocumentSection.sort_order)
    )
    count_stmt = select(func.count(DocumentSection.id)).where(*conditions)
    total = db.execute(count_stmt).scalar_one()

    stmt = stmt.limit(limit).offset(offset)
    rows = db.execute(stmt).scalars().all()

    # Iegūstam dokumentus
    doc_ids = list({r.document_id for r in rows})
    docs_by_id: dict[int, Document] = {}
    if doc_ids:
        docs = db.execute(
            select(Document).where(Document.id.in_(doc_ids))
        ).scalars().all()
        docs_by_id = {d.id: d for d in docs}

    # Breadcrumb: loupes hierarhiju caur parent_id
    all_for_docs = {}
    if doc_ids:
        parents = db.execute(
            select(DocumentSection).where(DocumentSection.document_id.in_(doc_ids))
        ).scalars().all()
        all_for_docs = {p.id: p for p in parents}

    items: list[SectionHitOut] = []
    for r in rows:
        doc = docs_by_id.get(r.document_id)
        if not doc:
            continue
        crumbs: list[str] = [doc.title]
        chain: list[DocumentSection] = []
        cur: Optional[DocumentSection] = r
        while cur is not None:
            chain.append(cur)
            cur = all_for_docs.get(cur.parent_id) if cur.parent_id else None
        for s in reversed(chain):
            label = s.number
            if s.level == SectionLevel.PANTS:
                label = f"{s.number}. pants"
            elif s.level == SectionLevel.DALA:
                label = f"{s.number}. daļa"
            elif s.level == SectionLevel.PUNKTS:
                label = f"{s.number}. punkts"
            elif s.level == SectionLevel.APAKSPUNKTS:
                label = f"{s.number}. apakšpunkts"
            elif s.level == SectionLevel.NODALA:
                label = f"{s.number}. nodaļa"
            if s.title:
                label = f"{label} — {s.title}"
            crumbs.append(label)

        items.append(SectionHitOut(
            id=r.id,
            document_id=r.document_id,
            document_title=doc.title,
            document_number=doc.number,
            document_type=doc.doc_type,
            level=r.level,
            number=r.number,
            path=r.path,
            title=r.title,
            snippet=r.snippet,
            deep_link=_deep_link(doc, r),
            breadcrumb=crumbs,
        ))

    return SectionSearchOut(total=total, items=items)
