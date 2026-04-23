"""Adapters Valsts ienemumu dienesta (VID) publiskajiem skaidrojumiem.

VID (www.vid.gov.lv) publicē:
  * Metodiskie materiali (nodokļu skaidrojumi, vadlinijas)
  * Pazinojumi un aktualitates
  * Biezak uzdotie jautajumi

Sis adapters:
  * Apstaiga VID publiskoto metodisko materialu un pazinojumu sarakstu.
  * Izvelk virsrakstu, saiti, datumu.
  * NELASA pilnu tekstu — tikai metadatus un saiti uz oficialo avotu.

Piezime: VID vietne var mainit savu strukturu. Adapters izmanto
vairakas heuristikas saisu atrasanai (a href ar /nodoklu-skaidrojumi/
vai /metodiskie-materiali/ fragmentu). Ja vietne mainas — pielagot
INDEX_PATHS un _parse_index regex.
"""
from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from typing import Iterable, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from ..config import settings
from .base import SourceAdapter, SourceMeta, NormalizedDocument

logger = logging.getLogger(__name__)

BASE_URL = "https://www.vid.gov.lv"

# VID publisko sadalu saraksts. Pievienot, ja vajag vairak.
INDEX_PATHS = [
    "/lv/metodiskie-materiali",
    "/lv/nodoklu-skaidrojumi",
    "/lv/pazinojumi",
]

MAX_INDEX_PAGES = 5

# URL fragmenti, kas raksturo VID dokumenta saiti
DOC_URL_MARKERS = (
    "/metodiskie-materiali/",
    "/nodoklu-skaidrojumi/",
    "/pazinojumi/",
    "/skaidrojumi/",
)


@dataclass
class VidEntry:
    ext_id: str       # relativais cels
    title: str
    full_url: str
    date_hint: Optional[str] = None


class VidAdapter(SourceAdapter):
    """VID publisko materialu HTML-based adapters."""

    SOURCE_CODE = "vid"

    def get_source_meta(self) -> SourceMeta:
        return SourceMeta(
            code=self.SOURCE_CODE,
            name="VID — Valsts ieņēmumu dienests (publiskie skaidrojumi)",
            base_url=BASE_URL,
            license_notes=(
                "VID publisko metodisko materialu un skaidrojumu saturs pieder "
                "Valsts ienemumu dienestam. Sistema glaba tikai metadatus un "
                "saites uz oficialo publikaciju www.vid.gov.lv."
            ),
        )

    def fetch_batch(self, limit: int = 50, query: Optional[str] = None) -> Iterable[NormalizedDocument]:
        headers = {"User-Agent": settings.user_agent}

        with httpx.Client(timeout=30.0, headers=headers, follow_redirects=True) as client:
            entries: list[VidEntry] = []
            seen: set[str] = set()

            for path in self._index_paths(query):
                if len(entries) >= limit:
                    break
                url = urljoin(BASE_URL, path)
                logger.info("VID: indeksa lapa %s", url)
                try:
                    resp = client.get(url)
                    resp.raise_for_status()
                except httpx.HTTPError as e:
                    logger.warning("VID indeksa lapa %s nepieejama: %s", url, e)
                    continue

                for entry in self._parse_index(resp.text):
                    if entry.ext_id in seen:
                        continue
                    seen.add(entry.ext_id)
                    entries.append(entry)
                    if len(entries) >= limit:
                        break

                time.sleep(settings.fetch_delay_sec)

            logger.info("VID: atrasti %d unikali materiali", len(entries))

            for entry in entries[:limit]:
                yield self._to_normalized(entry)

    def _index_paths(self, query: Optional[str]) -> list[str]:
        """Atgriez indeksa celu sarakstu ar paging atbalstu."""
        if query:
            # VID meklesana — vienkarss query parametrs
            return ["/lv/meklet?q=%s" % query]
        paths = []
        for base in INDEX_PATHS:
            paths.append(base)
            for page in range(2, MAX_INDEX_PAGES + 1):
                sep = "&" if "?" in base else "?"
                paths.append("%s%spage=%d" % (base, sep, page))
        return paths

    def _parse_index(self, html: str) -> Iterable[VidEntry]:
        soup = BeautifulSoup(html, "lxml")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not any(marker in href for marker in DOC_URL_MARKERS):
                continue
            # Izlaist sadalu virsvirsrakstu saites (paši indeksu celi)
            if href.rstrip("/") in [p.rstrip("/") for p in INDEX_PATHS]:
                continue
            title = (a.get_text(strip=True) or "")[:500]
            if not title or len(title) < 8:
                continue
            full_url = urljoin(BASE_URL, href)
            parsed = urlparse(full_url)
            ext_id = parsed.path
            # Megin atrast datumu tuvaka vecaka elementa
            date_hint = self._find_nearby_date(a)
            yield VidEntry(ext_id=ext_id, title=title, full_url=full_url, date_hint=date_hint)

    @staticmethod
    def _find_nearby_date(a_tag) -> Optional[str]:
        """Meklee dd.mm.yyyy vai yyyy-mm-dd pee saites tuvakajiem elementiem."""
        date_re = re.compile(r"(\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4}|\d{4}-\d{2}-\d{2})")
        # parbauda brala un veecaka elementa tekstu
        for node in (a_tag.parent, a_tag.find_previous("time"), a_tag.find_next("time")):
            if not node:
                continue
            text = node.get_text(" ", strip=True) if hasattr(node, "get_text") else str(node)
            m = date_re.search(text)
            if m:
                return m.group(1)
        return None

    def _to_normalized(self, entry: VidEntry) -> NormalizedDocument:
        adopted = None
        if entry.date_hint:
            try:
                adopted = date_parser.parse(entry.date_hint, dayfirst=True, fuzzy=True).date()
            except (ValueError, TypeError, OverflowError):
                adopted = None

        doc_type = self._guess_doc_type(entry.ext_id, entry.title)

        return NormalizedDocument(
            external_id="%s:%s" % (self.SOURCE_CODE, entry.ext_id),
            source=self.SOURCE_CODE,
            doc_type=doc_type,
            title=entry.title,
            number=None,
            issuer="Valsts ieņēmumu dienests",
            adopted_date=adopted,
            effective_date=None,
            status="speka",  # VID publicetie materiali ir aktualie
            official_url=entry.full_url,
            summary=None,
            license=None,
            topics=["nodokli"],
        )

    @staticmethod
    def _guess_doc_type(path: str, title: str) -> str:
        blob = (path + " " + title).lower()
        if "metodisk" in blob:
            return "vadlinijas"
        if "skaidrojum" in blob:
            return "vadlinijas"
        if "pazinojum" in blob:
            return "pazinojums"
        if "instrukcij" in blob:
            return "instrukcija"
        return "vadlinijas"
