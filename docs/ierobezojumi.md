# Ierobežojumi un piesardzības apsvērumi

Šis dokuments skaidri definē, kur sistēmai ir robežas — gan juridiskas, gan tehniskas.

## Juridiskie ierobežojumi

### 1. Nav juridiska konsultācija

Sistēma ir **pārlūkošanas rīks oficiāliem publiskiem avotiem**, nevis juridiska konsultācija. Katrā UI lapā jābūt skaidrai norādei:

> "Šis rīks nav juridiska konsultācija. Autoritatīvais teksts ir oficiālajā avotā. Pirms rīcības sazinieties ar kvalificētu juristu."

### 2. Autoritatīvais ir oficiālais avots

Sistēma **neveic** tiesību akta "pārrakstīšanu" vai interpretāciju. Visi dokumentu "apraksti" nāk **tieši no oficiālā avota** metadatiem — nekad no automātiskas ģenerēšanas vai pārfrāzēšanas. Tas novērš risku, ka sistēma radītu neprecīzu interpretāciju.

### 3. Pilns teksts netiek glabāts lokāli

Attiecībā uz tiesību aktiem (likumi.lv) sistēma glabā **tikai metadatus un saiti** uz oficiālo publikāciju. Pilnu tekstu lietotājs lasa oficiālajā avotā.

**Papildinājums sekcijām (pants/daļa/punkts):** Lai varētu piedāvāt TOC (satura rādītāju) un meklēšanu panta/punkta līmenī, sistēma glabā:

- hierarhisko struktūru (pants → daļa → punkts → apakšpunkts);
- numurus, virsrakstus un ceļu (piem., "46.1");
- **īsu ievada fragmentu** (`snippet`) — max **~280 rakstzīmes** — pārskatam meklēšanā;
- HTML anchor saiti uz oficiālo publikāciju (piem., `#p5.3`).

Pilnu panta tekstu sistēma **NEGLABĀ** — katrs sekcijas virsraksts/numurs ir deep-link uz `likumi.lv`, kur lietotājs izlasa autoritatīvo tekstu. Snippet garums ir apzināti ierobežots, lai izvairītos no autortiesību riska.

### 4. Licences tiek respektētas

- Atvērto datu kopām (data.gov.lv) parāda licenci katram ierakstam.
- Ja avotā licence nav norādīta — ieraksts tiek iekļauts tikai ar saiti uz oficiālo avotu, bez satura kopēšanas.

## Tehniskie ierobežojumi

### 1. Izmaiņu (grozījumu) izsekošanas ierobežojums

Sistēma var parādīt:

- Dokumenta `status` lauku (spēkā / zaudējis spēku / grozīts), **ja un tikai ja** oficiālais avots šo informāciju izdod strukturētā formā.
- `document_relations` saites (piem., "šis MK noteikumi groza X"), **ja** oficiālais avots to publicē metadatos.

Sistēma **NEVAR** automātiski izsekot izmaiņām tekstā, ja avots neizdod strukturētus grozījumu metadatus. Tas ir norādīts UI katrā kartītē.

### 2. Pilntekst meklēšana ierobežota ar metadatiem

MVP pilntekstu meklēšana (SQLite FTS5) darbojas pār:

- dokumenta nosaukumu
- numuru
- iestādi
- oficiālo kopsavilkumu (ja pieejams avotā)

Meklēšana **pa pilno tiesību akta tekstu nedarbojas**, jo sistēma tekstu neglabā. Lietotājam tiek piedāvāts atvērt oficiālo avotu un veikt meklēšanu tur.

### 3. Tēmu klasifikācija nav pilnībā automātiska

Tēmu klasifikācija (`document_topics`) MVP posmā tiek iegūta:

1. **Primāri** no avota metadatiem (ja data.gov.lv datu kopai ir organizācija "Satiksmes ministrija" → tēma `transports`).
2. **Sekundāri** ar atslēgvārdu palīdzību nosaukumā (piemēram, "pievienotās vērtības nodoklis" → `nodokli`).
3. **Tercārs** — manuāla apstiprināšana datu pārvaldniekam (ja sistēmā būs admin panelis).

Atslēgvārdu pieeja var kļūdīties. Klasifikācija nav autoritatīva — autoritatīvā iestāde un dokumenta saturs paliek oficiālajā avotā.

### 4. Avota struktūras izmaiņas

likumi.lv un citas HTML lapas var mainīt savu struktūru. Tad adapters jāpielāgo. MVP sistēmā tas tiek risināts ar:

- Audita žurnālu (`import_runs`) — ja importi neizdodas, tas tiek reģistrēts.
- Skaidru atsevišķu adapteru slāni — bojājums vienā avotā neietekmē pārējos.

### 5. Rate limiting un etiķete

Adapters, kas lasa HTML lapas:

- Ievēro `robots.txt`.
- Ieliek 2 sekunžu pauzi starp pieprasījumiem.
- Ievieto atpazīstamu `User-Agent` (piem., `TiesibuAktuPārlūks/1.0`).
- Kešo rezultātus, lai neielasītu to pašu nevajadzīgi.

### 6. Privātuma ierobežojumi

MVP posmā sistēma:

- **Neglabā** lietotāju datus (nav reģistrācijas, login).
- **Neseko** lietotāju meklēšanas vēsturei.
- Nelieto trešo pušu analītiku / cookie bannerus.

## Kur pilna automatizācija nav iespējama

| Joma | Iemesls | Risinājums MVP |
|---|---|---|
| Grozījumu konsolidācija | Oficiālais avots neizdod strukturētu diff/patch | Parādīt saiti uz konkrētu redakciju; norādīt "grozīts" statusu |
| Pilnteksta indeksēšana | Licences/autortiesību riski glabāt pilnu tekstu | Meklēšana tikai metadatos |
| Tēmu klasifikācija uz specifiskām apakšnozarēm | Oficiālie avoti neizdod šādas taksonomijas | Manuāla apstiprināšana / heuristika ar skaidru atzīmi |
| Juridiska interpretācija | Ārpus sistēmas mērķa | Jurista konsultācija |
| Tulkojumi uz angļu | Oficiāli tulkojumi pieejami daļēji | Ja `likumi.lv` piedāvā EN saiti, to attēlojam; citādi nē |

## Ko sistēma apzināti NEdara

- Nestāsta lietotājam "kas jādara" juridiskā situācijā.
- Nesaistīsta ar konkrētas personas datiem (privātpersonas vai uzņēmuma specifika — tur ir atsevišķi UR/VID kanāli).
- Nesniedz tikšanos/epastu formā strukturētu atbildi uz juridisku jautājumu.
- Nekopē PDF / HTML pilnu tekstu lokālai glabāšanai.
- Neklasificē dokumentus jomās, kurās nav skaidras sasaistes ar avota metadatiem (rāda "nezinams" kategoriju ar skaidrojumu).

## Kopsavilkums

Sistēmas uzdevums ir **ātri atvērt oficiālo avotu** — ne to aizstāt. Katra kartīte beidzas ar pogu "Atvērt oficiālo avotu", un tā ir galvenais darbības izsaukums.
