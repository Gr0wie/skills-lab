#!/usr/bin/env node
/**
 * Bygger screeningens præsentation som .pptx — seks slides ud af samme data.json,
 * som regnearket bygges af, så de to leverancer ikke kan vise forskellige tal.
 *
 *   node build_deck.js data.json "Screening.pptx" [--pdf "Screening.pdf"]
 *
 * Kræver pptxgenjs:  npm install pptxgenjs
 *
 * Alle grafer er rigtige PowerPoint-diagrammer (addChart), ikke billeder — modtageren
 * skal kunne klikke på en søjle og se tallet bag.
 *
 * Paletten er tre farver plus gråtoner. Blå er "inden for kriteriet", orange er
 * "uden for", grøn er den tredje fravalgsgruppe. Læg ikke en fjerde farve til:
 * fire kategorifarver på ét slide er ikke længere en kode, læseren kan holde i hovedet.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

// Node leder efter moduler ved siden af scriptet, ikke i arbejdsmappen. Skillen ligger
// et helt andet sted end den mappe, screeningen bygges i, så vi leder begge steder —
// ellers skal brugeren installere pptxgenjs inde i skillens egen mappe.
let PptxGenJS;
try {
  PptxGenJS = require('pptxgenjs');
} catch (e1) {
  try {
    PptxGenJS = require(require.resolve('pptxgenjs', {
      paths: [process.cwd(), path.join(process.cwd(), 'node_modules')],
    }));
  } catch (e2) {
    console.error('FEJL: pptxgenjs mangler. Kør:  npm install pptxgenjs');
    process.exit(2);
  }
}

// ---------------------------------------------------------------- palet og mål

const C = {
  blaa: '2A78D6',
  orange: 'EB6834',
  groen: '1BAF7A',
  blaek: '111111',   // overskrifter og tal
  tekst: '3C3B38',   // brødtekst
  daemp: '6E6C66',   // undertekster, akser
  linje: 'E4E3DE',   // gitterlinjer
  flade: 'F4F4F2',   // felter og chips
  hvid: 'FFFFFF',
};
const GRUPPE_FARVE = { ejerskab: C.blaa, stoerrelse: C.orange, oevrigt: C.groen };
const GRUPPE_NAVN = { ejerskab: 'Ejerskab', stoerrelse: 'Størrelse', oevrigt: 'Øvrigt' };

const FONT = 'Arial';
const W = 13.333, H = 7.5;          // LAYOUT_WIDE
const M = 0.6;                       // sidemargen
const CW = W - 2 * M;                // indholdsbredde

// Mindste brødtekst. Kan indholdet ikke være der ved denne størrelse, skal det
// skæres væk og henvises til regnearket — ikke skrumpes ned under grænsen.
const MIN_PT = 12;

// ---------------------------------------------------------------- småting

const tal = (n) => (n === null || n === undefined || n === ''
  ? '—'
  : Number(n).toLocaleString('da-DK', { maximumFractionDigits: 1 }));

/**
 * Klipper ved sidste sætningsslut før grænsen. Er der ingen, klippes ved et ordskel,
 * og småord og tegn i enden fjernes — "… enheder inde i …" er en dårligere afslutning
 * end "… enheder inde …", og begge skal signalere, at resten står i regnearket.
 */
function klip(txt, maks) {
  const s = String(txt || '').trim();
  if (s.length <= maks) return s;
  const del = s.slice(0, maks);
  const p = Math.max(del.lastIndexOf('. '), del.lastIndexOf('? '), del.lastIndexOf('! '));
  if (p > maks * 0.5) return del.slice(0, p + 1);
  let ord = del.slice(0, del.lastIndexOf(' ')).split(' ');
  while (ord.length > 3 && ord[ord.length - 1].replace(/[^\wæøåÆØÅ]/g, '').length <= 2) ord.pop();
  return ord.join(' ').replace(/[\s,;:—–-]+$/, '') + ' …';
}

const enheder = (s) => String(s)
  .replace(/&nbsp;/g, '\u00A0')
  .replace(/&amp;/g, '&')
  .replace(/&lt;/g, '<')
  .replace(/&gt;/g, '>');

