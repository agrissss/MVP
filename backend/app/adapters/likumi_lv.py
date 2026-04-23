"""Adapters likumi.lv / Latvijas Vestnesis publiskajam lapam.

Sis adapters:
  * Apstaiga vairakas indeksa lapas (jaunakie akti, meklesanas rezultati).
  * Ievieš paging — apstaiga page=1..MAX_INDEX_PAGES katram indeksam.
  * Apmekle KATRA akta atseviskaju lapu un izvelk pilnus metadatus
    (virsraksts, tips, numurs, iestade, pienemsanas un speka stasanas
    datumi, statuss).
  * Izvelk HIERARHISKU sekciju struktūru (pants / daļa / punkts /
    apakšpunkts) ar deep-link anchoriem — bet tikai ievada fragmentus
    (max 300 rakstz.), NE pilnu tekstu.
  * Ievero politu rate limiting (settings.fetch_delay_sec starp
    pieprasijumiem) un ieklauj atpazistamu User-Agent.

Svarigi: sistema NEGLABA pilnu tiesibu akta tekstu. Tikai metadatus,
strukturu, isus fragmentus un saiti uz oficialo avotu.

Uzmaniba: likumi.lv HTML struktura var mainities. Adapters izmanto
vairakas fallback-strategijas, bet laika gaita var prasit pielagojumus.
"""
from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from datetime import date as _date
from typing import Iterable, Iterator, List, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from ..config import settings
from .base import SourceAdapter, SourceMeta, NormalizedDocument, NormalizedSection

logger = logging.getLogger(__name__)

BASE_URL = "https://likumi.lv"

DEFAULT_INDEX_PAGES = [
    "/ta/jaunakie",
    "/ta/pieskirtas-redakcijas",
]

MAX_INDEX_PAGES = 10

# Maksimala fragmenta garuma (rakstzimes), ko glabajam no katra panta/punkta.
# Uzmaniba par autortiesibam — neglabat pilnu tekstu.
MAX_SNIPPET_LEN = 280

# Menesu nosaukumi latviski -> numuri
LV_MONTHS = {
    "janvaris": 1, "janvari": 1,
    "februaris": 2, "februari": 2,
    "marts": 3, "marta": 3,
    "aprilis": 4, "aprili": 4,
    "maijs": 5, "maija": 5,
    "junijs": 6, "junija": 6,
    "julijs": 7, "julija": 7,
    "augusts": 8, "augusta": 8,
    "septembris": 9, "septembri": 9,
    "oktobris": 10, "oktobri": 10,
    "novembris": 11, "novembri": 11,
    "decembris": 12, "decembri": 12,
}

DIACRITIC_MAP = str.maketrans({
    "\u0101": "a", "\u010d": "c", "\u0113": "e", "\u0123": "g",
    "\u012b": "i", "\u0137": "k", "\u013c": "l", "\u0146": "n",
    "\u0161": "s", "\u016b": "u", "\u017e": "z",
    "\u0100": "A", "\u010c": "C", "\u0112": "E", "\u0122": "G",
    "\u012a": "I", "\u0136": "K", "\u013b": "L", "\u0145": "N",
    "\u0160": "S", "\u016a": "U", "\u017d": "Z",
})


def _strip_diacritics(s: str) -> str:
    return s.translate(DIACRITIC_MAP)


@dataclass
class IndexEntry:
    ext_id: str
    title: str
    full_url: str


