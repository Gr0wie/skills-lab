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
---

# Screening af danske opkøbsemner

*Version 0.2 — nu med referencefiler. Stadig ingen scripts; dokumenterne bygges i hånden.*

## Hvad du leverer

To filer, og som udgangspunkt begge:

1. **Et regneark** med præcis tre faner: `Kandidater`, `Fravalgte`, `Metode og forbehold`.
2. **En A4 one pager i PDF** — nøgletal, hovedkonklusion, en graf over kandidaternes
   omsætning mod kriteriet, dækning pr. segment, fordeling af fravalgsårsager.

Byg dem med de værktøjer, du har til rådighed. Sørg for, at tallene i de to dokumenter
stemmer overens — det er lettere sagt end gjort, når man skriver dem hver for sig.
`references/datamodel.md` beskriver den datastruktur, du med fordel kan samle tallene i
først, netop for at undgå at de to dokumenter kommer i utakt.

## Arbejdsgangen

**1. Læs mandatet, og skriv kriterierne ned.** Typisk: omsætningsinterval, dansk
hovedsæde, ikke børsnoteret, ikke del af større koncern, ikke kapitalfondsejet, gerne
tegn på generationsskifte. Har brugeren ikke sat et omsætningsinterval, så spørg.
Segmenter: brug brugerens egne, ellers foreslå 6–8 og få dem bekræftet.

**2. Byg en bruttoliste pr. segment.** Navne kommer fra brancheorganisationers
medlemslister, branchesøgninger, fagpressen og egen brancheviden. Sigt efter 5–10 navne
pr. segment.

**3. Slå hvert selskab op — ejerforhold først, så regnskab.** Ejerkæden frasorterer
typisk halvdelen af listen, og regnskabstal på et selskab, der viser sig at være
udenlandsk ejet, er spildt arbejde. Læs femårsoversigten, ikke kun seneste år.
`references/kilder-og-opslag.md` har de konkrete kilder, URL-mønstre og den rækkefølge,
der sparer mest tid.

**4. Skriv de to dokumenter, og kontrollér dem mod hinanden.**

## Kildekravet

- **Ingen kilde, ingen påstand.** Hvert faktuelt felt skal kunne føres tilbage til CVR,
  en offentliggjort årsrapport, selskabets hjemmeside, en brancheorganisation eller en
  pressemeddelelse.
- **Kan du ikke finde noget, så skriv "ikke fundet".** Udfyld aldrig et hul selv.
- **Angiv altid regnskabsår.**
- **Brug ikke betalingsdatabaser**, og skriv i metodefanen, at der ikke er brugt nogen.

## Når omsætningen ikke er oplyst

Danske selskaber i regnskabsklasse B må nøjes med at oplyse bruttofortjeneste, og i
praksis vil 70–90 % af kandidaterne gøre netop det. Skriv **"ikke oplyst"** i
omsætningsfeltet, anfør bruttofortjeneste og antal ansatte i stedet, og læg et skøn i
usikkerhedsfeltet indledt med `OMSÆTNING ESTIMERET`. Beregn skønnet på to uafhængige
måder — bruttomargin og omsætning pr. ansat — og skriv begge resultater, så læseren kan
se, om de er enige. Gæt aldrig et tal uden at markere det som skøn.

Faktorer, worked examples og det bedste anker af alle — et tidligere år, hvor selskabet
faktisk oplyste omsætning — står i `references/omsatningsskon.md`.

## Faldgruber

- Navneskift skjuler opkøb; søg på CVR-nummer, ikke navn, og tjek binavne.
- Dansk navn og dansk bestyrelse betyder ikke dansk ejerskab — følg kæden helt til tops.
- "Del af et koncern" er ikke nok; find ud af hvilken.
- Antal ansatte findes i to versioner — årsrapportens gennemsnit og CVR's aktuelle tal
  kan afvige 10–35 %. Brug årsrapportens.
- Moderselskaber med navne som "BidCo" eller "StandbyCo" er opkøbsvehikler.

## Fanen "Fravalgte" er lige så vigtig som kandidatlisten

For en, der sourcer, er "vi kiggede på X, og her er hvorfor den er ude" mindst lige så
værdifuldt som et nyt navn. Vælg 5–10 fravalg, der hver illustrerer sin egen
afvisningsgrund. Er markedet allerede konsolideret, **er det screeningens vigtigste
fund** og skal stå som hovedkonklusion, ikke i en fodnote.

## Vær ærlig om, hvor tynd listen er

Sigt efter 15–25 kandidater, men lever ikke 20, hvis kun 12 holder. Skriv i metodefanen,
hvilke segmenter der er dårligst dækket, og hvad du fandt i stedet.

## Filerne i denne skill

| Fil | Læs den når |
|---|---|
| `references/kilder-og-opslag.md` | Du skal slå selskaber op — konkrete kilder, URL-mønstre, rækkefølge |
| `references/omsatningsskon.md` | Omsætningen ikke er oplyst — faktorer, worked examples, faldgruber |
| `references/datamodel.md` | Du vil samle tallene ét sted, før du bygger de to dokumenter |

Skriv på brugerens sprog.