/** Oversætter datamodellens <b>/<br> til pptxgenjs-runs. Andet markup findes ikke i data. */
function rich(src, base) {
  const runs = [];
  let fed = false;
  const dele = String(src || '').split(/(<\/?b>|<br\s*\/?>)/gi);
  for (const del of dele) {
    if (!del) continue;
    const t = del.toLowerCase();
    if (t === '<b>') { fed = true; continue; }
    if (t === '</b>') { fed = false; continue; }
    if (/^<br\s*\/?>$/.test(t)) {
      if (runs.length) runs[runs.length - 1].options.breakLine = true;
      else runs.push({ text: '', options: Object.assign({}, base, { breakLine: true }) });
      continue;
    }
    runs.push({ text: enheder(del), options: Object.assign({}, base, { bold: fed || !!base.bold }) });
  }
  return runs.length ? runs : [{ text: '', options: base }];
}

const PAENE = [1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000];

/** Runde akseværdier: mindste pæne skridt, der giver højst 8 mærker og går rent op. */
function skridt(maks) {
  for (const s of PAENE) if (maks / s <= 8 && maks % s === 0) return s;
  for (const s of PAENE) if (maks / s <= 8) return s;
  return Math.ceil(maks / 8);
}

/** Runder aksens top op til et helt antal skridt, så sidste mærke er et rundt tal. */
function akse(maks, luft) {
  const raa = Math.max(1, Math.ceil(maks * (luft || 1)));
  const s = skridt(raa);
  return { maks: Math.ceil(raa / s) * s, skridt: s };
}

// ---------------------------------------------------------------- byggeklodser

function overskrift(s, titel, undertitel) {
  s.addText(titel, {
    x: M, y: 0.42, w: CW, h: 0.5, fontFace: FONT, fontSize: 24, bold: true,
    color: C.blaek, valign: 'top',
  });
  if (undertitel) {
    s.addText(undertitel, {
      x: M, y: 0.98, w: CW, h: 0.5, fontFace: FONT, fontSize: MIN_PT,
      color: C.daemp, valign: 'top', lineSpacingMultiple: 1.2,
    });
  }
}

function sidefod(s, nr, ialt, note) {
  if (note) {
    s.addText(note, {
      x: M, y: H - 0.52, w: CW - 1.3, h: 0.3, fontFace: FONT, fontSize: MIN_PT,
      color: C.daemp, valign: 'middle',
    });
  }
  s.addText(nr + ' / ' + ialt, {
    x: W - M - 1.1, y: H - 0.52, w: 1.1, h: 0.3, fontFace: FONT, fontSize: MIN_PT,
    color: C.daemp, align: 'right', valign: 'middle',
  });
}

/**
 * Signaturforklaring af farveprikker. Kald kun med de poster, der faktisk optræder —
 * og bemærk, at der ombrydes til en ny linje frem for at droppe en post. En manglende
 * forklaring på en farve, der står i grafen, er værre end to linjers signatur.
 */
function signatur(s, poster, x, y, bredde) {
  if (!poster.length) return;
  const sw = 0.2, mellem = 0.34;
  // Bred nok til, at teksten ikke selv ombrydes: ombrudt signaturtekst er det,
  // der først får et slide til at se sjusket ud.
  const tekstbredde = function (t) { return 0.088 * t.length + 0.35; };
  let cx = x, cy = y;
  for (const p of poster) {
    const tb = tekstbredde(p.tekst);
    if (cx + sw + 0.08 + tb > x + bredde && cx > x) { cx = x; cy += 0.34; }
    s.addShape('rect', {
      x: cx, y: cy + 0.055, w: sw, h: sw,
      fill: { color: p.farve }, line: { color: p.farve, width: 0 },
    });
    s.addText(p.tekst, {
      x: cx + sw + 0.08, y: cy, w: tb, h: 0.32, fontFace: FONT, fontSize: MIN_PT,
      color: C.tekst, valign: 'middle',
    });
    cx += sw + 0.08 + tb + mellem;
  }
}

const GRAF_BASIS = {
  chartArea: { fill: { color: C.hvid } },
  plotArea: { fill: { color: C.hvid } },
  showLegend: false,
  showTitle: false,
  catGridLine: { style: 'none' },
  valGridLine: { color: C.linje, size: 1 },
  catAxisLineShow: false,
  valAxisLineShow: false,
  catAxisLabelFontFace: FONT,
  catAxisLabelFontSize: MIN_PT,
  catAxisLabelColor: C.tekst,
  valAxisLabelFontFace: FONT,
  valAxisLabelFontSize: MIN_PT,
  valAxisLabelColor: C.daemp,
  catAxisMajorTickMark: 'none',
  catAxisMinorTickMark: 'none',
  valAxisMajorTickMark: 'none',
  valAxisMinorTickMark: 'none',
  dataLabelFontFace: FONT,
  dataLabelFontSize: MIN_PT,
};

