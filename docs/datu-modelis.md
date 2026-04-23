# Datu modelis

## Pamatprincipi

1. **Vienots metadatu modelis** — visi avoti tiek normalizēti uz vienu `Document` shēmu.
2. **Nodalīti slāņi** — oficiālais teksts/saite, metadati, iekšējā klasifikācija glabājas atsevišķi.
3. **Obligāts avots** — katram `Document` ierakstam jābūt `official_url`.
4. **Auditējamība** — katrs ieraksts zina, no kura avota un kad tas nāk.

## Tabulas

### `documents`

Galvenā tabula — viens ieraksts = viens oficiāls dokuments (likums, MK noteikumi, datu kopa, vadlīnijas).

| Kolonna | Tips | Obligāts | Apraksts |
|---|---|---|---|
| `id` | int (PK) | jā | iekšējais identifikators |
| `external_id` | str | jā | unikāls avota kontekstā (piem., "likumi.lv:123456") |
| `source` | str | jā | avota kods: `likumi_lv`, `data_gov_lv`, u.c. |
| `doc_type` | enum | jā | `likums`, `mk_noteikumi`, `instrukcija`, `vadlinijas`, `datu_kopa`, `cits` |
| `title` | str | jā | oficiālais nosaukums |
| `number` | str | nē | dokumenta numurs (piem., "Nr. 123") |
| `issuer` | str | nē | atbildīgā iestāde (Saeima, Ministru kabinets, VID u.c.) |
| `adopted_date` | date | nē | pieņemšanas datums |
| `effective_date` | date | nē | spēkā stāšanās datums |
| `status` | enum | jā | `speka`, `zaudejis_speku`, `grozits`, `nezinams` |
| `official_url` | str | jā | URL uz oficiālo publikāciju |
| `summary` | text | nē | īss apraksts (tikai ja avots to nodrošina oficiāli) |
| `license` | str | nē | licences nosaukums (datu kopām — piem., CC-BY) |
| `last_imported` | datetime | jā | audita lauks |
| `created_at` | datetime | jā | ieraksts pirmo reizi saņemts |
| `updated_at` | datetime | jā | pēdējās izmaiņas datumā vai metadatos |

**Indeksi:** `(source, external_id)` unikāls, `doc_type`, `status`, `issuer`, `adopted_date`, `effective_date`.

### `document_topics`

Daudz-pret-daudz saite uz tēmām (viens dokuments var būt vairākās tēmās).

| Kolonna | Tips | Apraksts |
|---|---|---|
| `document_id` | int (FK) | |
| `topic` | str | kods: `nodokli`, `gramatvediba`, `darba_tiesibas`, `logistika`, `transports`, `e_komercija`, `datu_aizsardziba`, `muita`, `komercdarbiba` |

### `document_relations`

Saistīto dokumentu saites (likums → MK noteikumi → vadlīnijas u.c.).

| Kolonna | Tips | Apraksts |
|---|---|---|
| `from_id` | int (FK) | |
| `to_id` | int (FK) | |
| `relation_type` | enum | `implements` (piemēro), `amends` (groza), `replaces` (aizvieto), `related` (saistīts), `references` (atsaucas) |

### `document_sections`

Hierarhiska dokumenta struktūra (pants → daļa → punkts → apakšpunkts). Paredzēts tikai **strukturālajiem metadatiem un īsiem ievada fragmentiem** — autoritatīvais teksts vienmēr tiek lasīts oficiālajā avotā.

| Kolonna | Tips | Obligāts | Apraksts |
|---|---|---|---|
| `id` | int (PK) | jā | |
| `document_id` | int (FK) | jā | vecāka dokumenta ID |
| `parent_id` | int (FK, nullable) | nē | pašreferenca hierarhijai (pants → daļa → punkts) |
| `level` | enum | jā | `sadala`, `nodala`, `pants`, `dala`, `punkts`, `apakspunkts` |
| `number` | str | jā | numurs ("5", "5.3", "IV", "1") |
| `path` | str | jā | hierarhiskais ceļš ("5.3.2") kārtošanai un unikalitātei |
| `title` | str | nē | sekcijas virsraksts, ja ir |
| `snippet` | str (max 400) | nē | īss ievada fragments (≤ ~280 rakstz.) meklēšanai |
| `anchor` | str | nē | HTML anchor oficiālajā avotā (piem., `p5.3`) |
| `sort_order` | int | jā | kārtošanas kārtība pie viena vecāka |

