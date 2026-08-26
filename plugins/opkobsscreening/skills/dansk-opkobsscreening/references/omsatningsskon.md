# Omsætningsskøn, når omsætningen ikke er oplyst

Selskaber i regnskabsklasse B må undlade at oplyse nettoomsætning. I praksis oplyser
70–90 % af kandidaterne i en typisk screening kun bruttofortjeneste. Skønnet er derfor
ikke en randbemærkning — det er den beregning, der afgør, om et selskab overhovedet
hører til på listen.

## Reglen

1. `omsaetning: null` i datafilen → regnearket skriver "ikke oplyst".
2. Bruttofortjeneste og antal ansatte anføres i deres egne felter.
3. Usikkerhedsfeltet indledes med `OMSÆTNING ESTIMERET` efterfulgt af intervallet og
   **begge** beregninger.
4. `skoen.lav` og `skoen.hoej` sættes til det samlede interval, du står inde for.

Gæt aldrig et tal uden at markere det som skøn. Et markeret skøn er brugbart; et
umarkeret skøn er en fejl, der forplanter sig hele vejen til en indikation.

## Metode A — bruttomargin

`omsætning ≈ bruttofortjeneste ÷ bruttomargin`

| Forretningstype | Typisk bruttomargin |
|---|---|
| EPC og anlægsbyggeri | 15–25 % |
| Produktion med høj materialeandel | 20–35 % |
| Tavle- og køretøjsproduktion, distribution | 30–45 % |
| Teknisk entreprise og installation | 35–45 % |
| Servicevirksomhed uden materialesalg | 45–65 % |

## Metode B — omsætning pr. ansat

`omsætning ≈ antal ansatte × omsætning pr. ansat`

| Forretningstype | Typisk omsætning pr. ansat (mio. DKK) |
|---|---|
| Produktion | 1,5–2,5 |
| Service og rådgivning | 1,0–2,5 |
| Distribution, anlæg med høj materialegennemstrømning | 2,5–4,0 |

Brug **årsrapportens** antal ansatte, ikke CVR's aktuelle månedstal. De to kan afvige
10–35 %, og forskellen slår direkte igennem i denne beregning.

## Kør altid begge, og skriv begge

De to metoder er uafhængige, og det er hele værdien. Når de peger samme sted, har du et
skøn, du kan bruge. Når de er uenige, har du fundet noget — enten en usædvanlig
forretningsmodel eller et tal, der skal verificeres — og det er en oplysning, læseren
skal have, ikke noget du skal glatte ud ved at tage et gennemsnit.

**Eksempel, enige:** En tavleproducent med bruttofortjeneste 191,3 mio. og 242 ansatte.
Metode A: 191,3 ÷ 0,35–0,45 = 425–546 mio. Metode B: 242 × 1,8–2,5 = 435–605 mio.
Begge peger på, at selskabet ligger lige omkring eller over 500 mio. Skriv 430–550 og
markér det som muligt over loftet.

**Eksempel, uenige:** En smedje med bruttofortjeneste 66,0 mio. og 75 ansatte.
Metode A: 66,0 ÷ 0,25–0,35 = 189–264 mio. Metode B: 75 × 1,5–2,5 = 113–188 mio.
Intervallerne rører knap hinanden. Skriv det brede interval 120–260 mio., skriv begge
beregninger, og skriv at selskabet derfor kan ligge under den nedre grænse. Det er en
ærlig og brugbar konklusion.

## Det bedste anker: selskabets eget tidligere år

Kig altid femårsoversigten igennem for et år, hvor omsætningen faktisk **var** oplyst.
Det sker oftere, end man tror — kravene skifter, når et selskab krydser en
størrelsesgrænse, eller ledelsen skifter praksis. Har du sådan et år, kan du beregne
selskabets **egen** bruttomargin og bruge den på de senere år i stedet for en
branchetypisk. Det er størrelsesordener mere præcist.

**Eksempel:** En varmepumpeproducent oplyste omsætning 357,5 mio. i 2022/23 mod en
bruttofortjeneste på 86,7 mio. — altså en bruttomargin på 24,2 %. Anvendt på FY2025's
bruttofortjeneste på 91,7 mio. giver det 378 mio. Skriv 360–400 mio. og forklar
ankeret. Det er det mest velunderbyggede skøn, screeningen kan producere, og det er
værd at nævne i metodefanen som noget, der bør eftersøges for hvert selskab.

## Hvor usikkert er det?

Ti procentpoints fejl i den antagne bruttomargin flytter estimatet 30–50 %. Sig det
rent ud i metodefanen. Skønnene er gode nok til at afgøre, om et selskab er værd at
kigge nærmere på, og ikke til andet.

## Sanity-checks der fanger fejl

- **Årets resultat over ~⅓ af bruttofortjenesten** kommer sjældent fra driften. Kig
  efter resultatandele fra dattervirksomheder, og skriv det som en usikkerhed.
- **Egenkapital på under en tiendedel af den skønnede omsætning** i en
  produktionsvirksomhed er lavt. Enten er skønnet for højt, eller også er selskabet
  tyndt kapitaliseret — begge dele er værd at nævne.
- **Bruttofortjeneste, der fordobles på ét år**, gør alle forholdstal upålidelige. Udvid
  intervallet, og skriv hvorfor.
- **Negativ bruttofortjeneste i et år** i en EPC-forretning betyder, at marginmetoden
  ikke kan bruges meningsfuldt på det selskab. Sig det.
