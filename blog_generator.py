"""
=============================================================
  CAVEA BLOG AUTOMATION — BLOG GENERATOR
  Generates SEO-optimized HTML blog posts using Claude AI,
  fetches a relevant image, and saves the post ready to publish.
=============================================================

HOW IT WORKS (beginner explanation):
  1. This script reads the list of blog topics from topics.json
  2. It picks the next topic that hasn't been published yet
  3. It calls the Claude AI API to write a full SEO blog post in Dutch
  4. It fetches a beautiful wine photo from Pexels (free)
  5. It wraps everything in a professional HTML file
  6. It saves the HTML file and marks the topic as 'done'

SETUP:
  1. pip install anthropic requests
  2. Set your API keys in config.json (see README)
  3. Run: python scripts/blog_generator.py
"""

import json
import os
import re
import datetime
import requests
import anthropic

# ─── Load config ───────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
TOPICS_PATH = os.path.join(BASE_DIR, "topics.json")
POSTS_DIR   = os.path.join(BASE_DIR, "posts")
os.makedirs(POSTS_DIR, exist_ok=True)

with open(CONFIG_PATH) as f:
    config = json.load(f)

ANTHROPIC_API_KEY = config["anthropic_api_key"]
PEXELS_API_KEY    = config["pexels_api_key"]
SITE_URL          = config["site_url"]          # e.g. "https://cavea.nl"
BLOG_FOLDER       = config["blog_folder"]       # e.g. "blog"
CONTACT_PAGE      = config.get("contact_page", "contact.html")


# ─── Helper: pick the next pending topic ──────────────────
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


# ─── Helper: fetch a wine image from Pexels ──────────────
def fetch_wine_image(query="fine wine cellar bordeaux"):
    """
    Pexels is a free stock photo site. We use their API to get
    a relevant, professional wine photo for each blog post.
    """
    if not PEXELS_API_KEY or PEXELS_API_KEY == "YOUR_PEXELS_API_KEY":
        # Fallback image if no API key is set
        return {
            "url": "https://images.pexels.com/photos/1407846/pexels-photo-1407846.jpeg?auto=compress&cs=tinysrgb&w=1200",
            "alt": "Exclusieve wijnflessen in een kelder"
        }

    headers = {"Authorization": PEXELS_API_KEY}
    params  = {"query": query, "per_page": 1, "orientation": "landscape"}
    try:
        resp = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=10)
        data = resp.json()
        if data.get("photos"):
            photo = data["photos"][0]
            return {
                "url": photo["src"]["large2x"],
                "alt": photo.get("alt", query)
            }
    except Exception as e:
        print(f"  ⚠️  Pexels fout: {e} — gebruik standaardafbeelding")

    return {
        "url": "https://images.pexels.com/photos/1407846/pexels-photo-1407846.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "alt": "Exclusieve wijnflessen in een kelder"
    }


# ─── Helper: generate blog content via Claude API ────────
def generate_blog_content(topic):
    """
    This function sends a prompt to Claude (the AI) and asks it
    to write a full, SEO-optimized Dutch blog post.
    Think of it as hiring a professional writer who works instantly.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""Schrijf een volledig SEO-geoptimaliseerd blogartikel in het Nederlands voor Cavea,
een premium wijninvesteringsbedrijf.

ONDERWERP: {topic['short_tail']}
FOCUSTITEL: {topic['title_1']}
KEYWORD FOCUS: {topic['keyword_focus_1']}
SLUG: {topic['slug']}

VEREISTEN:
- Taal: Nederlands, professioneel maar toegankelijk
- Lengte: 900–1200 woorden
- Toon: Deskundig, betrouwbaar, licht enthousiast over wijn
- Doelgroep: Nederlanders die interesse hebben in wijn als belegging (beginners tot gevorderden)

SEO-VEREISTEN:
- Gebruik het hoofdkeyword "{topic['short_tail']}" in de eerste 100 woorden
- Gebruik variaties zoals "wijninvestering", "wijn als belegging", "beleggen in wijn"
- Schrijf een pakkende meta description van max 155 tekens (geef dit apart aan)
- Gebruik H2- en H3-koppen die keywords bevatten

STRUCTUUR (verplicht):
1. Pakkende inleiding (150–200 woorden) — zet de lezer direct aan het denken
2. Minimaal 3 H2-secties met inhoud
3. Een praktisch voorbeeld of vergelijking (tabel of lijst mag)
4. Een highlight-box met een tip of waarschuwing (begin de sectie met [HIGHLIGHT_BOX] en eindig met [/HIGHLIGHT_BOX])
5. Een call-to-action sectie richting Cavea (begin met [CTA] en eindig met [/CTA])
6. Sterke conclusie

FORMAT VOOR DE OUTPUT:
Geef ALLEEN de volgende drie blokken terug, niets anders:

[META_DESCRIPTION]
Jouw meta description hier (max 155 tekens)
[/META_DESCRIPTION]

[KEYWORDS]
keyword1, keyword2, keyword3, keyword4, keyword5
[/KEYWORDS]

[CONTENT]
De volledige HTML-inhoud van het artikel hier (alleen de inhoud binnen <article>, geen <html>/<head>/<body>)
Gebruik: <h2>, <h3>, <p>, <ul>, <ol>, <table>, <strong>, <em>
Gebruik klasse "highlight-box" voor de tip-box, "cta-box" voor de CTA, "data-table" voor tabellen
[/CONTENT]
"""

    print(f"  ✍️  Claude schrijft artikel: '{topic['title_1']}'...")
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


