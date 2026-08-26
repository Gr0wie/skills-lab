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
  "metode": [ ... ],
  "footer_kort": [ ... ]
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
  "skala_max": 800,
  "antal_vurderet": 80,
  "hovedkonklusion": "Markedet er allerede konsolideret. <b>Ejerforhold — ikke størrelse — er den hyppigste årsag til fravalg.</b> …",
  "kilder_linje": "Kilder: CVR / datacvr.virk.dk · offentliggjorte årsrapporter gengivet på proff.dk · ejerdata via ownr.dk · …"
}
```

`skala_max` sætter x-aksens maksimum på one pageren. Vælg et rundt tal over det højeste
skøn. `hovedkonklusion` må indeholde `<b>` og `&nbsp;` — intet andet markup.

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
  "omsaetning": null,
  "bruttofortjeneste": 91.7,
  "regnskabsaar": "2024/25 (afsluttet 30.06.2025)",
  "ansatte": 142,
  "egenkapital": 205.4,
  "ejerforhold": "100 % ejet af Nilan Holding A/S. Torben Andersen står som ultimativ ejer …",
  "beskrivelse": "Udvikler og producerer luft/vand-varmepumper samt ventilation …",
  "fit": "Stærkeste kandidat på listen. …",
  "usikkerheder": "OMSÆTNING ESTIMERET ca. 360–400 mio. DKK. …",
  "kilde": "Regnskabstal: proff.dk … Ejerforhold: ownr.dk … Primærkilde: https://datacvr.virk.dk/enhed/virksomhed/11773397",
  "skoen": { "lav": 360, "hoej": 400, "status": "inde", "flag": "inden for" }
}
```

- `omsaetning`: tal hvis oplyst i årsrapporten, ellers `null`. Ved `null` **skal**
  `usikkerheder` begynde med `OMSÆTNING ESTIMERET`, og `skoen.lav`/`skoen.hoej` udfyldes.
- `segment_kort` er den lille undertekst i one pagerens graf. Hold den under ~34 tegn.
  Udelades den, bruges `segment`.
- `skoen.status`: `"inde"`, `"over"` eller `"under"`. Styrer, om søjlen tegnes fyldt
  (inde) eller lys med kant (uden for kriteriet), og farven på flagteksten.
- `skoen.flag`: den korte tekst yderst til højre i grafen. Brug `▲` for over og `▼` for
  under, fx `"▲ formentlig over"`. Ved oplyst omsætning: `"oplyst"`.
- Er `omsaetning` udfyldt, kan `skoen` udelades; så tegnes en rombe på det faktiske tal.
- Ukendte felter: skriv `"ikke fundet"`. Lad dem aldrig stå tomme.

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

## oevrige_fravalgte

Alle øvrige fravalgte, grupperet efter den årsag, der afgjorde sagen. Driver både
metodefanens oversigt og one pagerens fravalgsgraf, så tallene kan ikke komme i utakt.

```json
{
  "aarsag": "Udenlandsk industriel ejer",
  "antal": 10,
  "gruppe": "ejerskab",
  "selskaber": "Airmaster A/S (Lindab, SE) · Brunata A/S (Minol Brunata, DE) · …"
}
```

Tilføj `"aarsag_kort"`, hvis årsagen er for lang til søjlegrafen på one pageren — den har
plads til ca. 34 tegn. Uden feltet afkortes teksten med ellipse, og en afkortet
afvisningsgrund er ubrugelig for læseren.

`gruppe` skal være `"ejerskab"`, `"stoerrelse"` eller `"oevrigt"` — den bestemmer farven
i grafen og den opsummering, der står under den. `antal` skal være det faktiske antal
selskaber i `selskaber`; validatoren tæller separatoren `·` og advarer ved uoverensstemmelse.

Summen af `antal` plus antallet af kandidater skal give `meta.antal_vurderet`. De 5–10
poster i `fravalgte` er en delmængde af disse og tælles ikke oveni.

## segmentdaekning

Ét punkt pr. segment i mandatet — også dem med nul kandidater. Nullerne er ofte
screeningens vigtigste udsagn, og one pageren markerer dem særskilt.

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

## footer_kort

Præcis tre kort nederst på one pageren. Brug dem til: hvem man starter med, hvilket
forbehold der betyder mest, og hvad der er signal frem for oplysning.

```json
[ {"titel": "Tre at starte med", "tekst": "<b>Nilan A/S</b>, Hedensted — …"} ]
```

`tekst` må indeholde `<b>` og `<br>`.
