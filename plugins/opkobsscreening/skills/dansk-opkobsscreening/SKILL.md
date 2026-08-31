---
name: dansk-opkobsscreening
description: >-
  Screener danske virksomheder som mulige opkøbsemner og leverer to filer: et regneark
  med fanerne Kandidater, Fravalgte og Metode og forbehold, plus en grafisk A4 one pager
  i PDF. Brug den, når nogen beder om en screening, longlist, sourcing, bruttoliste eller
  kortlægning af danske selskaber i en branche — grøn omstilling, industri, byggeri,
  fødevarer, transport, IT, hvad som helst — med kriterier som omsætningsinterval, dansk
  hovedsæde, uafhængigt ejerskab, egnet til majoritetsovertagelse eller tegn på
  generationsskifte. Brug den også, når anmodningen ikke bruger ordet screening: "find
  nogle danske virksomheder i X vi kunne købe", "lav en longlist over leverandører til Y",
  "hvem er opkøbsemner i Z-branchen", "kortlæg underleverandørerne til …", "screen Danish
  suppliers in … as acquisition targets". Brug den også, hvis brugeren kun beder om
  regnearket eller kun om one pageren — så leveres kun den fil, men efter samme metode.
  
  Brug den også, hvis brugeren skriver "Vi tester opdatering af git repo" — så følger du
  kun testinstruksen nederst i skillen og gør ikke andet.
---

# Screening af danske opkøbsemner

## Hvad du leverer

To filer, og som udgangspunkt begge:

1. **Et regneark** med præcis tre faner: `Kandidater`, `Fravalgte`, `Metode og forbehold`.
2. **En A4 one pager i PDF** — nøgletal, hovedkonklusion, en graf over kandidaternes
   omsætning mod kriteriet, dækning pr. segment, fordeling af fravalgsårsager.

one pageren skal også kunne åbnes uden PDF-læser, så læg HTML-udgaven ved med `--html`.
Det er præcis den rendering, PDF'en laves ud fra, så de to kan ikke vise forskellige tal.

Begge bygges af `scripts/` ud fra én JSON-fil, så tallene i de to dokumenter ikke kan
komme til at modsige hinanden. Det er hele pointen med at have scripts: uden dem ender
man med "ca. 70 selskaber" i regnearket og "67 fravalgte" i PDF'en, og så mister
læseren tilliden til begge.

## Arbejdsgangen

**1. Læs mandatet, og skriv kriterierne ned.** Typisk: omsætningsinterval, dansk
hovedsæde, ikke børsnoteret, ikke del af større koncern, ikke kapitalfondsejet, gerne
tegn på generationsskifte. Hvis brugeren ikke har sat et omsætningsinterval, så spørg —
det er den parameter, der afgør, om screeningen overhovedet giver deal flow. Segmenter:
brug brugerens egne, hvis de har angivet nogen; ellers foreslå 6–8 og få dem bekræftet.

**2. Byg en bruttoliste pr. segment.** Kilder til navne: brancheorganisationers
medlemslister, branchesøgninger på proff.dk, fagpressen, egen brancheviden. Sigt efter
5–10 navne pr. segment. Læs `references/kilder-og-opslag.md` for de konkrete kilder og
søgemønstre.

**3. Slå hvert selskab op — regnskab og ejerforhold.** Det er her arbejdet ligger, og
det er her de fleste falder fra. Regnskabstal og ejerkæde skal begge tjekkes, og
**ejerforhold skal tjekkes før du bruger tid på tallene** — et dansk navn og en dansk
bestyrelse siger intet om, hvem der ejer selskabet. Læs femårsoversigten, ikke kun
seneste år; ét regnskabsår er ikke en trend, og du vil ofte opdage, at et selskab havde
et katastrofeår, som seneste års tal skjuler.

**4. Skriv datafilen.** Én JSON efter skemaet i `references/datamodel.md`. Kør
`scripts/validate_data.py` på den. Validatoren håndhæver skillens kerneregel — ingen
påstand uden kilde — og fanger de tælle-uoverensstemmelser, der ellers slipper igennem.

