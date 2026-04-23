# Palaišana un izstrāde

## Priekšnosacījumi

- Python 3.11 vai jaunāks
- Node.js 20 vai jaunāks
- (Neobligāti) Git

## Backend palaišana

```bash
cd backend

# 1. Virtuālā vide
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# vai
.venv\Scripts\activate             # Windows PowerShell

# 2. Atkarības
pip install -r requirements.txt

# 3. Sēklas dati (SQLite datubāze ar demo dokumentiem)
python seed_data.py

# 4. Palaist API
uvicorn app.main:app --reload
```

API būs pieejams: <http://localhost:8000>
Interaktīvā dokumentācija: <http://localhost:8000/docs>

### Reāls imports no oficiālajiem avotiem

Sēklas dati ir demonstrācijai. Lai ielasītu datus no reāliem oficiālajiem avotiem:

```bash
# data.gov.lv CKAN API (drošs un oficiāls)
python import_runner.py --source data_gov_lv --limit 50

# likumi.lv (piesardzīgi — rate limited)
python import_runner.py --source likumi_lv --limit 10
```

> **Piezīme:** `likumi_lv` adapters ievēro `robots.txt` un 2 sekunžu pauzi starp pieprasījumiem. Liels `--limit` aizņems laiku.

### Importa plānošana (produkcija)

MVP neietver cron shēduli, bet arhitektūra to atbalsta. Ieteiktā konfigurācija:

```cron
# Reizi diennaktī plkst. 03:00
0 3 * * * cd /path/to/backend && .venv/bin/python import_runner.py --source data_gov_lv
15 3 * * * cd /path/to/backend && .venv/bin/python import_runner.py --source likumi_lv
```

## Frontend palaišana

```bash
cd frontend
npm install
npm run dev
```

UI būs pieejams: <http://localhost:5173>

Vite dev serveris proksē `/api/*` pieprasījumus uz backend (http://localhost:8000).

## Ražošanas būve

### Backend

```bash
# ar gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend

```bash
cd frontend
npm run build          # ģenerē dist/ mapi
# servējiet dist/ ar nginx / Caddy / Vercel u.c.
```

Produkcijā iestatiet `VITE_API_URL` environment mainīgo, ja API ir citā hostā.

## Vides mainīgie

| Mainīgais | Noklusējums | Apraksts |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data.db` | SQLAlchemy savienojuma URL |
| `CORS_ORIGINS` | `http://localhost:5173` | atļautie frontend hosti |
| `USER_AGENT` | `TiesibuAktuPārlūks/1.0` | HTTP User-Agent adapteriem |
| `FETCH_DELAY_SEC` | `2.0` | pauze starp likumi.lv pieprasījumiem |
| `VITE_API_URL` (frontend) | `/api` | backend saknes URL |

## Datubāzes migrācijas

MVP izmanto SQLAlchemy `create_all()` (bez Alembic). Pāreja uz Alembic nākotnes iterācijā:

```bash
pip install alembic
alembic init migrations
# pielāgojiet env.py, lai norādītu uz app.models.Base
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

## Testi (nākotnē)

```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest
```

MVP iekļauj pamata smoke testus `backend/tests/` (ja izveidoti).

## Problēmu atrisināšana

### "sqlite3.OperationalError: no such table"

Palaidiet `python seed_data.py` — tas izveido tabulas un ielādē demo datus.

### Shēmas izmaiņas (pievienoti jauni lauki vai tabulas)

MVP izmanto `create_all()`, kas **nepievieno** kolonnas esošām tabulām. Ja shēma mainās (piem., pievienota `document_sections` tabula):

```bash
# 1. Apstādiniet uvicorn
# 2. Izdzēsiet SQLite failu
rm backend/data.db        # Linux/macOS
del backend\data.db       # Windows

# 3. Palaidiet seed_data.py no jauna
cd backend
python seed_data.py
```

Produkcijā šo aizstāj ar Alembic migrācijām (skat. sadaļu "Datubāzes migrācijas").

### Frontend redzams, bet dati netiek ielādēti

Pārbaudiet, vai backend darbojas uz :8000. Frontend Vite proksē ir konfigurēts `frontend/vite.config.js`.

### CORS kļūda pārlūkā

Pievienojiet frontend URL `CORS_ORIGINS` vides mainīgajā.

### likumi.lv imports neizdodas

Ticamākais iemesls — avota HTML struktūra ir mainījusies. Pārbaudiet `backend/app/adapters/likumi_lv.py` selektorus. Audita žurnāls (`import_runs` tabula) parāda kļūdas tekstu.
