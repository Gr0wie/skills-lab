# Datamodel

Én JSON-fil driver begge dokumenter. Skriv den, kør `validate_data.py`, byg derefter.
Alle beløb i mio. DKK som tal (ikke tekst, ikke tusinder).

## Overordnet struktur

```json
{
  "meta": { ... },
  "kandidater": [ ... ],
  "fravalgte": [ ... ],
  "oevrige_fravalgte": [ ... ],
  "segmentdaekning": [ ... ],
  "metode": [ ... ]
}
```

## meta

```json
{
  "titel": "Danske leverandører til den grønne omstilling",
  "undertitel": "Screening af opkøbsemner med dansk hovedsæde, egnet til majoritetsovertagelse. Bygget udelukkende på CVR, offentliggjorte årsrapporter, selskabernes hjemmesider og brancheorganisationer.",
  "dato": "25. august 2026",
  "periode_note": "Regnskabsår 2024/25",
  "kriterier": ["Omsætning 100–500 mio. DKK", "Dansk hovedsæde", "Ikke børsnoteret", "Ikke koncernejet", "Ikke kapitalfondsejet", "Bonus: tegn på generationsskifte"],
  "oms_min": 100,
  "oms_max": 500,
  "antal_vurderet": 80,
  "hovedkonklusion": "Markedet er allerede konsolideret. <b>Ejerforhold — ikke størrelse — er den hyppigste årsag til fravalg.</b> …",
  "kilder_linje": "Kilder: CVR / datacvr.virk.dk · offentliggjorte årsrapporter gengivet på proff.dk · ejerdata via ownr.dk · …"
}
```

Intervalgrafens x-akse sættes ikke i datafilen. Slide 3 beregner den selv som nærmeste
runde hundrede over det højeste tal, der tegnes — dog altid mindst op til `oms_max`, så
kriteriefeltet kan vises helt. Det er med vilje: en skala, der skrives i hånden, kommer
før eller siden til at ligge under et skøn, og så løber en søjle ud over aksen.

`hovedkonklusion` må indeholde `<b>` og `&nbsp;` — intet andet markup.

## kandidater

Rækkefølgen i filen er den rækkefølge, læseren møder. Sortér efter samlet fit, ikke
efter omsætning — det er den rangordning, modtageren skal bruge.

```json
{
  "navn": "Nilan A/S",
  "cvr": "11773397",
  "segment": "Varmepumper og ventilation",
  "segment_kort": "Varmepumper og ventilation",
  "by": "Hedensted",
  "hjemmeside": "nilan.dk",
  "omsaetning": null,
  "bruttofortjeneste": 91.7,
  "regnskabsaar": "2024/25 (afsluttet 30.06.2025)",
  "ansatte": 142,
  "egenkapital": 205.4,
  "ejerforhold": "100 % ejet af Nilan Holding A/S. Torben Andersen står som ultimativ ejer … Ikke del af nogen koncern ifølge selskabets om-side, sidefoden og ejerkæden.",
  "beskrivelse": "Udvikler og producerer luft/vand-varmepumper samt ventilation …",
  "fit": "Stærkeste kandidat på listen. …",
  "usikkerheder": "OMSÆTNING ESTIMERET ca. 360–400 mio. DKK. …",
  "kilde": "Regnskabstal: proff.dk … Ejerkæde: ownr.dk … Eget site: nilan.dk/om-nilan og sidefoden. Primærkilde: https://datacvr.virk.dk/enhed/virksomhed/11773397",
  "skoen": { "lav": 360, "hoej": 400, "status": "inde", "flag": "inden for", "forretningsmodel": "producent" }
}
```

- `omsaetning`: tal hvis oplyst i årsrapporten, ellers `null`. Ved `null` **skal**
  `usikkerheder` begynde med `OMSÆTNING ESTIMERET`, og `skoen.lav`/`skoen.hoej` udfyldes.