// ---------------------------------------------------------------- slide 1

function slideForside(pres, d, ctx) {
  const m = d.meta;
  const s = pres.addSlide();
  s.background = { color: C.hvid };

  s.addText('SCREENING AF OPKØBSEMNER', {
    x: M, y: 0.5, w: CW, h: 0.3, fontFace: FONT, fontSize: MIN_PT, bold: true,
    color: C.blaa, charSpacing: 1.4,
  });
  s.addText(m.titel, {
    x: M, y: 0.92, w: 9.1, h: 1.35, fontFace: FONT, fontSize: 34, bold: true,
    color: C.blaek, valign: 'top', lineSpacingMultiple: 1.05,
  });
  s.addText([
    { text: m.dato || '', options: { bold: true, color: C.tekst, breakLine: true } },
    { text: m.periode_note || '', options: { color: C.daemp, breakLine: true } },
    { text: 'Beløb i mio. DKK', options: { color: C.daemp } },
  ], {
    x: 10.0, y: 0.94, w: W - M - 10.0, h: 1.1, fontFace: FONT, fontSize: MIN_PT,
    align: 'right', valign: 'top', lineSpacingMultiple: 1.35,
  });

  s.addText(klip(m.undertitel || '', 330), {
    x: M, y: 2.34, w: 10.4, h: 0.95, fontFace: FONT, fontSize: 14,
    color: C.tekst, valign: 'top', lineSpacingMultiple: 1.3,
  });

  // Kriterier som chips. Ny række, når rækken er fuld — chips skal ikke skrumpes.
  const krit = m.kriterier || [];
  const raekker = [[]];
  let cx = M;
  krit.forEach(function (k) {
    const bw = 0.085 * k.length + 0.44;
    if (cx + bw > M + CW && raekker[raekker.length - 1].length) { raekker.push([]); cx = M; }
    raekker[raekker.length - 1].push({ tekst: k, x: cx, w: bw });
    cx += bw + 0.14;
  });
  raekker.forEach(function (r, ri) {
    r.forEach(function (c) {
      const y = 3.44 + ri * 0.5;
      s.addShape('roundRect', {
        x: c.x, y: y, w: c.w, h: 0.38, rectRadius: 0.09,
        fill: { color: C.flade }, line: { color: C.flade, width: 0 },
      });
      s.addText(c.tekst, {
        x: c.x, y: y, w: c.w, h: 0.38, fontFace: FONT, fontSize: MIN_PT,
        color: C.tekst, align: 'center', valign: 'middle',
      });
    });
  });

  // Fire nøgletal.
  const kw = (CW - 3 * 0.28) / 4;
  ctx.kpis.slice(0, 4).forEach(function (kpi, i) {
    const x = M + i * (kw + 0.28), y = 4.92;
    s.addShape('roundRect', {
      x: x, y: y, w: kw, h: 1.6, rectRadius: 0.09,
      fill: { color: C.flade }, line: { color: C.flade, width: 0 },
    });
    s.addText(String(kpi.n), {
      x: x + 0.22, y: y + 0.14, w: kw - 0.44, h: 0.64, fontFace: FONT, fontSize: 36,
      bold: true, color: C.blaek, valign: 'middle',
    });
    s.addText(kpi.l, {
      x: x + 0.22, y: y + 0.8, w: kw - 0.44, h: 0.68, fontFace: FONT, fontSize: MIN_PT,
      color: C.tekst, valign: 'top', lineSpacingMultiple: 1.18,
    });
  });

  sidefod(s, 1, 6, 'Kun offentlige kilder: CVR, offentliggjorte årsrapporter, selskabernes hjemmesider.');
}

// ---------------------------------------------------------------- slide 2

