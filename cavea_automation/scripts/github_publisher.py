"""
CAVEA BLOG AUTOMATION — GITHUB PUBLISHER (v2)
Pushes blog posts to GitHub and inserts a correctly styled card
into blog.html using the site's existing bl-lg CSS classes.
"""

import json
import os
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


def build_blog_card(topic, image_url, meta_description, publish_date, delay_class="rv-d1"):
    """
    Builds a card in the exact same format as the existing bl-lg cards
    on the Cavea blog page. This ensures the new post looks identical
    to the four existing posts.
    """
    date_nl = format_date_nl(publish_date)
    return f"""
    <!-- Blog post: {topic['slug']} | Added: {publish_date} -->
    <div class="bl-lg rv {delay_class}">
      <div class="bl-lg-img-wrap">
        <img class="bl-lg-img" src="{image_url}" alt="{topic['title_1']}" loading="lazy">
      </div>
      <div class="bl-lg-body">
        <span class="bl-tag">Investering</span>
        <div class="bl-meta"><span>{date_nl}</span><span>8 min leestijd</span></div>
        <h2>{topic['title_1']}</h2>
        <p>{meta_description}</p>
        <a href="{BLOG_FOLDER}/{topic['slug']}.html" class="bl-read">Lees het artikel →</a>
      </div>
    </div>"""


def update_blog_index(topic, image_url, meta_description, publish_date):
    """
    Inserts the new card at the TOP of the bl-grid-lg div in blog.html,
    so the newest post always appears first.

    The marker <!-- BLOG_POSTS_START --> must be the first thing
    inside <div class="bl-grid-lg">.
    """
    current_html = get_current_blog_index()
    if not current_html:
        print("  Kan blog.html niet ophalen. Index niet bijgewerkt.")
        return False

    # We look for the marker inside the grid
    marker = "<!-- BLOG_POSTS_START -->"
    if marker not in current_html:
        print(f"  Marker '{marker}' niet gevonden in blog.html.")
        print("  Voeg dit toe als eerste regel binnen <div class=\"bl-grid-lg\">")
        return False

    new_card    = build_blog_card(topic, image_url, meta_description, publish_date)
    updated_html = current_html.replace(marker, marker + new_card)

    return push_file(
        "blog.html",
        updated_html,
        f"Blog index bijgewerkt: '{topic['title_1']}'"
    )


def publish_post(topic, html_content, image_url, meta_description):
    publish_date = datetime.date.today().isoformat()
    file_path    = f"{BLOG_FOLDER}/{topic['slug']}.html"

    print(f"\nPubliceer naar GitHub: '{topic['title_1']}'")

    success = push_file(file_path, html_content, f"Nieuwe blogpost: {topic['title_1']}")

    if success:
        update_blog_index(topic, image_url, meta_description, publish_date)
        live_url = f"{SITE_URL}/{file_path}"
        print(f"\nLive op: {live_url}")
        return live_url

    return None
