"""
CAVEA BLOG AUTOMATION — GITHUB PUBLISHER (v3)
Pushes blog posts to GitHub and inserts correctly styled cards
into blog.html and index.html.

CHANGES in v3:
- Entire blog card is now clickable (wrapped in <a> tag)
- Fixed blue/purple link text: added color:inherit to <a> wrappers
- Fixed regex that was breaking homepage card detection
- Tag comes from Claude (no longer hardcoded to "Investering")
- Image URL tracked per-topic to avoid duplicate images
"""

import json
import os
import re
import base64
import requests
import datetime

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

with open(CONFIG_PATH) as f:
    config = json.load(f)

GITHUB_TOKEN = config["github_token"]
GITHUB_REPO  = config["github_repo"]
BLOG_FOLDER  = config["blog_folder"]
SITE_URL     = config["site_url"]

HEADERS  = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
API_BASE = f"https://api.github.com/repos/{GITHUB_REPO}"


def get_file_sha(path):
    resp = requests.get(f"{API_BASE}/contents/{path}", headers=HEADERS)
    if resp.status_code == 200:
        return resp.json()["sha"]
    return None


def push_file(path, content_str, commit_message):
    encoded = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
    sha     = get_file_sha(path)
    payload = {"message": commit_message, "content": encoded, "branch": "main"}
    if sha:
        payload["sha"] = sha

    resp = requests.put(f"{API_BASE}/contents/{path}", headers=HEADERS, json=payload)
    if resp.status_code in (200, 201):
        print(f"  GitHub: bestand gepubliceerd → {path}")
        return True
    else:
        print(f"  GitHub fout ({resp.status_code}): {resp.json().get('message')}")
        return False


def get_current_blog_index():
    resp = requests.get(f"{API_BASE}/contents/blog.html", headers=HEADERS)
    if resp.status_code == 200:
        return base64.b64decode(resp.json()["content"]).decode("utf-8")
    return None


def format_date_nl(iso_date):
    months = ["januari","februari","maart","april","mei","juni",
              "juli","augustus","september","oktober","november","december"]
    d = datetime.date.fromisoformat(iso_date)
    return f"{d.day} {months[d.month-1]} {d.year}"


def build_blog_card(topic, image_url, meta_description, publish_date, tag="Investering", delay_class="rv-d1"):
    """
    Builds a card for the blog.html listing page.
    The entire card is now wrapped in an <a> tag so users can click anywhere.
    color:inherit prevents the browser's default blue/purple link color.
    """
    date_nl = format_date_nl(publish_date)
    slug_url = f"{BLOG_FOLDER}/{topic['slug']}.html"
    return f"""
    <!-- Blog post: {topic['slug']} | Added: {publish_date} -->
    <a href="{slug_url}" class="bl-lg-link" style="text-decoration:none;color:inherit;display:block">
      <div class="bl-lg rv {delay_class}">
        <div class="bl-lg-img-wrap">
          <img class="bl-lg-img" src="{image_url}" alt="{topic['title']}" loading="lazy">
        </div>
        <div class="bl-lg-body">
          <span class="bl-tag">{tag}</span>
          <div class="bl-meta"><span>{date_nl}</span><span>8 min leestijd</span></div>
          <h2>{topic['title']}</h2>
          <p>{meta_description}</p>
          <span class="bl-read">Lees het artikel →</span>
        </div>
      </div>
    </a>"""


def update_blog_index(topic, image_url, meta_description, publish_date, tag="Investering"):
    """
    Inserts the new card at the TOP of the bl-grid-lg div in blog.html,
    so the newest post always appears first.
    """
    current_html = get_current_blog_index()
    if not current_html:
        print("  Kan blog.html niet ophalen. Index niet bijgewerkt.")
        return False

    marker = "<!-- BLOG_POSTS_START -->"
    if marker not in current_html:
        print(f"  Marker '{marker}' niet gevonden in blog.html.")
        return False

    new_card = build_blog_card(topic, image_url, meta_description, publish_date, tag)
    updated_html = current_html.replace(marker, marker + new_card)

    return push_file(
        "blog.html",
        updated_html,
        f"Blog index bijgewerkt: '{topic['title']}'"
    )