function slideKonklusion(pres, d, ctx) {
  const m = d.meta;
  const s = pres.addSlide();
  s.background = { color: C.hvid };

  s.addText('HOVEDKONKLUSION', {
    x: M, y: 0.5, w: CW, h: 0.3, fontFace: FONT, fontSize: MIN_PT, bold: true,
    color: C.blaa, charSpacing: 1.4,
  });

  const raa = String(m.hovedkonklusion || '');
  const rent = enheder(raa.replace(/<[^>]+>/g, ''));
  const pt = rent.length > 460 ? 22 : rent.length > 300 ? 26 : 30;
  s.addText(rich(raa, { fontFace: FONT, fontSize: pt, color: C.blaek }), {
    x: M, y: 1.15, w: 11.8, h: 3.6, valign: 'top', lineSpacingMultiple: 1.28,
  });

  // Tre tal, der bærer udsagnet. Alle er talt i data — ingen af dem er skrevet i hånden.
  const fakta = [
    { n: String(ctx.antalVurderet), l: 'selskaber gennemgået i ' + ctx.antalSegmenter + ' segmenter' },
    { n: String(ctx.fravalgIalt), l: 'fravalgt undervejs' },
    { n: String(ctx.ejerskabAntal), l: 'af fravalgene skyldtes ejerforhold alene' },
  ];
  const bw = (CW - 2 * 0.28) / 3;
  fakta.forEach(function (f, i) {
    const x = M + i * (bw + 0.28), y = 5.14;
    s.addShape('roundRect', {
      x: x, y: y, w: bw, h: 1.2, rectRadius: 0.09,
      fill: { color: C.flade }, line: { color: C.flade, width: 0 },
    });
    s.addText(f.n, {
      x: x + 0.22, y: y + 0.12, w: bw - 0.44, h: 0.58, fontFace: FONT, fontSize: 30,
      bold: true, color: C.blaek, valign: 'middle',
    });
    s.addText(f.l, {
      x: x + 0.22, y: y + 0.7, w: bw - 0.44, h: 0.5, fontFace: FONT, fontSize: MIN_PT,
      color: C.tekst, valign: 'top', lineSpacingMultiple: 1.18,
    });
  });

  sidefod(s, 2, 6, 'Alle fravalg med begrundelse: regnearkets faner «Fravalgte» og «Metode og forbehold».');
}

// ---------------------------------------------------------------- slide 3

function slideKandidater(pres, d, ctx) {
  const m = d.meta;
  const s = pres.addSlide();
  s.background = { color: C.hvid };

  const vis = d.kandidater.slice(0, 8);
  const flere = d.kandidater.length - vis.length;
  const smax = m.skala_max || Math.ceil(m.oms_max * 1.6);
  const a = akse(smax, 1);
  const tik = Math.max(smax / 50, 1);   // punktmarkør for oplyst omsætning

  overskrift(s,
    'De ' + vis.length + ' stærkeste kandidater',
    'Sorteret efter samlet fit, ikke efter størrelse. Kriteriet er ' + tal(m.oms_min) + '–'
    + tal(m.oms_max) + ' mio. DKK. Skøn er beregnet på både bruttomargin og omsætning pr. ansat.'
    + (flere > 0 ? ' De øvrige ' + flere + ' kandidater står i regnearket.' : ''));

  const kat = [], afs = [], inde = [], ude = [], oplyst = [];
  d.kandidater.slice(0, 8).forEach(function (k) {
    const sk = k.skoen || {};
    if (k.omsaetning !== null && k.omsaetning !== undefined) {
      const v = Number(k.omsaetning);
      kat.push(k.navn + ' · ' + tal(v) + ' oplyst');
      afs.push(Math.max(0, v - tik / 2));
      inde.push(0); ude.push(0); oplyst.push(tik);
    } else {
      const lav = Number(sk.lav), hoej = Number(sk.hoej);
      kat.push(k.navn + ' · ' + tal(lav) + '–' + tal(hoej));
      afs.push(lav);
      const spaend = Math.max(hoej - lav, tik);
      if ((sk.status || 'inde') === 'inde') { inde.push(spaend); ude.push(0); }
      else { inde.push(0); ude.push(spaend); }
      oplyst.push(0);
    }
  });

  // Serie 1 er et usynligt afsæt ('transparent' giver noFill, altså transparency 100),
  // så de synlige serier begynder ved intervallets nedre grænse i stedet for ved nul.
  // Serier uden data udelades helt — ellers står der en forklaring på noget, der
  // ikke er tegnet.
  // pptxgenjs kan ikke vende kategoriaksen (catAxisOrderReverse skrives ikke ud),
  // og en søjlegraf sætter den første kategori nederst. Vi vender derfor rækkerne
  // selv, så den bedste kandidat står øverst — det er den rangordning, læseren læser.
  [kat, afs, inde, ude, oplyst].forEach(function (r) { r.reverse(); });

  const serier = [{ name: 'afsæt', labels: kat, values: afs }];
  const farver = ['transparent'];
  const sign = [];
  if (inde.some(function (v) { return v > 0; })) {
    serier.push({ name: 'Skønnet interval inden for kriteriet', labels: kat, values: inde });
    farver.push(C.blaa);
    sign.push({ farve: C.blaa, tekst: 'Skønnet interval inden for kriteriet' });
  }
  if (ude.some(function (v) { return v > 0; })) {
    serier.push({ name: 'Helt eller delvis uden for kriteriet', labels: kat, values: ude });
    farver.push(C.orange);
    sign.push({ farve: C.orange, tekst: 'Helt eller delvis uden for kriteriet' });
  }
  if (oplyst.some(function (v) { return v > 0; })) {
    serier.push({ name: 'Omsætning oplyst i årsrapporten', labels: kat, values: oplyst });
    farver.push(C.tekst);
    sign.push({ farve: C.tekst, tekst: 'Omsætning oplyst i årsrapporten' });
  }

  s.addChart(pres.ChartType.bar, serier, Object.assign({}, GRAF_BASIS, {
    x: M, y: 1.66, w: CW, h: 4.5,
    barDir: 'bar',
    barGrouping: 'stacked',
    barGapWidthPct: 55,
    chartColors: farver,
    valAxisMinVal: 0,
    valAxisMaxVal: a.maks,
    valAxisMajorUnit: a.skridt,
    valAxisLabelFormatCode: '#,##0',
    showValue: false,
  }));

  s.addText('mio. DKK', {
    x: W - M - 1.6, y: 6.18, w: 1.6, h: 0.28, fontFace: FONT, fontSize: MIN_PT,
    color: C.daemp, align: 'right', valign: 'middle',
  });
  signatur(s, sign, M, 6.52, CW);

  sidefod(s, 3, 6, null);
}

