"""Link integrity audit for the Local Lift Studio site.

Scans every .html in docs/ for:
- Internal links that point at files that don't exist (404s waiting to happen)
- External links that return non-200 on a HEAD request
- og:image meta tags pointing at missing image files
- Sitemap entries pointing at pages that don't exist locally

Run manually: python3 scripts/link_audit.py

Re-runnable. Returns non-zero exit if any failures found, so it can be
wired into a pre-push git hook later.
"""

import re
import sys
import urllib.request
import urllib.error
import ssl
import socket
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"

INTERNAL_LINK_RE = re.compile(r'(?:href|src)="([^"#?][^"#?]*?)"', re.IGNORECASE)
OG_IMAGE_RE = re.compile(r'<meta\s+property="og:image"\s+content="([^"]+)"', re.IGNORECASE)
EXTERNAL_LINK_RE = re.compile(r'href="(https?://[^"]+)"', re.IGNORECASE)


def is_internal(url: str) -> bool:
    # Protocol-relative URLs (//host/path) are external, not local
    if url.startswith("//"):
        return False
    return not url.startswith(("http://", "https://", "mailto:", "tel:", "#"))


def check_local_file(target: str, html_file: Path) -> bool:
    # URL-decode percent escapes so "Free%20Lead%20Magnet" matches "Free Lead Magnet"
    from urllib.parse import unquote
    target = unquote(target)
    # Resolve relative paths against the file's directory or docs/ root
    if target.startswith("/"):
        candidate = DOCS / target.lstrip("/")
    else:
        candidate = html_file.parent / target
    # Strip query/fragment if any
    candidate = Path(str(candidate).split("?")[0].split("#")[0])
    return candidate.exists()


def check_external(url: str, timeout: float = 6.0) -> tuple[bool, int]:
    """Returns (ok, status_code). Uses curl subprocess for reliable HTTPS handling."""
    import subprocess
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "-o", "/dev/null",
             "-w", "%{http_code}",
             "--max-time", str(int(timeout)),
             "-A", "Mozilla/5.0 LinkAudit/1.0",
             url],
            capture_output=True, text=True, timeout=timeout + 2,
        )
        code = int(result.stdout.strip() or "0")
        return (200 <= code < 400), code
    except (subprocess.TimeoutExpired, ValueError, OSError):
        return False, 0


def main():
    issues = []
    external_to_check = set()

    # Pass 1: scan all html for internal link / og:image issues
    for html in sorted(DOCS.glob("*.html")):
        text = html.read_text(encoding="utf-8")

        # og:image check
        for m in OG_IMAGE_RE.finditer(text):
            og_url = m.group(1)
            if og_url.startswith("http"):
                external_to_check.add(og_url)
            else:
                if not check_local_file(og_url, html):
                    issues.append(f"{html.name}: og:image missing → {og_url}")

        # Internal href/src check
        for m in INTERNAL_LINK_RE.finditer(text):
            target = m.group(1)
            if not is_internal(target):
                continue
            # Skip anchors and queries-only
            if target.startswith("#") or target == "":
                continue
            # Skip data: URIs and similar
            if target.startswith("data:"):
                continue
            if not check_local_file(target, html):
                issues.append(f"{html.name}: internal link 404 → {target}")

        # Collect external links for later
        for m in EXTERNAL_LINK_RE.finditer(text):
            external_to_check.add(m.group(1))

    # Pass 2: sitemap check
    sitemap = DOCS / "sitemap.xml"
    if sitemap.exists():
        sitemap_text = sitemap.read_text(encoding="utf-8")
        for m in re.finditer(r'<loc>([^<]+)</loc>', sitemap_text):
            sm_url = m.group(1)
            # Convert public URL to local path
            if "/localliftkits/" in sm_url:
                tail = sm_url.split("/localliftkits/")[-1]
                tail = tail or "index.html"
                candidate = DOCS / tail
                if not candidate.exists():
                    issues.append(f"sitemap.xml: entry missing locally → {sm_url}")

    # Pass 3: external link spot check (sample 10 to avoid hammering)
    sample = sorted(external_to_check)[:10]
    print(f"[external link spot-check: {len(sample)} of {len(external_to_check)} URLs]")
    for url in sample:
        ok, code = check_external(url)
        if not ok:
            issues.append(f"external link failed → {url} (HTTP {code})")
        else:
            print(f"  ok  {url}")

    print()
    if not issues:
        print(f"link audit PASSED. scanned {len(list(DOCS.glob('*.html')))} pages.")
        sys.exit(0)
    print(f"link audit FOUND {len(issues)} ISSUE(S):")
    for i in issues:
        print(f"  - {i}")
    sys.exit(1)


if __name__ == "__main__":
    main()