- `segment_kort` er segmentteksten på profilslidet (slide 5). Hold den under ~34 tegn.
  Udelades den, bruges `segment`.
- `skoen.status`: `"inde"`, `"over"` eller `"under"`. Styrer intervalbjælkens farve på
  slide 3: blå for `inde`, orange for `over` og `under`.
- `skoen.flag`: kort statustekst. Bruges i regnearket; præsentationen viser status som
  farve. Brug `▲` for over og `▼` for under, fx `"▲ formentlig over"`.
- Er `omsaetning` udfyldt, kan `skoen` udelades; så tegnes en mørk punktmarkør på det
  faktiske tal i stedet for en intervalbjælke.
- `hjemmeside`: selskabets eget domæne, uden protokol. Obligatorisk. For de **tre
  øverste** kandidater skal domænet også stå i `kilde` sammen med `ownr.dk`, og
  `ejerforhold` skal indeholde en eksplicit koncernvurdering — ellers afviser
  validatoren filen. De tre øverste bærer slide 5.
- `skoen.forretningsmodel`: obligatorisk, når omsætningen er skønnet. En af
  `producent`, `grossist`, `entreprenoer`, `service`, `ems`. `usikkerheder` skal sige,
  hvorfor modellen er valgt, før de to beregninger — se `omsatningsskon.md`.
- `aarets_resultat`, `personaleomkostninger`, `afskrivninger`, `ebit`: valgfrie tal fra
  årsrapporten, mio. DKK. Er de udfyldt, kører validatoren tre sanity-checks, og hvert
  fund skal enten rettes eller anerkendes med et nøgleord i `usikkerheder`:

  | Kontrol | Betyder typisk | Anerkend med |
  |---|---|---|
  | bruttofortjeneste ÷ ansatte under 0,4 | Bruttofortjeneste opgjort efter personale, eller produktion i udlandet | "bruttofortjeneste pr. ansat" eller "udland" |
  | årets resultat over ⅓ af bruttofortjenesten | Resultatandele fra dattervirksomheder | "resultatandel" eller "dattervirksomhed" |
  | bruttofortjeneste − personale − afskrivninger ≠ EBIT | Bruttofortjeneste opgjort efter personale; skønnet er for lavt | "personaleomkostninger" |

  Den første kører altid, fordi den kun bruger felter, der allerede er obligatoriske.
- `ejerskifte`: valgfrit objekt, samme form som under `fravalgte` nedenfor. Brug det på
  en kandidat, der har haft et ejerskifte i historikken.
- **Tre måder at skrive et hul, og de betyder hver sit.** `"ikke fundet"`: der blev
  søgt, og intet kom frem — så skal `kilde` indeholde `Søgt uden fund:` efterfulgt af
  mindst to kilder (købers eget newsroom og brancheorganer), ellers afviser validatoren
  filen. `"ikke undersøgt"`: der blev ikke søgt, fx fordi et site blokerede eller
  søgebudgettet var brugt — altid tilladt, men samles i en advarsel, og metodefanen skal
  nævne dem. `ejerforhold` må ikke være nogen af delene: er ejeren ikke slået op, kan
  selskabet ikke stå som kandidat. Lad aldrig et felt stå tomt.

## fravalgte

5–10 poster. Vælg dem, så hver illustrerer sin egen afvisningsgrund.

```json
{
  "navn": "Bigadan A/S",
  "cvr": "25191153",
  "segment": "Biogas",
  "noegletal": "Omsætning 337,2 mio. DKK (FY2025), 62 ansatte, egenkapital 320,3 mio.",
  "begrundelse": "Passede på alle finansielle kriterier … Fravalgt fordi Arjun Infrastructure Partners overtog fuld kontrol — godkendt 8. november 2024.",
  "kilde": "energy-supply.dk 08.11.2024; proff.dk; ownr.dk"
}
```