// ---------------------------------------------------------------- slide 4

function slideGrafer(pres, d, ctx) {
  const s = pres.addSlide();
  s.background = { color: C.hvid };

  overskrift(s, 'Hvor kandidaterne kom fra — og hvorfor resten faldt fra',
    'Venstre: antal kandidater pr. segment. Højre: den årsag, der afgjorde sagen, for hvert fravalgt selskab.');

  const kolW = (CW - 0.6) / 2;
  const vx = M, hx = M + kolW + 0.6;
  const gy = 2.04, gh = 3.95;

  // --- segmentdækning ---
  // Rækkerne vendes, fordi en søjlegraf sætter første kategori nederst og pptxgenjs
  // ikke skriver catAxisOrderReverse ud. Sorteret faldende, så det største står øverst.
  const seg = (d.segmentdaekning || []).slice()
    .sort(function (a2, b2) { return a2.antal - b2.antal; });
  s.addText('Kandidater pr. segment', {
    x: vx, y: 1.62, w: kolW, h: 0.34, fontFace: FONT, fontSize: 14, bold: true, color: C.blaek,
  });
  if (seg.length) {
    const sa = akse(Math.max.apply(null, seg.map(function (x) { return x.antal; }).concat([1])), 1.12);
    s.addChart(pres.ChartType.bar, [{
      name: 'Kandidater',
      labels: seg.map(function (x) { return klip(x.navn, 30); }),
      values: seg.map(function (x) { return x.antal; }),
    }], Object.assign({}, GRAF_BASIS, {
      x: vx, y: gy, w: kolW, h: gh,
      barDir: 'bar', barGapWidthPct: 45,
      chartColors: [C.blaa],
      valAxisMinVal: 0, valAxisMaxVal: sa.maks, valAxisMajorUnit: sa.skridt,
      showValue: true, dataLabelPosition: 'outEnd',
      dataLabelColor: C.tekst, dataLabelFontBold: true, dataLabelFormatCode: '0',
    }));
  }
  const nul = seg.filter(function (x) { return !x.antal; }).map(function (x) { return x.navn; });
  s.addText(nul.length
    ? 'Nul kandidater i ' + nul.join(' og ') + '. Det er et resultat, ikke et hul i researchen — se metodefanen.'
    : 'Alle segmenter blev søgt lige grundigt.', {
    x: vx, y: gy + gh + 0.14, w: kolW, h: 0.6, fontFace: FONT, fontSize: MIN_PT,
    color: C.tekst, valign: 'top', lineSpacingMultiple: 1.2,
  });

  // --- fravalgsårsager ---
  // De otte hyppigste, stigende i arrayet så den hyppigste ender øverst i grafen.
  const oev = (d.oevrige_fravalgte || []).slice()
    .sort(function (a2, b2) { return b2.antal - a2.antal; }).slice(0, 8).reverse();
  s.addText('Hvorfor ' + ctx.fravalgIalt + ' faldt fra', {
    x: hx, y: 1.62, w: kolW, h: 0.34, fontFace: FONT, fontSize: 14, bold: true, color: C.blaek,
  });
  if (oev.length) {
    const fa = akse(Math.max.apply(null, oev.map(function (x) { return x.antal; }).concat([1])), 1.12);
    // Én serie med farve pr. søjle. Det er grunden til, at grafen ikke er stablet:
    // kun en ustablet søjle må have tallet stående uden for søjlen (outEnd).
    s.addChart(pres.ChartType.bar, [{
      name: 'Fravalgte',
      labels: oev.map(function (x) { return klip(x.aarsag_kort || x.aarsag, 32); }),
      values: oev.map(function (x) { return x.antal; }),
    }], Object.assign({}, GRAF_BASIS, {
      x: hx, y: gy, w: kolW, h: gh,
      barDir: 'bar', barGapWidthPct: 45,
      chartColors: oev.map(function (x) { return GRUPPE_FARVE[x.gruppe] || C.daemp; }),
      valAxisMinVal: 0, valAxisMaxVal: fa.maks, valAxisMajorUnit: fa.skridt,
      showValue: true, dataLabelPosition: 'outEnd',
      dataLabelColor: C.tekst, dataLabelFontBold: true, dataLabelFormatCode: '0',
    }));
  }
  const grp = {};
  (d.oevrige_fravalgte || []).forEach(function (o) { grp[o.gruppe] = (grp[o.gruppe] || 0) + o.antal; });
  signatur(s, Object.keys(grp)
    .sort(function (a2, b2) { return grp[b2] - grp[a2]; })
    .map(function (g) {
      return { farve: GRUPPE_FARVE[g] || C.daemp, tekst: (GRUPPE_NAVN[g] || g) + ' ' + grp[g] };
    }), hx, gy + gh + 0.14, kolW);

  sidefod(s, 4, 6, null);
}

