"""
=============================================================
  CAVEA BLOG AUTOMATION — GITHUB PUBLISHER
  Pushes a finished HTML blog post directly to your GitHub
  repository using the GitHub API. No manual uploading needed!
=============================================================

HOW IT WORKS (beginner explanation):
  Think of this like a robot that opens your GitHub, creates a
  new file in the right folder, and saves it — just like you
  would do manually, but automatically.

  It also:
  - Updates your blog index page (blog.html) with the new post
  - Adds a preview card so visitors can see and click the new article

SETUP:
  1. Go to GitHub → Settings → Developer settings → Personal access tokens
  2. Create a token with 'repo' permissions
  3. Paste the token into config.json as "github_token"
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
GITHUB_REPO  = config["github_repo"]   # e.g. "Luukiotje/cavea-site"
BLOG_FOLDER  = config["blog_folder"]   # e.g. "blog"
SITE_URL     = config["site_url"]

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
API_BASE = f"https://api.github.com/repos/{GITHUB_REPO}"


# ─── Get current file SHA (needed to update existing files) ─
def get_file_sha(path):
    """
    GitHub requires us to know the current 'SHA' (a unique ID)
    of a file before we can update it. This function fetches it.
    If the file doesn't exist yet, it returns None.
    """
    resp = requests.get(f"{API_BASE}/contents/{path}", headers=HEADERS)
    if resp.status_code == 200:
        return resp.json()["sha"]
    return None


# ─── Upload or update a file on GitHub ───────────────────
def push_file(path, content_str, commit_message):
    """
    Uploads a file to GitHub. If the file already exists,
    it updates it. If it's new, it creates it.

    'path' is where the file goes in your repo, e.g. "blog/my-post.html"
    'content_str' is the full HTML text of the file
    'commit_message' is the message shown in your GitHub commit history
    """
    encoded = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
    sha = get_file_sha(path)

    payload = {
        "message": commit_message,
        "content": encoded,
        "branch":  "main"
    }
    if sha:
        payload["sha"] = sha  # Required for updating an existing file

    resp = requests.put(f"{API_BASE}/contents/{path}", headers=HEADERS, json=payload)

    if resp.status_code in (200, 201):
        action = "bijgewerkt" if sha else "aangemaakt"
        print(f"  ✅ GitHub: bestand {action} → {path}")
        return True
    else:
        print(f"  ❌ GitHub fout ({resp.status_code}): {resp.json().get('message')}")
        return False


# ─── Read current blog.html from GitHub ──────────────────
def get_current_blog_index():
    """Downloads the current blog.html from your GitHub repo."""
    resp = requests.get(f"{API_BASE}/contents/blog.html", headers=HEADERS)
    if resp.status_code == 200:
        encoded = resp.json()["content"]
        return base64.b64decode(encoded).decode("utf-8")
    return None


# ─── Build a blog card HTML snippet ──────────────────────
def build_blog_card(topic, image_url, meta_description, publish_date):
    """
    Creates a small HTML preview card for your blog index page.
    This is what visitors see when they browse your blog — a clickable
    card with the title, image, and a short description.
    """
    return f"""
    <!-- Blog post: {topic['slug']} | Added: {publish_date} -->
    <article class="blog-card">
      <a href="{BLOG_FOLDER}/{topic['slug']}.html">
        <img src="{image_url}" alt="{topic['title_1']}" loading="lazy" />
        <div class="blog-card-content">
          <span class="blog-card-date">{publish_date}</span>
          <h2>{topic['title_1']}</h2>
          <p>{meta_description}</p>
          <span class="read-more">Lees meer →</span>
        </div>
      </a>
    </article>"""


# ─── Insert new card into blog.html ──────────────────────
def update_blog_index(topic, image_url, meta_description, publish_date):
    """
    Opens your blog.html, finds the spot where blog posts are listed,
    and inserts the new post card at the TOP (newest first).

    Your blog.html needs to have this comment marker somewhere in it:
        <!-- BLOG_POSTS_START -->
    """
    current_html = get_current_blog_index()
    if not current_html:
        print("  ⚠️  Kan blog.html niet ophalen. Index niet bijgewerkt.")
        return False

    marker = "<!-- BLOG_POSTS_START -->"
    if marker not in current_html:
        print(f"  ⚠️  Marker '{marker}' niet gevonden in blog.html.")
        print("       Voeg deze toe aan je blog.html op de plek waar posts moeten verschijnen.")
        return False

    new_card = build_blog_card(topic, image_url, meta_description, publish_date)
    updated_html = current_html.replace(marker, marker + new_card)

    return push_file(
        "blog.html",
        updated_html,
        f"📝 Blog index bijgewerkt: '{topic['title_1']}'"
    )


# ─── MAIN: publish one post to GitHub ────────────────────
def publish_post(topic, html_content, image_url, meta_description):
    """
    The main function that does everything:
    1. Uploads the new blog post HTML to GitHub
    2. Updates blog.html with a new preview card
    """
    publish_date = datetime.date.today().isoformat()
    file_path    = f"{BLOG_FOLDER}/{topic['slug']}.html"
    commit_msg   = f"🍷 Nieuwe blogpost: {topic['title_1']}"

    print(f"\n🚀 Publiceer naar GitHub: '{topic['title_1']}'")

    success = push_file(file_path, html_content, commit_msg)

    if success:
        update_blog_index(topic, image_url, meta_description, publish_date)
        live_url = f"{SITE_URL}/{file_path}"
        print(f"\n🌐 Live op: {live_url}")
        return live_url

    return None
