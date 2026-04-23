# Tiesību aktu un oficiālo datu pārlūks — MVP

Vienota meklēšana pa Latvijas oficiālajiem tiesību aktu un atvērto datu avotiem.
Rīks palīdz atrast un sasaistīt likumus, MK noteikumus, iestāžu vadlīnijas un publiskos datus **tikai no oficiāliem avotiem**.

> **Svarīgi:** Šī sistēma **nav juridiska konsultācija**. Tā ir tikai oficiālu publisku avotu pārlūkošanas rīks. Autoritatīvais teksts vienmēr ir oficiālajā avotā (piem., Latvijas Vēstnesī vai likumi.lv).

## Saturs

```
MVP/
├── README.md               ← šis fails
├── docs/                   ← tehniskā dokumentācija latviski
│   ├── arhitektura.md      ← sistēmas arhitektūra + diagramma
│   ├── datu-modelis.md     ← datu modelis un metadatu lauki
│   ├── avotu-saraksts.md   ← oficiālie avoti un to izmantošanas loģika
│   ├── ierobezojumi.md     ← juridiskie/tehniskie ierobežojumi
│   └── palaisana.md        ← kā palaist sistēmu lokāli
├── backend/                ← FastAPI + SQLite + SQLAlchemy
│   ├── app/
│   │   ├── adapters/       ← avotu adapteri (likumi.lv, data.gov.lv)
│   │   ├── api/            ← REST galapunkti
│   │   ├── models.py       ← SQLAlchemy datu modelis
│   │   ├── schemas.py      ← Pydantic shēmas
│   │   ├── normalizer.py   ← metadatu normalizācija
│   │   └── main.py
│   ├── requirements.txt
│   ├── seed_data.py        ← demo dati (likumi, MK noteikumi, datu kopas)
│   └── import_runner.py    ← reāls imports no oficiālajiem avotiem
└── frontend/               ← React + Vite + Tailwind
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   └── api.js
    ├── package.json
    └── vite.config.js
```

## Ātrā palaišana

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python seed_data.py              # ielādē demo datus SQLite datubāzē
python seed_sections.py          # pievieno dziļu nodaļa/pants/daļa/punkts hierarhiju
uvicorn app.main:app --reload    # palaiž API uz http://localhost:8000
```

API dokumentācija pieejama: <http://localhost:8000/docs>

### Frontend

```bash
cd frontend
npm install
npm run dev                      # palaiž UI uz http://localhost:5173
```

## Galvenās iespējas MVP

- Vienota meklēšana pa oficiālajiem avotiem
- Filtri pēc nozares, iestādes, dokumenta tipa, statusa, datuma
- Dokumentu kartītes ar pilnu metadatu komplektu un saiti uz oficiālo avotu
- Tēmu kolekcijas (grāmatvedība, nodokļi, loģistika, darba tiesības u.c.)
- Tumšais/gaišais režīms, responsīvs dizains
- Audita ieraksts — kad katrs avots pēdējo reizi importēts
- Skaidra datu izcelsme katram ierakstam

## Dokumentācija

Pilna tehniskā dokumentācija atrodama `docs/` mapē. Sāc ar [docs/arhitektura.md](docs/arhitektura.md).

## Ierobežojumi

Sistēma strikti izmanto **tikai** oficiālos publiskos avotus. Detalizēts saraksts: [docs/avotu-saraksts.md](docs/avotu-saraksts.md). Juridiskie un tehniskie ierobežojumi: [docs/ierobezojumi.md](docs/ierobezojumi.md).