// ---------------------------------------------------------------- slide 5

function slideProfiler(pres, d, ctx) {
  const s = pres.addSlide();
  s.background = { color: C.hvid };

  overskrift(s, 'Tre at starte med',
    'De tre øverste på fit-rangeringen. Fuld profil, ejerkæde, kilder og forbehold står i regnearkets fane «Kandidater».');

  const tre = d.kandidater.slice(0, 3);
  const kw = (CW - 2 * 0.34) / 3;
  tre.forEach(function (k, i) {
    const x = M + i * (kw + 0.34), y = 1.74, h = 4.5;
    s.addShape('roundRect', {
      x: x, y: y, w: kw, h: h, rectRadius: 0.09,
      fill: { color: C.flade }, line: { color: C.flade, width: 0 },
    });
    const ix = x + 0.28, iw = kw - 0.56;

    s.addText(k.navn, {
      x: ix, y: y + 0.24, w: iw, h: 0.6, fontFace: FONT, fontSize: 18, bold: true,
      color: C.blaek, valign: 'top', lineSpacingMultiple: 1.05,
    });
    s.addText(k.by + ' · ' + (k.segment_kort || k.segment), {
      x: ix, y: y + 0.88, w: iw, h: 0.34, fontFace: FONT, fontSize: MIN_PT, color: C.daemp,
    });

    const sk = k.skoen || {};
    const oms = (k.omsaetning !== null && k.omsaetning !== undefined)
      ? 'Omsætning ' + tal(k.omsaetning) + ' mio. (oplyst)'
      : 'Omsætning skønnet ' + tal(sk.lav) + '–' + tal(sk.hoej) + ' mio.';
    s.addText([
      { text: oms, options: { bold: true, color: C.blaek, breakLine: true } },
      { text: 'Bruttofortjeneste ' + tal(k.bruttofortjeneste) + ' mio. · ' + tal(k.ansatte) + ' ansatte', options: { breakLine: true } },
      { text: 'Egenkapital ' + tal(k.egenkapital) + ' mio. · ' + k.regnskabsaar, options: {} },
    ], {
      x: ix, y: y + 1.28, w: iw, h: 1.05, fontFace: FONT, fontSize: MIN_PT,
      color: C.tekst, valign: 'top', lineSpacingMultiple: 1.25,
    });

    s.addText(klip(k.fit, 300), {
      x: ix, y: y + 2.4, w: iw, h: 1.86, fontFace: FONT, fontSize: MIN_PT,
      color: C.tekst, valign: 'top', lineSpacingMultiple: 1.28,
    });
  });

  sidefod(s, 5, 6, 'Beløb i mio. DKK. Et skøn er markeret som skøn — det er ikke selskabets eget tal.');
}

