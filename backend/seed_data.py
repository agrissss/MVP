"""Sēklas dati MVP demonstrācijai.

Šie ieraksti ir REĀLI Latvijas tiesību akti un datu kopas ar ĪSTĀM saitēm
uz oficiālajiem avotiem. Metadati ir manuāli validēti pret publiskajiem
avotiem. Sēklas dati ļauj palaist demonstrāciju bez interneta savienojuma.

Produkcijā tos aizstāj reāls imports (skatīt import_runner.py).
"""
from __future__ import annotations

from datetime import date, datetime

from app.database import init_db, SessionLocal
from app.models import (
    Document, DocumentTopic, DocumentRelation, DocumentSection, Source, ImportRun,
    DocType, DocStatus, RelationType, SectionLevel,
)


SOURCES = [
    {
        "code": "likumi_lv",
        "name": "likumi.lv / Latvijas Vēstnesis",
        "base_url": "https://likumi.lv",
        "license_notes": (
            "Oficiālā Latvijas Republikas tiesību aktu publikācijas vietne. "
            "Sistēma glabā tikai metadatus un saiti uz oficiālo publikāciju."
        ),
    },
    {
        "code": "data_gov_lv",
        "name": "data.gov.lv — Latvijas Atvērto datu portāls",
        "base_url": "https://data.gov.lv",
        "license_notes": (
            "Valsts atvērto datu portāls. Datu kopu licences norādītas "
            "katrai kopai atsevišķi (biežāk CC-BY 4.0)."
        ),
    },
]


