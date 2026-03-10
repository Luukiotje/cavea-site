# 🍷 Cavea Blog Automation

Automatisch SEO-blogposts schrijven en publiceren naar GitHub — zonder handmatig werk.

---

## Wat doet dit systeem?

Elke dag om 9:00 uur 's ochtends:
1. Pakt de volgende ongepubliceerde topic uit jouw lijst
2. Laat Claude AI een volledig Nederlandstalig SEO-artikel schrijven (~1000 woorden)
3. Zoekt een professionele wijnfoto op (via Pexels)
4. Verpakt alles in een nette HTML-pagina met meta tags, schema markup, etc.
5. Zet de pagina automatisch op je GitHub website
6. Voegt een preview-kaart toe aan je blog.html

Je doet zelf: **niets**. Het systeem doet het allemaal.

---

## Stap-voor-stap Setup (eenmalig, ~30 minuten)

### Stap 1 — API-sleutels aanmaken

Je hebt 3 sleutels nodig:

**A) Anthropic API-sleutel (voor Claude AI)**
1. Ga naar: https://console.anthropic.com
2. Maak een account (je hebt $5 gratis krediet om te beginnen)
3. Ga naar "API Keys" → "Create Key"
4. Kopieer de sleutel (begint met `sk-ant-...`)

**B) Pexels API-sleutel (voor foto's — 100% gratis)**
1. Ga naar: https://www.pexels.com/api/
2. Maak een gratis account
3. Ga naar je dashboard → kopieer je API-sleutel

**C) GitHub Personal Access Token**
1. Ga naar: https://github.com/settings/tokens
2. Klik "Generate new token (classic)"
3. Geef het een naam: "Cavea Blog Bot"
4. Vink aan: **repo** (volledige toegang)
5. Klik "Generate token" → kopieer het direct (je ziet het maar één keer!)

---

### Stap 2 — Voeg je sleutels toe aan GitHub Secrets

Dit zorgt ervoor dat je sleutels veilig zijn en niet in je code komen:

1. Ga naar je GitHub repo: https://github.com/Luukiotje/cavea-site
2. Klik op: **Settings** → **Secrets and variables** → **Actions**
3. Voeg drie secrets toe (klik telkens op "New repository secret"):

| Naam | Waarde |
|------|--------|
| `ANTHROPIC_API_KEY` | jouw Anthropic sleutel |
| `PEXELS_API_KEY` | jouw Pexels sleutel |
| `GH_TOKEN` | jouw GitHub token |

---

### Stap 3 — Kopieer de automatiseringsbestanden naar je repo

Kopieer de volgende mappen/bestanden naar de **root** van je GitHub repo:

```
cavea_automation/
  ├── topics.json                    ← Lijst van alle blogonderwerpen
  ├── config.json                    ← Instellingen (vul in!)
  ├── scripts/
  │   ├── blog_generator.py          ← Schrijft de blogpost met AI
  │   ├── github_publisher.py        ← Zet de post op GitHub
  │   └── run_automation.py          ← Hoofdscript (dit wordt uitgevoerd)
  └── posts/                         ← Lokale kopieën van gegenereerde posts

.github/
  └── workflows/
      └── auto-blog.yml              ← Zegt aan GitHub wanneer het moet draaien
```

---

### Stap 4 — Voeg de marker toe aan je blog.html

Open je `blog.html` en voeg op de plek waar je blogposts wil tonen dit toe:

```html
<!-- BLOG_POSTS_START -->
```

Het automation-systeem voegt automatisch nieuwe kaartjes IN BOVEN dit commentaar.

Voeg ook CSS toe voor de blogkaartjes in je stylesheet (`css/styles.css`):

```css
.blog-card {
  border: 1px solid #e8d5c4;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s;
}
.blog-card:hover { transform: translateY(-3px); }
.blog-card a { text-decoration: none; color: inherit; }
.blog-card img { width: 100%; height: 200px; object-fit: cover; }
.blog-card-content { padding: 1.25rem; }
.blog-card-date { font-size: 0.8rem; color: #999; }
.blog-card h2 { font-size: 1.1rem; margin: 0.5rem 0; color: #1a1a1a; }
.blog-card p { font-size: 0.9rem; color: #555; }
.read-more { color: #8b1a1a; font-weight: bold; }
```

---

### Stap 5 — Test het systeem

Ga naar je GitHub repo → **Actions** → **🍷 Cavea Daily Blog Post** → **Run workflow**

Vink "Dry run" aan voor een test zonder publicatie, of laat leeg voor echte publicatie.

---

## Handmatig een extra post publiceren

Wil je een extra post buiten het dagschema om publiceren?

1. Ga naar GitHub → Actions → "Cavea Daily Blog Post"
2. Klik "Run workflow"
3. Vul bij "topic_id" het nummer in van het onderwerp (zie topics.json)
4. Klik "Run workflow"

Klaar! De post staat binnen 2 minuten live.

---

## Bestanden overzicht

| Bestand | Wat het doet |
|---------|-------------|
| `topics.json` | Lijst van alle 46 blogonderwerpen. Status: pending/published |
| `config.json` | Instellingen zoals site URL en mapnaam |
| `scripts/blog_generator.py` | Roept Claude AI aan om artikel te schrijven |
| `scripts/github_publisher.py` | Zet het artikel op GitHub via de API |
| `scripts/run_automation.py` | Combineert alles en is het hoofdscript |
| `.github/workflows/auto-blog.yml` | Schema: elke dag 9:00 uur |
| `EXPOSURE_PLAN.md` | Volledige marketingstrategie voor meer bereik |

---

## Kosten

| Service | Kosten |
|---------|--------|
| Claude API (per artikel ~1000 woorden) | ~€0,02 per artikel |
| Pexels API | Gratis |
| GitHub Actions | Gratis (2000 minuten/maand inbegrepen) |
| **Totaal per maand (30 posts)** | **~€0,60** |

---

## Vragen of problemen?

Kijk eerst in de GitHub Actions logs voor foutmeldingen.
De meest voorkomende problemen:
- ❌ `401 Unauthorized` → GitHub token is verlopen, maak een nieuwe aan
- ❌ `402 Payment Required` → Anthropic krediet op, top-up op console.anthropic.com
- ❌ `Marker niet gevonden` → Voeg `<!-- BLOG_POSTS_START -->` toe aan blog.html
