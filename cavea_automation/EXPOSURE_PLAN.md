# 📈 Cavea — Exposure & Marketing Groeiplan

## Doel: Van 0 naar organisch verkeer in 90 dagen

---

## FASE 1: SEO-Fundament (Week 1–2)
*Doe dit VOORDAT je begint te posten*

### 1.1 Google Search Console
- Ga naar: https://search.google.com/search-console
- Voeg je website toe en verifieer eigenaarschap
- Stuur je sitemap in (zie stap hieronder)
- **Waarom?** Zo vertelt Google dat je site bestaat. Zonder dit duurt indexering weken langer.

### 1.2 Maak een sitemap.xml
Voeg dit bestand toe aan de root van je GitHub repo:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://cavea.nl/</loc></url>
  <url><loc>https://cavea.nl/blog.html</loc></url>
  <!-- Elke nieuwe blogpost wordt hier automatisch toegevoegd door de automation -->
</urlset>
```

### 1.3 Google Analytics 4
- Maak een gratis account op: https://analytics.google.com
- Voeg de tracking-code toe aan je `<head>` in alle HTML-pagina's
- **Waarom?** Je kunt zien hoeveel bezoekers je krijgt, welke pagina's scoren en waar ze vandaan komen.

### 1.4 Schema Markup uitbreiden
Elk blogpost heeft al schema markup (zit in de automation). Voeg ook dit toe aan je homepage:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Cavea",
  "url": "https://cavea.nl",
  "description": "Premium wijninvestering — wijnportefeuilles, advies en opslag.",
  "sameAs": [
    "https://www.linkedin.com/company/cavea",
    "https://www.instagram.com/cavea.nl"
  ]
}
</script>
```

---

## FASE 2: Content Strategie (Week 3–12)
*De blogposts doen het zware werk*

### 2.1 Publicatieplanning
| Week | Blogpost |
|------|----------|
| Week 1 | Startersgids voor Investeren in Wijn |
| Week 2 | Wijn als Belegging: Fiscale Voordelen |
| Week 3 | Beste Wijnen om in te Investeren 2025 |
| Week 4 | BTW Vrij Wijn Kopen en Opslaan |
| ... | (46 posts totaal, 1–2 per week) |

### 2.2 Interne linking (BELANGRIJK voor SEO)
Elke nieuwe blogpost moet linken naar minstens 2 andere posts op je site.
Dit helpt Google te begrijpen welke pagina's bij elkaar horen.

Voorbeeld: In het artikel over Sassicaia, link je naar "En Primeur Kopen" en "Wijnportefeuille Samenstellen".

### 2.3 Content Clusters
Groepeer je content rondom 5 hoofdthema's:
1. **Beginnen met wijninvestering** → 5 artikelen
2. **Specifieke wijnen & regio's** → 8 artikelen (Bordeaux, Bourgogne, Italië)
3. **Strategie & portefeuille** → 6 artikelen
4. **Opslag & fiscaliteit** → 4 artikelen
5. **Marktanalyse & trends** → 7 artikelen

---

## FASE 3: Social Media Automation (Week 2+)

### 3.1 LinkedIn (Meest waardevol voor wijninvestering)
**Doelgroep:** Professionals 35–60 jaar, geïnteresseerd in alternatieve beleggingen

**Posting strategie:**
- Post élke keer als een nieuw blogartikel live gaat
- Gebruik de eerste 2 zinnen van het artikel als post-tekst
- Voeg een vraag toe om reacties te stimuleren
- Tag: #wijninvestering #beleggen #finewine #wijn

**Template:**
```
🍷 Nieuw op de Cavea blog:

[Eerste 2 zinnen van artikel]

→ Lees het volledige artikel: [LINK]

Wat is jouw ervaring met wijninvestering? 👇

#wijninvestering #wijn #beleggen #finewine #Bordeaux
```

### 3.2 Instagram (Voor visuele merkbekendheid)
**Formaat:** Carousel posts (10 slides) werken het beste

**Idee per blogpost:**
- Slide 1: Pakkende titel + wijnfoto
- Slides 2–8: Kernpunten uit het artikel (1 punt per slide)
- Slide 9: Samenvatting
- Slide 10: CTA + link in bio