# ─── Helper: parse Claude's response ─────────────────────
def parse_claude_response(raw_text):
    def extract(tag, text):
        pattern = rf"\[{tag}\](.*?)\[/{tag}\]"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else ""

    return {
        "meta_description": extract("META_DESCRIPTION", raw_text),
        "keywords":         extract("KEYWORDS", raw_text),
        "content":          extract("CONTENT", raw_text)
    }


# ─── Helper: build the full HTML page ────────────────────
def build_html_page(topic, parsed, image, publish_date):
    """
    This function assembles all the pieces into a complete HTML file:
    - SEO meta tags (so Google can understand the page)
    - Open Graph tags (so Facebook/LinkedIn show a nice preview)
    - Schema markup (structured data that Google loves)
    - The article content Claude wrote
    """
    depth = "../"  # Adjust if blog posts are at root level

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <!-- SEO META TAGS -->
  <title>{topic['title_1']} | Cavea</title>
  <meta name="description" content="{parsed['meta_description']}" />
  <meta name="keywords" content="{parsed['keywords']}" />
  <meta name="author" content="Cavea" />
  <link rel="canonical" href="{SITE_URL}/{BLOG_FOLDER}/{topic['slug']}.html" />

  <!-- OPEN GRAPH -->
  <meta property="og:title" content="{topic['title_1']}" />
  <meta property="og:description" content="{parsed['meta_description']}" />
  <meta property="og:image" content="{image['url']}" />
  <meta property="og:url" content="{SITE_URL}/{BLOG_FOLDER}/{topic['slug']}.html" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="Cavea" />

  <!-- TWITTER CARD -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{topic['title_1']}" />
  <meta name="twitter:description" content="{parsed['meta_description']}" />
  <meta name="twitter:image" content="{image['url']}" />

  <!-- SCHEMA MARKUP -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "{topic['title_1']}",
    "description": "{parsed['meta_description']}",
    "image": "{image['url']}",
    "author": {{"@type": "Organization", "name": "Cavea"}},
    "publisher": {{
      "@type": "Organization",
      "name": "Cavea",
      "logo": {{"@type": "ImageObject", "url": "{SITE_URL}/images/logo.png"}}
    }},
    "datePublished": "{publish_date}",
    "dateModified": "{publish_date}",
    "mainEntityOfPage": {{"@type": "WebPage", "@id": "{SITE_URL}/{BLOG_FOLDER}/{topic['slug']}.html"}}
  }}
  </script>

  <link rel="stylesheet" href="{depth}css/styles.css" />
  <style>
    .blog-hero {{width:100%;max-height:480px;object-fit:cover;border-radius:8px;margin-bottom:2rem;}}
    .blog-article {{max-width:780px;margin:0 auto;padding:2rem 1.5rem 4rem;font-family:'Georgia',serif;color:#1a1a1a;line-height:1.8;}}
    .blog-article h1 {{font-size:2.2rem;font-weight:700;margin-bottom:.5rem;color:#1a1a1a;}}
    .blog-meta {{color:#777;font-size:.9rem;margin-bottom:2rem;font-family:sans-serif;}}
    .blog-meta span {{margin-right:1.5rem;}}
    .blog-article h2 {{font-size:1.5rem;font-weight:700;margin:2.5rem 0 1rem;color:#2c1a0e;border-left:4px solid #8b1a1a;padding-left:.75rem;}}
    .blog-article h3 {{font-size:1.2rem;font-weight:700;margin:1.8rem 0 .75rem;color:#3a2a1a;}}
    .blog-article p {{margin-bottom:1.4rem;}}
    .blog-article ul,.blog-article ol {{margin:0 0 1.4rem 1.5rem;}}
    .blog-article li {{margin-bottom:.5rem;}}
    .highlight-box {{background:#fdf6f0;border:1px solid #e8d5c4;border-left:5px solid #8b1a1a;padding:1.25rem 1.5rem;border-radius:6px;margin:2rem 0;}}
    .highlight-box p {{margin:0;font-style:italic;color:#5a3a2a;}}
    .cta-box {{background:#2c1a0e;color:#fff;padding:2rem;border-radius:8px;text-align:center;margin:3rem 0;}}
    .cta-box h3 {{color:#f0d9c0;margin:0 0 .75rem;font-size:1.3rem;}}
    .cta-box p {{color:#d4b896;margin-bottom:1.25rem;}}
    .cta-btn {{display:inline-block;background:#8b1a1a;color:#fff;padding:.75rem 2rem;border-radius:4px;text-decoration:none;font-weight:700;font-family:sans-serif;}}
    .cta-btn:hover {{background:#a52020;}}
    .data-table {{width:100%;border-collapse:collapse;margin:1.5rem 0 2rem;font-size:.95rem;font-family:sans-serif;}}
    .data-table th {{background:#2c1a0e;color:#fff;padding:.75rem 1rem;text-align:left;}}
    .data-table td {{padding:.65rem 1rem;border-bottom:1px solid #e8d5c4;}}
    .data-table tr:nth-child(even) td {{background:#fdf6f0;}}
    .tag-list {{display:flex;flex-wrap:wrap;gap:.5rem;margin:2rem 0 0;font-family:sans-serif;}}
    .tag {{background:#f0ebe5;color:#5a3a2a;padding:.3rem .75rem;border-radius:20px;font-size:.82rem;}}
  </style>
</head>
<body>

  <nav><!-- Jouw bestaande navigatie --></nav>

  <main>
    <article class="blog-article">
      <img class="blog-hero" src="{image['url']}" alt="{image['alt']}" loading="lazy" />
      <h1>{topic['title_1']}</h1>
      <div class="blog-meta">
        <span>📅 {publish_date}</span>
        <span>✍️ Cavea Redactie</span>
        <span>⏱️ 8 minuten lezen</span>
      </div>

      {parsed['content']}

      <div class="tag-list">
        {"".join(f'<span class="tag">{kw.strip()}</span>' for kw in parsed["keywords"].split(",")[:6])}
      </div>
    </article>
  </main>

  <footer><!-- Jouw bestaande footer --></footer>
</body>
</html>"""


# ─── MAIN: generate one blog post ────────────────────────
def generate_one_post():
    topic, all_topics = get_next_topic()
    if not topic:
        print("✅ Alle blogposts zijn al gepubliceerd!")
        return None

    print(f"\n📝 Volgende blogpost: '{topic['title_1']}'")

    # 1. Fetch image
    print("  🖼️  Zoekt wijnfoto op Pexels...")
    image = fetch_wine_image(f"fine wine {topic['short_tail']}")

    # 2. Generate content via Claude
    raw = generate_blog_content(topic)
    parsed = parse_claude_response(raw)

    if not parsed["content"]:
        print("  ❌ Claude gaf geen bruikbare inhoud terug. Probeer opnieuw.")
        return None

    # 3. Build HTML
    publish_date = datetime.date.today().isoformat()
    html = build_html_page(topic, parsed, image, publish_date)

    # 4. Save file
    output_path = os.path.join(POSTS_DIR, f"{topic['slug']}.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  💾 Opgeslagen: {output_path}")

    # 5. Mark as published
    mark_topic_published(all_topics, topic["id"])
    print(f"  ✅ Onderwerp #{topic['id']} gemarkeerd als gepubliceerd.")

    return {"topic": topic, "file": output_path, "publish_date": publish_date}


if __name__ == "__main__":
    result = generate_one_post()
    if result:
        print(f"\n🎉 Klaar! Blogpost aangemaakt: {result['file']}")
