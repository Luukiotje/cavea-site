"""
ONE-TIME FIX SCRIPT
Fixes blog.html by:
1. Removing the badly-inserted <article class="blog-card"> card
2. Moving the <!-- BLOG_POSTS_START --> marker to inside <div class="bl-grid-lg">
3. Re-inserting the first automation post as a correct bl-lg card
Run this ONCE: python scripts/fix_blog_index.py
"""

import json, os, base64, requests, datetime

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

with open(CONFIG_PATH) as f:
    config = json.load(f)

HEADERS  = {"Authorization": f"token {config['github_token']}", "Accept": "application/vnd.github.v3+json"}
API_BASE = f"https://api.github.com/repos/{config['github_repo']}"

# Download current blog.html
resp = requests.get(f"{API_BASE}/contents/blog.html", headers=HEADERS)
data = resp.json()
sha  = data["sha"]
html = base64.b64decode(data["content"]).decode("utf-8")

# ── Step 1: Remove the badly-inserted <article class="blog-card">...</article> block
import re
html = re.sub(
    r'\s*<!-- Blog post:.*?-->\s*<article class="blog-card">.*?</article>',
    '',
    html,
    flags=re.DOTALL
)

# ── Step 2: Remove the old <!-- BLOG_POSTS_START --> marker (wherever it is now)
html = html.replace("<!-- BLOG_POSTS_START -->", "")

# ── Step 3: Insert the marker as first item inside <div class="bl-grid-lg">
# AND insert the first automation post as a correct bl-lg card
months = ["januari","februari","maart","april","mei","juni",
          "juli","augustus","september","oktober","november","december"]
today  = datetime.date.today()
date_nl = f"{today.day} {months[today.month-1]} {today.year}"

new_card = f"""<!-- BLOG_POSTS_START -->
    <!-- Blog post: startersgids-investeren-in-wijn | Added: {today.isoformat()} -->
    <div class="bl-lg rv rv-d1">
      <div class="bl-lg-img-wrap">
        <img class="bl-lg-img" src="https://images.pexels.com/photos/7347206/pexels-photo-7347206.jpeg?auto=compress&cs=tinysrgb&w=700&h=400&fit=crop" alt="De Ultieme Startersgids voor Investeren in Wijn" loading="lazy">
      </div>
      <div class="bl-lg-body">
        <span class="bl-tag">Investering</span>
        <div class="bl-meta"><span>{date_nl}</span><span>8 min leestijd</span></div>
        <h2>De Ultieme Startersgids voor Investeren in Wijn</h2>
        <p>Ontdek hoe investeren in wijn werkt. Leer de basis van wijninvestering en start slim met deze complete startersgids van Cavea.</p>
        <a href="blog/startersgids-investeren-in-wijn.html" class="bl-read">Lees het artikel →</a>
      </div>
    </div>"""

# Insert right after the opening of bl-grid-lg
html = html.replace(
    '<div class="bl-grid-lg">',
    '<div class="bl-grid-lg">\n' + new_card
)

# ── Step 4: Push the fixed file back to GitHub
encoded = base64.b64encode(html.encode("utf-8")).decode("utf-8")
payload = {
    "message": "Fix blog index: correct card format en marker positie",
    "content": encoded,
    "sha":     sha,
    "branch":  "main"
}
result = requests.put(f"{API_BASE}/contents/blog.html", headers=HEADERS, json=payload)
if result.status_code in (200, 201):
    print("blog.html succesvol gerepareerd en gepusht naar GitHub!")
    print(f"Bekijk de live site op: {config['site_url']}/blog.html")
else:
    print(f"Fout ({result.status_code}): {result.json().get('message')}")
