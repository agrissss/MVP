"""Avota adaptera bāzes interfeiss un kopīgie datu strukti."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Iterable, Optional


@dataclass
class NormalizedSection:
    """Viena hierarhiska sekcija (pants / daļa / punkts / apakšpunkts).

    Glabājam tikai strukturālos metadatus un īsu fragmentu — pilno
    tekstu lietotājs lasa avota vietnē (likumi.lv) ar deep-link.
    """
    level: str            # "pants" / "dala" / "punkts" / "apakspunkts" / "nodala" / "sadala"
    number: str           # "5" / "5.3" / "IV"
    path: str             # hierarhiskais path, piem., "5.3.2" priekš apakšpunkta
    title: Optional[str] = None
    snippet: Optional[str] = None   # max ~300 rakstzīmes priekš meklēšanas
    anchor: Optional[str] = None    # HTML anchor uz avota lapas, piem., "p5"
    sort_order: int = 0
    # Saraksts ar bērnu sekcijām (apakš-hierarhija)
    children: list["NormalizedSection"] = field(default_factory=list)


@dataclass
class NormalizedDocument:
    """Normalizēts dokumenta ieraksts, ko adapters atgriež uz galveno sistēmu."""

    external_id: str
    source: str
    doc_type: str   # kartēts caur normalizer.classify_doc_type
    title: str
    official_url: str
    number: Optional[str] = None
    issuer: Optional[str] = None
    adopted_date: Optional[date] = None
    effective_date: Optional[date] = None
    status: Optional[str] = None           # kartēts caur normalizer.classify_status
    summary: Optional[str] = None
    license: Optional[str] = None
    topics: list[str] = field(default_factory=list)
    # Hierarhisks sekciju saraksts (ja adapters spēj to izvilkt).
    # Pēc noklusējuma tukšs — ne visi adapteri to atbalsta.
    sections: list[NormalizedSection] = field(default_factory=list)


@dataclass
class SourceMeta:
    code: str
    name: str
    base_url: str
    license_notes: str


class SourceAdapter(ABC):
    """Kopīgais interfeiss visiem avotiem."""

    @abstractmethod
    def get_source_meta(self) -> SourceMeta:
        """Atgriež statisku informāciju par avotu (nosaukums, URL, licence)."""

    @abstractmethod
    def fetch_batch(self, limit: int = 50, query: Optional[str] = None) -> Iterable[NormalizedDocument]:
        """Iegūst dokumentu paku no avota.

        Args:
            limit: maksimālais dokumentu skaits.
            query: neobligāts meklēšanas vaicājums (atkarīgs no avota atbalsta).

        Yields:
            NormalizedDocument objektus.
        """
