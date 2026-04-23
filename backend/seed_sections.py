"""Bagātinātas sekciju seed dati — dziļa hierarhija (nodaļa → pants → daļa → punkts).

Palaižams PĒC seed_data.py — dzēš esošās sekcijas un ievieto bagātāku struktūru
vairākiem galvenajiem likumiem. MVP galvenā doma: viegli un ātri sekot līdzi
likumiem — tāpēc katrs likums ir sadalīts nodaļās, pantos un to sīkākās daļās
ar īsiem fragmentiem, kas palīdz orientēties.

Šie dati ir vienkāršoti izvilkumi demonstrācijai. Autoritatīvais teksts vienmēr
atrodas oficiālajā avotā (likumi.lv).
"""
from __future__ import annotations

from app.database import SessionLocal
from app.models import Document, DocumentSection, SectionLevel


# ---------- Palīgi sekciju veidošanai ----------

def N(number, title, anchor, children):
    """Nodaļa."""
    return {
        "level": SectionLevel.NODALA,
        "number": number,
        "path": f"n{number}",
        "title": title,
        "anchor": anchor,
        "children": children,
    }

def P(number, title, snippet, anchor=None, children=None):
    """Pants."""
    return {
        "level": SectionLevel.PANTS,
        "number": number,
        "path": number,
        "title": title,
        "snippet": snippet,
        "anchor": anchor or f"p{number}",
        "children": children or [],
    }

def D(parent_pants, number, snippet, title=None, children=None):
    """Daļa — apakšvienība pantā."""
    return {
        "level": SectionLevel.DALA,
        "number": number,
        "path": f"{parent_pants}.{number}",
        "title": title,
        "snippet": snippet,
        "anchor": f"p{parent_pants}.{number}",
        "children": children or [],
    }

def PT(parent, number, snippet, title=None):
    """Punkts — saraksta vienums."""
    return {
        "level": SectionLevel.PUNKTS,
        "number": number,
        "path": f"{parent}.{number}",
        "title": title,
        "snippet": snippet,
        "anchor": f"pt{parent}.{number}",
        "children": [],
    }


# ---------- Bagātināti sekciju koki ----------