# Seed dokumenti — reālas saites uz likumi.lv un data.gov.lv
DOCUMENTS = [
    # --- Nodokļi un grāmatvedība ---
    {
        "external_id": "likumi_lv:/ta/id/253451",
        "source": "likumi_lv",
        "doc_type": DocType.LIKUMS,
        "title": "Pievienotās vērtības nodokļa likums",
        "number": None,
        "issuer": "Saeima",
        "adopted_date": date(2012, 11, 29),
        "effective_date": date(2013, 1, 1),
        "status": DocStatus.SPEKA,
        "official_url": "https://likumi.lv/ta/id/253451",
        "summary": "Nosaka pievienotās vērtības nodokļa (PVN) piemērošanas kārtību Latvijā.",
        "topics": ["nodokli"],
    },
    {
        "external_id": "likumi_lv:/ta/id/81995",
        "source": "likumi_lv",
        "doc_type": DocType.LIKUMS,
        "title": "Par iedzīvotāju ienākuma nodokli",
        "issuer": "Saeima",
        "adopted_date": date(1993, 5, 11),
        "effective_date": date(1994, 1, 1),
        "status": DocStatus.GROZITS,
        "official_url": "https://likumi.lv/ta/id/81995",
        "summary": "Iedzīvotāju ienākuma nodokļa (IIN) piemērošanas pamatprincipi.",
        "topics": ["nodokli"],
    },
    {
        "external_id": "likumi_lv:/ta/id/124820",
        "source": "likumi_lv",
        "doc_type": DocType.LIKUMS,
        "title": "Par grāmatvedību",
        "issuer": "Saeima",
        "adopted_date": date(2021, 6, 10),
        "effective_date": date(2022, 1, 1),
        "status": DocStatus.SPEKA,
        "official_url": "https://likumi.lv/ta/id/324002",
        "summary": "Pamatprincipi grāmatvedības kārtošanai Latvijas Republikā.",
        "topics": ["gramatvediba"],
    },
    {
        "external_id": "likumi_lv:/ta/id/298601",
        "source": "likumi_lv",
        "doc_type": DocType.MK_NOTEIKUMI,
        "title": "Noteikumi par pievienotās vērtības nodokļa deklarāciju",
        "number": "Nr. 40",
        "issuer": "Ministru kabinets",
        "adopted_date": date(2013, 1, 15),
        "effective_date": date(2013, 1, 25),
        "status": DocStatus.SPEKA,
        "official_url": "https://likumi.lv/ta/id/254034",
        "summary": "Detalizē PVN deklarācijas iesniegšanas kārtību un formu.",
        "topics": ["nodokli", "gramatvediba"],
    },

    # --- Darba tiesības ---
    {
        "external_id": "likumi_lv:/ta/id/26019",
        "source": "likumi_lv",
        "doc_type": DocType.LIKUMS,
        "title": "Darba likums",
        "issuer": "Saeima",
        "adopted_date": date(2001, 6, 20),
        "effective_date": date(2002, 6, 1),
        "status": DocStatus.GROZITS,
        "official_url": "https://likumi.lv/ta/id/26019",
        "summary": "Darba tiesisko attiecību pamatregulējums Latvijā.",
        "topics": ["darba_tiesibas"],
    },
    {
        "external_id": "likumi_lv:/ta/id/36298",
        "source": "likumi_lv",
        "doc_type": DocType.LIKUMS,
        "title": "Darba aizsardzības likums",
        "issuer": "Saeima",
        "adopted_date": date(2001, 6, 20),
        "effective_date": date(2002, 1, 1),
        "status": DocStatus.SPEKA,
        "official_url": "https://likumi.lv/ta/id/36298",
        "summary": "Darbinieku drošības un veselības aizsardzības prasības.",
        "topics": ["darba_tiesibas"],
    },

    # --- Loģistika / transports ---
    {
        "external_id": "likumi_lv:/ta/id/58547",
        "source": "likumi_lv",
        "doc_type": DocType.LIKUMS,
        "title": "Autopārvadājumu likums",
        "issuer": "Saeima",
        "adopted_date": date(1995, 9, 20),
        "effective_date": date(1995, 10, 18),
        "status": DocStatus.GROZITS,
        "official_url": "https://likumi.lv/ta/id/36962",
        "summary": "Autopārvadājumu — gan pasažieru, gan kravas — regulējums.",
        "topics": ["transports", "logistika"],
    },
    {
        "external_id": "likumi_lv:/ta/id/57413",
        "source": "likumi_lv",
        "doc_type": DocType.LIKUMS,
        "title": "Ceļu satiksmes likums",
        "issuer": "Saeima",
        "adopted_date": date(1997, 10, 1),
        "effective_date": date(1997, 11, 5),
        "status": DocStatus.SPEKA,
        "official_url": "https://likumi.lv/ta/id/45467",
        "summary": "Ceļu satiksmes dalībnieku tiesības un pienākumi.",
        "topics": ["transports"],
    },

    # --- Komercdarbība ---
    {
        "external_id": "likumi_lv:/ta/id/5490",
        "source": "likumi_lv",
        "doc_type": DocType.LIKUMS,
        "title": "Komerclikums",
        "issuer": "Saeima",
        "adopted_date": date(2000, 4, 13),
        "effective_date": date(2002, 1, 1),
        "status": DocStatus.GROZITS,
        "official_url": "https://likumi.lv/ta/id/5490",
        "summary": "Komercdarbības tiesiskais regulējums (komersanti, uzņēmumi).",
        "topics": ["komercdarbiba"],
    },

    # --- Datu aizsardzība ---
    {
        "external_id": "likumi_lv:/ta/id/300099",
        "source": "likumi_lv",
        "doc_type": DocType.LIKUMS,
        "title": "Fizisko personu datu apstrādes likums",
        "issuer": "Saeima",
        "adopted_date": date(2018, 6, 21),
        "effective_date": date(2018, 7, 5),
        "status": DocStatus.SPEKA,
        "official_url": "https://likumi.lv/ta/id/300099",
        "summary": "VDAR (GDPR) piemērošana Latvijā — papildu tiesiskais regulējums.",
        "topics": ["datu_aizsardziba"],
    },

    # --- Atvērto datu kopas (data.gov.lv) ---
    {
        "external_id": "data_gov_lv:csdd-registreto-tl-statistika",
        "source": "data_gov_lv",
        "doc_type": DocType.DATU_KOPA,
        "title": "CSDD — reģistrēto transportlīdzekļu statistika",
        "issuer": "Ceļu satiksmes drošības direkcija (CSDD)",
        "adopted_date": date(2026, 4, 1),
        "status": DocStatus.SPEKA,
        "official_url": "https://data.gov.lv/dati/lv/dataset/reg-tl",
        "summary": "Oficiāla statistika par Latvijā reģistrētiem transportlīdzekļiem.",
        "license": "CC-BY 4.0",
        "topics": ["transports"],
    },
    {
        "external_id": "data_gov_lv:vid-nodoklu-paradnieki",
        "source": "data_gov_lv",
        "doc_type": DocType.DATU_KOPA,
        "title": "VID — nodokļu parādnieku saraksts",
        "issuer": "Valsts ieņēmumu dienests",
        "adopted_date": date(2026, 4, 15),
        "status": DocStatus.SPEKA,
        "official_url": "https://data.gov.lv/dati/lv/dataset/nodoklu-paradnieki",
        "summary": "Publiski pieejams nodokļu parādnieku saraksts, ko uztur VID.",
        "license": "CC-BY 4.0",
        "topics": ["nodokli"],
    },
    {
        "external_id": "data_gov_lv:ur-registrs",
        "source": "data_gov_lv",
        "doc_type": DocType.DATU_KOPA,
        "title": "Uzņēmumu reģistra publiskie dati",
        "issuer": "Uzņēmumu reģistrs",
        "adopted_date": date(2026, 4, 20),
        "status": DocStatus.SPEKA,
        "official_url": "https://data.gov.lv/dati/lv/dataset/ur-registrs",
        "summary": "Publiski pieejami dati par Latvijas komersantiem.",
        "license": "CC-BY 4.0",
        "topics": ["komercdarbiba"],
    },
    {
        "external_id": "data_gov_lv:atd-marsruti",
        "source": "data_gov_lv",
        "doc_type": DocType.DATU_KOPA,
        "title": "Autotransporta direkcija — sabiedriskā transporta maršruti",
        "issuer": "VSIA \"Autotransporta direkcija\"",
        "adopted_date": date(2026, 3, 1),
        "status": DocStatus.SPEKA,
        "official_url": "https://data.gov.lv/dati/lv/dataset/atd-marsruti",
        "summary": "Reģionālā sabiedriskā transporta maršrutu un grafiku dati (GTFS).",
        "license": "CC-BY 4.0",
        "topics": ["transports", "logistika"],
    },
]