// ---------------------------------------------------------------- slide 6

function slideMetode(pres, d, ctx) {
  const m = d.meta;
  const s = pres.addSlide();
  s.background = { color: C.hvid };

  overskrift(s, 'Metode, forbehold og kilder',
    'Kort udgave. Den fulde metodebeskrivelse og alle fravalgte selskaber står i regnearket.');

  const met = d.metode || [];
  const trin = met.filter(function (r) { return r[0] === 'h2'; })
    .map(function (r) { return r[1].replace(/^\s*\d+[.)]\s*/, ''); });

  // Forbeholdene ligger i det afsnit, der handler om dem; findes afsnittet ikke,
  // tages de sidste punkter i metodelisten.
  let forbehold = [];
  const start = met.findIndex(function (r) {
    return r[0] === 'h2' && /forbehold|usikker|skeptisk|verific|svaghed/i.test(r[1]);
  });
  if (start >= 0) {
    for (let i = start + 1; i < met.length && met[i][0] !== 'h2' && met[i][0] !== 'h1'; i++) {
      forbehold.push(met[i][1]);
    }
  }
  if (!forbehold.length) {
    forbehold = met.filter(function (r) { return r[0] === 'b'; }).slice(-4)
      .map(function (r) { return r[1]; });
  }

  // Spalten har plads til ca. 15 linjer ved 12 pt. Fire punkter à højst 150 tegn holder
  // sig inden for det. Er der flere forbehold, hører de hjemme i regnearkets metodefane —
  // teksten skrumpes ikke ned for at få dem med.
  const kw = (CW - 0.7) / 2;
  const kolonner = [
    { titel: 'Sådan er den lavet', poster: trin.slice(0, 6), maks: 110, x: M },
    { titel: 'Det skal du vide, før du bruger den', poster: forbehold.slice(0, 4), maks: 170, x: M + kw + 0.7 },
  ];
  kolonner.forEach(function (kol) {
    s.addText(kol.titel, {
      x: kol.x, y: 1.62, w: kw, h: 0.34, fontFace: FONT, fontSize: 14, bold: true, color: C.blaek,
    });
    s.addText(kol.poster.map(function (p, i) {
      return {
        text: klip(enheder(String(p).replace(/<[^>]+>/g, '')), kol.maks),
        options: {
          bullet: { code: '2022' },
          breakLine: i < kol.poster.length - 1,
          paraSpaceAfter: 8,
        },
      };
    }), {
      x: kol.x, y: 2.06, w: kw, h: 3.35, fontFace: FONT, fontSize: MIN_PT,
      color: C.tekst, valign: 'top', lineSpacingMultiple: 1.24,
    });
  });

  const kilder = klip(enheder(String(m.kilder_linje || '').replace(/<[^>]+>/g, '')), 290);
  s.addShape('roundRect', {
    x: M, y: 5.6, w: CW, h: 1.05, rectRadius: 0.09,
    fill: { color: C.flade }, line: { color: C.flade, width: 0 },
  });
  s.addText(kilder + '  Ingen betalingsdatabaser er brugt — alt kan efterprøves af enhver.', {
    x: M + 0.26, y: 5.72, w: CW - 0.52, h: 0.82, fontFace: FONT, fontSize: MIN_PT,
    color: C.tekst, valign: 'top', lineSpacingMultiple: 1.22,
  });

  sidefod(s, 6, 6, null);
}

// ---------------------------------------------------------------- PDF