SECTIONS = {

    # =========================================================================
    # DARBA LIKUMS — 9 nodaļas, 40+ panti, 80+ daļas
    # =========================================================================
    "likumi_lv:/ta/id/26019": [
        N("1", "Vispārīgie noteikumi", "n1", [
            P("1", "Likumā lietotie termini",
              "Likumā lietoti šādi termini: darba devējs, darbinieks, darba tiesiskās attiecības, darba koplīgums, arodbiedrība, darba samaksa u.c."),
            P("2", "Likuma darbības joma",
              "Šis likums regulē darba tiesiskās attiecības starp darba devēju un darbinieku."),
            P("3", "Darbinieks",
              "Darbinieks ir fiziskā persona, kas uz darba līguma pamata par nolīgto darba samaksu veic noteiktu darbu darba devēja vadībā."),
            P("4", "Darba devējs",
              "Darba devējs ir fiziskā vai juridiskā persona vai arī tiesībspējīga personālsabiedrība, kas uz darba līguma pamata nodarbina vismaz vienu darbinieku."),
            P("5", "Darba tiesisko attiecību tiesiskā regulējuma avoti",
              "Darba tiesiskās attiecības regulē šis likums, citi normatīvie akti, darba koplīgums un darba līgums."),
            P("7", "Vienlīdzīgas attieksmes princips",
              "Ikvienam ir vienlīdzīgas tiesības uz darbu, taisnīgiem, drošiem un veselībai nekaitīgiem darba apstākļiem, kā arī uz taisnīgu darba samaksu.",
              children=[
                  D("7", "1", "Atšķirīgas attieksmes aizliegums atkarībā no darbinieka rases, ādas krāsas, dzimuma, vecuma, invaliditātes, reliģiskās, politiskās vai citas pārliecības."),
                  D("7", "2", "Atšķirīga attieksme pieļaujama tikai tad, ja tai ir objektīvs pamats un likumīgs mērķis."),
                  D("7", "3", "Personai, kura uzskata, ka pret viņu izrādīta atšķirīga attieksme, ir tiesības prasīt atšķirīgas attieksmes izbeigšanu un zaudējumu atlīdzību."),
              ]),
            P("9", "Aizliegums radīt nelabvēlīgas sekas",
              "Aizliegts sodīt darbinieku vai citādi tieši vai netieši radīt viņam nelabvēlīgas sekas tāpēc, ka darbinieks pieļaujamā veidā izmanto savas tiesības.",
              children=[
                  D("9", "1", "Nelabvēlīgo seku radīšanas aizliegums attiecas arī uz lieciniekiem un personām, kas palīdz darbiniekam izmantot tiesības."),
                  D("9", "2", "Ja darba devējs pārkāpj šo aizliegumu, darbiniekam ir tiesības uz zaudējumu atlīdzību un morālā kaitējuma kompensāciju."),
              ]),
            P("10", "Darbinieka tiesības apvienoties organizācijās",
              "Darbiniekiem ir tiesības brīvi bez jebkādas tiešas vai netiešas diskriminācijas apvienoties organizācijās, lai aizstāvētu savas sociālās, ekonomiskās un profesionālās intereses."),
            P("11", "Darba devēja tiesības apvienoties organizācijās",
              "Darba devējiem ir tiesības brīvi apvienoties organizācijās un to apvienībās, lai aizstāvētu un pārstāvētu savas intereses."),
        ]),

        N("2", "Koplīgums", "n2", [
            P("18", "Koplīguma puses",
              "Koplīgumu uzņēmumā slēdz darba devējs un darbinieku arodbiedrība vai darbinieku pilnvaroti pārstāvji, ja uzņēmumā nedarbojas arodbiedrība."),
            P("19", "Koplīgumā ietveramie noteikumi",
              "Koplīgumā puses vienojas par darba samaksu, darba aizsardzību, darba un atpūtas laiku, darba līguma noslēgšanas un izbeigšanas kārtību u.c.",
              children=[
                  D("19", "1", "Koplīguma noteikumi nedrīkst pasliktināt darbinieka tiesisko stāvokli salīdzinājumā ar likumu."),
                  D("19", "2", "Koplīguma noteikumi, kas pasliktina darbinieka stāvokli, nav spēkā."),
              ]),
            P("20", "Koplīguma noslēgšanas kārtība",
              "Koplīgumu slēdz rakstveidā. Koplīguma projektu puses apspriež sarunu ceļā."),
            P("23", "Koplīguma spēkā stāšanās un darbības ilgums",
              "Koplīgums stājas spēkā tā parakstīšanas dienā, ja koplīgumā nav noteikts citādi."),
        ]),

        N("4", "Darba līgums", "n4", [
            P("28", "Darba līguma jēdziens un tā puses",
              "Ar darba līgumu darbinieks uzņemas veikt noteiktu darbu, pakļaujoties darba devēja noteiktai darba kārtībai un rīkojumiem, bet darba devējs — maksāt nolīgto darba samaksu."),
            P("29", "Atšķirīgas attieksmes aizliegums, dibinot darba tiesiskās attiecības",
              "Dibinot darba tiesiskās attiecības, darba devējam aizliegts izrādīt atšķirīgu attieksmi atkarībā no personas dzimuma, vecuma u.c. pazīmēm.",
              children=[
                  D("29", "1", "Darba devējam ir pienākums pamatot, ka atšķirīga attieksme nav izrādīta."),
                  D("29", "8", "Personai, kurai nepamatoti atteikts pieņemt darbā, ir tiesības prasīt zaudējumu atlīdzību un morālā kaitējuma kompensāciju."),
              ]),
            P("32", "Darba sludinājums",
              "Darba sludinājumā aizliegts norādīt ierobežojumus pēc dzimuma, vecuma, tautības u.c. pazīmēm, izņemot gadījumus, kad tam ir objektīvs pamats."),
            P("33", "Darba intervija",
              "Darba intervijā darba devējs nedrīkst uzdot jautājumus, kas nav saistīti ar veicamo darbu vai darbinieka piemērotību.",
              children=[
                  D("33", "1", "Aizliegts jautāt par grūtniecību, ģimenes stāvokli, reliģisko pārliecību, sodāmību (izņemot ar darbu saistītos gadījumos)."),
                  D("33", "2", "Darbiniekam nav pienākuma uz šādiem jautājumiem atbildēt."),
              ]),
            P("37", "Aizliegums nodarbināt personas, kuras ir jaunākas par 15 gadiem",
              "Aizliegts darba tiesiskajās attiecībās nodarbināt personas, kuras ir jaunākas par 15 gadiem, izņemot likumā paredzētos gadījumus."),
            P("38", "Darba līgumā ietveramā informācija",
              "Darba līgumā norāda darbinieka un darba devēja vārdu, uzvārdu, personas kodu, dzīvesvietu/juridisko adresi, darba vietu, amatu, līguma noslēgšanas un darba uzsākšanas dienu.",
              children=[
                  D("38", "1", "Obligātie elementi: puses, darba vieta, amats, darba līguma termiņš, darba samaksas apmērs un izmaksas kārtība.",
                    children=[
                        PT("38.1", "1", "Vārds, uzvārds, personas kods, dzīvesvieta/juridiskā adrese."),
                        PT("38.1", "2", "Darba uzsākšanas diena un līguma ilgums."),
                        PT("38.1", "3", "Darba vieta un amats (ieņemamās amata nosaukums)."),
                        PT("38.1", "4", "Darba samaksas apmērs un izmaksas termiņš."),
                        PT("38.1", "5", "Nolīgtais dienas vai nedēļas darba laiks."),
                        PT("38.1", "6", "Ikgadējā apmaksātā atvaļinājuma ilgums."),
                        PT("38.1", "7", "Uzteikuma termiņš."),
                    ]),
                  D("38", "2", "Ja darba līgumā nav norādīts termiņš, uzskatāms, ka tas noslēgts uz nenoteiktu laiku."),
                  D("38", "3", "Darbiniekam, ko nosūta darbā uz ārvalstīm uz laiku, kas ilgāks par mēnesi, papildus norādāms paredzamais darba ilgums, valūta, piemaksas u.c."),
              ]),
            P("39", "Darba līguma noslēgšana",
              "Darba līgums uzskatāms par noslēgtu no brīža, kad darbinieks un darba devējs ir vienojušies par darba līguma noteikumiem."),
            P("40", "Darba līguma forma",
              "Darba līgums slēdzams rakstveidā. Viens eksemplārs glabājas pie darba devēja, otrs — pie darbinieka.",
              children=[
                  D("40", "1", "Ja darba līgums nav noslēgts rakstveidā, darba līguma noslēgšanu darbiniekam jāpierāda ar visiem pieļaujamajiem pierādījumiem."),
                  D("40", "2", "Rakstveida forma neattiecas uz gadījumu, kad darbs jau uzsākts un puses praktiski pilda darba līguma nosacījumus."),
              ]),
            P("41", "Darba līguma paraugs",
              "Darba līguma paraugs nav obligāts, bet puses var izmantot Ministru kabineta apstiprinātu paraugu."),
            P("44", "Darba līgums uz noteiktu laiku",
              "Darba līgumu uz noteiktu laiku var noslēgt tikai likumā paredzētajos gadījumos (sezonas darbs, aizstājējs, konkrēts projekts u.c.).",
              children=[
                  D("44", "1", "Maksimālais termiņa līguma ilgums — pieci gadi, ieskaitot pagarinājumus."),
                  D("44", "2", "Termiņa līgumu var noslēgt sezonas darbam, konkrētu pasākumu veikšanai, projekta darbam u.c."),
                  D("44", "3", "Darba devējs nedrīkst noslēgt termiņa līgumu tādu pienākumu izpildei, kas ir ikdienišķi un pastāvīgi."),
                  D("44", "4", "Ja darbinieks turpina strādāt pēc termiņa beigām un neviena puse to neapstrīd, līgums uzskatāms par noslēgtu uz nenoteiktu laiku."),
              ]),
            P("45", "Termiņa pagarināšana",
              "Termiņa darba līgumu pusēm rakstveidā vienojoties var pagarināt, bet kopējais termiņš nedrīkst pārsniegt piecus gadus."),
            P("46", "Pārbaudes laiks",
              "Slēdzot darba līgumu, var noteikt pārbaudes laiku, lai noskaidrotu, vai darbinieks atbilst veicamajam darbam.",
              children=[
                  D("46", "1", "Pārbaudes laiks nedrīkst būt ilgāks par trim mēnešiem."),
                  D("46", "2", "Pārbaudes laiku nedrīkst noteikt personām, kuras ir jaunākas par 18 gadiem."),
                  D("46", "3", "Pārbaudes laikā neieskaita darbinieka pārejošas darba nespējas laiku."),
                  D("46", "4", "Pārbaudes laiks jānorāda darba līgumā rakstveidā."),
                  D("46", "5", "Pārbaudes laikā darba devējam un darbiniekam ir tiesības rakstveidā uzteikt darba līgumu trīs dienas iepriekš."),
              ]),
            P("47", "Darba līguma uzteikums pārbaudes laikā",
              "Pārbaudes laikā rakstveida uzteikums jāizsniedz ne vēlāk kā trīs dienas iepriekš. Uzteikuma pamatojumu norādīt nav obligāti."),
            P("50", "Pienākums informēt darbinieku par darba apstākļiem",
              "Darba devējam ir pienākums darba līgumā vai atsevišķā dokumentā rakstveidā informēt darbinieku par būtiskiem darba apstākļiem."),
        ]),

        N("5", "Darba laiks", "n5", [
            P("131", "Darba laika jēdziens",
              "Darba laiks ir laika posms no darba sākuma līdz beigām, kura ietvaros darbinieks veic darbu un atrodas darba devēja rīcībā.",
              children=[
                  D("131", "1", "Darba laikā neieskaita ikdienas un ikgadējā atpūtas laiku, izņemot likumā noteiktos gadījumus."),
                  D("131", "2", "Īstermiņa pārtraukumi, kas tiek dotie darba procesa ietvaros, ieskaitāmi darba laikā."),
              ]),
            P("132", "Normālais darba laiks",
              "Darbinieka normālais dienas darba laiks nedrīkst pārsniegt astoņas stundas, bet normālais nedēļas darba laiks — 40 stundas.",
              children=[
                  D("132", "1", "Piecu darba dienu nedēļā dienas darba laiks — astoņas stundas."),
                  D("132", "2", "Sešu darba dienu nedēļā dienas darba laiks nedrīkst pārsniegt septiņas stundas."),
                  D("132", "3", "Nedēļā pirms svētku dienām dienas darba laiks saīsināms par vienu stundu."),
              ]),
            P("133", "Saīsinātais darba laiks",
              "Saīsināts darba laiks nosakāms pusaudžiem, personām, kuras strādā apstākļos ar īpašu risku, u.c."),
            P("134", "Nepilns darba laiks",
              "Darbinieks un darba devējs var vienoties par nepilna darba laika noteikšanu.",
              children=[
                  D("134", "1", "Nepilns darba laiks ir īsāks par normālu dienas vai nedēļas darba laiku."),
                  D("134", "2", "Darbiniekam, kurš strādā nepilnu darba laiku, nedrīkst piemērot atšķirīgu attieksmi."),
                  D("134", "4", "Pēc darbinieka rakstveida pieprasījuma darba devējam jāpāriet uz nepilnu darba laiku, ja tam ir pamatoti iemesli."),
              ]),
            P("136", "Virsstundu darbs",
              "Virsstundu darbs ir darbs, kuru darbinieks veic virs normālā darba laika.",
              children=[
                  D("136", "1", "Virsstundu darbs pieļaujams tikai ar darbinieka rakstveida piekrišanu."),
                  D("136", "2", "Virsstundu darbu bez darbinieka piekrišanas darba devējs var norīkot tikai izņēmuma gadījumos (nelaimes gadījumos, avārijās)."),
                  D("136", "3", "Aizliegts norīkot virsstundu darbu grūtniecēm, sievietēm pēcdzemdību periodā, pusaudžiem."),
                  D("136", "5", "Virsstundu darbs nedrīkst pārsniegt vidēji astoņas stundas nedēļā četru mēnešu pārskata periodā."),
              ]),
            P("138", "Nakts darbs",
              "Nakts darbs ir darbs, kas tiek veikts laikā no pulksten 22:00 līdz 6:00, ja šis laiks ir vismaz divas stundas.",
              children=[
                  D("138", "1", "Nakts darbinieks ir darbinieks, kurš vismaz 50 dienu gadā strādā nakts laikā."),
                  D("138", "2", "Aizliegts nodarbināt nakts darbā grūtnieces, sievietes pēcdzemdību periodā, pusaudžus."),
              ]),
            P("140", "Summētais darba laiks",
              "Ja darba īpatnību dēļ nav iespējams ievērot normālo dienas vai nedēļas darba laiku, darba devējs var noteikt summēto darba laiku."),
            P("142", "Ikdienas un ikgadējais atpūtas laiks",
              "Darbiniekam pēc ikdienas darba jānodrošina atpūtas laiks, kas ilgst vismaz 12 stundas bez pārtraukuma."),
            P("143", "Nedēļas atpūtas laiks",
              "Darbiniekam septiņu dienu periodā jānodrošina atpūtas laiks vismaz 42 stundas bez pārtraukuma."),
            P("145", "Pārtraukumi darbā",
              "Darbiniekam, kura darba laiks pārsniedz sešas stundas, nodrošināms pārtraukums ne īsāks par 30 minūtēm.",
              children=[
                  D("145", "1", "Pārtraukumu neieskaita darba laikā, ja vien koplīgumā vai darba līgumā nav noteikts citādi."),
                  D("145", "2", "Pārtraukuma laikā darbinieks drīkst atstāt savu darba vietu."),
              ]),
        ]),

        N("9", "Darba tiesisko attiecību izbeigšana", "n9", [
            P("100", "Darbinieka uzteikums",
              "Darbiniekam ir tiesības rakstveidā uzteikt darba līgumu vienu mēnesi iepriekš, ja darba koplīgumā vai darba līgumā nav noteikts īsāks termiņš.",
              children=[
                  D("100", "1", "Uzteikuma termiņš skaitāms no dienas, kad darba devējs saņēmis uzteikumu."),
                  D("100", "5", "Darbiniekam ir tiesības uzteikt darba līgumu nekavējoties, ja tam ir svarīgs iemesls."),
              ]),
            P("101", "Darba devēja uzteikums",
              "Darba devējam ir tiesības rakstveidā uzteikt darba līgumu tikai uz likumā noteiktu pamatu.",
              children=[
                  D("101", "1", "Uzteikuma pamati: darbinieka rupjš darba pienākumu pārkāpums; nespēja veikt darbu veselības stāvokļa dēļ; amata skaita samazināšana; uzņēmuma likvidācija u.c.",
                    children=[
                        PT("101.1", "1", "Darbinieks bez attaisnojoša iemesla būtiski pārkāpis darba līgumu vai darba kārtību."),
                        PT("101.1", "2", "Darbinieks, veicot darbu, rīkojies prettiesiski un tādējādi zaudējis darba devēja uzticību."),
                        PT("101.1", "3", "Darbinieks, veicot darbu, rīkojies pretēji labiem tikumiem."),
                        PT("101.1", "7", "Darbinieks nespēj veikt nolīgto darbu veselības stāvokļa dēļ."),
                        PT("101.1", "9", "Tiek samazināts darbinieku skaits."),
                        PT("101.1", "10", "Tiek likvidēts darba devējs."),
                    ]),
                  D("101", "6", "Uzteikuma pamatojumu darba devējs izklāstā rakstveidā darbinieka izsniegtajā uzteikumā."),
              ]),
            P("102", "Darba devēja uzteikuma termiņi",
              "Uzteikuma termiņi ir atkarīgi no uzteikuma pamata un ir no 10 dienām līdz vienam mēnesim.",
              children=[
                  D("102", "1", "Uzteikums 10 dienas iepriekš — ja pārkāpums ir rupjš."),
                  D("102", "2", "Uzteikums viens mēnesis iepriekš — ja darbinieks nespēj veikt darbu veselības dēļ."),
                  D("102", "3", "Uzteikums viens mēnesis iepriekš — ja tiek samazināts darbinieku skaits."),
              ]),
            P("109", "Aizliegums uzteikt darba līgumu",
              "Darba devējam ir aizliegts uzteikt darba līgumu ar grūtnieci, sievieti pēcdzemdību periodā, personām, kuras kopj bērnu līdz 4 gadu vecumam.",
              children=[
                  D("109", "1", "Aizliegums nav piemērojams, ja darba devējs tiek likvidēts."),
                  D("109", "2", "Aizliegums nav piemērojams, ja darbinieks būtiski pārkāpis darba līgumu."),
              ]),
            P("112", "Atlaišanas pabalsts",
              "Atlaižot darbinieku saskaņā ar darba devēja uzteikumu, izmaksājams atlaišanas pabalsts.",
              children=[
                  D("112", "1", "Viena mēneša vidējā izpeļņa — ja darbinieks nostrādājis mazāk par 5 gadiem."),
                  D("112", "2", "Divu mēnešu vidējā izpeļņa — ja nostrādājis no 5 līdz 10 gadiem."),
                  D("112", "3", "Triju mēnešu vidējā izpeļņa — ja nostrādājis no 10 līdz 20 gadiem."),
                  D("112", "4", "Četru mēnešu vidējā izpeļņa — ja nostrādājis vairāk par 20 gadiem."),
              ]),
            P("113", "Darba devēja pienākums izsniegt izziņu",
              "Darba devējam darbinieka prasījuma gadījumā ir pienākums izsniegt izziņu par darba tiesisko attiecību ilgumu un nolīgto darba samaksu."),
            P("117", "Darba strīdu izšķiršana",
              "Individuālos darba strīdus, kurus nav izdevies atrisināt sarunu ceļā, izšķir tiesa."),
        ]),

        N("10", "Atvaļinājumi", "n10", [
            P("149", "Ikgadējais apmaksātais atvaļinājums",
              "Darbiniekam katru gadu piešķirams ikgadējais apmaksātais atvaļinājums.",
              children=[
                  D("149", "1", "Ikgadējā apmaksātā atvaļinājuma ilgums ir četras kalendāra nedēļas (28 kalendārās dienas), neieskaitot svētku dienas."),
                  D("149", "2", "Atvaļinājumu var sadalīt, taču viena daļa nedrīkst būt īsāka par divām nepārtrauktām kalendāra nedēļām."),
                  D("149", "3", "Atvaļinājumu piešķir par katru darba gadu."),
                  D("149", "4", "Atvaļinājuma laiku nosaka, pusēm vienojoties, ņemot vērā uzņēmuma darba organizācijas vajadzības."),
              ]),
            P("150", "Pirmā darba gada atvaļinājums",
              "Tiesības uz pilnu atvaļinājumu darbinieks iegūst pēc sešu mēnešu nepārtrauktas nodarbinātības pie viena darba devēja."),
            P("151", "Atvaļinājuma pārnešana",
              "Atvaļinājumu var pārnest uz nākamo gadu, ja tā piešķiršana kārtējā gadā nebūtu iespējama, taču ne vēlāk kā uz nākamo gadu."),
            P("152", "Papildatvaļinājums",
              "Papildatvaļinājums piešķirams darbiniekiem, kuri ir saistīti ar īpašu risku, strādā nakts darbu vai audzina bērnus.",
              children=[
                  D("152", "1", "Darbiniekiem, kuriem ir trīs un vairāk bērnu līdz 16 gadu vecumam, — trīs darba dienas."),
                  D("152", "3", "Darbiniekiem, kuru darbs saistīts ar īpašu risku, — līdz divām kalendāra nedēļām."),
                  D("152", "4", "Darbiniekiem, kas strādā ilgstošu nakts darbu, — trīs darba dienas."),
              ]),
            P("153", "Ikgadējā atvaļinājuma apmaksa",
              "Ikgadējā apmaksātā atvaļinājuma laikā darbiniekam izmaksā vidējo izpeļņu, kas aprēķināta par pēdējiem sešiem kalendāra mēnešiem."),
            P("154", "Grūtniecības un dzemdību atvaļinājums",
              "Sievietei piešķirams grūtniecības atvaļinājums — 56 kalendārās dienas un dzemdību atvaļinājums — 56 kalendārās dienas.",
              children=[
                  D("154", "1", "Grūtniecības un dzemdību atvaļinājums tiek aprēķināts kopā — 112 kalendārās dienas."),
                  D("154", "2", "Ja dzemdības ir sarežģītas, atvaļinājumu pagarina par 14 kalendārajām dienām."),
              ]),
            P("155", "Bērna kopšanas atvaļinājums",
              "Ikvienam darbiniekam sakarā ar bērna piedzimšanu vai adopciju ir tiesības uz bērna kopšanas atvaļinājumu uz laiku, kas nav ilgāks par pusotru gadu."),
            P("156", "Atvaļinājums bez darba samaksas saglabāšanas",
              "Darba devējs var piešķirt atvaļinājumu bez darba samaksas saglabāšanas, pusēm par to vienojoties."),
            P("157", "Mācību atvaļinājums",
              "Darbiniekam, kas bez darba pārtraukšanas mācās izglītības iestādē, piešķirams mācību atvaļinājums ar darba samaksas saglabāšanu vai bez tās."),
        ]),

        N("17", "Darba samaksa", "n17", [
            P("62", "Darba samaksas jēdziens",
              "Darba samaksa ir atlīdzība, kuru darba devējs maksā darbiniekam par darbu — mēnešalga, piemaksas, prēmijas u.c.",
              children=[
                  D("62", "1", "Darba samaksas sistēmu nosaka darba koplīgums vai darba līgums."),
                  D("62", "2", "Darba samaksa nedrīkst būt mazāka par valstī noteikto minimālo darba algu."),
              ]),
            P("63", "Valstī noteiktā minimālā mēneša darba alga",
              "Minimālo mēneša darba algu nosaka Ministru kabinets. 2026. gadā tā ir 700 eiro mēnesī."),
            P("64", "Darba samaksas izmaksa",
              "Darba samaksu izmaksā divas reizes mēnesī, ja darbinieks un darba devējs nav vienojušies par izmaksu vienu reizi mēnesī."),
            P("65", "Darba samaksas izmaksa sakarā ar darba tiesisko attiecību izbeigšanu",
              "Izbeidzoties darba tiesiskajām attiecībām, visas darbiniekam pienākošās summas izmaksājamas pēdējā darba dienā."),
            P("68", "Piemaksa par virsstundu darbu",
              "Ja darbinieks veic virsstundu darbu, viņš saņem piemaksu ne mazāk kā 100 procentu apmērā no viņam noteiktās stundas vai dienas algas likmes.",
              children=[
                  D("68", "1", "Piemaksa nedrīkst būt mazāka par 100%. Koplīgumā var vienoties par lielāku piemaksu."),
                  D("68", "2", "Ja puses vienojušās, virsstundu darbu var kompensēt ar papildatpūtu."),
              ]),
            P("69", "Piemaksa par darbu svētku dienā",
              "Ja darbinieks strādā svētku dienā, viņš saņem piemaksu ne mazāk kā 100 procentu apmērā no viņa stundas vai dienas algas likmes."),
            P("70", "Piemaksa par darbu nedēļas atpūtas dienā",
              "Par darbu nedēļas atpūtas dienā darbiniekam izmaksā piemaksu vai piešķir citu atpūtas dienu."),
            P("71", "Piemaksa par nakts darbu",
              "Darbinieks, kas veic nakts darbu, saņem piemaksu ne mazāk kā 50 procentu apmērā no viņam noteiktās stundas vai dienas algas likmes."),
            P("74", "Atlīdzība gadījumos, kad darbinieks neveic darbu",
              "Gadījumos, kad darbinieks neveic darbu attaisnojošu iemeslu dēļ, darba devējs izmaksā Ministru kabineta noteiktajā apmērā noteikto vidējo izpeļņu.",
              children=[
                  D("74", "1", "Attaisnojoši iemesli: tiesas uzaicinājums, donora pienākumu pildīšana, ģimenes locekļa nāve (līdz 2 dienām)."),
                  D("74", "2", "Saglabājamā samaksa aprēķināma atbilstoši vidējai izpeļņai."),
              ]),
            P("75", "Vidējās izpeļņas aprēķināšana",
              "Vidējo izpeļņu aprēķina par pēdējiem sešiem kalendāra mēnešiem, dalot darba samaksas summu ar nostrādāto dienu skaitu."),
            P("78", "Darba samaksas aprēķina izziņa",
              "Darba devējs katru mēnesi izsniedz darbiniekam rakstveida aprēķinu (algas lapu), kurā norāda aprēķinātās un izmaksātās summas."),
        ]),
    ],

    # =========================================================================
    # PVN LIKUMS — 6 nodaļas, 30+ panti, daļas + punkti
    # =========================================================================
    "likumi_lv:/ta/id/253451": [
        N("I", "Vispārīgie jautājumi", "nI", [
            P("1", "Likumā lietotie termini",
              "Likumā lietoti šādi termini: preces, pakalpojumi, ar nodokli apliekamais darījums, iekšzeme, Eiropas Savienības teritorija, nodokļa maksātājs."),
            P("2", "Ar nodokli apliekamā persona",
              "Ar nodokli apliekamā persona ir jebkura persona, kas patstāvīgi veic saimniecisku darbību neatkarīgi no šīs darbības mērķa vai rezultāta.",
              children=[
                  D("2", "1", "Saimnieciskā darbība aptver ražošanu, tirdzniecību, pakalpojumu sniegšanu u.c."),
                  D("2", "2", "Ar nodokli apliekamā persona nav personas, kas darbojas valsts varas ietvaros."),
              ]),
            P("3", "Nodokļa maksātāji",
              "Nodokļa maksātāji ir ar nodokli apliekamās personas, kas reģistrētas Valsts ieņēmumu dienestā kā PVN maksātāji.",
              children=[
                  D("3", "1", "Reģistrēšanās pienākums iestājas, ja apliekamo darījumu vērtība 12 mēnešu periodā pārsniedz 50 000 eiro."),
                  D("3", "2", "Reģistrēšanās jāveic līdz nākamā mēneša 30. datumam pēc sliekšņa sasniegšanas."),
                  D("3", "3", "Persona var reģistrēties brīvprātīgi, nesasniedzot 50 000 eiro slieksni."),
                  D("3", "4", "VID izsniedz reģistrācijas apliecību 10 darba dienu laikā."),
                  D("3", "8", "No nodokļa maksātāju reģistra var izslēgt, ja persona iesniedz attiecīgu iesniegumu un VID pārliecinās, ka slieksnis nav pārsniegts."),
              ]),
            P("4", "Saimnieciskā darbība",
              "Saimnieciskā darbība ir jebkāda sistemātiska darbība, kas ir vērsta uz ienākumu gūšanu."),
            P("5", "Ar nodokli apliekamie darījumi",
              "Ar nodokli apliek: preču piegādi iekšzemē, pakalpojumu sniegšanu iekšzemē, preču iegādi ES teritorijā, preču importu.",
              children=[
                  D("5", "1", "Preču piegāde ir tiesību nodošana rīkoties ar precēm kā īpašniekam."),
                  D("5", "2", "Pakalpojumu sniegšana ir jebkurš darījums, kas nav preču piegāde.",
                    children=[
                        PT("5.2", "1", "Tiesību (tai skaitā intelektuālā īpašuma) nodošana."),
                        PT("5.2", "2", "Pienākuma atturēties no darbības."),
                        PT("5.2", "3", "Pakalpojumu sniegšana pret atlīdzību."),
                    ]),
                  D("5", "3", "Preču iegāde ES teritorijā ir preču saņemšana no cita ES dalībvalsts PVN maksātāja."),
                  D("5", "4", "Preču imports ir preču ievešana no ārpus ES teritorijas."),
              ]),
            P("7", "Ar nodokli neapliekamie darījumi",
              "Ar nodokli neapliek darījumus, kas nav vērsti uz ienākuma gūšanu, dāvinājumus līdz noteiktam slieksnim u.c."),
        ]),

        N("II", "Nodokļa bāze un aprēķināšana", "nII", [
            P("14", "Ar nodokli apliekamā vērtība preču piegādei",
              "Ar nodokli apliekamo vērtību nosaka atbilstoši saņemamajai atlīdzībai par preču piegādi."),
            P("15", "Ar nodokli apliekamā vērtība pakalpojumu sniegšanai",
              "Ar nodokli apliekamo vērtību nosaka atbilstoši saņemamajai atlīdzībai par pakalpojumu sniegšanu.",
              children=[
                  D("15", "1", "Atlīdzība ietver visus maksājumus — gan naudā, gan natūrā."),
                  D("15", "2", "Atlīdzībā neieskaita pašu PVN."),
              ]),
            P("16", "Atlīdzība natūrā",
              "Ja atlīdzība saņemta natūrā, apliekamo vērtību nosaka atbilstoši tirgus cenai."),
        ]),

        N("III", "Nodokļa piemērošanas vieta", "nIII", [
            P("20", "Preču piegādes vieta",
              "Preču piegādes vieta ir vieta, kur preces atrodas piegādes uzsākšanas brīdī. Ja preces tiek transportētas — vieta, kur transportēšana sākas."),
            P("21", "Preču piegādes vieta distancpārdošanā",
              "Preču distancpārdošanā fiziskām personām citā ES dalībvalstī piegādes vieta ir patērētāja dalībvalsts, ja distancpārdošanas slieksnis pārsniegts."),
            P("27", "Pakalpojumu sniegšanas vieta",
              "Pakalpojumu sniegšanas vieta nodokļa maksātājam ir vieta, kur atrodas pakalpojumu saņēmēja saimnieciskās darbības mītnes vieta.",
              children=[
                  D("27", "1", "B2B pakalpojumi — saņēmēja dalībvalstī."),
                  D("27", "2", "B2C pakalpojumi — sniedzēja dalībvalstī (pamatnoteikums)."),
                  D("27", "3", "Izņēmumi noteikti 28.–34. pantā."),
              ]),
            P("28", "Nekustamā īpašuma pakalpojumu sniegšanas vieta",
              "Ar nekustamo īpašumu saistītu pakalpojumu sniegšanas vieta ir vieta, kur atrodas nekustamais īpašums."),
            P("30", "Pasažieru pārvadājumu pakalpojumu sniegšanas vieta",
              "Pasažieru pārvadājumu pakalpojumu sniegšanas vieta ir vieta, kur pārvadājums notiek, ievērojot nobraukto attālumu."),
        ]),

        N("IV", "Nodokļa likmes", "nIV", [
            P("41", "Nodokļa standartlikme",
              "Ar nodokli apliekamajiem darījumiem piemēro standartlikmi 21 procenta apmērā no darījuma vērtības."),
            P("42", "Samazinātā nodokļa likme",
              "Samazināto nodokļa likmi 12 procentu apmērā piemēro noteiktām preču un pakalpojumu grupām.",
              children=[
                  D("42", "1", "Medicīnas precēm un ierīcēm."),
                  D("42", "2", "Grāmatām un žurnāliem, kas nav reklāmas izdevumi."),
                  D("42", "3", "Zāļu iepakojumiem un veterinārās medicīnas precēm."),
                  D("42", "4", "Zīdaiņu pārtikai."),
                  D("42", "5", "Sabiedriskajam transportam iekšzemē."),
                  D("42", "9", "Dzīvokļa īres un komunālajiem pakalpojumiem (apkure u.c.)."),
                  D("42", "11", "Atsevišķiem pārtikas produktiem (svaigi augļi un dārzeņi) — 5% likmē."),
              ]),
            P("43", "Nulles likme",
              "Ar nodokli piemēro nulles likmi preču eksportam ārpus ES un preču piegādēm ES iekšienē, ja saņēmējs ir reģistrēts PVN maksātājs citā dalībvalstī.",
              children=[
                  D("43", "1", "Preču eksportam ārpus ES teritorijas."),
                  D("43", "2", "Preču piegādēm Eiropas Savienības ietvaros (iekšienē)."),
                  D("43", "3", "Starptautiskajiem pasažieru un kravu pārvadājumiem."),
                  D("43", "6", "Pakalpojumiem, kas sniegti diplomātiskajām pārstāvniecībām."),
              ]),
            P("52", "Nodokļa atbrīvojumi",
              "No nodokļa atbrīvoti noteikti darījumi — veselības aprūpes pakalpojumi, izglītības pakalpojumi, finanšu pakalpojumi, nekustamā īpašuma darījumi u.c.",
              children=[
                  D("52", "1", "Medicīniskās palīdzības sniegšana un ar to saistītās preces."),
                  D("52", "2", "Sociālās aprūpes pakalpojumi."),
                  D("52", "3", "Pamatskolas, vidējās un augstākās izglītības pakalpojumi.",
                    children=[
                        PT("52.3", "1", "Pirmsskolas izglītība."),
                        PT("52.3", "2", "Vispārējā pamatizglītība."),
                        PT("52.3", "3", "Vidējā izglītība."),
                        PT("52.3", "4", "Augstākā izglītība."),
                        PT("52.3", "5", "Profesionālā izglītība."),
                    ]),
                  D("52", "8", "Kultūras pakalpojumi, ko sniedz sabiedrisko tiesību subjekti."),
                  D("52", "17", "Apdrošināšanas un pārapdrošināšanas pakalpojumi."),
                  D("52", "21", "Finanšu pakalpojumi — kredīti, apdrošināšana, vērtspapīru pirkšana/pārdošana."),
                  D("52", "25", "Iedzīvoto un neapstrādāto zemes gabalu pārdošana."),
              ]),
        ]),

        N("V", "Nodokļa rēķini un dokumentācija", "nV", [
            P("125", "Nodokļa rēķins",
              "Nodokļa maksātājs izraksta nodokļa rēķinu par veikto preču piegādi vai pakalpojumu sniegšanu.",
              children=[
                  D("125", "1", "Rēķins izrakstāms ne vēlāk kā 15 dienu laikā pēc darījuma."),
                  D("125", "2", "Rēķina obligātie rekvizīti: izrakstītāja un saņēmēja rekvizīti, rēķina datums un numurs, preču/pakalpojumu apraksts, cena, PVN likme, PVN summa."),
                  D("125", "3", "Elektroniskais rēķins pielīdzināms papīra rēķinam."),
              ]),
            P("126", "Rēķina uzglabāšana",
              "Nodokļa rēķins un ar darījumiem saistītie dokumenti glabājami vismaz 5 gadus."),
        ]),

        N("VI", "Nodokļa priekšnodoklis un aprēķināšana", "nVI", [
            P("92", "Priekšnodokļa atskaitīšana",
              "Reģistrēts nodokļa maksātājs var atskaitīt priekšnodokli, kas samaksāts par iegādātajām precēm un pakalpojumiem, ja tie tiek izmantoti ar nodokli apliekamajos darījumos.",
              children=[
                  D("92", "1", "Priekšnodoklis atskaitāms tikai par precēm/pakalpojumiem, kas saistīti ar apliekamajiem darījumiem."),
                  D("92", "2", "Ja preces/pakalpojumi izmantoti gan apliekamos, gan neapliekamos darījumos — piemēro proporcionālo atskaitījumu."),
                  D("92", "5", "Priekšnodoklis nav atskaitāms par pasažieru automobīļu iegādi (izņēmumi atļauti)."),
              ]),
            P("95", "Priekšnodokļa korekcija",
              "Priekšnodoklis ir jākoriģē, ja mainās preču/pakalpojumu izmantošanas apstākļi."),
            P("118", "Nodokļa deklarācija",
              "Reģistrēti nodokļa maksātāji iesniedz PVN deklarāciju par katru taksācijas periodu.",
              children=[
                  D("118", "1", "Taksācijas periods ir viens kalendāra mēnesis."),
                  D("118", "2", "Nelielajiem uzņēmumiem (apgrozījums līdz 40 000 eiro) — ceturksnis."),
                  D("118", "3", "Deklarācija iesniedzama līdz nākamā mēneša 20. datumam."),
                  D("118", "4", "Deklarācija iesniedzama elektroniski VID EDS sistēmā."),
              ]),
            P("119", "Nodokļa samaksa",
              "Nodokli samaksā līdz tā paša mēneša 23. datumam, kad iesniedzama deklarācija."),
            P("120", "Nodokļa pārmaksas atmaksa",
              "Ja priekšnodokļa summa pārsniedz aprēķināto nodokļa summu, pārmaksa atmaksājama 30 dienu laikā pēc deklarācijas saņemšanas."),
        ]),
    ],

    # =========================================================================
    # KOMERCLIKUMS — 5 nodaļas, 20+ panti
    # =========================================================================
    "likumi_lv:/ta/id/5490": [
        N("A", "Vispārīgie noteikumi", "nA", [
            P("1", "Komersants",
              "Komersants ir komercreģistrā ierakstīts individuālais komersants vai komercsabiedrība."),
            P("2", "Komercdarbība",
              "Komercdarbība ir atklāta saimnieciskā darbība, kuru savā vārdā peļņas gūšanas nolūkā veic komersants."),
            P("3", "Komercdarījums",
              "Komercdarījums ir darījums, kuru komersants noslēdzis savas komercdarbības ietvaros."),
            P("5", "Komercreģistrs",
              "Komercreģistrs ir publisks reģistrs, kurā ieraksta komersantus un ziņas par tiem. Komercreģistru uztur Uzņēmumu reģistrs.",
              children=[
                  D("5", "1", "Komercreģistra ieraksti ir publiski pieejami."),
                  D("5", "2", "Uz komercreģistra ierakstiem var paļauties, ja vien trešajai personai nav zināms, ka ieraksts nav patiess."),
                  D("5", "3", "Ieraksta spēkā stāšanās datums — ieraksta publikācijas datums oficiālajā izdevumā."),
              ]),
            P("6", "Firma",
              "Firma ir nosaukums, ar kādu komersants ir reģistrēts komercreģistrā un kādu tas izmanto, slēdzot darījumus."),
            P("8", "Firmas izvēle",
              "Firma skaidri jāatšķir no citām komercreģistrā ierakstītajām firmām. Firma nedrīkst būt maldinoša."),
        ]),

        N("B", "Individuālais komersants", "nB", [
            P("75", "Individuālais komersants",
              "Individuālais komersants ir fiziskā persona, kas kā komersants ierakstīta komercreģistrā."),
            P("76", "Reģistrācijas pienākums",
              "Fiziskajai personai ir pienākums reģistrēties kā individuālajam komersantam, ja apgrozījums pārskata gadā pārsniedz 284 600 eiro vai ja tā nodarbojas ar komercaģenta darbību.",
              children=[
                  D("76", "1", "Pienākums iestājas, kad slieksnis pārsniegts."),
                  D("76", "3", "Fiziskā persona var reģistrēties brīvprātīgi, nesasniedzot slieksni."),
              ]),
            P("77", "Individuālā komersanta firma",
              "Individuālā komersanta firmā ietver personas vārdu un uzvārdu."),
            P("78", "Individuālā komersanta atbildība",
              "Individuālais komersants par savām saistībām atbild ar visu savu mantu."),
        ]),

        N("C", "Komercsabiedrības — vispārīgie noteikumi", "nC", [
            P("134", "Komercsabiedrības veidi",
              "Komercsabiedrības ir personālsabiedrības (pilnsabiedrība, komandītsabiedrība) un kapitālsabiedrības (SIA, akciju sabiedrība)."),
            P("135", "Juridiskā statusa iegūšana",
              "Komercsabiedrība iegūst juridiskās personas statusu no ieraksta izdarīšanas komercreģistrā."),
            P("137", "Dibināšanas līgums",
              "Komercsabiedrību dibina, rakstveidā noslēdzot dibināšanas līgumu, kas notariāli apliecināts."),
            P("139", "Statūti",
              "Komercsabiedrības statūti ir dokuments, kas nosaka sabiedrības organizāciju un darbības pamatnoteikumus.",
              children=[
                  D("139", "1", "Statūtos norāda firmu, juridisko adresi, darbības mērķus."),
                  D("139", "2", "Kapitālsabiedrības statūtos papildus norāda pamatkapitāla lielumu, daļas (akcijas) skaitu un vērtību."),
              ]),
        ]),

        N("D", "Sabiedrība ar ierobežotu atbildību (SIA)", "nD", [
            P("185", "Sabiedrība ar ierobežotu atbildību",
              "SIA ir komercsabiedrība, kuras pamatkapitāls sastāv no daļām. Dalībnieki neatbild par sabiedrības saistībām.",
              children=[
                  D("185", "1", "Minimālais pamatkapitāls ir 2 800 eiro."),
                  D("185", "2", "SIA var dibināt viens vai vairāki dibinātāji — fiziskas vai juridiskas personas."),
                  D("185", "3", "Dalībnieki saņem dividendes proporcionāli viņu īpašumā esošo daļu skaitam."),
              ]),
            P("186", "Mazkapitāla SIA",
              "Mazkapitāla SIA ir SIA ar pamatkapitālu no 1 līdz 2 800 eiro. Uz to attiecas papildu ierobežojumi.",
              children=[
                  D("186", "1", "Dibinātāji — fiziskas personas."),
                  D("186", "2", "Maksimālais dalībnieku skaits — 5."),
                  D("186", "3", "Peļņas sadales ierobežojumi līdz pamatkapitāls sasniedz 2 800 eiro."),
              ]),
            P("210", "Dalībnieku sapulce",
              "Dalībnieku sapulce ir SIA augstākā lēmējinstitūcija.",
              children=[
                  D("210", "1", "Kārtēja sapulce sasaucama vismaz reizi gadā."),
                  D("210", "2", "Ārkārtas sapulci sasauc pēc valdes, padomes vai dalībnieku, kas pārstāv 10%, pieprasījuma."),
              ]),
            P("214", "Valde",
              "SIA valde ir izpildinstitūcija, kas vada un pārstāv sabiedrību."),
        ]),

        N("E", "Akciju sabiedrība (AS)", "nE", [
            P("225", "Akciju sabiedrība",
              "AS ir komercsabiedrība, kuras pamatkapitāls sastāv no akcijām.",
              children=[
                  D("225", "1", "Minimālais pamatkapitāls — 35 000 eiro."),
                  D("225", "2", "Akcijas var būt reģistrētas vai uzrādītāja akcijas."),
              ]),
            P("267", "Akcionāru sapulce",
              "Akcionāru sapulce ir AS augstākā lēmējinstitūcija."),
            P("292", "Valde un padome",
              "AS obligāti ir valde un padome. Padome uzrauga valdes darbu."),
        ]),
    ],

    # =========================================================================
    # AUTOPĀRVADĀJUMU LIKUMS — 5 nodaļas
    # =========================================================================
    "likumi_lv:/ta/id/58547": [
        N("1", "Vispārīgie noteikumi", "n1", [
            P("1", "Likumā lietotie termini",
              "Likumā lietoti šādi termini: autopārvadājums, pārvadātājs, transportlīdzeklis, maršruts, autoosta, sabiedriskais transports."),
            P("2", "Likuma mērķis",
              "Likuma mērķis ir regulēt autopārvadājumu jomu, nodrošinot drošus, kvalitatīvus un konkurētspējīgus pārvadājumus."),
            P("3", "Autopārvadājumu veidi",
              "Autopārvadājumi iedalās: pasažieru komercpārvadājumos, kravu komercpārvadājumos, pašpārvadājumos.",
              children=[
                  D("3", "1", "Komercpārvadājumi — par atlīdzību trešās personas uzdevumā."),
                  D("3", "2", "Pašpārvadājumi — komersanta paša vajadzībām."),
              ]),
        ]),
        N("2", "Pasažieru pārvadājumi", "n2", [
            P("17", "Pasažieru regulārie pārvadājumi",
              "Regulārie pārvadājumi ir pārvadājumi pēc apstiprināta saraksta un maršruta, uz kuriem attiecas vienots biļešu tarifs.",
              children=[
                  D("17", "1", "Pilsētas nozīmes regulārie pārvadājumi."),
                  D("17", "2", "Reģionālie regulārie pārvadājumi."),
                  D("17", "3", "Starptautiskie regulārie pārvadājumi."),
              ]),
            P("18", "Regulāro pārvadājumu licencēšana",
              "Regulāros pārvadājumus var veikt tikai licencēts pārvadātājs, kurš saņēmis atļauju konkrētam maršrutam."),
            P("20", "Pasažieru neregulārie pārvadājumi",
              "Neregulārie pārvadājumi ir pasažieru grupas pārvadājumi, kad grupu izveido pasūtītājs, un tie nav regulāri.",
              children=[
                  D("20", "1", "Neregulārajiem pārvadājumiem nav nepieciešama licence konkrētam maršrutam."),
                  D("20", "2", "Pārvadātājam jābūt vispārējai pārvadātāja licencei."),
              ]),
            P("22", "Taksometru pārvadājumi",
              "Taksometru pārvadājumi ir pasažieru pārvadājumi, kas tiek veikti ar vieglajiem automobiļiem pēc pieprasījuma."),
        ]),
        N("3", "Kravu pārvadājumi", "n3", [
            P("26", "Kravu komercpārvadājumi",
              "Kravu komercpārvadājumus var veikt tikai komersants, kuram izsniegta Eiropas Kopienas autopārvadātāja licence."),
            P("27", "Kravas pavadzīme",
              "Veicot kravas pārvadājumu, jāizraksta kravas pavadzīme (CMR konvencija).",
              children=[
                  D("27", "1", "Pavadzīmi izraksta trīs eksemplāros — nosūtītājam, pārvadātājam, saņēmējam."),
                  D("27", "2", "Pavadzīmē norāda: sūtītāju, saņēmēju, kravas aprakstu, svaru, iekraušanas vietu un datumu."),
              ]),
        ]),
        N("4", "Autopārvadājumu vadītāji", "n4", [
            P("35", "Autovadītāja profesionālā kvalifikācija",
              "Autovadītājam, kurš veic komercpārvadājumus, jābūt derīgam profesionālās kompetences sertifikātam."),
            P("36", "Autovadītāja apmācība",
              "Autovadītāji, kuri nodarbojas ar komercpārvadājumiem, regulāri apgūst profesionālās tālākizglītības apmācības kursus (katrus 5 gadus, 35 stundas)."),
            P("37", "Autovadītāja darba un atpūtas laiks",
              "Autovadītāja darba un atpūtas laiku nosaka saskaņā ar Eiropas Savienības regulējumu (Reg. 561/2006).",
              children=[
                  D("37", "1", "Dienas braukšanas laiks nedrīkst pārsniegt deviņas stundas."),
                  D("37", "2", "Pēc četrarpus braukšanas stundām jāievēro vismaz 45 minūšu pārtraukums."),
                  D("37", "3", "Nedēļas braukšanas laiks nedrīkst pārsniegt 56 stundas."),
                  D("37", "4", "Divu secīgu nedēļu laikā kopējais braukšanas laiks nepārsniedz 90 stundas."),
                  D("37", "5", "Dienas atpūtas laiks — vismaz 11 stundas."),
                  D("37", "6", "Nedēļas atpūtas laiks — vismaz 45 stundas nedēļā."),
              ]),
            P("38", "Tahogrāfs",
              "Komercpārvadājumu transportlīdzekļiem, kuru svars pārsniedz 3,5 tonnas, obligāti uzstādīts digitālais tahogrāfs."),
        ]),
        N("5", "Administratīvā atbildība", "n5", [
            P("55", "Pārkāpumi un sodi",
              "Par šī likuma pārkāpumiem fiziskām un juridiskām personām piemēro naudas sodus.",
              children=[
                  D("55", "1", "Par pārvadājumu bez licences — naudas sods no 140 līdz 1400 eiro fiziskai personai."),
                  D("55", "2", "Par autovadītāja darba un atpūtas laika pārkāpumiem — naudas sods no 70 līdz 700 eiro."),
                  D("55", "3", "Par tahogrāfa uzstādīšanas vai izmantošanas kārtības pārkāpumiem — no 140 līdz 1400 eiro."),
              ]),
        ]),
    ],

    # =========================================================================
    # FIZISKO PERSONU DATU APSTRĀDES LIKUMS — 4 nodaļas
    # =========================================================================
    "likumi_lv:/ta/id/300099": [
        N("1", "Vispārīgie noteikumi", "n1", [
            P("1", "Likuma mērķis",
              "Likuma mērķis ir aizsargāt fiziskās personas pamattiesības un brīvības, it īpaši — tiesības uz personas datu aizsardzību."),
            P("2", "Likumā lietotie termini",
              "Likumā lietoti Regulas 2016/679 (GDPR) terminu nozīmē: personas dati, apstrāde, pārzinis, apstrādātājs, datu subjekts."),
            P("3", "Likuma darbības joma",
              "Likums attiecas uz personas datu apstrādi, kas veikta Latvijas teritorijā vai attiecībā uz Latvijas iedzīvotājiem."),
            P("5", "Apstrādes pamats",
              "Personas datu apstrāde ir likumīga tikai tad, ja ir piemērojams viens no GDPR 6. pantā norādītajiem apstrādes pamatiem.",
              children=[
                  D("5", "1", "Datu subjekta piekrišana."),
                  D("5", "2", "Līguma izpilde vai pasākumi pirms līguma noslēgšanas."),
                  D("5", "3", "Juridiska pienākuma izpilde."),
                  D("5", "4", "Datu subjekta vai citas fiziskās personas vitālo interešu aizsardzība."),
                  D("5", "5", "Sabiedrības intereses vai oficiāla pilnvarojuma izpilde."),
                  D("5", "6", "Pārziņa vai trešās personas leģitīmas intereses."),
              ]),
        ]),

        N("2", "Datu subjekta tiesības", "n2", [
            P("8", "Informēšanas pienākums",
              "Pārzinim ir pienākums informēt datu subjektu par personas datu apstrādi kodolīgā, pārredzamā un viegli uztveramā veidā.",
              children=[
                  D("8", "1", "Informēšana jāsniedz datu vākšanas brīdī."),
                  D("8", "2", "Jānorāda: pārziņa identitāte, apstrādes mērķis, juridiskais pamats, glabāšanas ilgums."),
              ]),
            P("9", "Piekļuves tiesības",
              "Datu subjektam ir tiesības saņemt informāciju par to, vai tā personas dati tiek apstrādāti, un piekļūt šiem datiem."),
            P("10", "Labošanas tiesības",
              "Datu subjektam ir tiesības pieprasīt neprecīzu personas datu labošanu."),
            P("11", "Dzēšanas tiesības (tiesības tikt aizmirstam)",
              "Datu subjektam ir tiesības pieprasīt personas datu dzēšanu likumā noteiktos gadījumos.",
              children=[
                  D("11", "1", "Dati vairs nav nepieciešami mērķim, kuram tie tika vākti."),
                  D("11", "2", "Datu subjekts atsauc piekrišanu un nav cita juridiska pamata."),
                  D("11", "3", "Dati ir apstrādāti nelikumīgi."),
              ]),
            P("12", "Datu pārnesamības tiesības",
              "Datu subjektam ir tiesības saņemt personas datus strukturētā, plaši izmantotā formātā."),
        ]),

        N("3", "Datu valsts inspekcija", "n3", [
            P("12", "Datu valsts inspekcija",
              "Datu valsts inspekcija ir neatkarīga uzraudzības iestāde, kas pārrauga datu aizsardzības regulējuma ievērošanu Latvijā."),
            P("13", "Inspekcijas uzdevumi",
              "Inspekcija: izskata sūdzības, veic pārbaudes, sadarbojas ar citu ES valstu datu aizsardzības iestādēm, piemēro sodus."),
            P("15", "Sūdzību izskatīšana",
              "Datu subjektam ir tiesības iesniegt sūdzību Datu valsts inspekcijā, ja tas uzskata, ka viņa datu apstrāde neatbilst normatīvajiem aktiem.",
              children=[
                  D("15", "1", "Sūdzību var iesniegt rakstveidā vai elektroniski."),
                  D("15", "2", "Inspekcija atbild uz sūdzību trīs mēnešu laikā."),
              ]),
        ]),

        N("4", "Atbildība", "n4", [
            P("25", "Administratīvā atbildība",
              "Par GDPR un šī likuma pārkāpumiem piemēro administratīvo atbildību.",
              children=[
                  D("25", "1", "Naudas sodu apmērs fiziskām personām — līdz 20 miljoniem eiro."),
                  D("25", "2", "Naudas sodu apmērs juridiskām personām — līdz 4% no gada globālā apgrozījuma."),
              ]),
            P("26", "Zaudējumu atlīdzība",
              "Datu subjektam ir tiesības saņemt zaudējumu atlīdzību par materiālo un nemateriālo kaitējumu."),
        ]),
    ],
}


def run() -> None:
    print("Ielādē bagātināto sekciju struktūru…")
    db = SessionLocal()
    try:
        total = 0
        for ext_id, nodes in SECTIONS.items():
            doc = db.query(Document).filter_by(external_id=ext_id).first()
            if not doc:
                print(f"  [SKIP] {ext_id} — dokuments nav atrasts DB.")
                continue
            # Dzēš esošās šī dokumenta sekcijas
            db.query(DocumentSection).filter_by(document_id=doc.id).delete()
            db.flush()
            count = insert_sections(db, doc.id, nodes, parent_id=None)
            total += count
            print(f"  [OK] {doc.title[:60]} — {count} sekcijas")
        db.commit()
        print(f"Gatavs! Ievietotas {total} sekcijas {len(SECTIONS)} dokumentos.")
    finally:
        db.close()


def insert_sections(db, doc_id: int, nodes: list, parent_id):
    count = 0
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
        count += 1
        kids = node.get("children") or []
        if kids:
            count += insert_sections(db, doc_id, kids, row.id)
    return count


if __name__ == "__main__":
    run()
