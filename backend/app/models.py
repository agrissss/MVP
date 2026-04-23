"""SQLAlchemy datu modelis.

Skat. docs/datu-modelis.md sīkākam aprakstam.
"""
from __future__ import annotations

import enum
from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import (
    String, Integer, Text, DateTime, Date, Enum, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class DocType(str, enum.Enum):
    LIKUMS = "likums"
    MK_NOTEIKUMI = "mk_noteikumi"
    INSTRUKCIJA = "instrukcija"
    VADLINIJAS = "vadlinijas"
    DATU_KOPA = "datu_kopa"
    PAZINOJUMS = "pazinojums"
    CITS = "cits"


class DocStatus(str, enum.Enum):
    SPEKA = "speka"
    ZAUDEJIS_SPEKU = "zaudejis_speku"
    GROZITS = "grozits"
    NEZINAMS = "nezinams"


class RelationType(str, enum.Enum):
    IMPLEMENTS = "implements"     # piemēro (MK noteikumi piemēro likumu)
    AMENDS = "amends"             # groza
    REPLACES = "replaces"         # aizvieto
    RELATED = "related"           # saistīts
    REFERENCES = "references"     # atsaucas


class SectionLevel(str, enum.Enum):
    """Hierarhijas līmeņi Latvijas normatīvajos aktos."""
    SADALA = "sadala"          # Sadaļa (ļoti reti, dažos kodeksos)
    NODALA = "nodala"          # Nodaļa
    PANTS = "pants"            # Pants (likumos) / punkts (MK noteikumos)
    DALA = "dala"              # Daļa (panta daļa)
    PUNKTS = "punkts"          # Punkts
    APAKSPUNKTS = "apakspunkts"  # Apakšpunkts


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_source_external_id"),
        Index("ix_documents_doc_type", "doc_type"),
        Index("ix_documents_status", "status"),
        Index("ix_documents_issuer", "issuer"),
        Index("ix_documents_adopted_date", "adopted_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String(200), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    doc_type: Mapped[DocType] = mapped_column(Enum(DocType), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    number: Mapped[Optional[str]] = mapped_column(String(100))
    issuer: Mapped[Optional[str]] = mapped_column(String(200))
    adopted_date: Mapped[Optional[date]] = mapped_column(Date)
    effective_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[DocStatus] = mapped_column(Enum(DocStatus), default=DocStatus.NEZINAMS, nullable=False)
    official_url: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    license: Mapped[Optional[str]] = mapped_column(String(200))
    last_imported: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    topics: Mapped[List["DocumentTopic"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
    relations_from: Mapped[List["DocumentRelation"]] = relationship(
        foreign_keys="DocumentRelation.from_id",
        back_populates="from_doc",
        cascade="all, delete-orphan",
    )
    relations_to: Mapped[List["DocumentRelation"]] = relationship(
        foreign_keys="DocumentRelation.to_id",
        back_populates="to_doc",
    )
    sections: Mapped[List["DocumentSection"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentSection.sort_order",
    )


class DocumentTopic(Base):
    __tablename__ = "document_topics"
    __table_args__ = (
        UniqueConstraint("document_id", "topic", name="uq_doc_topic"),
        Index("ix_document_topics_topic", "topic"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    topic: Mapped[str] = mapped_column(String(50), nullable=False)

    document: Mapped[Document] = relationship(back_populates="topics")


class DocumentRelation(Base):
    __tablename__ = "document_relations"
    __table_args__ = (
        UniqueConstraint("from_id", "to_id", "relation_type", name="uq_relation"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    to_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    relation_type: Mapped[RelationType] = mapped_column(Enum(RelationType), nullable=False)

    from_doc: Mapped[Document] = relationship(foreign_keys=[from_id], back_populates="relations_from")
    to_doc: Mapped[Document] = relationship(foreign_keys=[to_id], back_populates="relations_to")


class DocumentSection(Base):
    """Dokumenta hierarhiska sekcija (pants / daļa / punkts / apakšpunkts).

    Glabā TIKAI strukturālos metadatus un īsu ievada fragmentu (max 300 rakstz.)
    priekš meklēšanas. Pilno tekstu lietotājs lasa likumi.lv pēc deep-link klikšķa.
    """
    __tablename__ = "document_sections"
    __table_args__ = (
        Index("ix_sections_document_id", "document_id"),
        Index("ix_sections_parent_id", "parent_id"),
        Index("ix_sections_path", "path"),
        Index("ix_sections_level", "level"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("document_sections.id", ondelete="CASCADE")
    )
    level: Mapped[SectionLevel] = mapped_column(Enum(SectionLevel), nullable=False)
    number: Mapped[str] = mapped_column(String(50), nullable=False)
    # "5" / "5.3" / "5.3.2" / "IV" — hierarhiskā path priekš ātras atlases un kārtošanas
    path: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500))
    # Īss fragments priekš meklēšanas priekšskatījuma — max 300 rakstzīmes
    snippet: Mapped[Optional[str]] = mapped_column(String(400))
    # HTML anchor uz likumi.lv (piem., "p5" vai "p5.3")
    anchor: Mapped[Optional[str]] = mapped_column(String(50))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    document: Mapped[Document] = relationship(back_populates="sections")
    parent: Mapped[Optional["DocumentSection"]] = relationship(
        remote_side="DocumentSection.id", back_populates="children"
    )
    children: Mapped[List["DocumentSection"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="DocumentSection.sort_order",
    )

    def deep_link_url(self, base_url: str) -> str:
        """Salika likumi.lv URL ar anchor, ja pieejams."""
        if self.anchor:
            return f"{base_url}#{self.anchor}"
        return base_url


class Source(Base):
    __tablename__ = "sources"

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    base_url: Mapped[str] = mapped_column(Text, nullable=False)
    license_notes: Mapped[Optional[str]] = mapped_column(Text)
    last_import_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_import_count: Mapped[Optional[int]] = mapped_column(Integer)
    last_import_status: Mapped[Optional[str]] = mapped_column(String(20))
    last_import_error: Mapped[Optional[str]] = mapped_column(Text)


class ImportRun(Base):
    __tablename__ = "import_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="running", nullable=False)
    doc_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
