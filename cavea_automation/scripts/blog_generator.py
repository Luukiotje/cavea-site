"""
CAVEA BLOG AUTOMATION — BLOG GENERATOR (v2 — matches dark theme)
Generates SEO-optimized HTML blog posts using Claude AI,
fetches a wine photo, and outputs HTML matching cavea-site's exact style.
"""

import json
import os
import re
import datetime
import requests
import anthropic

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
TOPICS_PATH = os.path.join(BASE_DIR, "topics.json")
POSTS_DIR   = os.path.join(BASE_DIR, "posts")
os.makedirs(POSTS_DIR, exist_ok=True)

with open(CONFIG_PATH) as f:
    config = json.load(f)

ANTHROPIC_API_KEY = config["anthropic_api_key"]
PEXELS_API_KEY    = config["pexels_api_key"]
SITE_URL          = config["site_url"]
BLOG_FOLDER       = config["blog_folder"]


def get_next_topic():
    with open(TOPICS_PATH) as f:
        topics = json.load(f)
    for topic in topics:
        if topic.get("status") == "pending":
            return topic, topics
    return None, topics


def mark_topic_published(topics, topic_id):
    for t in topics:
        if t["id"] == topic_id:
            t["status"] = "published"
            t["published_date"] = datetime.date.today().isoformat()
    with open(TOPICS_PATH, "w") as f:
        json.dump(topics, f, ensure_ascii=False, indent=2)


def fetch_wine_image(query="fine wine cellar bordeaux"):
    if not PEXELS_API_KEY or PEXELS_API_KEY == "YOUR_PEXELS_API_KEY":
        return {
            "url": "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=1400&q=85&auto=format&fit=crop",
            "alt": "Exclusieve wijnflessen in een kelder"
        }
    headers = {"Authorization": PEXELS_API_KEY}
    params  = {"query": query, "per_page": 1, "orientation": "landscape"}
    try:
        resp = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=10)
        data = resp.json()
        if data.get("photos"):
            photo = data["photos"][0]
            return {"url": photo["src"]["large2x"], "alt": photo.get("alt", query)}
    except Exception as e:
        print(f"  Pexels fout: {e} — gebruik standaardafbeelding")
    return {
        "url": "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=1400&q=85&auto=format&fit=crop",
        "alt": "Exclusieve wijnflessen in een kelder"
    }


def generate_blog_content(topic, retries=3):
    """
    Calls Claude API to write the blog post.
    If Anthropic's servers have a temporary hiccup (500 error),
    it automatically tries again up to 3 times before giving up.
    """
    import time
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""Schrijf een volledig SEO-geoptimaliseerd blogartikel in het Nederlands voor Cavea,
een premium wijninvesteringsbedrijf met een donker, luxueus design.

ONDERWERP: {topic['short_tail']}
FOCUSTITEL: {topic['title_1']}
KEYWORD FOCUS: {topic['keyword_focus_1']}

TOON & STIJL:
- Professioneel, luxueus en deskundig — zoals een exclusief wijnmagazijn
- Gebruik "u" (formeel) als aanspreking, niet "je/jij"
- Schrijf voor vermogende investeerders en wijnliefhebbers
- Lengte: 800–1100 woorden

SEO:
- Gebruik het keyword "{topic['short_tail']}" in de eerste 100 woorden
- Gebruik variaties: "wijninvestering", "wijn als belegging", "beleggen in wijn"
- Meta description: max 155 tekens (geef dit apart aan)

STRUCTUUR (gebruik EXACT deze HTML-klassen):
1. Introductie als eerste <p> — pakkend, direct, geen <h2>
2. Minimaal 3 secties met <h2>-koppen
3. Gebruik <h3> voor subsecties
4. Gebruik <ul> of <ol> voor lijsten
5. Gebruik precies 1-2 pull-quotes met klasse "pull-quote":
   <div class="pull-quote"><p>"quote tekst hier"</p></div>
6. Gebruik <strong> voor nadruk
7. GEEN tabellen
8. GEEN <div class="highlight-box"> of andere klassen — alleen bovenstaande

GEEF EXACT DEZE DRIE BLOKKEN TERUG:

[META_DESCRIPTION]
max 155 tekens hier
[/META_DESCRIPTION]

[TAG]
Één woord als categorie (bijv: Investering, Bordeaux, Strategie, Fiscaal, Bourgogne)
[/TAG]