function findSoffice() {
  if (process.env.SOFFICE && fs.existsSync(process.env.SOFFICE)) return process.env.SOFFICE;
  const bud = [
    'soffice', 'libreoffice',
    'C:\\Program Files\\LibreOffice\\program\\soffice.exe',
    'C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe',
    '/Applications/LibreOffice.app/Contents/MacOS/soffice',
    '/usr/bin/soffice', '/usr/bin/libreoffice', '/usr/lib/libreoffice/program/soffice',
  ];
  for (const b of bud) {
    try {
      if (b.indexOf('/') >= 0 || b.indexOf('\\') >= 0) {
        if (fs.existsSync(b)) return b;
      } else {
        execFileSync(b, ['--version'], { stdio: 'ignore' });
        return b;
      }
    } catch (e) { /* prøv næste */ }
  }
  return null;
}

function tilPdf(pptxSti, pdfSti) {
  const soffice = findSoffice();
  if (!soffice) {
    console.error('ADVARSEL: LibreOffice (soffice) blev ikke fundet — PDF blev ikke lavet.\n'
      + '          Sæt SOFFICE=<sti til soffice>, eller konvertér selv. Præsentationen er skrevet.');
    return false;
  }
  const ud = path.dirname(path.resolve(pdfSti));
  execFileSync(soffice, ['--headless', '--norestore', '--convert-to', 'pdf', '--outdir', ud,
    path.resolve(pptxSti)], { stdio: 'ignore' });
  const lavet = path.join(ud, path.basename(pptxSti).replace(/\.pptx$/i, '.pdf'));
  if (!fs.existsSync(lavet)) {
    console.error('ADVARSEL: soffice skrev ingen PDF. Præsentationen er skrevet.');
    return false;
  }
  if (path.resolve(lavet) !== path.resolve(pdfSti)) {
    fs.copyFileSync(lavet, pdfSti);
    fs.unlinkSync(lavet);
  }
  return true;
}

// ---------------------------------------------------------------- hovedprogram

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('brug: build_deck.js <data.json> <ud.pptx> [--pdf <ud.pdf>]');
    process.exit(2);
  }
  const dataSti = args[0], pptxSti = args[1];
  let pdfSti = null;
  const pi = args.indexOf('--pdf');
  if (pi >= 0) pdfSti = args[pi + 1] || pptxSti.replace(/\.pptx$/i, '.pdf');

  const d = JSON.parse(fs.readFileSync(dataSti, 'utf8'));
  const m = d.meta || {};

  // Alt, der tælles, tælles ét sted — så to slides ikke kan vise hvert sit tal.
  const oev = d.oevrige_fravalgte || [];
  const grp = {};
  oev.forEach(function (o) { grp[o.gruppe] = (grp[o.gruppe] || 0) + o.antal; });
  const ctx = {
    fravalgIalt: oev.reduce(function (a, o) { return a + o.antal; }, 0),
    ejerskabAntal: grp.ejerskab || 0,
    antalSegmenter: (d.segmentdaekning || []).length,
  };
  ctx.antalVurderet = m.antal_vurderet || (d.kandidater.length + ctx.fravalgIalt);
  const udenOms = d.kandidater.filter(function (k) {
    return k.omsaetning === null || k.omsaetning === undefined;
  }).length;
  ctx.kpis = m.kpis || [
    { n: ctx.antalVurderet, l: 'selskaber vurderet i ' + ctx.antalSegmenter + ' segmenter' },
    { n: d.kandidater.length, l: 'kandidater tilbage efter screening' },
    { n: d.kandidater.length - udenOms, l: 'oplyser faktisk omsætning — resten er regnskabsklasse B' },
    { n: ctx.ejerskabAntal, l: 'fravalgt alene på grund af ejerforhold' },
  ];

  const pres = new PptxGenJS();
  pres.layout = 'LAYOUT_WIDE';           // skal sættes før første slide
  pres.author = 'dansk-opkobsscreening';
  pres.title = m.titel || 'Screening';
  pres.subject = enheder(String(m.undertitel || '').replace(/<[^>]+>/g, ''));

  slideForside(pres, d, ctx);
  slideKonklusion(pres, d, ctx);
  slideKandidater(pres, d, ctx);
  slideGrafer(pres, d, ctx);
  slideProfiler(pres, d, ctx);
  slideMetode(pres, d, ctx);

  await pres.writeFile({ fileName: pptxSti });
  console.log('skrevet: ' + pptxSti + '  (6 slides)');

  if (pdfSti && tilPdf(pptxSti, pdfSti)) console.log('skrevet: ' + pdfSti);

  console.log('Se slidesene som billeder, før du sender dem. Validatoren tjekker tal, '
    + 'ikke om en etiket løber ud over kanten.');
}

main().catch(function (e) { console.error(e); process.exit(1); });
