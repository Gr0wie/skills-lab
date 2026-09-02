#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrollerer datafilen, før der bygges.

Håndhæver screeningens kerneregel — ingen påstand uden kilde — og fanger de
tælle-uoverensstemmelser, der ellers først opdages, når læseren finder dem.

Siden 1.5.0 fanger den også fem substansfejl, som en rigtig kørsel beviste kunne
slippe igennem:
  · ejerforhold skal være slået op — og for de tre øverste på både selskabets eget
    site og i ejerkæden — før et selskab kan stå på slide 5
  · en påstand om, at en kilde ikke findes, kræver at søgningen er dokumenteret
    ("Søgt uden fund: …"); ellers hedder det "ikke undersøgt"
  · et ejerskifte med årstal kræver en kilde med dato, eller et 'ejerskifte'-objekt
  · et omsætningsskøn skal navngive forretningsmodellen, det bygger på
  · tre regnskabsmæssige sanity-checks skal enten rettes eller anerkendes i
    'usikkerheder' — de må ikke bare stå og se rigtige ud

    python3 validate_data.py data.json

FEJL blokerer for bygning. ADVARSEL er noget, du bør se på, men som ikke stopper noget.
Exitkode 1 ved mindst én fejl.
"""
import json, re, sys

FEJL, ADVARSEL = [], []
def fejl(m): FEJL.append(m)
def advar(m): ADVARSEL.append(m)

PAAKRAEVET_KANDIDAT = ["navn", "cvr", "segment", "by", "hjemmeside", "bruttofortjeneste",
                       "regnskabsaar", "ansatte", "egenkapital", "ejerforhold",
                       "beskrivelse", "fit", "usikkerheder", "kilde"]
PAAKRAEVET_FRAVALGT = ["navn", "segment", "begrundelse", "kilde"]
GRUPPER = {"ejerskab", "stoerrelse", "oevrigt"}
FORRETNINGSMODELLER = {"producent", "grossist", "entreprenoer", "service", "ems"}
MODEL_ORD = {"producent": ("producent", "produktion"),
             "grossist": ("grossist", "distribut", "handelsvirksomhed", "forhandler"),
             "entreprenoer": ("entreprenør", "entreprenoer", "entreprise"),
             "service": ("service", "rådgivning"),
             "ems": ("ems", "kontraktproduktion", "elektronikproduktion")}
IKKE_FUNDET, IKKE_UNDERSOEGT = "ikke fundet", "ikke undersøgt"
SOEGT_MARKOER = "søgt uden fund:"
TOP = 3                       # de tre øverste bærer slide 5 og har skærpede krav
MIN_BF_PR_ANSAT = 0.4         # mio. DKK — derunder er dansk drift usandsynlig

# Sætningsfelter, hvor en påstand om fravær af kilder skal være dokumenteret
SAETNINGSFELTER_K = ("ejerforhold", "usikkerheder", "fit", "beskrivelse")
FRAVAER = re.compile(r"ikke fundet|ingen pressemeddelelse|kun dokumenteret i|ingen presse(?:kilde|dækning|omtale)"
                     r"|pressekilde ikke|ikke omtalt", re.I)
EJERSKIFTE = re.compile(r"overtag|opkøb|købt af|solgt|erhvervet|fusion|acqui|overdrag|ejerskift|majoritet", re.I)
AARSTAL = re.compile(r"\b(?:19|20)\d\d\b")
MAANEDER = "januar|februar|marts|april|maj|juni|juli|august|september|oktober|november|december"
DATO = re.compile(r"\b\d{1,2}\.\s?\d{1,2}\.\s?(?:19|20)\d\d\b"                      # 20.04.2026
                  r"|\b(?:19|20)\d\d-\d\d-\d\d\b"                                    # 2026-04-20
                  r"|\b(?:\d{1,2}\.\s?)?(?:" + MAANEDER + r")\s(?:19|20)\d\d\b", re.I)  # 7. april 2022
ISO = re.compile(r"^(?:19|20)\d\d-\d\d-\d\d$")
DOMAENE = re.compile(r"\b[\w-]+(?:\.[\w-]+)*\.(?:dk|com|net|org|io|eu|se|no|de|uk|biz|fi|nl|ch|at|example)\b", re.I)


def tom(v):
    return v is None or (isinstance(v, str) and not v.strip())

def tekst(v):
    return v if isinstance(v, str) else ""

def tal(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None

def er_hul(v):
    return tekst(v).strip().lower() in (IKKE_FUNDET, IKKE_UNDERSOEGT)

def domaene(h):
    h = tekst(h).strip().lower()
    h = re.sub(r"^https?://", "", h)
    h = re.sub(r"^www\.", "", h)
    return h.split("/")[0]

def soegt_dokumenteret(kilde):
    """'Søgt uden fund: a.dk, b.com' med mindst to forskellige kilder efter markøren."""
    k = tekst(kilde)
    i = k.lower().find(SOEGT_MARKOER)
    if i < 0:
        return False
    fundne = {m.lower() for m in DOMAENE.findall(k[i + len(SOEGT_MARKOER):])}
    return len(fundne) >= 2

def fravaer_tjek(nav, felt, vaerdi, kilde):
    if FRAVAER.search(tekst(vaerdi)) and not soegt_dokumenteret(kilde):
        fejl(f"{nav}: '{felt}' påstår, at noget ikke findes, men 'kilde' viser ikke, hvor der blev søgt. "
             f"Skriv 'Søgt uden fund: <købers newsroom>, <mindst to brancheorganer>' i kilden — "
             f"eller skriv 'ikke undersøgt', hvis der ikke blev søgt")

def ejerskifte_tjek(nav, obj):
    """True hvis 'ejerskifte' er udfyldt gyldigt: mindst én ISO-dato, og hver dato har sin kilde."""
    if not isinstance(obj, dict):
        fejl(f"{nav}: 'ejerskifte' skal være et objekt med annonceret, closing, koeber og kilder")
        return False
    ok = True
    if tom(obj.get("koeber")):
        fejl(f"{nav}: ejerskifte.koeber mangler"); ok = False
    har_dato = False
    for felt, kildefelt in (("annonceret", "kilde_annoncering"), ("closing", "kilde_closing")):
        v = obj.get(felt)
        if v is None:
            continue
        har_dato = True
        if not ISO.match(tekst(v)):
            fejl(f"{nav}: ejerskifte.{felt} skal skrives som ÅÅÅÅ-MM-DD, ikke '{v}'"); ok = False
        if len(tekst(obj.get(kildefelt)).strip()) < 15:
            fejl(f"{nav}: ejerskifte.{felt} er udfyldt, men {kildefelt} mangler — hver dato skal have sin egen kilde"); ok = False
    if not har_dato:
        fejl(f"{nav}: 'ejerskifte' har hverken annonceret eller closing"); ok = False
    return ok

def dateret_tjek(nav, felt, vaerdi, kilde, ejerskifte_ok):
    t = tekst(vaerdi)
    if EJERSKIFTE.search(t) and AARSTAL.search(t) and not ejerskifte_ok and not DATO.search(tekst(kilde)):
        fejl(f"{nav}: '{felt}' nævner et ejerskifte med årstal, men ingen kilde bærer en dato. "
             f"Skriv kilden med publiceringsdato (fx 'kapwatch.dk, 21.04.2026'), eller udfyld 'ejerskifte' "
             f"med annonceret og closing hver for sig")


def valider(d):
    meta = d.get("meta") or {}
    for f in ["titel", "dato", "oms_min", "oms_max", "kriterier"]:
        if f not in meta or tom(meta.get(f)):
            fejl(f"meta.{f} mangler")
    if meta.get("oms_min") is not None and meta.get("oms_max") is not None:
        if meta["oms_min"] >= meta["oms_max"]:
            fejl("meta.oms_min skal være mindre end meta.oms_max")

    kand = d.get("kandidater") or []
    if not kand:
        fejl("ingen kandidater i filen")
    if 0 < len(kand) < 5:
        advar(f"kun {len(kand)} kandidater — er listen for tynd, så forklar hvorfor i metodefanen")

    huller_undersoegt, huller_fundet, mangler_resultat = [], [], 0
    cvr_set = {}
    for i, k in enumerate(kand, 1):
        nav = k.get("navn") or f"kandidat #{i}"
        for f in PAAKRAEVET_KANDIDAT:
            if tom(k.get(f)):
                fejl(f"{nav}: feltet '{f}' er tomt — skriv 'ikke fundet' (der blev søgt) eller "
                     f"'ikke undersøgt' (der blev ikke søgt); lad det aldrig stå tomt")
        for f, v in k.items():
            if isinstance(v, str) and v.strip().lower() == IKKE_UNDERSOEGT:
                huller_undersoegt.append(f"{nav}.{f}")
            elif isinstance(v, str) and v.strip().lower() == IKKE_FUNDET and f not in SAETNINGSFELTER_K:
                huller_fundet.append(f"{nav}.{f}")
        cvr = str(k.get("cvr", "")).strip()
        if cvr and cvr != "—":
            if not cvr.isdigit() or len(cvr) != 8:
                advar(f"{nav}: CVR '{cvr}' ser ikke ud som et 8-cifret nummer")
            if cvr in cvr_set:
                fejl(f"{nav}: samme CVR som {cvr_set[cvr]} — dubletter i kandidatlisten")
            cvr_set[cvr] = nav
        kilde = tekst(k.get("kilde"))
        if len(kilde.strip()) < 15:
            fejl(f"{nav}: kilden er for kortfattet til at kunne efterprøves")

        # --- ejerforhold: et hul her er et manglende fravalg, ikke et ærligt hul
        ejer = tekst(k.get("ejerforhold"))
        if er_hul(ejer):
            fejl(f"{nav}: 'ejerforhold' er '{ejer.strip()}' — ejerkæden skal være slået op, før et selskab "
                 f"kan stå som kandidat. Er ejeren en koncern, hører selskabet til i 'fravalgte'")
        elif "koncern" not in ejer.lower():
            if i <= TOP:
                fejl(f"{nav}: står blandt de {TOP} øverste, men 'ejerforhold' mangler en eksplicit koncernvurdering, "
                     f"fx 'ikke del af nogen koncern ifølge selskabets egne sider og ejerkæden'")
            else:
                advar(f"{nav}: 'ejerforhold' siger ikke, om selskabet er del af en koncern — skriv det udtrykkeligt")
        if i <= TOP:
            h = domaene(k.get("hjemmeside"))
            if not h or er_hul(k.get("hjemmeside")):
                fejl(f"{nav}: står blandt de {TOP} øverste, men 'hjemmeside' er ikke udfyldt — selskabets eget site "
                     f"(forside, om-side, sidefod) skal være læst, før det kan stå på slide 5")
            elif h not in kilde.lower():
                fejl(f"{nav}: står blandt de {TOP} øverste, men 'kilde' nævner ikke selskabets eget site ({h}). "
                     f"Sidefoden og om-siden er den kilde, der afgør koncerntilhør")
            if "ownr.dk" not in kilde.lower():
                fejl(f"{nav}: står blandt de {TOP} øverste, men 'kilde' nævner ikke ownr.dk — ejerkæden skal være slået op")

        # --- påstande om fravær, og ejerskifter uden dato
        ejerskifte_ok = ejerskifte_tjek(nav, k["ejerskifte"]) if "ejerskifte" in k else False
        for f in SAETNINGSFELTER_K:
            fravaer_tjek(nav, f, k.get(f), kilde)
        dateret_tjek(nav, "ejerforhold", ejer, kilde, ejerskifte_ok)

        # --- omsætning: oplyst eller skønnet med navngiven forretningsmodel
        oms, sk = k.get("omsaetning"), k.get("skoen") or {}
        usik = tekst(k.get("usikkerheder"))
        if oms is None:
            if "OMSÆTNING ESTIMERET" not in usik:
                fejl(f"{nav}: omsætning er ikke oplyst, så 'usikkerheder' skal indledes med "
                     f"'OMSÆTNING ESTIMERET' og forklare skønnet")
            if sk.get("lav") is None or sk.get("hoej") is None:
                fejl(f"{nav}: omsætning er ikke oplyst, så skoen.lav og skoen.hoej skal udfyldes")
            else:
                if sk["lav"] > sk["hoej"]:
                    fejl(f"{nav}: skoen.lav er større end skoen.hoej")
                if "÷" not in usik and "pr. ansat" not in usik:
                    advar(f"{nav}: skønnet ser ud til kun at bygge på én metode — "
                          f"anfør både bruttomargin og omsætning pr. ansat")
            fm = tekst(sk.get("forretningsmodel")).strip().lower()
            if not fm:
                fejl(f"{nav}: omsætningen er skønnet, så skoen.forretningsmodel skal udfyldes "
                     f"({', '.join(sorted(FORRETNINGSMODELLER))}) — marginen afhænger af, om selskabet "
                     f"er producent eller grossist, og det skal være afgjort før beregningen")
            elif fm not in FORRETNINGSMODELLER:
                fejl(f"{nav}: skoen.forretningsmodel '{fm}' skal være en af {', '.join(sorted(FORRETNINGSMODELLER))}")
            elif not any(o in usik.lower() for o in MODEL_ORD[fm]):
                advar(f"{nav}: skønnet bygger på modellen '{fm}', men 'usikkerheder' siger ikke hvorfor — "
                      f"skriv antagelsen før de to beregninger")
        st = sk.get("status")
        if st and st not in {"inde", "over", "under"}:
            fejl(f"{nav}: skoen.status '{st}' skal være inde, over eller under")
        lo, hi = meta.get("oms_min"), meta.get("oms_max")
        if lo is not None and st == "inde":
            lav = sk.get("lav", oms); hoej = sk.get("hoej", oms)
            if lav is not None and hoej is not None and (hoej < lo or lav > hi):
                fejl(f"{nav}: markeret 'inde', men intervallet {lav}–{hoej} ligger uden for "
                     f"kriteriet {lo}–{hi}")

        # --- sanity-checks: ret tallet, eller anerkend det i 'usikkerheder'
        u = usik.lower()
        bf, ans = tal(k.get("bruttofortjeneste")), tal(k.get("ansatte"))
        if bf is not None and ans and ans > 0 and bf / ans < MIN_BF_PR_ANSAT:
            if not any(o in u for o in ("bruttofortjeneste pr. ansat", "udland", "koncernen", "produktionen ligger")):
                fejl(f"{nav}: bruttofortjeneste pr. ansat er {bf / ans:.2f} mio. — under {MIN_BF_PR_ANSAT} er "
                     f"usandsynligt for dansk drift. Enten er bruttofortjenesten opgjort efter personaleomkostninger, "
                     f"eller også ligger produktionen i udlandet. Ret tallet, eller skriv forklaringen i "
                     f"'usikkerheder' (nævn 'bruttofortjeneste pr. ansat' eller 'udland')")
        res = tal(k.get("aarets_resultat"))
        if res is None:
            mangler_resultat += 1
        elif bf and bf > 0 and res > bf / 3:
            if not any(o in u for o in ("resultatandel", "dattervirksomhed", "datterselskab", "døtre")):
                fejl(f"{nav}: årets resultat {res} er over en tredjedel af bruttofortjenesten {bf} — det kommer "
                     f"sjældent fra driften. Kig efter resultatandele fra dattervirksomheder, og skriv det i "
                     f"'usikkerheder' (nævn 'resultatandel' eller 'dattervirksomhed')")
        pers, afs, ebit = tal(k.get("personaleomkostninger")), tal(k.get("afskrivninger")) or 0, tal(k.get("ebit"))
        if bf is not None and pers is not None and ebit is not None:
            beregnet = bf - pers - afs
            if abs(beregnet - ebit) > max(1.0, 0.1 * abs(bf)) and "personaleomkostninger" not in u:
                fejl(f"{nav}: bruttofortjeneste {bf} minus personaleomkostninger {pers} og afskrivninger {afs} "
                     f"giver EBIT {beregnet:.1f}, men EBIT er {ebit}. Så er bruttofortjenesten formentlig opgjort "
                     f"efter personaleomkostninger, og skønnet er for lavt. Ret tallene, eller forklar det i "
                     f"'usikkerheder' (nævn 'personaleomkostninger')")

    if mangler_resultat:
        advar(f"{mangler_resultat} kandidater mangler 'aarets_resultat' — kontrollen for resultatandele fra "
              f"dattervirksomheder kan ikke køres på dem")

    frav = d.get("fravalgte") or []
    if not (5 <= len(frav) <= 10):
        advar(f"{len(frav)} poster i 'fravalgte' — 5-10 er det, fanen er tænkt til")
    for i, f_ in enumerate(frav, 1):
        nav = f_.get("navn") or f"fravalgt #{i}"
        for f in PAAKRAEVET_FRAVALGT:
            if tom(f_.get(f)):
                fejl(f"fravalgt {nav}: feltet '{f}' er tomt")
        for f, v in f_.items():
            if isinstance(v, str) and v.strip().lower() == IKKE_UNDERSOEGT:
                huller_undersoegt.append(f"{nav}.{f}")
        beg, kilde = tekst(f_.get("begrundelse")), tekst(f_.get("kilde"))
        if len(beg.strip()) < 40:
            advar(f"fravalgt {nav}: begrundelsen er så kort, at læseren ikke kan se, hvad der blev tjekket")
        ejerskifte_ok = ejerskifte_tjek(f"fravalgt {nav}", f_["ejerskifte"]) if "ejerskifte" in f_ else False
        fravaer_tjek(f"fravalgt {nav}", "begrundelse", beg, kilde)
        dateret_tjek(f"fravalgt {nav}", "begrundelse", beg, kilde, ejerskifte_ok)

    if huller_undersoegt:
        advar(f"'ikke undersøgt' i {len(huller_undersoegt)} felter — nævn dem i metodefanen: " + ", ".join(huller_undersoegt))
    if huller_fundet:
        advar(f"'ikke fundet' i {len(huller_fundet)} felter — er der faktisk søgt? Ellers hedder det "
              f"'ikke undersøgt': " + ", ".join(huller_fundet))

    oev = d.get("oevrige_fravalgte") or []
    sum_oev = 0
    for o in oev:
        aar = o.get("aarsag") or "?"
        if o.get("gruppe") not in GRUPPER:
            fejl(f"øvrige fravalgte '{aar}': gruppe skal være en af {sorted(GRUPPER)}")
        n = o.get("antal")
        if not isinstance(n, int) or n < 1:
            fejl(f"øvrige fravalgte '{aar}': antal skal være et helt tal over 0")
        else:
            sum_oev += n
            talt = len([s for s in (o.get("selskaber") or "").split("·") if s.strip()])
            if talt and talt != n:
                advar(f"øvrige fravalgte '{aar}': antal er {n}, men der er listet {talt} selskaber")

    if meta.get("antal_vurderet") is not None and oev:
        forventet = len(kand) + sum_oev
        if forventet != meta["antal_vurderet"]:
            fejl(f"meta.antal_vurderet er {meta['antal_vurderet']}, men kandidater ({len(kand)}) "
                 f"plus øvrige fravalgte ({sum_oev}) giver {forventet}. "
                 f"De to dokumenter ville vise forskellige tal.")

    seg = d.get("segmentdaekning") or []
    if seg:
        s = sum(x.get("antal", 0) for x in seg)
        if s != len(kand):
            fejl(f"segmentdækningen summer til {s}, men der er {len(kand)} kandidater")
        if not any(x.get("antal", 0) == 0 for x in seg):
            advar("ingen segmenter med nul kandidater — er alle mandatets segmenter med i listen?")

    met = d.get("metode") or []
    if not met:
        fejl("metode mangler — fanen 'Metode og forbehold' er en del af leverancen")
    else:
        typer = {t for t, _ in met}
        if "h1" not in typer:
            advar("metode har ingen h1-overskrift")
        tekst_ = " ".join(t for _, t in met).lower()
        for emne, ord_ in [("hvordan der blev søgt", "søgt"),
                           ("omsætningsskøn", "estimer"),
                           ("hvad der ikke kunne verificeres", "verificer"),
                           ("hvad man skal være skeptisk over for", "skeptisk")]:
            if ord_ not in tekst_:
                advar(f"metodefanen dækker måske ikke {emne}")
        if huller_undersoegt and IKKE_UNDERSOEGT not in tekst_:
            advar("der er felter med 'ikke undersøgt', men metodefanen nævner ikke, hvad der ikke blev undersøgt")


def main():
    if len(sys.argv) < 2:
        print("brug: validate_data.py <data.json>"); sys.exit(2)
    with open(sys.argv[1], encoding="utf-8") as f:
        d = json.load(f)
    valider(d)
    for m in ADVARSEL:
        print(f"ADVARSEL  {m}")
    for m in FEJL:
        print(f"FEJL      {m}")
    k = len(d.get("kandidater") or []); fr = len(d.get("fravalgte") or [])
    print(f"\n{k} kandidater · {fr} fravalgte · {len(FEJL)} fejl · {len(ADVARSEL)} advarsler")
    sys.exit(1 if FEJL else 0)


if __name__ == "__main__":
    main()
