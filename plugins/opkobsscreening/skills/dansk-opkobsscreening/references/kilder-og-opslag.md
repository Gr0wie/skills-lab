# Kilder og opslag

Alt herunder er gratis og offentligt tilgængeligt. Brug ikke betalingsdatabaser, med
mindre brugeren udtrykkeligt beder om det og har adgang.

## Rækkefølgen der sparer mest tid

Tjek **ejerforhold før regnskabstal**. Et opslag i ejerkæden tager ét kald og
frasorterer typisk halvdelen af bruttolisten. Regnskabstal på et selskab, der viser sig
at være ejet af Lindab, er spildt arbejde.

1. Find CVR-nummer og ejerkæde
2. Er ejeren en udenlandsk koncern, en fond eller en større dansk koncern → fravalgt,
   notér begrundelse og gå videre
3. Ellers: hent femårs-regnskabstal
4. Er selskabet i intervallet → hent forretningsbeskrivelse fra egen hjemmeside
5. Er ejerskiftet afgørende for fravalget → find en pressekilde, der bekræfter det

## De fire kilder

### CVR — datacvr.virk.dk
Den autoritative kilde. Primærkildelinket til hvert selskab er
`https://datacvr.virk.dk/enhed/virksomhed/<CVR-NR>`. Siden er JavaScript-drevet og lader
sig sjældent hente programmatisk — men linket hører alligevel i kildekolonnen, fordi det
er det, en læser skal klikke på for at efterprøve. Registret over **reelle ejere** kræver
godkendelse (siden 1. september 2025), så skriv aldrig "reelle ejere" om noget, du har
udledt af ejerkæden. Skriv "ultimative ejere ifølge ejerkæden".

### proff.dk — regnskabstal
Gengiver de årsrapporter, selskaberne har indleveret til Erhvervsstyrelsen. To sider pr.
selskab er værd at kende:

- `proff.dk/firma/<slug>/<by>/<branche>/<id>` — stamdata, seneste år, moderselskab
- `proff.dk/regnskab/<slug>/<by>/<branche>/<id>` — **femårsoversigten**, som er den, du
  vil have: omsætning, bruttofortjeneste, årets resultat, egenkapital og antal ansatte
  for fem år. Brug den som standard.

Find id'et ved at søge med `allowed_domains: ["proff.dk"]` på selskabsnavn + by + CVR.
`proff.dk/branchesøg?q=<søgeord>` giver brancheoversigter med bruttofortjeneste — nyttigt
til at finde navne, du ikke selv kendte, men vær opmærksom på, at listerne blandes med
projektselskaber og enkeltmandsvirksomheder.

Skriv i metodeafsnittet, at tallene er læst hos proff.dk og ikke i PDF-årsrapporten, og
at de bør kontrolleres i årsrapporten, før de bruges i en indikation. Det er en reel
gengivelsesrisiko, og læseren skal kende den.

### ownr.dk — ejerforhold
`https://ownr.dk/companies/public-profile/<CVR-NR>` — rent CVR-nummer i URL'en, så det
er hurtigt, når du har nummeret. Viser legale ejere med ejerandele (i intervaller som
"33,34–49,99 %") og en udledt liste over ultimative ejere. Det er her, du fanger de
udenlandske moderselskaber.

Læs listen af ultimative ejere som et signal om ejertype, ikke kun som navne:

- Flere personer med samme efternavn, ofte to generationer → familieejet, muligt
  generationsskifte. Det er det stærkeste positive signal, screeningen kan give.
- Et enkelt udenlandsk selskabsnavn → koncernejet, fravalgt.
- En blanding af personer med hver sit efternavn plus en institutionel investor →
  investorgruppe. Prøv at finde en pressekilde; kan du ikke, så skriv at ejerforholdet
  ikke er verificeret, i stedet for at gætte.

### Pressekilder — når et ejerskifte afgør sagen
Søg på selskabsnavn plus "opkøb", "overtager", "kapitalfond" eller ejerens navn. De
danske kilder, der oftest har historien: energy-supply.dk, kapwatch.dk, borsen.dk,
finans.dk, licitationen.dk, medwatch.dk, fødevarewatch.dk — plus køberens egen
pressemeddelelse (news.cision.com, via.ritzau.dk, selskabets investor-side). En
pressemeddelelse fra køberen er den stærkeste kilde, du kan få, fordi den er
førstehåndsudsagn.

## Brancheorganisationers medlemslister

De er den bedste kilde til navne, du ikke selv kender, fordi de er kuraterede af
branchen. Nogle blokerer for hentning; prøv alligevel. Eksempler efter område:

- Energi og forsyning: Green Power Denmark, Biogas Danmark, Brintbranchen, Dansk Fjernvarme
- Industri og produktion: Dansk Industri, DI Byggeri, Plastindustrien
- Byggeri: TEKNIQ Arbejdsgiverne, Danske Byggecentre
- Fødevarer: Landbrug & Fødevarer, Dansk Erhverv
- Transport: DTL, ITD, Danske Havne

Læs listen med et filter: de fleste medlemmer vil være rådgivere, forsyningsselskaber,
udenlandske leverandører eller startups. Producenterne og udstyrsleverandørerne er dem,
du leder efter.

## Hvad hver kilde ikke kan

- **proff.dk** kender ikke ejerforhold ud over nærmeste moderselskab.
- **ownr.dk** viser ikke regnskabstal.
- **Brancheorganisationer** siger intet om størrelse eller ejerskab.
- **Ingen af dem** fortæller, hvor stor en andel af omsætningen der er relevant for
  mandatet. Det står kun i selskabets egen kommunikation, og som regel ikke i tal. Skriv
  det som en usikkerhed frem for at antage.
