# Oficiālo avotu saraksts

Šajā dokumentā ir aprakstīts katrs oficiālais avots, kas izmantots sistēmā, tā piekļuves metode, licences apsvērumi un tehniskie ierobežojumi.

> **Princips:** sistēma izmanto **tikai** oficiālus publiskus avotus. Neoficiāli agregatori, komerciālas datubāzes bez oficiāla mandāta, nezināmas izcelsmes PDF un manuāli kopēti dati nav pieļaujami.

## Integrētie avoti (MVP)

### 1. likumi.lv / Latvijas Vēstnesis

| Parametrs | Vērtība |
|---|---|
| URL | <https://likumi.lv> |
| Tips | HTML lapas + atsevišķi RSS feed |
| Oficialitātes statuss | Oficiālais tiesību aktu publikācijas portāls (SIA "Latvijas Vēstnesis") |
| Piekļuves metode | HTTP GET, HTML parsēšana (BeautifulSoup) |
| API | Nav publiska oficiāla REST API |
| Izmantotie dati | Dokumenta metadati: virsraksts, tips, numurs, pieņemšanas datums, spēkā stāšanās, iestāde, URL |
| Pilnteksts | NAV glabāts lokāli — tikai saite uz oficiālo publikāciju |
| Ielasīšanas režīms | Rate limited (2 sek. starp pieprasījumiem), ievēro `robots.txt` |
| Licence / noteikumi | Saturs ir oficiāla publikācija. Sistēma **neglabā** pilnu tekstu — tikai metadatus un saiti atpakaļ uz oficiālo avotu. |

**Adapters:** `backend/app/adapters/likumi_lv.py`

**Ierobežojumi:**

- Nav oficiāla API, tāpēc adapters parsē HTML lapas. Avota struktūras izmaiņas var prasīt adaptera pielāgošanu.
- Sistēma **neglabā pilnu tiesību akta tekstu** — tikai metadatus un saiti. Lietotājs vienmēr tiek novirzīts uz likumi.lv, lai lasītu autoritatīvo redakciju.
- Izmaiņu (grozījumu) izsekošana MVP posmā notiek tikai tiktāl, cik likumi.lv pati atzīmē redakcijas datumus vai `status` lauku.

### 2. data.gov.lv (Latvijas Atvērto datu portāls)

| Parametrs | Vērtība |
|---|---|
| URL | <https://data.gov.lv> |
| API | CKAN v3 API |
| Bāzes API URL | <https://data.gov.lv/dati/lv/api/3/> |
| Galvenie galapunkti | `package_search`, `package_show`, `organization_list`, `group_list` |
| Oficialitātes statuss | Valsts oficiāls atvērto datu portāls (VARAM pārraudzībā) |
| Izmantotie dati | Datu kopu metadati: virsraksts, organizācija, apraksts, licence, resursu URL, pēdējā atjaunināšana |
| Licence | Katrai datu kopai atsevišķi (biežāk CC-BY 4.0) |

**Adapters:** `backend/app/adapters/data_gov_lv.py`

**Piemērs:**

```
GET https://data.gov.lv/dati/lv/api/3/action/package_search?q=transports&rows=10
```

**Izmantošanas loģika:**

- CKAN API ir oficiāls un publisks — nav autentifikācijas prasību lasīšanai.
- Sistēma glabā tikai metadatus un resursu saites. Faili (CSV, JSON, u.c.) netiek kopēti lokāli — lietotājs tos lejupielādē tieši no oficiālā avota.
- Filtrēšana pēc organizācijas ļauj nodalīt transporta (SM), finanšu (VID), u.c. sektorus.

### 3. Valsts ieņēmumu dienests (VID)

| Parametrs | Vērtība |
|---|---|
| URL | <https://www.vid.gov.lv> |
| Tips | Publiskas HTML lapas |
| Publiskie dokumenti | Metodiskie materiāli, nodokļu skaidrojumi, paziņojumi |
| Piekļuves metode | HTTP GET, HTML parsēšana (BeautifulSoup) |
| Indeksa ceļi | `/lv/metodiskie-materiali`, `/lv/nodoklu-skaidrojumi`, `/lv/pazinojumi` |
| Paging | `?page=N`, līdz `MAX_INDEX_PAGES` (noklusēti 5) |
| Izmantotie dati | Virsraksts, saite, datums (ja pieejams), publicētājs |
| Pilnteksts | NAV glabāts lokāli — tikai saite uz vid.gov.lv |
| Ielasīšanas režīms | Rate limited (2 sek.), identificēts User-Agent |

