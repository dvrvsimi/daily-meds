"""
fetch_meditations.py
────────────────────
ONE-TIME SETUP SCRIPT — run this once locally before pushing to GitHub.

Downloads Marcus Aurelius's Meditations (George Long translation, 1862)
from the Standard Ebooks GitHub repository, parses each book's XHTML into
individual passages, and writes them to meditations.json.

The George Long translation is public domain (published 1862).
Standard Ebooks' source files are in the public domain.

Usage:
    python fetch_meditations.py

Requires:
    pip install requests beautifulsoup4
"""

import json
import re
import sys

import requests
from bs4 import BeautifulSoup

# ── Standard Ebooks raw GitHub URLs for each book ─────────────────────
BASE_URL = (
    "https://raw.githubusercontent.com/"
    "standardebooks/marcus-aurelius_meditations_george-long/"
    "master/src/epub/text/book-{}.xhtml"
)
TOTAL_BOOKS = 12


def fetch_book_xhtml(book_num):
    """Download the XHTML source for a single book (1–12)."""
    url = BASE_URL.format(book_num)
    print(f"  Fetching Book {book_num}... ", end="", flush=True)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    print("OK")
    return resp.text


def parse_passages(xhtml_text, book_num):
    """
    Extract individual passages from a book's XHTML.

    Standard Ebooks structures each section inside <p> tags.
    Some paragraphs are sub-parts of a single numbered section,
    so we group them by the nearest preceding heading or section marker.
    """
    soup = BeautifulSoup(xhtml_text, "html.parser")
    passages = []
    section_num = 0

    # Standard Ebooks wraps each numbered meditation in its own
    # section or uses <p> tags directly. We treat each substantive
    # paragraph as its own passage for daily email purposes.
    for element in soup.find_all("p"):
        text = element.get_text(separator=" ", strip=True)

        # Skip empty paragraphs and very short fragments (headers, numbers)
        if not text or len(text) < 20:
            continue

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text).strip()

        section_num += 1
        passages.append({
            "book": book_num,
            "section": section_num,
            "text": text,
        })

    return passages


def main():
    print("=" * 60)
    print("Fetching Meditations by Marcus Aurelius")
    print("George Long translation (1862) · Public domain")
    print("Source: Standard Ebooks (GitHub)")
    print("=" * 60)

    all_passages = []

    for book_num in range(1, TOTAL_BOOKS + 1):
        try:
            xhtml = fetch_book_xhtml(book_num)
            passages = parse_passages(xhtml, book_num)
            all_passages.extend(passages)
            print(f"    → {len(passages)} passages extracted")
        except requests.RequestException as e:
            print(f"FAILED: {e}")
            sys.exit(1)

    # ── Write the JSON file ───────────────────────────────────────────
    output_file = "meditations.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_passages, f, indent=2, ensure_ascii=False)

    print()
    print(f"Done! {len(all_passages)} total passages → {output_file}")
    print(f"File size: {len(json.dumps(all_passages)) / 1024:.1f} KB")
    print()
    print("Next step: commit meditations.json to your repo and push.")


if __name__ == "__main__":
    main()
