#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrollerer datafilen, før der bygges.

Håndhæver screeningens kerneregel — ingen påstand uden kilde — og fanger de
tælle-uoverensstemmelser, der ellers først opdages, når læseren finder dem.

    python3 validate_data.py data.json

FEJL blokerer for bygning. ADVARSEL er noget, du bør se på, men som ikke stopper noget.
Exitkode 1 ved mindst én fejl.
"""
import json, sys, unicodedata

FEJL, ADVARSEL = [], []
def fejl(m): FEJL.append(m)
def advar(m): ADVARSEL.append(m)

PAAKRAEVET_KANDIDAT = ["navn", "cvr", "segment", "by", "bruttofortjeneste",
                       "regnskabsaar", "ansatte", "egenkapital", "ejerforhold",
                       "beskrivelse", "fit", "usikkerheder", "kilde"]
PAAKRAEVET_FRAVALGT = ["navn", "segment", "begrundelse", "kilde"]
GRUPPER = {"ejerskab", "stoerrelse", "oevrigt"}


def tom(v):
    return v is None or (isinstance(v, str) and not v.strip())


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

    cvr_set = {}
    for i, k in enumerate(kand, 1):
        nav = k.get("navn") or f"kandidat #{i}"
        for f in PAAKRAEVET_KANDIDAT:
            if tom(k.get(f)):
                fejl(f"{nav}: feltet '{f}' er tomt — skriv 'ikke fundet', hvis oplysningen ikke findes")
        cvr = str(k.get("cvr", "")).strip()
        if cvr and cvr != "—":
            if not cvr.isdigit() or len(cvr) != 8:
                advar(f"{nav}: CVR '{cvr}' ser ikke ud som et 8-cifret nummer")
            if cvr in cvr_set:
                fejl(f"{nav}: samme CVR som {cvr_set[cvr]} — dubletter i kandidatlisten")
            cvr_set[cvr] = nav
        kilde = k.get("kilde") or ""
        if len(kilde.strip()) < 15:
            fejl(f"{nav}: kilden er for kortfattet til at kunne efterprøves")

        oms, sk = k.get("omsaetning"), k.get("skoen") or {}
        if oms is None:
            if "OMSÆTNING ESTIMERET" not in (k.get("usikkerheder") or ""):
                fejl(f"{nav}: omsætning er ikke oplyst, så 'usikkerheder' skal indledes med "
                     f"'OMSÆTNING ESTIMERET' og forklare skønnet")
            if sk.get("lav") is None or sk.get("hoej") is None:
                fejl(f"{nav}: omsætning er ikke oplyst, så skoen.lav og skoen.hoej skal udfyldes")
            else:
                if sk["lav"] > sk["hoej"]:
                    fejl(f"{nav}: skoen.lav er større end skoen.hoej")
                if "÷" not in k["usikkerheder"] and "pr. ansat" not in k["usikkerheder"]:
                    advar(f"{nav}: skønnet ser ud til kun at bygge på én metode — "
                          f"anfør både bruttomargin og omsætning pr. ansat")
        st = sk.get("status")
        if st and st not in {"inde", "over", "under"}:
            fejl(f"{nav}: skoen.status '{st}' skal være inde, over eller under")
        lo, hi = meta.get("oms_min"), meta.get("oms_max")
        if lo is not None and st == "inde":
            lav = sk.get("lav", oms); hoej = sk.get("hoej", oms)
            if lav is not None and hoej is not None and (hoej < lo or lav > hi):
                fejl(f"{nav}: markeret 'inde', men intervallet {lav}–{hoej} ligger uden for "
                     f"kriteriet {lo}–{hi}")

    frav = d.get("fravalgte") or []
    if not (5 <= len(frav) <= 10):
        advar(f"{len(frav)} poster i 'fravalgte' — 5-10 er det, fanen er tænkt til")
    for i, f_ in enumerate(frav, 1):
        nav = f_.get("navn") or f"fravalgt #{i}"
        for f in PAAKRAEVET_FRAVALGT:
            if tom(f_.get(f)):
                fejl(f"fravalgt {nav}: feltet '{f}' er tomt")
        if len((f_.get("begrundelse") or "").strip()) < 40:
            advar(f"fravalgt {nav}: begrundelsen er så kort, at læseren ikke kan se, hvad der blev tjekket")

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
        tekst = " ".join(t for _, t in met).lower()
        for emne, ord_ in [("hvordan der blev søgt", "søgt"),
                           ("omsætningsskøn", "estimer"),
                           ("hvad der ikke kunne verificeres", "verificer"),
                           ("hvad man skal være skeptisk over for", "skeptisk")]:
            if ord_ not in tekst:
                advar(f"metodefanen dækker måske ikke {emne}")



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