**Adapters:** `backend/app/adapters/vid.py`

**Piezīme:** EDS API (<https://eds.vid.gov.lv>) prasa autentifikāciju un ir paredzēta nodokļu maksātāju datu iesniegšanai — tā **netiek** izmantota dokumentu agregācijā. Sistēma izmanto tikai VID publiskās informatīvās un metodisko materiālu lapas.

### 4. ATD / transportdata.gov.lv

| Parametrs | Vērtība |
|---|---|
| URL | <https://transportdata.gov.lv> |
| API | CKAN v3 API (saderīgs ar data.gov.lv) |
| Bāzes API URL | <https://transportdata.gov.lv/dati/lv/api/3/> |
| Galvenie galapunkti | `package_search`, `package_show` |
| Oficialitātes statuss | Autotransporta direkcijas (ATD) atvērto datu portāls |
| Izmantotie dati | Sabiedriskā transporta datu kopu metadati — maršruti, GTFS, biļešu statistika |
| Licence | Katrai datu kopai atsevišķi (biežāk CC-BY 4.0) |

**Adapters:** `backend/app/adapters/atd.py`

**Piemērs:**

```
GET https://transportdata.gov.lv/dati/lv/api/3/action/package_search?q=marsruti&rows=50
```

**Izmantošanas loģika:**

- Tāds pats CKAN protokols kā data.gov.lv; adapters uzliek `topics=["transports"]` visiem ierakstiem, lai tie parādās transporta tēmas kolekcijā.
- Resursu faili netiek kopēti lokāli — tikai metadati un saites.

## Plānotie avoti (nākotnes iterācijas)

### 5. Uzņēmumu reģistrs (UR)

| Parametrs | Vērtība |
|---|---|
| URL | <https://www.ur.gov.lv> |
| Publiskie dati | Reģistra izraksti, uzņēmumu pamatinformācija |
| API | Daļēji publiska (daži pakalpojumi par maksu) |
| Izmantošana MVP kontekstā | Netiek pievienots MVP iterācijā — biznesa regulējuma kontekstam pietiek ar likumi.lv |

## Skaidri neizmantotie avoti

Sistēma **nedrīkst** iegūt datus no:

- Neoficiāli agregatori vai "tulkotie likumi" portāli (piem., trešās puses juridiskie portāli).
- Komerciālas juridiskas datubāzes (piem., maksas juridisko pakalpojumu sniedzēju arhīvi) bez oficiāla mandāta.
- PDF arhīvi no foruma augšupielādēm, blogiem vai nezināmiem avotiem.
- Manuāli kopēts saturs (kopēt-ielīmēt no Ziņu portāliem u.tml.).

## Licencēšanas apsvērumi

1. **Oficiāli publicēti tiesību akti** — Latvijas tiesību normatīvie akti publikācijas brīdī ir publiski pieejami. Tomēr SIA "Latvijas Vēstnesis" portāla struktūra un papildinformācija (piem., sistematizēti saistījumi) var būt aizsargāti. Tāpēc sistēma glabā **tikai metadatus**, neglabā pilnu tekstu un vienmēr novirza uz oficiālo avotu.
2. **Atvērtie dati (data.gov.lv)** — licences norādītas katrai datu kopai (biežāk CC-BY 4.0). Sistēma saglabā licences lauku un to parāda lietotājam.
3. **VID publiskās lapas** — publiska informācija; ievērot `robots.txt` un polītu rate limiting.

## Datu svaiguma politika

| Avots | Ieteiktā atjaunināšanas frekvence |
|---|---|
| likumi.lv | Reizi diennaktī |
| data.gov.lv | Reizi diennaktī (CKAN metadati) |
| VID | Reizi 3 dienās |
| ATD (transportdata.gov.lv) | Reizi diennaktī (CKAN metadati) |

Katram ierakstam parādās `last_imported` lauks, lai lietotājs redzētu, cik svaigi ir dati.
