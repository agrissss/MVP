"""Metadatu normalizācija no adapteriem.

Konvertē avota specifisku payload uz vienotu Document modeli.
"""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Optional

from dateutil import parser as date_parser

from .models import DocType, DocStatus


# Atslēgvārdu → tēmu kartējums (heuristika — skatīt ierobežojumi.md).
TOPIC_KEYWORDS = {
    "nodokli": [
        "nodok", "pvn", "uin", "iin", "akcīz", "akciz", "muita", "ienākum", "ienakum"
    ],
    "gramatvediba": ["grāmatved", "gramatved", "grāmatvedīb", "finanšu pārskat", "finansu parskat"],
    "darba_tiesibas": ["darba likum", "darba tiesīb", "darba tiesib", "darbiniek", "darba aizsardz"],
    "logistika": ["loģistik", "logistik", "krav", "piegād", "piegad"],
    "transports": ["transport", "autotransport", "autoceļ", "autocel", "satiksm", "mobilitāt", "mobilitat", "dzelzceļ", "dzelzcel"],
    "muita": ["muit"],
    "e_komercija": ["e-komercij", "e-komerc", "elektronisk", "tiešsaist", "tiessaist"],
    "datu_aizsardziba": ["datu aizsardz", "personas dat", "GDPR", "VDAR"],
    "komercdarbiba": ["komercdarbīb", "komercdarb", "komersant", "uzņēmum", "uznem", "komerclikum"],
    "publiskie_iepirkumi": ["iepirkum", "publisk iepirk"],
}


def guess_topics(title: str, issuer: Optional[str] = None) -> list[str]:
    """Ieteiks tēmas pēc atslēgvārdiem. NAV autoritatīva klasifikācija.

    Skat. docs/ierobezojumi.md — lietotājam UI parādīt, ka tēmu piešķiršana ir
    heuristiska, nevis oficiāla.
    """
    text = (title or "").lower()
    if issuer:
        text += " " + issuer.lower()
    topics: list[str] = []
    for topic, kws in TOPIC_KEYWORDS.items():
        if any(kw.lower() in text for kw in kws):
            topics.append(topic)
    return topics


def parse_date(value) -> Optional[date]:
    """Drošs datuma parsētājs no dažādiem avota formātiem."""
    if value is None or value == "":
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    try:
        return date_parser.parse(str(value), dayfirst=True, fuzzy=True).date()
    except (ValueError, TypeError, OverflowError):
        return None


def classify_doc_type(raw_type: str) -> DocType:
    """Kartē avota dokumenta veida stringu uz mūsu enum."""
    t = (raw_type or "").lower().strip()
    if re.search(r"likum", t):
        return DocType.LIKUMS
    if re.search(r"mk\s*noteikum|ministru\s*kabinet", t):
        return DocType.MK_NOTEIKUMI
    if re.search(r"instrukcij", t):
        return DocType.INSTRUKCIJA
    if re.search(r"vadl[iī]nij", t):
        return DocType.VADLINIJAS
    if re.search(r"datu\s*kopa|dataset", t):
        return DocType.DATU_KOPA
    if re.search(r"pazi[ņn]ojum", t):
        return DocType.PAZINOJUMS
    return DocType.CITS


def classify_status(raw: Optional[str]) -> DocStatus:
    if not raw:
        return DocStatus.NEZINAMS
    s = raw.lower().strip()
    if "zaud" in s:
        return DocStatus.ZAUDEJIS_SPEKU
    if "groz" in s:
        return DocStatus.GROZITS
    if "spēkā" in s or "speka" in s or "sp\u0113k" in s or s in {"active", "in_force"}:
        return DocStatus.SPEKA
    return DocStatus.NEZINAMS