def get_current_index():
    """Fetches the current index.html from GitHub."""
    resp = requests.get(f"{API_BASE}/contents/index.html", headers=HEADERS)
    if resp.status_code == 200:
        return base64.b64decode(resp.json()["content"]).decode("utf-8")
    return None


def build_index_blog_card(topic, image_url, meta_description, tag="Investering"):
    """
    Builds a card for the homepage (index.html) blog section.
    Entire card is clickable. color:inherit prevents blue/purple link text.
    """
    slug_url = f"{BLOG_FOLDER}/{topic['slug']}.html"
    return f"""<div class="bl-c rv rv-d1">
                <a href="{slug_url}" style="text-decoration:none;color:inherit;display:block">
                <div class="bl-img-wrap"><img class="bl-c-img" src="{image_url}" alt="{topic['title']}" loading="lazy"></div>
                <div class="bl-body"><p class="bl-tag">{tag}</p><h3>{topic['title']}</h3><p>{meta_description}</p><span style="color:var(--gold);font-size:.72rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase">Lees meer →</span></div>
                </a>
            </div>"""


def update_index_blog_section(topic, image_url, meta_description, tag="Investering"):
    """
    Updates the blog section on index.html:
    - Adds the new post card at the top
    - Keeps only 3 cards total (removes the oldest)

    Uses a more robust approach: finds the bl-grid div and replaces
    everything between it and the "Alle artikelen" button.
    """
    current_html = get_current_index()
    if not current_html:
        print("  Kan index.html niet ophalen. Homepage niet bijgewerkt.")
        return False

    # More robust: find the grid opening and the "alle artikelen" div after it
    grid_pattern = r'(<div class="bl-grid">)(.*?)(</div>\s*<div style="text-align:center)'
    match = re.search(grid_pattern, current_html, re.DOTALL)
    if not match:
        print("  Blog grid niet gevonden in index.html. Homepage niet bijgewerkt.")
        return False

    grid_open = match.group(1)
    grid_content = match.group(2)
    grid_after = match.group(3)

    # More robust card matching: find each card by looking for bl-c div opening
    # and matching to the corresponding closing </div> at the same nesting level
    card_pattern = r'<div class="bl-c rv[^"]*">[\s\S]*?</a>\s*</div>'
    existing_cards = re.findall(card_pattern, grid_content)

    # Build new card list: new card first, then keep up to 2 old ones (3 total)
    new_card = build_index_blog_card(topic, image_url, meta_description, tag)
    cards_to_keep = [new_card] + existing_cards[:2]

    new_grid_content = "\n            ".join(cards_to_keep)
    updated_html = (
        current_html[:match.start()]
        + grid_open + "\n            " + new_grid_content + "\n        "
        + grid_after
        + current_html[match.end():]
    )

    return push_file(
        "index.html",
        updated_html,
        f"Homepage blog bijgewerkt: '{topic['title']}'"
    )


def publish_post(topic, html_content, image_url, meta_description, tag="Investering"):
    """
    Publishes a blog post to GitHub:
    1. Pushes the blog post HTML file
    2. Adds a card to blog.html (newest first)
    3. Updates the homepage (index.html) with latest 3 posts
    """
    publish_date = datetime.date.today().isoformat()
    file_path    = f"{BLOG_FOLDER}/{topic['slug']}.html"

    print(f"\nPubliceer naar GitHub: '{topic['title']}'")

    success = push_file(file_path, html_content, f"Nieuwe blogpost: {topic['title']}")

    if success:
        update_blog_index(topic, image_url, meta_description, publish_date, tag)
        update_index_blog_section(topic, image_url, meta_description, tag)
        live_url = f"{SITE_URL}/{file_path}"
        print(f"\nLive op: {live_url}")
        return live_url

    return None
