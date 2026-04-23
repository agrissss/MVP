"""Pydantic shēmas API atbildēm un pieprasījumiem."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field

from .models import DocType, DocStatus, RelationType, SectionLevel


class TopicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    topic: str


class RelatedDocOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    doc_type: DocType
    relation_type: RelationType
    official_url: str


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: str
    source: str
    doc_type: DocType
    title: str
    number: Optional[str] = None
    issuer: Optional[str] = None
    adopted_date: Optional[date] = None
    effective_date: Optional[date] = None
    status: DocStatus
    official_url: str
    summary: Optional[str] = None
    license: Optional[str] = None
    last_imported: datetime
    topics: List[str] = Field(default_factory=list)


class DocumentListOut(BaseModel):
    total: int
    items: List[DocumentOut]


class SectionOut(BaseModel):
    """Viena sekcija bez bērniem — atgriež plakanā sarakstā."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    parent_id: Optional[int] = None
    level: SectionLevel
    number: str
    path: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    anchor: Optional[str] = None
    deep_link: str  # pilnais URL uz likumi.lv ar anchor
    sort_order: int


class SectionTreeOut(SectionOut):
    """Sekcija ar bērniem — rekursīvi hierarhijai."""
    children: List["SectionTreeOut"] = Field(default_factory=list)


SectionTreeOut.model_rebuild()


class SectionHitOut(BaseModel):
    """Meklēšanas rezultāts sekcijas līmenī — satur arī dokumenta kontekstu."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    document_title: str
    document_number: Optional[str] = None
    document_type: DocType
    level: SectionLevel
    number: str
    path: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    deep_link: str
    breadcrumb: List[str] = Field(default_factory=list)
    # piem., ["Darba likums", "68. pants", "2. daļa"]


class SectionSearchOut(BaseModel):
    total: int
    items: List[SectionHitOut]


class TopicSiblingOut(BaseModel):
    """Minimāls dokumenta skats, ko rāda kategorijas sarakstā."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    doc_type: DocType
    title: str
    number: Optional[str] = None
    issuer: Optional[str] = None
    status: DocStatus


class TopicSiblingsGroupOut(BaseModel):
    """Grupa dokumentu, kas pieder vienai tēmai (bez paša pašreizējā dokumenta)."""
    topic: str
    total: int
    items: List[TopicSiblingOut] = Field(default_factory=list)


class DocumentDetailOut(DocumentOut):
    related: List[RelatedDocOut] = Field(default_factory=list)
    section_count: int = 0  # cik daudz sekciju pieejams (lai klients zina, vai radit TOC)
    topic_siblings: List[TopicSiblingsGroupOut] = Field(default_factory=list)


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    base_url: str
    license_notes: Optional[str] = None
    last_import_at: Optional[datetime] = None
    last_import_count: Optional[int] = None
    last_import_status: Optional[str] = None


class ImportResult(BaseModel):
    source: str
    status: str
    doc_count: int
    duration_sec: float
    error: Optional[str] = None
