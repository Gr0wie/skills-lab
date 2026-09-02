# Ændringer

Versionen står i `plugins/opkobsscreening/.claude-plugin/plugin.json` og i
`.claude-plugin/marketplace.json`, og de to skal følges ad. Kanariefuglen nederst i
`SKILL.md` svarer med det versionsnummer, Claude faktisk har hentet.

## 1.5.0 — 2. september 2026

En rigtig kørsel blev gennemlæst efter levering. Fire substansfejl var sluppet
gennem begge validatorer, og alle fire var af den slags, en modtager med
branchekendskab finder på sekunder. Denne version gør dem til kode.

**Ejerforhold skal være slået op, før et selskab kan stå øverst.** Et selskab stod
blandt "tre at starte med", selv om sidefoden på dets eget site sagde, at det var del
af en udenlandsk koncern; ejerkæden viste kun et procentinterval. Nu kræver
`validate_data.py`, at de tre øverste kandidater har selskabets eget domæne
(nyt felt `hjemmeside`) **og** ownr.dk i kildefeltet, og at `ejerforhold` indeholder
en eksplicit koncernvurdering. `ejerforhold` med værdien "ikke fundet" eller
"ikke undersøgt" er nu FEJL for alle kandidater — det er et manglende fravalg, ikke
et ærligt hul.

**"Ikke fundet" og "ikke undersøgt" betyder to forskellige ting.** En kørsel skrev
"ingen pressemeddelelse" om et opkøb, som køberen selv havde annonceret; sætningen
kom fra et opbrugt søgebudget og et blokeret newsroom, ikke fra et udtømt marked.
Nu kræver enhver påstand om fravær af kilder en linje `Søgt uden fund: …` med mindst
to kilder i kildefeltet — ellers skal der stå "ikke undersøgt". `SKILL.md` siger
desuden, at et opbrugt søgebudget skal rapporteres og udløse et genopslag, aldrig
en konklusion.

**Ejerskifter skal have daterede kilder.** Et årstal for et ejerskifte stod uden
kilde med dato, og det var closing-året, ikke annonceringsåret. Nævner en
begrundelse et ejerskifte med årstal, skal kilden bære en dato, eller posten skal
have et nyt `ejerskifte`-objekt med `annonceret` og `closing` hver for sig og en
kilde pr. dato.

**Omsætningsskøn skal navngive forretningsmodellen.** Marginerne blev anvendt uden
først at afgøre, om selskabet er producent eller grossist; for et selskab med
14 ansatte i Danmark og produktion i udlandet gav de to metoder vidt forskellige
tal, uden at årsagen blev navngivet. `skoen.forretningsmodel` er nu obligatorisk
(producent, grossist, entreprenoer, service, ems), og `omsatningsskon.md` har et
afsnit om, hvordan modellen afgøres, før der regnes.

**Tre sanity-checks i koden — ret eller anerkend.** Bruttofortjeneste pr. ansat under
0,4 mio., årets resultat over en tredjedel af bruttofortjenesten, og bruttofortjeneste
minus personaleomkostninger og afskrivninger, der ikke giver EBIT, er FEJL, medmindre
`usikkerheder` forklarer det. De to sidste kræver de nye, valgfrie felter
`aarets_resultat`, `personaleomkostninger`, `afskrivninger` og `ebit`.

Desuden: `scripts/test_validate_data.py` med to opdigtede fixtures i
`evals/fixtures/` — én, der skal fejle på hver regel, og én, der skal bestå; en
tredje eval-case; kolonnen Hjemmeside i regnearkets kandidatfane; og
ejerskifte-datoerne skrevet ind i fravalgsbegrundelsen. Deck-scriptet og
`validate_deck.py` er uændrede.

## 1.4.0 og tidligere

Se tabellen "Den trinvise gennemgang" i `README.md`: v0.1 kun `SKILL.md`, v0.2 plus
`references/`, v1.0 plus `scripts/` og `evals/`, 1.4.0 med deck i stedet for
one-pager og `validate_deck.py` som anden kvalitetsport.