Har et selskab intet CVR-nummer i sammenhængen (fx en koncern omtalt samlet), så skriv
`"—"`.

Nævner `begrundelse` et ejerskifte sammen med et årstal, skal `kilde` bære en dato
("kapwatch.dk, 21.04.2026"), eller posten skal have et `ejerskifte`-objekt. Det er
reglen, fordi annoncering og closing tit ligger i hver sit år, og den, der kun får det
ene tal, læser det forkert:

```json
"ejerskifte": {
  "annonceret": "2026-04-20",
  "closing": "2026-07-01",
  "koeber": "KK Group Invest A/S",
  "saelgers_andel_efter": "30 %",
  "kilde_annoncering": "kkgroup.com/media/news/…, gengivet på renews.biz 20.04.2026",
  "kilde_closing": "ownr.dk/companies/public-profile/…, ny ejer registreret 30.06.2026"
}
```

Datoer skrives `ÅÅÅÅ-MM-DD`; en dato, der ikke kendes, sættes til `null`. Mindst én af
de to skal være udfyldt, og hver udfyldt dato skal have sin egen kilde. `koeber` er
obligatorisk. Regnearket skriver objektet ind under begrundelsen på fanen Fravalgte.

## oevrige_fravalgte

Alle øvrige fravalgte, grupperet efter den årsag, der afgjorde sagen. Driver både
metodefanens oversigt og fravalgsgrafen på slide 4, så tallene kan ikke komme i utakt.

```json
{
  "aarsag": "Udenlandsk industriel ejer",
  "antal": 10,
  "gruppe": "ejerskab",
  "selskaber": "Airmaster A/S (Lindab, SE) · Brunata A/S (Minol Brunata, DE) · …"
}
```

Tilføj `"aarsag_kort"`, hvis årsagen er for lang til søjlegrafen på slide 4 — den har
plads til ca. 32 tegn. Uden feltet afkortes teksten med ellipse, og en afkortet
afvisningsgrund er ubrugelig for læseren.

`gruppe` skal være `"ejerskab"`, `"stoerrelse"` eller `"oevrigt"` — den bestemmer farven
i grafen og den opsummering, der står under den. `antal` skal være det faktiske antal
selskaber i `selskaber`; validatoren tæller separatoren `·` og advarer ved uoverensstemmelse.

Summen af `antal` plus antallet af kandidater skal give `meta.antal_vurderet`. De 5–10
poster i `fravalgte` er en delmængde af disse og tælles ikke oveni.

## segmentdaekning

Ét punkt pr. segment i mandatet — også dem med nul kandidater. Nullerne er ofte
screeningens vigtigste udsagn, og slide 4 markerer dem særskilt.

```json
[ {"navn": "Biogas", "antal": 6}, {"navn": "Sol", "antal": 0} ]
```

Summen skal være lig antallet af kandidater.

## metode

Fanen "Metode og forbehold" som en liste af `[type, tekst]`. Typerne er `h1` (én gang,
øverst), `h2` (afsnitsoverskrift), `p` (brødtekst) og `b` (punkt).

```json
[
  ["h1", "Metode og forbehold"],
  ["p", "Screening af … Alle beløb er i mio. DKK."],
  ["h2", "1. Sådan søgte jeg"],
  ["b", "Bruttoliste: brancheorganisationers medlemslister …"]
]
```

Dæk som minimum: hvordan der blev søgt, hvordan omsætningsskøn er lavet, hvilke
segmenter der er dårligst dækket, hvad der ikke kunne verificeres, og hvad man skal være
særligt skeptisk over for. Afslut med en overskrift til oversigten over øvrige fravalgte
— builderen indsætter tabellen efter det sidste element.

Slide 5 i præsentationen bygges på de tre øverste kandidater, ikke på et selvstændigt
felt. Der er derfor ingen `footer_kort`: profilerne skal komme fra de samme data som
resten, ellers kan kortet og kandidatlisten nå at sige hvert sit.
