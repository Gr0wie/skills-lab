#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bygger den grafiske A4 one pager som PDF.

    python3 build_onepager.py data.json "Onepager.pdf" [--html ud.html]

Rendrer via Chromium (Playwright), fordi typografi og millimeterpræcis A4-opsætning
er lettere at styre i HTML end i reportlab. Scriptet prøver sig frem med tætheden,
indtil indholdet passer på præcis én side, og fejler hellere end at levere to sider.

Farverne er den validerede palet fra dataviz-skillen: blå/orange/aqua klarer både
farveblindheds- og normalsynstærsklerne på alle par. Skift dem kun ud samlet.
"""
import json, sys, asyncio, os

P = {
    "ink": "#0b0b0b", "ink2": "#52514e", "muted": "#898781",
    "grid": "#e1e0d9", "axis": "#c3c2b7", "band": "#f0efec",
    "surface": "#fcfcfb", "plane": "#f9f9f7",
    "s1": "#2a78d6", "s1l": "#86b6ef", "s2": "#eb6834", "s3": "#1baf7a",
    "crit": "#d03b3b", "warn": "#b06a00", "navy": "#1F3864",
}
GRUPPE_FARVE = {"ejerskab": "s1", "stoerrelse": "s2", "oevrigt": "s3"}
GRUPPE_NAVN = {"ejerskab": "Ejerskab", "stoerrelse": "Størrelse", "oevrigt": "Øvrigt"}

TEMPLATE = r"""<!doctype html>
<html lang="da"><head><meta charset="utf-8"><title>__TITEL__</title>
<style>
:root{ __VARS__ --rowh:__ROWH__mm; --fs:__FS__; }
@page{ size:A4 portrait; margin:0; }
*{ box-sizing:border-box; margin:0; padding:0; }
html,body{ background:#fff; }
body{ font-family:"Liberation Sans", Arial, Helvetica, sans-serif; color:var(--ink);
      -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.page{ width:210mm; height:297mm; padding:8mm 10mm 6mm; display:flex; flex-direction:column; gap:2.7mm; }
header{ border-bottom:2px solid var(--navy); padding-bottom:2.2mm; }
.hrow{ display:flex; justify-content:space-between; align-items:flex-end; gap:6mm; }
h1{ font-size:calc(16.5pt*var(--fs)); line-height:1.1; letter-spacing:-.3pt; color:var(--navy); font-weight:700; }
.sub{ font-size:calc(8pt*var(--fs)); color:var(--ink2); margin-top:1.2mm; line-height:1.32; max-width:126mm; }
.stamp{ text-align:right; font-size:calc(7pt*var(--fs)); color:var(--muted); line-height:1.5; white-space:nowrap; }
.stamp b{ color:var(--ink2); font-weight:700; }
.chips{ display:flex; gap:1.5mm; margin-top:2mm; flex-wrap:wrap; }
.chip{ font-size:calc(6.9pt*var(--fs)); color:var(--ink2); background:var(--plane);
       border:0.4pt solid rgba(11,11,11,.10); border-radius:2mm; padding:.9mm 2mm; white-space:nowrap; }
.kpis{ display:grid; grid-template-columns:repeat(__NKPI__,1fr); gap:2.6mm; }
.kpi{ background:var(--plane); border:0.4pt solid rgba(11,11,11,.10); border-radius:1.6mm;
      padding:2mm 2.6mm; border-left:1.2mm solid var(--s1); }
.kpi.k2{ border-left-color:var(--s2); } .kpi.k3{ border-left-color:var(--s3); } .kpi.k4{ border-left-color:var(--crit); }
.kpi .n{ font-size:calc(17pt*var(--fs)); font-weight:700; line-height:1; letter-spacing:-.6pt; }
.kpi .l{ font-size:calc(6.7pt*var(--fs)); color:var(--ink2); margin-top:.9mm; line-height:1.3; }
.callout{ background:#eef3fa; border:0.4pt solid #cddcf1; border-left:1.2mm solid var(--navy);
          border-radius:1.6mm; padding:2.2mm 3mm; }
.callout h2{ font-size:calc(8.6pt*var(--fs)); color:var(--navy); margin-bottom:1.1mm;
             letter-spacing:.2pt; text-transform:uppercase; }
.callout p{ font-size:calc(8pt*var(--fs)); line-height:1.38; }
.panel{ border:0.4pt solid rgba(11,11,11,.10); border-radius:1.6mm; background:var(--surface); padding:2.3mm 3mm 1.9mm; }
.ptitle{ font-size:calc(9pt*var(--fs)); font-weight:700; color:var(--navy); }
.psub{ font-size:calc(6.9pt*var(--fs)); color:var(--muted); margin-top:.6mm; line-height:1.35; max-width:150mm; }
.legend{ display:flex; gap:5mm; font-size:calc(6.8pt*var(--fs)); color:var(--ink2); align-items:center;
         white-space:nowrap; margin-top:1.4mm; padding-top:1.2mm; border-top:0.4pt solid var(--grid); flex-wrap:wrap; }
.legend i{ display:inline-block; vertical-align:middle; margin-right:1mm; }
.sw-bar{ width:5mm; height:2mm; border-radius:1mm; background:var(--s1); }
.sw-out{ width:5mm; height:2mm; border-radius:1mm; background:var(--s1l); box-shadow:inset 0 0 0 .3mm var(--s1); }
.sw-dia{ width:2.4mm; height:2.4mm; background:var(--s2); transform:rotate(45deg); border-radius:.4mm; }
.sw-band{ width:5mm; height:2.6mm; background:var(--band); border:0.4pt solid var(--axis); }
.rc{ margin-top:1.5mm; }
.rcrow{ display:grid; grid-template-columns:41mm 1fr 21mm; align-items:center; column-gap:2mm;
        height:var(--rowh); overflow:hidden; }
.rcname{ font-size:calc(7.5pt*var(--fs)); line-height:1.15; text-align:right; }
.rcname .seg{ display:__SEGVIS__; font-size:calc(6.1pt*var(--fs)); color:var(--muted); margin-top:.25mm;
              white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.rcname .seg-inline{ display:__SEGINL__; color:var(--muted); font-size:calc(6.1pt*var(--fs)); }
.plot{ position:relative; height:var(--rowh); }
.plot .bandzone{ position:absolute; top:0; bottom:0; background:var(--band); }
.plot .gl{ position:absolute; top:0; bottom:0; width:0.4pt; background:var(--grid); }
.plot .gl.edge{ background:var(--axis); }
.bar{ position:absolute; top:50%; transform:translateY(-50%); height:2.6mm; border-radius:1.3mm; background:var(--s1); }
.bar.out{ background:var(--s1l); box-shadow:inset 0 0 0 .35mm var(--s1); }
.dia{ position:absolute; top:50%; width:2.6mm; height:2.6mm; background:var(--s2);
      transform:translate(-50%,-50%) rotate(45deg); border-radius:.4mm; box-shadow:0 0 0 .45mm var(--surface); }
.vlab{ position:absolute; top:50%; transform:translateY(-50%); font-size:calc(6.4pt*var(--fs));
       color:var(--ink2); white-space:nowrap; }
.rcflag{ font-size:calc(6.3pt*var(--fs)); line-height:1.15; white-space:nowrap; }
.rcflag.inde{ color:var(--muted); } .rcflag.over{ color:var(--crit); font-weight:700; }
.rcflag.under{ color:var(--warn); font-weight:700; }
.axis{ display:grid; grid-template-columns:41mm 1fr 21mm; column-gap:2mm; margin-top:.6mm; }
.ticks{ position:relative; height:4mm; }
.ticks span{ position:absolute; top:.6mm; font-size:calc(6.2pt*var(--fs)); color:var(--muted); transform:translateX(-50%); }
.axcap{ font-size:calc(6.3pt*var(--fs)); color:var(--muted); text-align:right; padding-top:.7mm; }
.cols{ display:grid; grid-template-columns:1fr 1fr; gap:3mm; }
.hb{ display:grid; grid-template-columns:43mm 1fr auto; align-items:center; column-gap:1.8mm; height:calc(var(--rowh)*.78); }
.hb .lbl{ font-size:calc(6.8pt*var(--fs)); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.hb .track{ position:relative; height:2.4mm; }
.hb .fill{ position:absolute; left:0; top:0; height:2.4mm; border-radius:1.2mm; }
.hb .val{ font-size:calc(7pt*var(--fs)); font-weight:700; min-width:4.5mm; text-align:right; }
.zero{ font-size:calc(6.4pt*var(--fs)); color:var(--crit); font-weight:700; }
.zerodot{ display:inline-block; width:1.8mm; height:1.8mm; border-radius:50%; background:var(--crit);
          margin-right:.8mm; vertical-align:-.15mm; }
.note{ font-size:calc(6.4pt*var(--fs)); color:var(--ink2); line-height:1.34; margin-top:1.5mm;
       padding-top:1.3mm; border-top:0.4pt solid var(--grid); }
.gkey{ display:inline-block; width:2.4mm; height:2.4mm; border-radius:.5mm; vertical-align:-.2mm; margin:0 1mm 0 1mm; }
.foot{ display:grid; grid-template-columns:repeat(__NFOOT__,1fr); gap:3mm; margin-top:auto; }
.fcard{ border:0.4pt solid rgba(11,11,11,.10); border-radius:1.6mm; padding:1.9mm 2.4mm; background:var(--plane); }
.fcard h3{ font-size:calc(7.2pt*var(--fs)); color:var(--navy); margin-bottom:1mm;
           text-transform:uppercase; letter-spacing:.2pt; }
.fcard p{ font-size:calc(6.4pt*var(--fs)); line-height:1.38; color:var(--ink2); }
.src{ font-size:calc(6pt*var(--fs)); color:var(--muted); text-align:center; padding-top:1.6mm;
      border-top:0.4pt solid var(--grid); line-height:1.45; }
</style></head><body><div class="page">
<header>
  <div class="hrow">
    <div><h1>__TITEL__</h1><div class="sub">__UNDERTITEL__</div></div>
    <div class="stamp">__STAMP__</div>
  </div>
  <div class="chips">__CHIPS__</div>
</header>
<div class="kpis">__KPIS__</div>
<div class="callout"><h2>Hovedkonklusion</h2><p>__KONKLUSION__</p></div>
<div class="panel">
  <div><div class="ptitle">__GRAFTITEL__</div><div class="psub">__GRAFSUB__</div></div>
  <div class="legend">
    <span><i class="sw-bar"></i>Skønnet omsætningsinterval</span>
    <span><i class="sw-out"></i>Interval helt eller delvis uden for kriteriet</span>
    <span><i class="sw-dia"></i>Omsætning oplyst i årsrapporten</span>
    <span><i class="sw-band"></i>Kriteriet __KRITERIE__ mio. DKK</span>
  </div>
  <div class="rc">__RC__</div>
  <div class="axis"><div></div><div class="ticks">__TICKS__</div><div class="axcap">mio. DKK</div></div>
</div>
<div class="cols">
  <div class="panel"><div class="ptitle">Dækning pr. segment</div>
    <div class="psub">Antal kandidater. Alle segmenter blev søgt lige grundigt.</div>
    <div style="margin-top:1.7mm">__SEG__</div>__SEGNOTE__</div>
  <div class="panel"><div class="ptitle">Hvorfor __NFRAV__ faldt fra</div>
    <div class="psub">Den årsag, der afgjorde sagen. Farve angiver hovedgruppe.</div>
    <div style="margin-top:1.7mm">__REJ__</div><div class="note">__REJKEY__</div></div>
</div>
<div class="foot">__FOOT__</div>
<div class="src">__SRC__</div>
</div></body></html>
"""


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if s is not None else "")


def html(d, rowh, fs):
    m = d["meta"]
    lo, hi = m["oms_min"], m["oms_max"]
    smax = m.get("skala_max") or int(hi * 1.6)
    pct = lambda v: v / smax * 100

    # --- kandidatrækker ---
    rows = []
    for k in d["kandidater"]:
        sk = k.get("skoen") or {}
        status = sk.get("status", "inde")
        flag = sk.get("flag", "oplyst" if k.get("omsaetning") is not None else "inden for")
        marks = [f'<div class="bandzone" style="left:{pct(lo)}%;width:{pct(hi)-pct(lo)}%"></div>']
        step = smax / 8
        for i in range(1, 8):
            t = step * i
            if abs(t - lo) > step / 4 and abs(t - hi) > step / 4:
                marks.append(f'<div class="gl" style="left:{pct(t)}%"></div>')
        marks += [f'<div class="gl edge" style="left:{pct(lo)}%"></div>',
                  f'<div class="gl edge" style="left:{pct(hi)}%"></div>']
        if k.get("omsaetning") is not None:
            v = k["omsaetning"]
            marks.append(f'<div class="dia" style="left:{pct(v)}%"></div>')
            marks.append(f'<div class="vlab" style="left:calc({pct(v)}% + 2.2mm)">{v:.0f}</div>')
        else:
            a, b = sk["lav"], sk["hoej"]
            cls = "bar" if status == "inde" else "bar out"
            marks.append(f'<div class="{cls}" style="left:{pct(a)}%;width:{pct(b)-pct(a)}%"></div>')
            if pct(b) > 84:
                marks.append(f'<div class="vlab" style="left:calc({pct(a)}% - 1.6mm);'
                             f'transform:translate(-100%,-50%)">{a:g}–{b:g}</div>')
            else:
                marks.append(f'<div class="vlab" style="left:calc({pct(b)}% + 1.6mm)">{a:g}–{b:g}</div>')
        seg = esc(k.get("segment_kort") or k["segment"])
        rows.append(f'<div class="rcrow"><div class="rcname">{esc(k["navn"])}'
                    f'<span class="seg">{seg}</span></div>'
                    f'<div class="plot">{"".join(marks)}</div>'
                    f'<div class="rcflag {status}">{esc(flag)}</div></div>')

    ticks = "".join(f'<span style="left:{pct(smax/8*i)}%">{smax/8*i:g}</span>' for i in range(9))

    # --- segmenter ---
    seg = d.get("segmentdaekning", [])
    segmax = max([s["antal"] for s in seg] + [1])
    segrows = []
    for s in seg:
        if s["antal"] > 0:
            track = (f'<div class="fill" style="width:{s["antal"]/segmax*100}%;'
                     f'background:var(--s1)"></div>')
        else:
            track = '<span class="zero"><span class="zerodot"></span>ingen kandidater fundet</span>'
        segrows.append(f'<div class="hb"><div class="lbl">{esc(s["navn"])}</div>'
                       f'<div class="track">{track}</div><div class="val">{s["antal"]}</div></div>')
    nul = [s["navn"] for s in seg if s["antal"] == 0]
    segnote = ""
    if m.get("segmentnote"):
        segnote = f'<div class="note">{m["segmentnote"]}</div>'
    elif nul:
        segnote = (f'<div class="note"><b>Nul kandidater i {" og ".join(esc(n) for n in nul)}.</b> '
                   f'Det er et resultat, ikke et hul i researchen — se metodefanen for, hvad der '
                   f'blev fundet i stedet.</div>')

    # --- fravalgsårsager ---
    oev = sorted(d.get("oevrige_fravalgte", []), key=lambda o: -o["antal"])
    rmax = max([o["antal"] for o in oev] + [1])
    rej = "".join(
        f'<div class="hb"><div class="lbl">{esc(o.get("aarsag_kort") or o["aarsag"])}</div>'
        f'<div class="track"><div class="fill" style="width:{o["antal"]/rmax*100}%;'
        f'background:var(--{GRUPPE_FARVE[o["gruppe"]]})"></div></div>'
        f'<div class="val">{o["antal"]}</div></div>' for o in oev)
    grp = {}
    for o in oev:
        grp[o["gruppe"]] = grp.get(o["gruppe"], 0) + o["antal"]
    rejkey = " ".join(
        f'<i class="gkey" style="background:var(--{GRUPPE_FARVE[g]})"></i><b>{GRUPPE_NAVN[g]} {n}</b>'
        for g, n in sorted(grp.items(), key=lambda x: -x[1]))
    nfrav = sum(o["antal"] for o in oev)

    # --- KPI'er ---
    kpis = m.get("kpis")
    if not kpis:
        uden = sum(1 for k in d["kandidater"] if k.get("omsaetning") is None)
        kpis = [
            {"n": m.get("antal_vurderet", len(d["kandidater"]) + nfrav),
             "l": f"selskaber vurderet på tværs af {len(seg)} segmenter"},
            {"n": len(d["kandidater"]), "l": "kandidater tilbage efter screening"},
            {"n": len(d["kandidater"]) - uden,
             "l": "oplyser faktisk omsætning — resten er regnskabsklasse B"},
            {"n": grp.get("ejerskab", 0), "l": "fravalgt alene på grund af ejerforhold"},
        ]
    kpihtml = "".join(
        f'<div class="kpi{" k"+str(i+1) if i else ""}"><div class="n">{esc(k["n"])}</div>'
        f'<div class="l">{esc(k["l"])}</div></div>' for i, k in enumerate(kpis))

    foot = "".join(f'<div class="fcard"><h3>{esc(c["titel"])}</h3><p>{c["tekst"]}</p></div>'
                   for c in d.get("footer_kort", []))

    out = TEMPLATE
    rep = {
        "__VARS__": " ".join(f"--{k}:{v};" for k, v in P.items()),
        "__ROWH__": f"{rowh:.2f}", "__FS__": f"{fs:.3f}",
        "__SEGVIS__": "block" if rowh >= 4.45 else "none",
        "__SEGINL__": "none" if rowh >= 4.45 else "inline",
        "__TITEL__": esc(m["titel"]), "__UNDERTITEL__": esc(m.get("undertitel", "")),
        "__STAMP__": f'<b>{esc(m["dato"])}</b><br>{esc(m.get("periode_note",""))}<br>Beløb i mio. DKK',
        "__CHIPS__": "".join(f'<span class="chip">{esc(c)}</span>' for c in m.get("kriterier", [])),
        "__NKPI__": str(len(kpis)), "__KPIS__": kpihtml,
        "__KONKLUSION__": m.get("hovedkonklusion", ""),
        "__GRAFTITEL__": f'De {len(d["kandidater"])} kandidater — omsætning mod kriteriet',
        "__GRAFSUB__": (f'Sorteret efter samlet fit. '
                        f'{sum(1 for k in d["kandidater"] if k.get("omsaetning") is None)} af '
                        f'{len(d["kandidater"])} oplyser ikke omsætning; deres interval er skønnet '
                        f'ud fra bruttomargin og omsætning pr. ansat.'),
        "__KRITERIE__": f"{lo:g}–{hi:g}",
        "__RC__": "".join(rows), "__TICKS__": ticks,
        "__SEG__": "".join(segrows), "__SEGNOTE__": segnote,
        "__NFRAV__": str(nfrav), "__REJ__": rej, "__REJKEY__": rejkey,
        "__NFOOT__": str(max(len(d.get("footer_kort", [])), 1)), "__FOOT__": foot,
        "__SRC__": m.get("kilder_linje", ""),
    }
    for k, v in rep.items():
        out = out.replace(k, v)
    return out


async def render(d, pdf_ud, html_ud):
    from playwright.async_api import async_playwright
    tmp = html_ud or "/tmp/_onepager.html"
    forsog = [(5.45, 1.0), (5.10, 1.0), (4.80, .98), (4.50, .96), (4.20, .94), (3.95, .92)]
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        for rowh, fs in forsog:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(html(d, rowh, fs))
            await pg.goto("file://" + os.path.abspath(tmp), wait_until="networkidle")
            mm = await pg.evaluate("()=>{const e=document.querySelector('.page');"
                                   "return {s:e.scrollHeight,c:e.clientHeight};}")
            if mm["s"] <= mm["c"]:
                bad = await pg.evaluate("""()=>{const o=[];const pg=document.querySelector('.page')
                  .getBoundingClientRect();document.querySelectorAll('.page *').forEach(e=>{
                  const r=e.getBoundingClientRect(); if(r.width===0&&r.height===0)return;
                  if(r.right>pg.right+0.6||r.left<pg.left-0.6||r.bottom>pg.bottom+0.6)
                    o.push((e.className||e.tagName)+': '+(e.textContent||'').slice(0,40));});return o;}""")
                await pg.pdf(path=pdf_ud, format="A4", print_background=True,
                             margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
                await b.close()
                return rowh, fs, bad
        overskud = mm["s"] - mm["c"]
        await b.close()
        raise SystemExit(
            f"FEJL: indholdet kan ikke presses ned på én A4-side — der er {overskud} px "
            f"({overskud/3.78:.0f} mm) for meget selv ved højeste tæthed.\n"
            f"Skær i teksten: færre kandidater, kortere hovedkonklusion, eller kortere "
            f"footer-kort. One pageren skal kunne læses, ikke bare passe.")


def main():
    if len(sys.argv) < 3:
        print("brug: build_onepager.py <data.json> <ud.pdf> [--html ud.html]"); sys.exit(2)
    html_ud = None
    if "--html" in sys.argv:
        html_ud = sys.argv[sys.argv.index("--html") + 1]
    with open(sys.argv[1], encoding="utf-8") as f:
        d = json.load(f)
    rowh, fs, bad = asyncio.run(render(d, sys.argv[2], html_ud))
    print(f"skrevet: {sys.argv[2]}  (rækkehøjde {rowh} mm, skriftskala {fs})")
    if rowh < 4.45:
        print("bemærk: listen er så lang, at segmentteksten er lagt ind på samme linje som "
              "selskabsnavnet for at få plads. Overvej at korte kandidatlisten ned eller "
              "forkorte 'segment_kort' — one pageren skal kunne læses i hånden.")
    if bad:
        print("ADVARSEL: noget rager ud over siden —")
        for x in bad[:10]:
            print("   ", x)
    else:
        print("ingen elementer rager ud over siden")
    print("Kig på PDF'en som billede, før du sender den. Validatoren tjekker tal, "
          "ikke om en etiket kolliderer med en søjle.")


if __name__ == "__main__":
    main()
