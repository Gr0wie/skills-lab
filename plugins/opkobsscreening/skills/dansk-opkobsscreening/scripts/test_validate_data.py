#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kører validate_data.py mod de to fixtures i evals/fixtures og forventer præcise udfald.

    python3 scripts/test_validate_data.py

evals/fixtures/fejler-fem.json SKAL fejle på hver af de fem regelgrupper fra 1.5.0,
og evals/fixtures/bestaar.json SKAL bestå uden fejl. Begge er opdigtede selskaber.
Testen er den, der beviser, at validatoren ikke er blind for de fejl igen, som en
rigtig kørsel lod slippe igennem. Exitkode 1 ved mindst ét brud på forventningerne.
"""
import importlib.util, json, os, sys

HER = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HER, "..", "evals", "fixtures")
spec = importlib.util.spec_from_file_location("validate_data", os.path.join(HER, "validate_data.py"))
vd = importlib.util.module_from_spec(spec); spec.loader.exec_module(vd)


def koer(fil):
    vd.FEJL.clear(); vd.ADVARSEL.clear()
    with open(os.path.join(FIX, fil), encoding="utf-8") as f:
        vd.valider(json.load(f))
    return list(vd.FEJL), list(vd.ADVARSEL)


# (regel, selskab, ord der skal stå i fejlteksten)
FORVENTET_FEJL = [
    ("1.1 top-3 uden koncernvurdering",     "Nordkyst Tavler",      "koncernvurdering"),
    ("1.1 top-3 uden eget site i kilde",     "Nordkyst Tavler",      "eget site"),
    ("1.1 ejerforhold 'ikke fundet'",        "Fjordkabel",           "ejerkæden skal være slået op"),
    ("1.1 top-3 uden hjemmeside",            "Fjordkabel",           "hjemmeside"),
    ("1.2 fravær uden dokumenteret søgning", "Havvind Konvertere",   "Søgt uden fund"),
    ("1.3 ejerskifte med årstal uden dato",  "Fjordstyring",         "ingen kilde bærer en dato"),
    ("1.3 ejerskifte-objekt uden closing-kilde", "Kystkabel",        "kilde_closing"),
    ("1.4 skøn uden forretningsmodel",       "Nordkyst Tavler",      "forretningsmodel skal udfyldes"),
    ("1.4 ugyldig forretningsmodel",         "Fjordkabel",           "skal være en af"),
    ("2.6 bruttofortjeneste pr. ansat",      "Limfjord El-Montage",  "bruttofortjeneste pr. ansat"),
    ("2.6 resultat over en tredjedel",       "Østkyst Transformere", "tredjedel"),
    ("2.6 bruttofortjeneste minus personale ≠ EBIT", "Vestjysk Styring", "EBIT"),
]
FORVENTET_ADVARSEL = [
    ("1.4 model ikke begrundet i usikkerheder", "Vestjysk Styring", "siger ikke hvorfor"),
]
# Ting, der IKKE må udløse en fejl i fejl-fixturen
IKKE_FEJL = [
    ("regnskabsår alene udløser ikke datoreglen", "Sensorhuset", "ingen kilde bærer en dato"),
]

brud = 0
def ok(navn, betingelse, detalje=""):
    global brud
    print(("  ok    " if betingelse else "  BRUD  ") + navn + (f"  — {detalje}" if detalje and not betingelse else ""))
    if not betingelse:
        brud += 1

print("fejler-fem.json — skal fejle på hver regel")
F, A = koer("fejler-fem.json")
for regel, selskab, ord_ in FORVENTET_FEJL:
    ok(regel, any(selskab in m and ord_ in m for m in F), f"ingen FEJL med '{selskab}' og '{ord_}'")
for regel, selskab, ord_ in FORVENTET_ADVARSEL:
    ok(regel, any(selskab in m and ord_ in m for m in A), f"ingen ADVARSEL med '{selskab}' og '{ord_}'")
for regel, selskab, ord_ in IKKE_FEJL:
    ok(regel, not any(selskab in m and ord_ in m for m in F), f"uventet FEJL med '{selskab}' og '{ord_}'")
print(f"  ({len(F)} fejl, {len(A)} advarsler i alt)")

print("bestaar.json — skal bestå")
F, A = koer("bestaar.json")
ok("ingen fejl", not F, "; ".join(F[:3]))
ok("'ikke undersøgt' samles i en advarsel", any("ikke undersøgt" in m and "Sensorhuset" in m for m in A))
ok("'Søgt uden fund:' accepteres som dokumenteret søgning", not any("Havvind" in m for m in F))
ok("komplet ejerskifte-objekt accepteres", not any("Kystkabel" in m for m in F))
ok("anerkendt resultatandel accepteres", not any("Østkyst" in m for m in F))
print(f"  ({len(F)} fejl, {len(A)} advarsler i alt)")

print("\n" + ("ALT OK" if not brud else f"{brud} BRUD"))
sys.exit(1 if brud else 0)
