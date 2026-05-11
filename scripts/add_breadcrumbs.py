"""Inject BreadcrumbList JSON-LD into each docs/*.html so Google can render
breadcrumb navigation in search snippets.

Skips index.html (home page has no parent).

Run: python3 scripts/add_breadcrumbs.py
"""

import json
import re
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
BASE = "https://tifychau-glitch.github.io/localliftkits"

# Map each page to its breadcrumb parent (None = direct child of home).
# This dictates the breadcrumb chain: home > [parent if any] > page
PARENT_MAP = {
    "resources-for-med-spa-owners.html": None,
    "build-log.html": None,
    "review-request-generator.html": ("Free tools", None),
    "negative-review-reply-generator.html": ("Free tools", None),
    "med-spa-review-volume-calculator.html": ("Free tools", None),
    "med-spa-review-reply-swipe-file.html": ("Products", None),
    "dental-review-reply-swipe-file.html": ("Products", None),
    "10-dollar-swipe-file-vs-29-dollar-growth-kit-med-spa.html": ("Buying guides", None),
    # everything else is treated as an "Articles" child
}
ARTICLE_PAGES = {
    "google-review-reply-templates-med-spas.html",
    "google-review-reply-examples-med-spa.html",
    "what-to-say-bad-review-med-spa.html",
    "hipaa-compliant-review-reply-med-spa.html",
    "how-to-respond-to-1-star-med-spa-review.html",
    "med-spa-review-request-after-treatment.html",
    "med-spa-review-request-templates.html",
    "med-spa-review-workflow-checklist.html",
    "simple-google-review-workflow-for-med-spas.html",
    "ask-med-spa-patients-for-reviews-without-being-pushy.html",
}
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def extract_title(text: str) -> str:
    m = TITLE_RE.search(text)
    if not m:
        return ""
    raw = m.group(1).strip()
    for sep in [" | Local Lift Studio", " - Local Lift Studio"]:
        if sep in raw:
            raw = raw.split(sep)[0].strip()
    return raw


def build_breadcrumbs(filename: str, page_title: str):
    items = [
        {"@type": "ListItem", "position": 1, "name": "Local Lift Studio", "item": BASE + "/"}
    ]
    parent = PARENT_MAP.get(filename)
    if filename in ARTICLE_PAGES:
        items.append({
            "@type": "ListItem", "position": 2, "name": "Articles",
            "item": BASE + "/resources-for-med-spa-owners.html",
        })
        items.append({
            "@type": "ListItem", "position": 3, "name": page_title,
            "item": f"{BASE}/{filename}",
        })
    elif isinstance(parent, tuple):
        items.append({
            "@type": "ListItem", "position": 2, "name": parent[0],
            "item": BASE + "/resources-for-med-spa-owners.html",
        })
        items.append({
            "@type": "ListItem", "position": 3, "name": page_title,
            "item": f"{BASE}/{filename}",
        })
    else:
        items.append({
            "@type": "ListItem", "position": 2, "name": page_title,
            "item": f"{BASE}/{filename}",
        })
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }


def main():
    updated = 0
    for html in sorted(DOCS.glob("*.html")):
        if html.name == "index.html":
            continue
        text = html.read_text(encoding="utf-8")
        if '"@type": "BreadcrumbList"' in text or '"@type":"BreadcrumbList"' in text:
            continue
        title = extract_title(text)
        if not title:
            continue
        crumbs = build_breadcrumbs(html.name, title)
        script_block = f'<script type="application/ld+json">\n{json.dumps(crumbs, indent=2)}\n</script>'
        # Insert just before </head>
        if "</head>" in text:
            new_text = text.replace("</head>", "  " + script_block + "\n</head>", 1)
            html.write_text(new_text, encoding="utf-8")
            updated += 1
    print(f"breadcrumb JSON-LD injected into {updated} pages")


if __name__ == "__main__":
    main()
