"""Adapters Autotransporta direkcijas (ATD) transportdata.gov.lv portalam.

Transportdata.gov.lv ir CKAN-saderigs portals, kas publice sabiedriska
transporta un cela satiksmes atvertos datus — GTFS, maršrutu saraksti,
biļešu statistika u.c.

Dokumentacija: https://transportdata.gov.lv/dati/lv/api/

Adapters izmanto CKAN v3 API package_search galapunktu — autentifikacija
nav vajadziga, tikai pietiekami politi pieprasijumi.
"""
from __future__ import annotations

import logging
from typing import Iterable, Optional

import httpx

from ..config import settings
from .base import SourceAdapter, SourceMeta, NormalizedDocument

logger = logging.getLogger(__name__)


CKAN_BASE = "https://transportdata.gov.lv/dati/lv/api/3/action"
PORTAL_BASE = "https://transportdata.gov.lv"


class AtdAdapter(SourceAdapter):
    """CKAN-based adapters transporta datu kopam."""

    SOURCE_CODE = "atd"

    def get_source_meta(self) -> SourceMeta:
        return SourceMeta(
            code=self.SOURCE_CODE,
            name="ATD — Autotransporta direkcija (transportdata.gov.lv)",
            base_url=PORTAL_BASE,
            license_notes=(
                "Sabiedriska transporta un cela satiksmes atvertie dati, "
                "publiceti atbilstosi katras kopas licencei (biezak CC-BY 4.0). "
                "Sistema glaba tikai metadatus un resursu saites, nevis "
                "pasus failus."
            ),
        )

    def fetch_batch(
        self, limit: int = 50, query: Optional[str] = None
    ) -> Iterable[NormalizedDocument]:
        """Izsauc CKAN `package_search` galapunktu transportdata.gov.lv."""
        params = {
            "rows": min(limit, 1000),
            "q": query or "*:*",
        }
        headers = {"User-Agent": settings.user_agent}
        url = "%s/package_search" % CKAN_BASE

        logger.info("ATD: pieprasijums %s params=%s", url, params)
        with httpx.Client(timeout=30.0, headers=headers) as client:
            try:
                resp = client.get(url, params=params)
                resp.raise_for_status()
            except httpx.HTTPError as e:
                logger.error("ATD CKAN API kluda: %s", e)
                return

            payload = resp.json()

        if not payload.get("success"):
            logger.warning("ATD atbilde success=False: %s", payload.get("error"))
            return

        result = payload.get("result", {})
        for pkg in result.get("results", []):
            yield self._to_normalized(pkg)

    def _to_normalized(self, pkg: dict) -> NormalizedDocument:
        name = pkg.get("name") or pkg.get("id") or ""
        external_id = "%s:%s" % (self.SOURCE_CODE, name)
        title = pkg.get("title") or name or "(Bez nosaukuma)"
        issuer = (pkg.get("organization") or {}).get("title") or "Autotransporta direkcija"
        license_name = pkg.get("license_title") or pkg.get("license_id")
        notes = pkg.get("notes") or None
        official_url = (
            "%s/dati/lv/dataset/%s" % (PORTAL_BASE, name) if name else PORTAL_BASE
        )

        from ..normalizer import parse_date
        modified = parse_date(pkg.get("metadata_modified"))

        # ATD tagiem daudzreiz nav vienotas struktures — saglaba ka topics
        topics_from_source = [
            t.get("display_name", t.get("name", ""))
            for t in pkg.get("tags", [])
            if t
        ]
        # Garantet transporta temu
        if "transports" not in topics_from_source:
            topics_from_source.append("transports")

        return NormalizedDocument(
            external_id=external_id,
            source=self.SOURCE_CODE,
            doc_type="datu_kopa",
            title=title,
            number=None,
            issuer=issuer,
            adopted_date=modified,
            effective_date=None,
            status="speka",
            official_url=official_url,
            summary=notes[:500] if notes else None,
            license=license_name,
            topics=topics_from_source,
        )