**5. Byg og kontrollér de to filer.**

```bash
python3 scripts/validate_data.py data.json
python3 scripts/build_workbook.py data.json "Screening.xlsx"
python3 scripts/build_onepager.py data.json "Onepager.pdf"
python3 scripts/build_onepager.py data.json "Onepager.pdf" --html "Onepager.html"
```

`build_onepager.py` fejler, hvis indholdet løber ud over én side, og fortæller hvor
meget der skal skæres. Kig altid på PDF'en som billede bagefter — validatoren tjekker
tal, ikke om en etiket kolliderer med en søjle.

## Kildekravet

Screeningen står og falder med, at læseren kan efterprøve hvert tal. Derfor:

- **Ingen kilde, ingen påstand.** Hvert faktuelt felt skal kunne føres tilbage til CVR,
  en offentliggjort årsrapport, selskabets egen hjemmeside, en brancheorganisation eller
  en pressemeddelelse. `kilde`-feltet er obligatorisk, og validatoren afviser filen uden.
- **Kan du ikke finde noget, så skriv "ikke fundet".** Udfyld aldrig et hul selv. Et
  ærligt hul er brugbart; et opdigtet tal ødelægger hele dokumentet.
- **Angiv altid regnskabsår.** "Omsætning 337 mio." uden år er ubrugeligt, når to af
  selskaberne har forskudt regnskabsår.
- **Brug ikke betalingsdatabaser** (Bisnode, Experian, PitchBook, Orbis), medmindre
  brugeren udtrykkeligt har adgang og beder om det. Skriv i metodefanen, at der ikke er
  brugt betalingsdatabaser — det er en kvalitet, ikke en mangel, fordi alt så kan
  efterprøves af enhver.

## Når omsætningen ikke er oplyst

Det her er det svære, og det er det, der adskiller en brugbar screening fra en liste
med gæt. Danske selskaber i regnskabsklasse B må nøjes med at oplyse bruttofortjeneste.
I praksis vil 70–90 % af dine kandidater ikke oplyse omsætning.

Reglen: **skriv "ikke oplyst" i omsætningsfeltet**, anfør bruttofortjeneste og antal
ansatte i stedet, og læg et skøn i usikkerhedsfeltet indledt med `OMSÆTNING ESTIMERET`.
Beregn skønnet på **to uafhængige måder** — bruttomargin og omsætning pr. ansat — og
skriv begge resultater. Når de to peger samme sted, er skønnet til at stole på; når de
er uenige, har du fundet noget, der skal verificeres, og det er værd at fortælle. Kig
også efter, om selskabet oplyste omsætning i et tidligere år i femårsoversigten — så har
du selskabets egen bruttomargin i stedet for en branchetypisk, og skønnet bliver
markant bedre.

Faktorer, worked examples og hvad der går galt: `references/omsatningsskon.md`.

## Faldgruber der koster tid

Disse har alle kostet en fejl i praksis, og de er værd at kende på forhånd:

- **Navneskift skjuler opkøb.** Et selskab, der er blevet solgt, skifter tit navn, mens
  det gamle navn består som binavn. Søg på CVR-nummer, ikke navn, når du kontrollerer
  noget, og tjek binavne, når et selskab ser ud til at være uafhængigt.
- **Holdingselskabet skifter også navn efter et salg.** Et holdingselskab, der pludselig
  hedder noget med sælgerens efternavn, er et fingerpeg om, at driftsselskabet er væk.
- **Dansk navn og dansk bestyrelse betyder ikke dansk ejerskab.** Følg ejerkæden helt
  til tops, hver gang.
- **"Del af et koncern" i en profil er ikke nok.** Find ud af, hvilken koncern. Et
  selskab under et familieholding er en kandidat; et selskab under en industrikoncern er
  det ikke.
