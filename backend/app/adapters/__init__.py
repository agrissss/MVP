"""Avotu adapteri. Katram avotam — atsevišķs modulis.

Jauna avota pievienošana:
    1. Izveido <jauns>.py ar klasi, kas manto no base.SourceAdapter.
    2. Pievieno to zemāk esošajā REGISTRY vārdnīcā.
    3. Nav jāmaina pārējā sistēma.
"""
from __future__ import annotations

from .base import SourceAdapter, NormalizedDocument
from .likumi_lv import LikumiLvAdapter
from .data_gov_lv import DataGovLvAdapter
from .vid import VidAdapter
from .atd import AtdAdapter


REGISTRY: dict[str, type[SourceAdapter]] = {
    "likumi_lv": LikumiLvAdapter,
    "data_gov_lv": DataGovLvAdapter,
    "vid": VidAdapter,
    "atd": AtdAdapter,
}


def get_adapter(code: str) -> SourceAdapter:
    """Atgriež adapteru pēc avota koda."""
    cls = REGISTRY.get(code)
    if not cls:
        raise ValueError(f"Nav adaptera avotam: {code}")
    return cls()


__all__ = ["SourceAdapter", "NormalizedDocument", "REGISTRY", "get_adapter"]