[CONTENT]
Alleen de HTML-inhoud voor binnen <div class="post-body"> — dus alleen <h2>, <h3>, <p>, <ul>, <ol>, <li>, <strong>, <em>, en <div class="pull-quote">
[/CONTENT]
"""

    print(f"  Claude schrijft: '{topic['title_1']}'...")
    for attempt in range(1, retries + 1):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-5-20241022",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            print(f"  Poging {attempt}/{retries} mislukt: {e}")
            if attempt < retries:
                wait = attempt * 15  # wait 15s, then 30s before retry
                print(f"  Wacht {wait} seconden en probeert opnieuw...")
                time.sleep(wait)
            else:
                raise


def parse_claude_response(raw_text):
    def extract(tag, text):
        pattern = rf"\[{tag}\](.*?)\[/{tag}\]"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else ""
    return {
        "meta_description": extract("META_DESCRIPTION", raw_text),
        "tag":              extract("TAG", raw_text) or "Investering",
        "content":          extract("CONTENT", raw_text)
    }


def build_html_page(topic, parsed, image, publish_date):
    """
    Builds a blog post page that exactly matches the style of the
    existing cavea-site posts (dark theme, Playfair Display + Raleway fonts,
    gold accents, same nav/footer structure).
    """
    # Format date in Dutch
    months = ["januari","februari","maart","april","mei","juni",
              "juli","augustus","september","oktober","november","december"]
    d = datetime.date.fromisoformat(publish_date)
    date_nl = f"{d.day} {months[d.month-1]} {d.year}"

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{topic['title_1']} — Cavea</title>
  <meta name="description" content="{parsed['meta_description']}">
  <link rel="canonical" href="{SITE_URL}/{BLOG_FOLDER}/{topic['slug']}.html" />

  <!-- Open Graph -->
  <meta property="og:title" content="{topic['title_1']}">
  <meta property="og:description" content="{parsed['meta_description']}">
  <meta property="og:image" content="{image['url']}">
  <meta property="og:url" content="{SITE_URL}/{BLOG_FOLDER}/{topic['slug']}.html">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Cavea">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{topic['title_1']}">
  <meta name="twitter:description" content="{parsed['meta_description']}">
  <meta name="twitter:image" content="{image['url']}">

  <!-- Schema Markup -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "{topic['title_1']}",
    "description": "{parsed['meta_description']}",
    "image": "{image['url']}",
    "author": {{"@type": "Organization", "name": "Cavea"}},
    "publisher": {{"@type": "Organization", "name": "Cavea"}},
    "datePublished": "{publish_date}",
    "dateModified": "{publish_date}",
    "mainEntityOfPage": {{"@type": "WebPage", "@id": "{SITE_URL}/{BLOG_FOLDER}/{topic['slug']}.html"}}
  }}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Raleway:wght@200;300;400;500;600;700&display=swap" rel="stylesheet">

  <style>
    *,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
    :root{{--bg:#080808;--surface:#0f0f0f;--card:#141414;--border:#252525;--border-lt:#333;--muted:#888;--body:#ccc;--heading:#f0ece4;--white:#faf8f2;--gold:#c4a24e;--gold-br:#dab756;--gold-dm:#9a7e36;--serif:'Playfair Display',Georgia,serif;--sans:'Raleway','Segoe UI',sans-serif}}
    html{{scroll-behavior:smooth}}
    body{{background:var(--bg);color:var(--body);font-family:var(--sans);font-weight:300;font-size:16px;line-height:1.75;overflow-x:hidden;-webkit-font-smoothing:antialiased}}
    nav{{position:fixed;top:0;left:0;right:0;z-index:1000;display:flex;justify-content:space-between;align-items:center;padding:1.5rem 5%;background:rgba(8,8,8,.97);backdrop-filter:blur(24px);box-shadow:0 1px 0 var(--border)}}
    .logo-link{{display:inline-block;text-decoration:none}}.logo-img{{height:44px;width:auto;display:block}}
    .nav-links{{display:flex;gap:2.2rem;align-items:center}}
    .nav-links a{{color:var(--body);text-decoration:none;font-size:.7rem;font-weight:500;letter-spacing:.18em;text-transform:uppercase;transition:color .3s}}
    .nav-links a:hover,.nav-links a.active{{color:var(--gold)}}
    .nav-cta{{background:var(--gold)!important;color:var(--bg)!important;padding:.65rem 1.8rem!important;font-weight:700!important;letter-spacing:.12em!important}}
    .mob-toggle{{display:none;flex-direction:column;gap:5px;background:none;border:none;cursor:pointer;padding:6px}}
    .mob-toggle span{{display:block;width:22px;height:1.5px;background:var(--heading)}}
    .post-hero{{position:relative;height:55vh;min-height:380px;overflow:hidden;margin-top:76px}}
    .post-hero img{{width:100%;height:100%;object-fit:cover;filter:brightness(.65)}}
    .post-hero-overlay{{position:absolute;inset:0;background:linear-gradient(to bottom,transparent 30%,rgba(8,8,8,.9) 100%)}}
    .back-link{{display:block;max-width:780px;margin:2.5rem auto 0;padding:0 5%;color:var(--muted);text-decoration:none;font-size:.75rem;letter-spacing:.15em;text-transform:uppercase;transition:color .3s}}
    .back-link:hover{{color:var(--gold)}}
    .post-header{{max-width:780px;margin:0 auto;padding:2rem 5% 0}}
    .post-tag{{font-size:.6rem;font-weight:700;letter-spacing:.3em;text-transform:uppercase;color:var(--gold);margin-bottom:1rem;display:block}}
    .post-title{{font-family:var(--serif);font-size:clamp(1.8rem,3.5vw,3rem);font-weight:400;color:var(--heading);line-height:1.2;margin-bottom:1.2rem}}
    .post-meta{{font-size:.78rem;color:var(--muted);display:flex;gap:1.5rem;flex-wrap:wrap;padding-bottom:2rem;border-bottom:1px solid var(--border);margin-bottom:2.5rem}}
    .post-body{{max-width:780px;margin:0 auto;padding:0 5% 5rem}}
    .post-body h2{{font-family:var(--serif);font-size:1.6rem;font-weight:400;color:var(--heading);margin:2.8rem 0 1rem;line-height:1.3}}
    .post-body h3{{font-family:var(--serif);font-size:1.2rem;font-weight:500;color:var(--heading);margin:2rem 0 .8rem}}
    .post-body p{{color:var(--body);line-height:1.85;margin-bottom:1.4rem;font-size:.97rem}}
    .post-body ul,.post-body ol{{color:var(--body);padding-left:1.5rem;margin-bottom:1.4rem}}
    .post-body li{{margin-bottom:.6rem;line-height:1.75;font-size:.97rem}}
    .post-body strong{{color:var(--heading);font-weight:600}}
    .pull-quote{{border-left:3px solid var(--gold);padding:1.5rem 2rem;margin:2.5rem 0;background:var(--surface)}}
    .pull-quote p{{font-family:var(--serif);font-style:italic;font-size:1.12rem;color:var(--heading);line-height:1.6;margin:0}}
    .post-cta{{background:var(--surface);border-top:1px solid var(--border);border-bottom:1px solid var(--border);padding:4.5rem 5%;text-align:center}}
    .post-cta h3{{font-family:var(--serif);font-size:1.9rem;color:var(--heading);margin-bottom:.8rem}}
    .post-cta p{{color:var(--muted);margin-bottom:2rem;max-width:500px;margin-left:auto;margin-right:auto;font-size:.95rem}}
    .post-cta a{{display:inline-block;background:var(--gold);color:var(--bg);font-family:var(--sans);font-size:.72rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;padding:1rem 2.8rem;text-decoration:none;transition:all .3s}}
    .post-cta a:hover{{background:var(--gold-br);transform:translateY(-2px)}}
    footer{{background:var(--surface);border-top:1px solid var(--border);padding:4rem 5% 2rem}}
    .ft-in{{display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr;gap:3rem;max-width:1280px;margin:0 auto}}
    .ft-brand p{{font-size:.85rem;color:var(--muted);line-height:1.75;max-width:300px;margin-top:.8rem}}
    .ft-col h4{{font-size:.6rem;font-weight:700;letter-spacing:.25em;text-transform:uppercase;color:var(--heading);margin-bottom:1.3rem}}
    .ft-col a{{display:block;color:var(--muted);text-decoration:none;font-size:.88rem;margin-bottom:.65rem;transition:color .3s}}
    .ft-col a:hover{{color:var(--gold)}}
    .ft-bot{{max-width:1280px;margin:3rem auto 0;padding-top:2rem;border-top:1px solid var(--border);display:flex;justify-content:space-between;font-size:.78rem;color:var(--muted)}}
    @media(max-width:768px){{.nav-links{{display:none}}.mob-toggle{{display:flex}}.ft-in{{grid-template-columns:1fr 1fr}}}}
    @media(max-width:480px){{.ft-in{{grid-template-columns:1fr}}}}
  </style>
</head>
<body>

<nav>
  <a href="../index.html" class="logo-link"><img src="../logo.svg" alt="Cavea" class="logo-img"></a>
  <div class="nav-links">
    <a href="../index.html#pillars">Waarom Cavea</a>
    <a href="../index.html#producers">Wijnhuizen</a>
    <a href="../index.html#how">Hoe het werkt</a>
    <a href="../blog.html" class="active">Blog</a>
    <a href="../index.html#signup" class="nav-cta">Lid worden</a>
  </div>
  <button class="mob-toggle" aria-label="Menu"><span></span><span></span><span></span></button>
</nav>

<div class="post-hero">
  <img src="{image['url']}" alt="{image['alt']}">
  <div class="post-hero-overlay"></div>
</div>

<a href="../blog.html" class="back-link">← Terug naar blog</a>

<div class="post-header">
  <span class="post-tag">{parsed['tag']}</span>
  <h1 class="post-title">{topic['title_1']}</h1>
  <div class="post-meta">
    <span>{date_nl}</span>
    <span>Door Cavea</span>
    <span>8 min leestijd</span>
  </div>
</div>

<div class="post-body">
{parsed['content']}
</div>

<div class="post-cta">
  <h3>Klaar om te beginnen?</h3>
  <p>Vraag toegang aan als founding member en ontvang als eerste onze exclusieve wijn-drops — plus een persoonlijk onboardinggesprek met onze sommelier.</p>
  <a href="../index.html#signup">Vraag toegang aan</a>
</div>

<footer>
  <div class="ft-in">
    <div class="ft-brand">
      <a href="../index.html" class="logo-link"><img src="../logo.svg" alt="Cavea" class="logo-img" style="height:40px"></a>
      <p>Exclusieve toegang tot de zeldzaamste wijnen ter wereld.</p>
    </div>
    <div class="ft-col"><h4>Navigatie</h4><a href="../index.html#pillars">Waarom Cavea</a><a href="../index.html#producers">Wijnhuizen</a><a href="../blog.html">Blog</a><a href="../index.html#signup">Lid worden</a></div>
    <div class="ft-col"><h4>Artikelen</h4><a href="wijninvestering-101.html">Startersgids</a><a href="wijn-als-belegging.html">Fiscale voordelen</a><a href="exclusieve-wijn-kopen.html">Adressen</a><a href="sassicaia-kopen.html">Sassicaia</a></div>
    <div class="ft-col"><h4>Contact</h4><a href="mailto:info@cavea.wine">info@cavea.wine</a><a href="#">Instagram</a></div>
  </div>
  <div class="ft-bot"><span>&copy; 2025 Cavea. Alle rechten voorbehouden.</span><span>Drinken met mate. 18+</span></div>
</footer>

<script>
  window.addEventListener('scroll',()=>document.querySelector('nav').classList.toggle('slim',window.scrollY>60));
</script>
</body>
</html>"""


def generate_one_post():
    topic, all_topics = get_next_topic()
    if not topic:
        print("Alle blogposts zijn al gepubliceerd!")
        return None

    print(f"\nVolgende blogpost: '{topic['title_1']}'")

    image = fetch_wine_image(f"fine wine {topic['short_tail']}")
    raw   = generate_blog_content(topic)
    parsed = parse_claude_response(raw)

    if not parsed["content"]:
        print("Geen inhoud gegenereerd. Probeer opnieuw.")
        return None

    publish_date = datetime.date.today().isoformat()
    html = build_html_page(topic, parsed, image, publish_date)

    output_path = os.path.join(POSTS_DIR, f"{topic['slug']}.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Opgeslagen: {output_path}")

    mark_topic_published(all_topics, topic["id"])
    return {"topic": topic, "file": output_path, "publish_date": publish_date,
            "image_url": image["url"], "meta_description": parsed["meta_description"], "tag": parsed["tag"]}


if __name__ == "__main__":
    result = generate_one_post()
    if result:
        print(f"\nKlaar! Blogpost aangemaakt: {result['file']}")
