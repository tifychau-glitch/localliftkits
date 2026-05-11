"""Scan all public site content for AI-tell phrases and voice violations.

Tiffany's voice rules (from ~/.harry/voice/voice_profile.md) explicitly ban:
- em dashes
- "actually" as pseudo-emphasis
- "nobody else is doing it"
- "Not a X, not a Y, not a Z" listing pattern
- "grown-ups"
- "The fix is..."
- "Etsy thing" / calling her own product "a thing"

This script greps each docs/*.html for those patterns and reports per-line.

Some "actually"s are load-bearing (e.g., "what they actually remember"). The
script flags every hit; a human decides whether it earns its place.

Run: python3 scripts/voice_audit.py
"""

import re
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"

# (pattern, severity, description)
PATTERNS = [
    (r"—", "high", "em dash (banned)"),
    (r"–", "high", "en dash (banned)"),
    (r"\bactually\b", "low", "'actually' may be filler"),
    (r"\bnobody else is doing it\b", "high", "banned phrase"),
    (r"\bgrown-ups?\b", "high", "banned ('use adults or specific descriptor')"),
    (r"\bThe fix is\b", "high", "banned templated transition"),
    (r"\bgets? the bag\b", "high", "banned (Claude's framing, not hers)"),
    (r"\bEtsy thing\b", "high", "dismissive toward own product"),
    (r"my (Canva|Notion|Linear)", "low", "'in my [tool]' construction may sound forced"),
    (r"\bThings that bite people\b", "high", "banned folksy section header"),
]


def main():
    out_path = Path(__file__).resolve().parent.parent / "voice_audit_report.md"
    findings = []
    files_scanned = 0
    for html in sorted(DOCS.glob("*.html")):
        files_scanned += 1
        text = html.read_text(encoding="utf-8")
        # Skip <style>...</style> blocks (CSS uses dashes legitimately, etc.)
        body_text = re.sub(r"<style.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        body_text = re.sub(r"<script.*?</script>", "", body_text, flags=re.DOTALL | re.IGNORECASE)
        for pat, severity, desc in PATTERNS:
            for m in re.finditer(pat, body_text):
                # Find line number in original text
                start = m.start()
                line_no = body_text.count("\n", 0, start) + 1
                # Get surrounding context (up to 60 chars before, 60 after)
                ctx_start = max(0, start - 60)
                ctx_end = min(len(body_text), m.end() + 60)
                snippet = body_text[ctx_start:ctx_end].replace("\n", " ").strip()
                findings.append({
                    "file": html.name,
                    "severity": severity,
                    "issue": desc,
                    "snippet": snippet,
                    "match": m.group(0),
                })

    # Sort by severity then file
    sev_order = {"high": 0, "low": 1}
    findings.sort(key=lambda f: (sev_order[f["severity"]], f["file"]))

    high = [f for f in findings if f["severity"] == "high"]
    low = [f for f in findings if f["severity"] == "low"]

    lines = [f"# Voice audit report\n",
             f"Scanned {files_scanned} pages.\n",
             f"- {len(high)} high-severity issues",
             f"- {len(low)} low-severity (review filler words)\n"]
    if high:
        lines.append("## HIGH severity\n")
        for f in high:
            lines.append(f"**{f['file']}** - {f['issue']} (`{f['match']}`)")
            lines.append(f"  > ...{f['snippet']}...\n")
    if low:
        lines.append("## LOW severity (filler word watch)\n")
        for f in low:
            lines.append(f"**{f['file']}** - {f['issue']} (`{f['match']}`)")
            lines.append(f"  > ...{f['snippet']}...\n")
    out_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"voice audit: {len(high)} HIGH, {len(low)} LOW across {files_scanned} pages")
    print(f"report: {out_path}")
    if high:
        print("\nfirst 5 high-severity hits:")
        for f in high[:5]:
            print(f"  {f['file']}: {f['issue']} - {f['snippet'][:80]}")
    sys.exit(1 if high else 0)


if __name__ == "__main__":
    main()