**Indeksi:** `document_id`, `parent_id`, `path`, `level`.

**Kāpēc tāds modelis:**

- **Pašreferenca (`parent_id`)** — ļauj saglabāt neregulāru dziļumu (pants ar daļām, bet bez punktiem, vai otrādi) bez shēmas izmaiņām.
- **`path` lauks** — atļauj `ORDER BY path`, ātru filtrēšanu un URL anchor konstruēšanu.
- **Tikai īsi fragmenti** — izvairāmies no autortiesību riska; pilnais teksts paliek `likumi.lv`.
- **Cascade delete** — atkārtoti importējot dokumentu, vecās sekcijas tiek notīrītas un pārstrādātas.

### `sources`

Avotu reģistrs un audita dati.

| Kolonna | Tips | Apraksts |
|---|---|---|
| `code` | str (PK) | `likumi_lv`, `data_gov_lv` |
| `name` | str | cilvēkam lasāms nosaukums |
| `base_url` | str | |
| `license_notes` | text | licences/izmantošanas piezīmes |
| `last_import_at` | datetime | audits |
| `last_import_count` | int | cik dokumentu ieguts pēdējā importā |
| `last_import_status` | str | `ok`, `partial`, `failed` |
| `last_import_error` | text | kļūdas apraksts |

### `import_runs`

Pilna importēšanas vēsture (audita žurnāls).

| Kolonna | Tips | Apraksts |
|---|---|---|
| `id` | int (PK) | |
| `source` | str (FK) | |
| `started_at` | datetime | |
| `finished_at` | datetime | |
| `status` | str | `ok`, `failed`, `partial` |
| `doc_count` | int | |
| `error_message` | text | |

### `documents_fts` (FTS5 virtuālā tabula)

SQLite FTS5 pilnteksta indekss pār `title`, `number`, `issuer`, `summary` laukiem. Atjauninās caur trigeriem vai manuāli importa laikā.

## Tēmu klasifikatora saraksts

MVP piedāvā šīs tēmas (`document_topics.topic` vērtības):

- `nodokli` — nodokļi
- `gramatvediba` — grāmatvedība
- `darba_tiesibas` — darba tiesības
- `logistika` — loģistika
- `transports` — transports un mobilitāte
- `muita` — muitas regulējums
- `e_komercija` — e-komercija
- `datu_aizsardziba` — datu aizsardzība un digitālais regulējums
- `komercdarbiba` — komercdarbība un uzņēmumu pārvaldība
- `publiskie_iepirkumi` — publiskie iepirkumi

Tēmas tiek **ieteiktas** automātiski (pēc atslēgvārdiem nosaukumā + iestādes), bet **apstiprinātas manuāli** vai caur avota metadatiem, lai izvairītos no neprecīzas klasifikācijas. MVP sēklas datos tēmas tiek piešķirtas tieši.

## Kāpēc tieši šis modelis

- **Avota saite obligāta** — īsteno prasību "katram ierakstam obligāti jābūt avota saitei uz oficiālo publikāciju".
- **`last_imported` un `import_runs`** — īsteno auditējamības prasību.
- **`document_relations`** — īsteno saistīto dokumentu attēlošanu (likums → MK noteikumi → vadlīnijas → atvērtie dati).
- **`status` enum** — īsteno spēkā esamības filtrus.
- **`doc_type` enum** un `source` ir ierobežoti — viegli paplašināmi, bet nepieļauj brīvu tekstu, kas sabojātu meklēšanu.
- **Nodalīts `summary`** — glabā tikai oficiāli publiskus aprakstus; nekad nav automātiska pārrakstīšana, kas varētu radīt neprecīzu interpretāciju.

## Pāreja uz PostgreSQL

SQLite FTS5 aizstājams ar Postgres `tsvector` vai ārēju Meilisearch/Elasticsearch indeksu. Pati tabulu struktūra ir identiska (SQLAlchemy modelis nemainās).