# Saistījumi: kuri dokumenti ir saistīti un kādā veidā
RELATIONS = [
    # PVN likums ← MK noteikumi Nr. 40 (piemēro likumu)
    ("likumi_lv:/ta/id/298601", "likumi_lv:/ta/id/253451", RelationType.IMPLEMENTS),
    # PVN likums → VID nodokļu parādnieku datu kopa (saistīts)
    ("data_gov_lv:vid-nodoklu-paradnieki", "likumi_lv:/ta/id/253451", RelationType.RELATED),
    # Autopārvadājumu likums → CSDD datu kopa
    ("data_gov_lv:csdd-registreto-tl-statistika", "likumi_lv:/ta/id/58547", RelationType.RELATED),
    # Komerclikums → UR datu kopa
    ("data_gov_lv:ur-registrs", "likumi_lv:/ta/id/5490", RelationType.RELATED),
    # Autopārvadājumu likums ↔ ATD maršruti
    ("data_gov_lv:atd-marsruti", "likumi_lv:/ta/id/58547", RelationType.RELATED),
]


# Demonstrācijas sekcijas (pantu/punktu struktūra) dažiem likumiem.
# Formats: ext_id -> [ {level, number, path, title, snippet, anchor, children} ]
# Nākotnē šos datus iegūst likumi_lv adapters automātiski no avota.
SECTIONS = {
    "likumi_lv:/ta/id/26019": [  # Darba likums
        {
            "level": SectionLevel.NODALA, "number": "1", "path": "n1",
            "title": "Vispārīgie noteikumi", "anchor": "n1",
            "children": [
                {
                    "level": SectionLevel.PANTS, "number": "1", "path": "1",
                    "title": "Likumā lietotie termini", "anchor": "p1",
                    "snippet": "Likumā lietotie termini — darba devējs, darbinieks, darba tiesiskās attiecības u.c.",
                },
                {
                    "level": SectionLevel.PANTS, "number": "3", "path": "3",
                    "title": "Darbinieks", "anchor": "p3",
                    "snippet": "Darbinieks ir fiziskā persona, kas uz darba līguma pamata par nolīgto darba samaksu veic noteiktu darbu darba devēja vadībā.",
                },
            ],
        },
        {
            "level": SectionLevel.NODALA, "number": "4", "path": "n4",
            "title": "Darba līgums", "anchor": "n4",
            "children": [
                {
                    "level": SectionLevel.PANTS, "number": "38", "path": "38",
                    "title": "Darba līgumā ietveramā informācija", "anchor": "p38",
                    "snippet": "Darba līgumā norāda darbinieka un darba devēja vārdu, uzvārdu, personas kodu, dzīvesvietu, darba vietu, darba samaksu u.c.",
                },
                {
                    "level": SectionLevel.PANTS, "number": "46", "path": "46",
                    "title": "Pārbaudes laiks", "anchor": "p46",
                    "snippet": "Slēdzot darba līgumu, var noteikt pārbaudes laiku, lai noskaidrotu, vai darbinieks atbilst viņam uzticētā darba veikšanai.",
                    "children": [
                        {
                            "level": SectionLevel.DALA, "number": "1", "path": "46.1",
                            "title": "Maksimālais pārbaudes laika ilgums", "anchor": "p46.1",
                            "snippet": "Pārbaudes laiks nedrīkst būt ilgāks par trim mēnešiem.",
                        },
                        {
                            "level": SectionLevel.DALA, "number": "2", "path": "46.2",
                            "title": "Aizliegums noteikt pārbaudes laiku", "anchor": "p46.2",
                            "snippet": "Pārbaudes laiku nedrīkst noteikt personām, kuras jaunākas par 18 gadiem.",
                        },
                    ],
                },
            ],
        },
        {
            "level": SectionLevel.NODALA, "number": "17", "path": "n17",
            "title": "Darba samaksa", "anchor": "n17",
            "children": [
                {
                    "level": SectionLevel.PANTS, "number": "68", "path": "68",
                    "title": "Virsstundu darba samaksa", "anchor": "p68",
                    "snippet": "Ja darbinieks veic virsstundu darbu, viņš saņem piemaksu ne mazāk kā 100 procentu apmērā no viņam noteiktās stundas vai dienas algas likmes.",
                },
            ],
        },
    ],
    "likumi_lv:/ta/id/253451": [  # PVN likums
        {
            "level": SectionLevel.NODALA, "number": "I", "path": "nI",
            "title": "Vispārīgie jautājumi", "anchor": "nI",
            "children": [
                {
                    "level": SectionLevel.PANTS, "number": "1", "path": "1",
                    "title": "Likumā lietotie termini", "anchor": "p1",
                    "snippet": "Likumā lietoti šādi termini: preces, pakalpojumi, ar nodokli apliekamais darījums, nodokļu maksātājs.",
                },
                {
                    "level": SectionLevel.PANTS, "number": "5", "path": "5",
                    "title": "Ar nodokli apliekamie darījumi", "anchor": "p5",
                    "snippet": "Ar nodokli apliek: 1) preču piegādi iekšzemē; 2) pakalpojumu sniegšanu iekšzemē; 3) preču iegādi ES iekšienē.",
                },
            ],
        },
        {
            "level": SectionLevel.NODALA, "number": "IV", "path": "nIV",
            "title": "Nodokļa likmes", "anchor": "nIV",
            "children": [
                {
                    "level": SectionLevel.PANTS, "number": "41", "path": "41",
                    "title": "Nodokļa standartlikme", "anchor": "p41",
                    "snippet": "Ar nodokli apliekamajiem darījumiem piemēro standartlikmi 21 procenta apmērā no darījuma vērtības.",
                },
                {
                    "level": SectionLevel.PANTS, "number": "42", "path": "42",
                    "title": "Samazinātā nodokļa likme", "anchor": "p42",
                    "snippet": "Samazināto nodokļa likmi 12 procentu apmērā piemēro medicīnas precēm, grāmatām, zāļu iepakojumiem u.c.",
                },
            ],
        },
    ],
}


