"""
=============================================================
  CAVEA BLOG AUTOMATION — MAIN RUNNER
  This is the script you run to publish one blog post.
  It combines the generator and publisher into one command.
=============================================================

USAGE:
  # Publish the next scheduled post:
  python scripts/run_automation.py

  # Publish a specific topic by ID (for manual extra posts):
  python scripts/run_automation.py --id 5

  # Preview without actually publishing (dry run):
  python scripts/run_automation.py --dry-run
"""

import sys
import os
import argparse
import json

# Add parent directory so we can import our scripts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))

from blog_generator import (
    get_next_topic, generate_blog_content, parse_claude_response,
    fetch_wine_image, build_html_page, mark_topic_published,
    TOPICS_PATH, POSTS_DIR
)
from github_publisher import publish_post

import datetime


def get_topic_by_id(topic_id):
    with open(TOPICS_PATH) as f:
        topics = json.load(f)
    for topic in topics:
        if topic["id"] == topic_id:
            return topic, topics
    return None, topics


def run(topic_id=None, dry_run=False):
    print("\n" + "="*55)
    print("  🍷 CAVEA BLOG AUTOMATION")
    print("="*55)

    # 1. Get topic
    if topic_id:
        topic, all_topics = get_topic_by_id(topic_id)
        if not topic:
            print(f"❌ Onderwerp met ID {topic_id} niet gevonden.")
            return
    else:
        topic, all_topics = get_next_topic()
        if not topic:
            print("✅ Alle geplande blogposts zijn al gepubliceerd!")
            return

    print(f"\n📋 Onderwerp: {topic['title_1']}")
    print(f"   Slug:      {topic['slug']}")
    print(f"   Status:    {topic.get('status', 'pending')}")

    # 2. Fetch image
    print("\n🖼️  Zoekt relevante foto...")
    image = fetch_wine_image(f"fine wine {topic['short_tail']}")
    print(f"   Foto URL: {image['url'][:60]}...")

    # 3. Generate content
    print("\n✍️  Claude schrijft het artikel...")
    raw_content = generate_blog_content(topic)
    parsed = parse_claude_response(raw_content)

    if not parsed["content"]:
        print("❌ Geen inhoud gegenereerd. Probeer opnieuw.")
        return

    print(f"   Meta description: {parsed['meta_description'][:60]}...")
    print(f"   Keywords: {parsed['keywords'][:60]}...")

    # 4. Build HTML
    publish_date = datetime.date.today().isoformat()
    html_content = build_html_page(topic, parsed, image, publish_date)

    # 5. Save locally
    local_path = os.path.join(POSTS_DIR, f"{topic['slug']}.html")
    with open(local_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"\n💾 Lokaal opgeslagen: {local_path}")

    if dry_run:
        print("\n🔍 DRY RUN — niet gepubliceerd naar GitHub.")
        print("   Bekijk het bestand lokaal om te controleren.")
        return

    # 6. Publish to GitHub
    live_url = publish_post(topic, html_content, image["url"], parsed["meta_description"])

    # 7. Mark as published
    mark_topic_published(all_topics, topic["id"])

    if live_url:
        print(f"\n🎉 KLAAR! Blogpost live op:")
        print(f"   {live_url}")
    else:
        print("\n⚠️  Publicatie mislukt. Controleer je GitHub token en repository naam.")

    print("\n" + "="*55 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cavea Blog Automation")
    parser.add_argument("--id",      type=int, help="Publiceer specifiek onderwerp op ID")
    parser.add_argument("--dry-run", action="store_true", help="Genereer maar publiceer niet")
    args = parser.parse_args()

    run(topic_id=args.id, dry_run=args.dry_run)