class LikumiLvAdapter(SourceAdapter):
    """HTML-based adapters likumi.lv ar metadatu un sekciju struktūras izvilksanu."""

    SOURCE_CODE = "likumi_lv"

    def get_source_meta(self) -> SourceMeta:
        return SourceMeta(
            code=self.SOURCE_CODE,
            name="likumi.lv / Latvijas Vestnesis",
            base_url=BASE_URL,
            license_notes=(
                "Oficiala tiesibu aktu publikacijas vietne (SIA 'Latvijas "
                "Vestnesis'). Sistema glaba tikai metadatus, sekciju strukturu "
                "un isus fragmentus (max 300 rakstz.) priekš meklesanas. "
                "Pilns teksts tiek lasits tikai avota."
            ),
        )

    def fetch_batch(self, limit=50, query=None):
        headers = {"User-Agent": settings.user_agent}

        with httpx.Client(timeout=30.0, headers=headers, follow_redirects=True) as client:
            index_pages = self._index_pages_for(query)

            seen = set()
            entries = []

            for path in index_pages:
                if len(entries) >= limit:
                    break
                url = urljoin(BASE_URL, path)
                logger.info("likumi.lv: indeksa lapa %s", url)
                try:
                    resp = client.get(url)
                    resp.raise_for_status()
                except httpx.HTTPError as e:
                    logger.warning("Indeksa lapa %s nepieejama: %s", url, e)
                    continue

                page_added = 0
                for entry in self._parse_index(resp.text):
                    if entry.ext_id in seen:
                        continue
                    seen.add(entry.ext_id)
                    entries.append(entry)
                    page_added += 1
                    if len(entries) >= limit:
                        break

                if page_added == 0:
                    logger.info(
                        "likumi.lv: lapa %s bez jauniem ierakstiem, apturam šo atzaru",
                        url,
                    )

                time.sleep(settings.fetch_delay_sec)

            logger.info("likumi.lv: atrasti %d unikali akti indeksos", len(entries))

            for i, entry in enumerate(entries[:limit], start=1):
                try:
                    doc = self._fetch_document_metadata(client, entry)
                    yield doc
                except Exception as e:
                    logger.warning(
                        "Nevar ieladet akta metadatus %s: %s",
                        entry.full_url, e,
                    )
                    yield NormalizedDocument(
                        external_id="%s:%s" % (self.SOURCE_CODE, entry.ext_id),
                        source=self.SOURCE_CODE,
                        doc_type="cits",
                        title=entry.title,
                        official_url=entry.full_url,
                    )
                time.sleep(settings.fetch_delay_sec)
                if i % 10 == 0:
                    logger.info("likumi.lv: apstradati %d/%d", i, len(entries))

    def _index_pages_for(self, query):
        if query:
            return [
                "/ta/meklet?q=%s&page=%d" % (query, page)
                for page in range(1, MAX_INDEX_PAGES + 1)
            ]
        pages = []
        for base in DEFAULT_INDEX_PAGES:
            pages.append(base)
            for page in range(2, MAX_INDEX_PAGES + 1):
                sep = "&" if "?" in base else "?"
                pages.append("%s%spage=%d" % (base, sep, page))
        return pages

    def _parse_index(self, html):
        soup = BeautifulSoup(html, "lxml")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/ta/id/" not in href:
                continue
            full_url = urljoin(BASE_URL, href)
            parsed = urlparse(full_url)
            ext_id = parsed.path
            title = (a.get_text(strip=True) or "")[:500]
            if not title or len(title) < 5:
                continue
            yield IndexEntry(ext_id=ext_id, title=title, full_url=BASE_URL + ext_id)

    def _fetch_document_metadata(self, client, entry):
        resp = client.get(entry.full_url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        title_node = soup.find("h1")
        title = self._text_of(title_node) or entry.title

        meta = self._extract_metadata_block(soup)

        doc_type = self._guess_doc_type(meta.get("veids"), title)
        issuer = meta.get("izdevejs")
        number = meta.get("numurs") or self._extract_number_from_title(title)
        adopted = self._parse_lv_date(meta.get("pienemts"))
        effective = self._parse_lv_date(
            meta.get("stajas_speka") or meta.get("speka_no")
        )
        status = meta.get("statuss")

        sections = self._extract_sections(soup)

        return NormalizedDocument(
            external_id="%s:%s" % (self.SOURCE_CODE, entry.ext_id),
            source=self.SOURCE_CODE,
            doc_type=doc_type,
            title=title,
            number=number,
            issuer=issuer,
            adopted_date=adopted,
            effective_date=effective,
            status=status,
            official_url=entry.full_url,
            summary=None,
            license=None,
            topics=[],
            sections=sections,
        )

    # -------------------------------------------------------------------
    # Sekciju ekstrakcija
    # -------------------------------------------------------------------

    # Pantu virsrakstu mintas: "5. pants.", "5.pants", "5. pants. Nosaukums"
    PANT_RE = re.compile(r"^\s*(\d+)\.?\s*pant[saiu]\.?\s*(.*)", re.IGNORECASE)
    # Daļu mintas: "(1)", "(2)"
    DALA_RE = re.compile(r"^\s*\((\d+)\)\s*(.*)")
    # Punktu mintas: "1.", "1.1.", "1.1.1." sākumā rindas
    PUNKTS_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\.\s+(.*)")
    # Nodaļas: "I nodaļa", "1. nodaļa"
    NODALA_RE = re.compile(r"^\s*([IVXLCDM]+|\d+)\.\s*noda[lļ]a\.?\s*(.*)", re.IGNORECASE)

    def _extract_sections(self, soup: BeautifulSoup) -> List[NormalizedSection]:
        """Izvelk hierarhisku sekciju sarakstu no likuma HTML.

        Likumi.lv HTML lielakoties izmanto class="panta_nosaukums" priekš
        panta virsraksta un class="panta_teksts" priekš tekstiem. Šis kods
        tomēr atbalsta arī vispārēju fallback uz h1-h4 un rindkopām.
        """
        sections: List[NormalizedSection] = []

        # Pirma strategija: <div class="panta_nosaukums"> / id="p5"
        heading_nodes = soup.find_all(
            ["h1", "h2", "h3", "h4", "div", "p"],
            attrs={"class": re.compile(r"panta_nosaukums|nodala|sadala", re.I)},
        )

        if heading_nodes:
            return self._extract_from_headings(heading_nodes)

        # Otra strategija: jebkurš elements ar id="p<num>" anchor
        anchored = soup.find_all(id=re.compile(r"^p\d+"))
        if anchored:
            return self._extract_from_anchors(anchored)

        # Treša strategija: no pilna teksta plūsmas pēc regex
        body = soup.find(id="article_text") or soup.find("main") or soup.body
        if body is None:
            return sections
        return self._extract_from_text_flow(body)

    def _extract_from_headings(self, nodes) -> List[NormalizedSection]:
        """Izvelk nodaļas + pantus + daļas/punktus pantā.

        Nodaļas un pantu virsrakstus ņemam no virsrakstu mezgliem,
        bet daļas ("(1)", "(2)") un punktus ("1)", "2)") skenējam pantu
        tekstā ar _extract_pants_children().
        """
        result: List[NormalizedSection] = []
        current_nodala: Optional[NormalizedSection] = None
        order = 0
        for node in nodes:
            text = node.get_text(" ", strip=True)
            if not text:
                continue
            anchor = node.get("id")
            m_pant = self.PANT_RE.match(text)
            if m_pant:
                num = m_pant.group(1)
                title = self._clean_title(m_pant.group(2))
                # Savācam pilnu pantu tekstu — nākamie rindkopu mezgli
                # līdz nākamajam pantam vai nodaļai.
                full_text = self._collect_pants_body(node)
                snippet = self._truncate(full_text) if full_text else self._snippet_after(node)
                order += 1
                pants = NormalizedSection(
                    level="pants",
                    number=num,
                    path=num,
                    title=title,
                    snippet=snippet,
                    anchor=anchor or ("p%s" % num),
                    sort_order=order,
                )
                # Daļas un punkti pantā
                if full_text:
                    pants.children = self._extract_pants_children(num, full_text)
                result.append(pants)
                continue
            m_nod = self.NODALA_RE.match(text)
            if m_nod:
                num = m_nod.group(1)
                title = self._clean_title(m_nod.group(2))
                order += 1
                current_nodala = NormalizedSection(
                    level="nodala",
                    number=num,
                    path="n%s" % num,
                    title=title,
                    snippet=None,
                    anchor=anchor,
                    sort_order=order,
                )
                result.append(current_nodala)
        return result

    def _collect_pants_body(self, pants_heading) -> str:
        """No pants virsraksta uz priekšu savāc tekstu līdz nākamajam pantam/nodaļai."""
        parts: List[str] = []
        nxt = pants_heading
        # Eju caur sibling/next elementiem, apstājoties pie nākošā heading
        limit = 50  # drošības limits, lai neskrējam caur visu lapu
        for _ in range(limit):
            nxt = nxt.find_next(["p", "div", "h1", "h2", "h3", "h4"])
            if not nxt:
                break
            text = nxt.get_text(" ", strip=True)
            if not text:
                continue
            # Apstājas pie nākamā panta vai nodaļas virsraksta
            if self.PANT_RE.match(text) or self.NODALA_RE.match(text):
                break
            parts.append(text)
            if len(" ".join(parts)) > 2000:
                break
        return "\n".join(parts).strip()

    def _extract_pants_children(self, pants_num: str, body: str) -> List[NormalizedSection]:
        """Sadala pantu tekstu daļās "(1)" un punktos "1)" / "1."."""
        children: List[NormalizedSection] = []
        # Vispirms mēģinām daļas pēc "(N)" paraugā — tas ir likumu standarts
        dala_splits = re.split(r"(?<!\w)\((\d+)\)\s+", body)
        # Rezultāts: [pirms-pirmās-daļas, "1", "teksts1", "2", "teksts2", ...]
        if len(dala_splits) >= 3:
            order = 0
            # Ignorējam pirmo fragmentu (pirms "(1)")
            for i in range(1, len(dala_splits), 2):
                dala_num = dala_splits[i]
                dala_text = dala_splits[i + 1].strip() if i + 1 < len(dala_splits) else ""
                if not dala_text:
                    continue
                order += 1
                children.append(NormalizedSection(
                    level="dala",
                    number=dala_num,
                    path="%s.%s" % (pants_num, dala_num),
                    title=None,
                    snippet=self._truncate(dala_text),
                    anchor="p%s.%s" % (pants_num, dala_num),
                    sort_order=order,
                    children=self._extract_dala_punkts(pants_num, dala_num, dala_text),
                ))
            return children

        # Citādi mēģinām punktus "1)" vai "1."
        punkts_matches = list(re.finditer(r"(?:^|\s)(\d+)\)\s+", body))
        if len(punkts_matches) >= 2:
            order = 0
            for idx, m in enumerate(punkts_matches):
                start = m.end()
                end = (
                    punkts_matches[idx + 1].start()
                    if idx + 1 < len(punkts_matches)
                    else len(body)
                )
                pt_text = body[start:end].strip()
                if not pt_text:
                    continue
                order += 1
                children.append(NormalizedSection(
                    level="punkts",
                    number=m.group(1),
                    path="%s.%s" % (pants_num, m.group(1)),
                    title=None,
                    snippet=self._truncate(pt_text),
                    anchor="pt%s.%s" % (pants_num, m.group(1)),
                    sort_order=order,
                ))
        return children

    def _extract_dala_punkts(self, pants_num: str, dala_num: str, dala_text: str) -> List[NormalizedSection]:
        """Daļā var būt uzskaitījumi "1)", "2)" — atpazīstam tos kā punktus."""
        punkts_matches = list(re.finditer(r"(?:^|\s)(\d+)\)\s+", dala_text))
        if len(punkts_matches) < 2:
            return []
        children: List[NormalizedSection] = []
        order = 0
        parent_path = "%s.%s" % (pants_num, dala_num)
        for idx, m in enumerate(punkts_matches):
            start = m.end()
            end = (
                punkts_matches[idx + 1].start()
                if idx + 1 < len(punkts_matches)
                else len(dala_text)
            )
            pt_text = dala_text[start:end].strip()
            if not pt_text:
                continue
            order += 1
            children.append(NormalizedSection(
                level="punkts",
                number=m.group(1),
                path="%s.%s" % (parent_path, m.group(1)),
                title=None,
                snippet=self._truncate(pt_text),
                anchor="pt%s.%s" % (parent_path, m.group(1)),
                sort_order=order,
            ))
        return children

    def _extract_from_anchors(self, anchored_nodes) -> List[NormalizedSection]:
        result: List[NormalizedSection] = []
        order = 0
        for node in anchored_nodes:
            anchor = node.get("id", "")
            m = re.match(r"^p(\d+(?:[._]\d+)*)$", anchor)
            if not m:
                continue
            number = m.group(1).replace("_", ".")
            text = node.get_text(" ", strip=True)
            m_pant = self.PANT_RE.match(text)
            title = self._clean_title(m_pant.group(2)) if m_pant else None
            snippet = self._snippet_after(node)
            order += 1
            level = "pants" if "." not in number else "dala"
            result.append(NormalizedSection(
                level=level,
                number=number,
                path=number,
                title=title,
                snippet=snippet,
                anchor=anchor,
                sort_order=order,
            ))
        return result

    def _extract_from_text_flow(self, body) -> List[NormalizedSection]:
        """Pēdējais fallback: skenē paragrafu tekstu pēc pantu minusiem."""
        result: List[NormalizedSection] = []
        order = 0
        for p in body.find_all(["p", "div"]):
            text = p.get_text(" ", strip=True)
            if not text or len(text) < 5:
                continue
            m_pant = self.PANT_RE.match(text)
            if m_pant:
                num = m_pant.group(1)
                title = self._clean_title(m_pant.group(2))
                order += 1
                result.append(NormalizedSection(
                    level="pants",
                    number=num,
                    path=num,
                    title=title,
                    snippet=self._truncate(text),
                    anchor="p%s" % num,
                    sort_order=order,
                ))
        return result

    def _snippet_after(self, node) -> Optional[str]:
        """Satver tuvāko nākamo rindkopu kā īsu fragmentu (max MAX_SNIPPET_LEN)."""
        nxt = node.find_next(["p", "div"])
        if not nxt:
            return None
        text = nxt.get_text(" ", strip=True)
        if not text:
            return None
        return self._truncate(text)

    @staticmethod
    def _truncate(s: str, limit: int = MAX_SNIPPET_LEN) -> str:
        s = s.strip()
        if len(s) <= limit:
            return s
        # Apraut pie tuvakas vardas robežas
        cut = s[:limit].rsplit(" ", 1)[0]
        return cut + "…"

    @staticmethod
    def _clean_title(raw: str) -> Optional[str]:
        if not raw:
            return None
        # Atmest iekav-komentarus, lidz 200 rakstz.
        t = raw.strip().rstrip(".").strip()
        t = re.sub(r"\s+", " ", t)
        return t[:200] if t else None

    # -------------------------------------------------------------------
    # Metadata bloka izvilksana (jau eksistē)
    # -------------------------------------------------------------------

    @staticmethod
    def _text_of(node):
        if not node:
            return None
        text = node.get_text(" ", strip=True)
        return text[:500] if text else None

    def _extract_metadata_block(self, soup):
        """Savac label -> value parus no akta lapas informacijas bloka."""
        result = {}

        for dl in soup.find_all("dl"):
            dts = dl.find_all("dt")
            dds = dl.find_all("dd")
            for dt, dd in zip(dts, dds):
                key = self._norm_key(dt.get_text(" ", strip=True))
                val = dd.get_text(" ", strip=True)
                if key and val:
                    result.setdefault(key, val)

        for tr in soup.find_all("tr"):
            cells = tr.find_all(["th", "td"])
            if len(cells) >= 2:
                key = self._norm_key(cells[0].get_text(" ", strip=True))
                val = cells[1].get_text(" ", strip=True)
                if key and val:
                    result.setdefault(key, val)

        if not result:
            page_text = soup.get_text(" ", strip=True)
            for key_text, canonical in (
                ("Izdevejs", "izdevejs"),
                ("Veids", "veids"),
                ("Pienemts", "pienemts"),
                ("Stajas speka", "stajas_speka"),
                ("Speka no", "speka_no"),
                ("Statuss", "statuss"),
                ("Numurs", "numurs"),
            ):
                key_norm = _strip_diacritics(key_text)
                text_norm = _strip_diacritics(page_text)
                pattern = re.compile(
                    r"%s\s*[:\-]?\s*([^\n\r]{1,200})" % re.escape(key_norm)
                )
                m = pattern.search(text_norm)
                if m:
                    result[canonical] = m.group(1).strip()

        return result

    @staticmethod
    def _norm_key(raw):
        s = _strip_diacritics(raw).lower().rstrip(":").strip()
        s = re.sub(r"\s+", "_", s)
        return s

    @staticmethod
    def _guess_doc_type(veids_str, title):
        blob = _strip_diacritics(" ".join([veids_str or "", title or ""])).lower()
        if "mk noteikum" in blob or "ministru kabinet" in blob:
            return "mk_noteikumi"
        if "instrukcij" in blob:
            return "instrukcija"
        if "vadlinij" in blob:
            return "vadlinijas"
        if "pazinojum" in blob:
            return "pazinojums"
        if "likum" in blob:
            return "likums"
        return "cits"

    @staticmethod
    def _extract_number_from_title(title):
        m = re.search(r"(Nr\.?\s*\d+[A-Za-z0-9/\-]*)", title)
        return m.group(1) if m else None

    @staticmethod
    def _parse_lv_date(s):
        if not s:
            return None
        s = s.strip()
        s_ascii = _strip_diacritics(s).lower()

        m = re.search(r"(\d{4})\.\s*gad[a]\s*(\d{1,2})\.\s*(\w+)", s_ascii)
        if m:
            year = int(m.group(1))
            day = int(m.group(2))
            month_name = m.group(3).lower()
            month = LV_MONTHS.get(month_name)
            if month:
                try:
                    return _date(year, month, day)
                except ValueError:
                    pass

        try:
            return date_parser.parse(s, dayfirst=True, fuzzy=True).date()
        except (ValueError, TypeError, OverflowError):
            return None