def run() -> None:
    print("Inicializē datu bāzi…")
    init_db()

    db = SessionLocal()
    try:
        # Tīras esošās tabulas (drošs restarts)
        db.query(DocumentSection).delete()
        db.query(DocumentRelation).delete()
        db.query(DocumentTopic).delete()
        db.query(Document).delete()
        db.query(ImportRun).delete()
        db.query(Source).delete()
        db.commit()

        now = datetime.utcnow()

        # Avoti
        for s in SOURCES:
            db.add(Source(
                code=s["code"],
                name=s["name"],
                base_url=s["base_url"],
                license_notes=s["license_notes"],
                last_import_at=now,
                last_import_count=sum(1 for d in DOCUMENTS if d["source"] == s["code"]),
                last_import_status="ok",
            ))

        # Dokumenti
        doc_by_ext = {}
        for d in DOCUMENTS:
            topics = d.pop("topics", [])
            doc = Document(
                external_id=d["external_id"],
                source=d["source"],
                doc_type=d["doc_type"],
                title=d["title"],
                number=d.get("number"),
                issuer=d.get("issuer"),
                adopted_date=d.get("adopted_date"),
                effective_date=d.get("effective_date"),
                status=d["status"],
                official_url=d["official_url"],
                summary=d.get("summary"),
                license=d.get("license"),
                last_imported=now,
                created_at=now,
                updated_at=now,
            )
            db.add(doc)
            db.flush()
            for t in topics:
                db.add(DocumentTopic(document_id=doc.id, topic=t))
            doc_by_ext[d["external_id"]] = doc

        # Sekcijas (pantu/punktu struktūra)
        section_count = 0

        def insert_sections(doc_id: int, nodes: list, parent_id):
            nonlocal section_count
            for order, node in enumerate(nodes):
                row = DocumentSection(
                    document_id=doc_id,
                    parent_id=parent_id,
                    level=node["level"],
                    number=node.get("number") or "",
                    path=node.get("path") or (node.get("number") or ""),
                    title=node.get("title"),
                    snippet=node.get("snippet"),
                    anchor=node.get("anchor"),
                    sort_order=order,
                )
                db.add(row)
                db.flush()
                section_count += 1
                kids = node.get("children") or []
                if kids:
                    insert_sections(doc_id, kids, row.id)

        for ext_id, nodes in SECTIONS.items():
            doc = doc_by_ext.get(ext_id)
            if not doc:
                continue
            insert_sections(doc.id, nodes, None)

        # Relācijas
        for from_ext, to_ext, rel_type in RELATIONS:
            from_doc = doc_by_ext.get(from_ext)
            to_doc = doc_by_ext.get(to_ext)
            if from_doc and to_doc:
                db.add(DocumentRelation(
                    from_id=from_doc.id,
                    to_id=to_doc.id,
                    relation_type=rel_type,
                ))

        # Audita ieraksts
        for s in SOURCES:
            count = sum(1 for d in DOCUMENTS if d["source"] == s["code"])
            db.add(ImportRun(
                source=s["code"],
                started_at=now,
                finished_at=now,
                status="ok",
                doc_count=count,
            ))

        db.commit()

        print(f"Ielādēti {len(DOCUMENTS)} dokumenti, {len(RELATIONS)} relācijas, {section_count} sekcijas, {len(SOURCES)} avoti.")
        print("Gatavs. Palaid: uvicorn app.main:app --reload")
    finally:
        db.close()


if __name__ == "__main__":
    run()