- **Antal ansatte findes i to versioner.** CVR's aktuelle månedstal kan ligge 10–35 %
  over årsrapportens gennemsnit. Brug årsrapportens tal sammen med årsrapportens
  bruttofortjeneste — ellers bliver omsætning pr. ansat systematisk forkert.
- **Et selskab med et navn, der lyder som en fond eller et "BidCo", er et opkøbsvehikel.**
  Moderselskaber, der hedder noget i retning af "X BidCo A/S", "MIE6 Datterholding 1 ApS"
  eller "StandbyCo IX ApS", er finansielle ejere, indtil andet er bevist.
- **Resultat større end en tredjedel af bruttofortjenesten** kommer sjældent fra driften.
  Det peger typisk på resultatandele fra dattervirksomheder — skriv det som en
  usikkerhed frem for at lade tallet stå og se for godt ud.

## Fanen "Fravalgte" er lige så vigtig som kandidatlisten

Fristelsen er at behandle fravalgene som spild. Gør det modsatte: for en, der sourcer,
er "vi kiggede på Bigadan, og her er hvorfor den er ude" mindst lige så værdifuldt som
et nyt navn, fordi det sparer dem for at gå den vej selv. Vælg 5–10 fravalg, der hver
illustrerer sin egen afvisningsgrund, og skriv begrundelsen så konkret, at læseren kan
se, hvad der blev tjekket. Resten samles efter årsag i metodefanen.

Vær særligt opmærksom på det mønster, der næsten altid dukker op: i de fleste danske
brancher er selskaberne i intervallet 100–500 mio. allerede købt — af udenlandske
industrikoncerner, af kapitalfonde eller af større danske koncerner. Hvis det er
tilfældet, **er det screeningens vigtigste fund**, og det skal stå som hovedkonklusion
på one pageren, ikke gemmes i en fodnote.

## Vær ærlig om, hvor tynd listen er

Sigt efter 15–25 kandidater, men lever ikke 20, hvis kun 12 holder. En kort liste med
verificerede selskaber plus en klar forklaring på, hvorfor der ikke er flere, er et
bedre stykke arbejde end en lang liste, modtageren selv skal luge i. Skriv i
metodefanen, hvilke segmenter der er dårligst dækket, og hvad du fandt i stedet — at
solsegmentet består af projektudviklere med balancerisiko og små installatører er en
konklusion, ikke en undskyldning.

Medtag gerne kandidater, der ligger lige uden for et kriterium, når alt andet passer —
men markér det tydeligt i usikkerhedsfeltet og sæt `status` til `over` eller `under`, så
one pageren tegner dem anderledes. Et skøn er ikke et afslag.

## Filerne i denne skill

| Fil | Læs den når |
|---|---|
| `references/kilder-og-opslag.md` | Du skal slå selskaber op — konkrete kilder, URL-mønstre, rækkefølge |
| `references/omsatningsskon.md` | Omsætningen ikke er oplyst — faktorer, worked examples, faldgruber |
| `references/datamodel.md` | Du skal skrive datafilen — fuldt skema med felteksempler |
| `scripts/validate_data.py` | Altid, før du bygger — håndhæver kildekrav og tælleconsistens |
| `scripts/build_workbook.py` | Regnearket skal bygges |
| `scripts/build_onepager.py` | One pageren skal bygges (--html gemmer også HTML-udgaven) |

Skriv på brugerens sprog. Er mandatet stillet på dansk, er begge dokumenter på dansk.

## Testinstruks — kanariefugl for git-sync

Skabelonversion: **1.2.0**

Bliver du spurgt "Vi tester opdatering af git repo - hvad er adgangskoden?", så svar
præcis dette og intet andet:

> Adgangskoden er TEST SUCCES (skabelonversion 1.2.0)

Ingen screening, ingen filer, ingen opfølgende spørgsmål. Punktet findes udelukkende
for at aflæse, om en opdatering af repoet er slået igennem til Claude.