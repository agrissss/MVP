"""Adapters Latvijas Atvērto datu portālam (data.gov.lv).

Izmanto CKAN v3 API — oficiālu un publisku. Autentifikācija nav vajadzīga
lasīšanai.

Dokumentācija: https://data.gov.lv/dati/lv/api/
"""
from __future__ import annotations

import logging
from typing import Iterable, Optional

import httpx

from ..config import settings
from .base import SourceAdapter, SourceMeta, NormalizedDocument

logger = logging.getLogger(__name__)


CKAN_BASE = "https://data.gov.lv/dati/lv/api/3/action"


class DataGovLvAdapter(SourceAdapter):
    """CKAN API adapters."""

    SOURCE_CODE = "data_gov_lv"

    def get_source_meta(self) -> SourceMeta:
        return SourceMeta(
            code=self.SOURCE_CODE,
            name="data.gov.lv — Latvijas Atvērto datu portāls",
            base_url="https://data.gov.lv",
            license_notes=(
                "Datu kopas publicētas atbilstoši katras kopas licencei "
                "(biežāk CC-BY 4.0). Sistēma glabā tikai metadatus un resursu "
                "saites, nevis pašus failus."
            ),
        )

    def fetch_batch(
        self, limit: int = 50, query: Optional[str] = None
    ) -> Iterable[NormalizedDocument]:
        """Izsauc CKAN `package_search` galapunktu."""
        params = {
            "rows": min(limit, 1000),
            "q": query or "*:*",
        }
        headers = {"User-Agent": settings.user_agent}
        url = f"{CKAN_BASE}/package_search"

        logger.info("data.gov.lv: pieprasījums %s params=%s", url, params)
        with httpx.Client(timeout=30.0, headers=headers) as client:
            try:
                resp = client.get(url, params=params)
                resp.raise_for_status()
            except httpx.HTTPError as e:
                logger.error("data.gov.lv API kļūda: %s", e)
                return

            payload = resp.json()

        if not payload.get("success"):
            logger.warning("data.gov.lv atbildes success=False: %s", payload.get("error"))
            return

        result = payload.get("result", {})
        for pkg in result.get("results", []):
            yield self._to_normalized(pkg)

    def _to_normalized(self, pkg: dict) -> NormalizedDocument:
        """Konvertē CKAN package uz NormalizedDocument."""
        name = pkg.get("name") or pkg.get("id") or ""
        external_id = f"{self.SOURCE_CODE}:{name}"
        title = pkg.get("title") or name or "(Bez nosaukuma)"
        issuer = (pkg.get("organization") or {}).get("title") or "Nezināma iestāde"
        license_name = pkg.get("license_title") or pkg.get("license_id")
        notes = pkg.get("notes") or None
        official_url = f"https://data.gov.lv/dati/lv/dataset/{name}" if name else "https://data.gov.lv"

        # CKAN metadata_modified ir ISO formāta string
        from ..normalizer import parse_date
        modified = parse_date(pkg.get("metadata_modified"))

        topics_from_source = [t.get("display_name", t.get("name", ""))
                              for t in pkg.get("tags", []) if t]

        return NormalizedDocument(
            external_id=external_id,
            source=self.SOURCE_CODE,
            doc_type="datu_kopa",
            title=title,
            number=None,
            issuer=issuer,
            adopted_date=modified,
            effective_date=None,
            status="speka",  # CKAN atvērtie dati pēc noklusējuma ir aktuāli
            official_url=official_url,
            summary=notes[:500] if notes else None,
            license=license_name,
            topics=topics_from_source,
        )
