# skills-lab

Et Claude Code **plugin marketplace**. Repoet er både et arbejdsbord til at lære, hvordan
skills distribueres fra git, og den kilde, plugins herfra faktisk installeres og opdateres fra.

Marketplace-navnet er `skills-lab`. Plugins installeres med `@skills-lab`.

## Indhold

| Plugin | Hvad det gør |
|---|---|
| `opkobsscreening` | Screener danske virksomheder som mulige opkøbsemner ud fra CVR, offentliggjorte årsrapporter og offentlige ejerdata. Leverer et regneark med fanerne Kandidater, Fravalgte og Metode og forbehold plus en grafisk A4 one pager i PDF. |

```
skills-lab/
├── .claude-plugin/
│   └── marketplace.json          ← katalogfilen, skal ligge i repo-roden
└── plugins/
    └── opkobsscreening/
        ├── .claude-plugin/
        │   └── plugin.json       ← pluginnets eget manifest, med version
        └── skills/
            └── dansk-opkobsscreening/
                ├── SKILL.md
                ├── references/
                ├── scripts/
                └── evals/
```

Bemærk `plugins/<plugin>/skills/<skill>/` — et plugin kan indeholde flere skills, og hver
skill er sin egen mappe med `SKILL.md` i bunden.

## Sådan installerer man

**Claude Code:**

```bash
/plugin marketplace add Gr0wie/skills-lab
/plugin install opkobsscreening@skills-lab
```

**Cowork og Claude.ai:** Customize i venstre sidebar → fanen **Plugins** → knappen **+** →
**Add marketplace** → **Add from a repository** → `https://github.com/Gr0wie/skills-lab`

**For et helt team** (`.claude/settings.json` i virksomhedens repo):

```json
{
  "extraKnownMarketplaces": {
    "skills-lab": {
      "source": { "source": "github", "repo": "Gr0wie/skills-lab" }
    }
  },
  "enabledPlugins": {
    "opkobsscreening@skills-lab": true
  }
}
```

En organisationsejer på Team eller Enterprise kan i stedet lægge marketplacet ind under
**Organization settings → Plugins**. Så får alle det, og medlemmerne kan ikke redigere i det.
Det kræver, at både Cowork og Skills er slået til for organisationen.

## Sådan opdaterer man

Det, folk glemmer, er versionsbumpet. Uden det ser ingen din ændring.

1. Ret filerne
2. **Bump `version` i `plugins/<plugin>/.claude-plugin/plugin.json`** — og i den tilsvarende
   post i `.claude-plugin/marketplace.json`, så de to ikke kommer i utakt
3. Commit og push
4. Brugerne henter med `/plugin marketplace update`, eller får det via baggrundsopdatering

## Den trinvise gennemgang

Historikken i dette repo er lavet, så man kan se en skill vokse. Tre commits, tre tags:

| Tag | Version | Indhold | Hvad man lærer |
|---|---|---|---|
| `v0.1` | 0.1.0 | Kun `SKILL.md` | En skill uden bundlede filer virker faktisk — den bliver bare langsommere og mindre konsistent. Det er progressive disclosure i praksis. |
| `v0.2` | 0.2.0 | `+ references/` | Metoden bliver ensartet, men dokumenterne bygges stadig i hånden, og tal kan komme i utakt. |
| `v1.0` | 1.0.0 | `+ scripts/ + evals/` | Begge dokumenter bygges nu af den samme datafil, og en validator afviser manglende kilder. Forskellen mellem 0.2 og 1.0 er demoen værd. |

Vil du køre gennemgangen for et publikum, så push ét tag ad gangen. Hver er en
fast-forward af den forrige, så der er ingen force-push involveret:

```bash
git push origin v0.1:main      # installer, prøv skillen, mærk at den er svagere
git push origin v0.2:main      # /plugin marketplace update — se referencerne komme med
git push origin main           # v1.0 — nu bygger scripts dokumenterne
```

Vil du bare i gang, så `git push -u origin main` og spring det over.

## Kom i gang

```bash
git remote add origin git@github.com:Gr0wie/skills-lab.git
git push -u origin main
git push origin --tags
```

Repoet må gerne være privat. Så skal Claude Code bare kunne autentificere mod det —
`gh auth login` sætter en credential helper op til HTTPS. Det er værd at teste, inden
man står foran en kunde.

## Krav til `opkobsscreening`

Scripts i et plugin kører på den maskine, der bruger pluginnet. Dette plugin bruger
Python 3 med `openpyxl` (regnearket) og `playwright` med Chromium (PDF'en), samt
LibreOffice hvis regnearkets formler skal have cachede værdier med det samme. Det er
til stede i Cowork-miljøet, men ikke nødvendigvis i en tilfældig lokal installation.
Uden Playwright kan regnearket stadig bygges — kun PDF-delen falder væk.