**Frequentie:** 3x per week
**Hashtags:** #wijn #wijninvestering #finewine #bordeaux #beleggen #investeringen #nederlandsewijn

### 3.3 Automation met Make (vroeger Integromat) — GRATIS TIER
1. Maak account op: https://make.com
2. Maak een "scenario" dat:
   - Controleert of er een nieuwe HTML-file is in je GitHub repo (via GitHub webhook)
   - Automatisch een LinkedIn-post aanmaakt met de tittel en link
3. **Kosten:** Gratis tot 1000 operaties/maand

---

## FASE 4: Backlinks bouwen (Maand 2+)
*Backlinks = andere websites die naar jou linken = goud voor SEO*

### 4.1 Guest Posts
Benader wijnbloggers en financiële blogs voor gastartikelen:
- Neem contact op met: lavinoteca.shop, colaris.nl, rarewineinvest.nl/blog
- Schrijf een gastpost en vraag een link terug naar je site

### 4.2 HARO (Help A Reporter Out)
- Meld je aan op: https://www.helpareporter.com
- Reageer op journalisten die quotes zoeken over wijninvestering
- Elke vermelding in een artikel = gratis backlink van hoge kwaliteit

### 4.3 Forumparticipatie
Beantwoord vragen over wijninvestering op:
- Reddit: r/investing, r/winemaking
- Nederlandse forums: Tweakers.net (financieel subforum)
- LinkedIn Groups over beleggen

### 4.4 Vermeldingen aanvragen
Zoek op Google naar: `investeren in wijn` + `resources` of `aanbevolen sites`
Neem contact op met die sites en vraag om vermelding.

---

## FASE 5: E-maillijst opbouwen (Maand 1+)

### 5.1 Mailchimp (Gratis tot 500 subscribers)
- Maak account op: https://mailchimp.com
- Maak een aanmeldformulier voor je blog
- Automatische "welcome e-mail" met de beste artikelen

### 5.2 Lead Magnet ideeën
Bied iets gratis aan in ruil voor een e-mailadres:
- "De 5 Beste Wijnen voor €500 — Gratis Investeringsgids (PDF)"
- "Wijnportefeuille Checklist 2025"
- "Exclusieve Marktupdate per Kwartaal"

### 5.3 Nieuwsbrief automation
1x per maand: Stuur een overzicht van de beste artikelen van die maand.
Gebruik Mailchimp's automatische RSS-to-email feature.

---

## FASE 6: Advertenties (Optioneel, Maand 3+)

### 6.1 Google Ads (Zoekadvertenties)
- Keywords: "investeren in wijn", "wijn kopen als belegging", "wijnportefeuille"
- Budget: Start met €10/dag
- Gebruik alleen als je conversiepagina (bijv. contact/afspraak) goed werkt

### 6.2 LinkedIn Ads
- Specifiek targeten op: financiële professionals, 35–60 jaar, Nederland
- Format: Gesponsorde artikelen
- Budget: €500/maand minimum aanbevolen

---

## 📊 KPI Dashboard — Wat moet je meten?

| Metric | Doel (3 maanden) | Tool |
|--------|-----------------|------|
| Organisch verkeer/maand | 500+ bezoekers | Google Analytics |
| Geïndexeerde pagina's | 20+ | Google Search Console |
| Gemiddelde positie (Google) | Top 20 voor 5+ keywords | Search Console |
| LinkedIn bereik/post | 500+ weergaven | LinkedIn Analytics |
| E-mailabonnees | 50+ | Mailchimp |
| Conversies (afspraken) | 5+/maand | Google Analytics Goals |

---

## ⚡ Quick Wins — Doe deze deze week

1. ✅ Voeg je site toe aan Google Search Console
2. ✅ Maak een LinkedIn bedrijfspagina voor Cavea
3. ✅ Voeg schema markup toe aan je homepage
4. ✅ Publiceer je eerste blogpost
5. ✅ Deel de eerste post op LinkedIn met de template hierboven
6. ✅ Installeer Google Analytics op je site

---

*Plan gemaakt door Cavea Automation System — maart 2025*
