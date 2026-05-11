"""Generate per-article Open Graph share images at 1200x630.

Reads each .html in docs/, extracts the <title>, renders a branded card.
Saves PNGs to docs/og/<slug>.png.

Re-runnable. Skips images that already exist unless --force is passed.
"""

import re
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DOCS = Path(__file__).resolve().parent.parent / "docs"
OG_DIR = DOCS / "og"
OG_DIR.mkdir(parents=True, exist_ok=True)

# Brand palette (matches the article CSS palette)
CREAM = (251, 247, 239)
PINK_TINT = (248, 238, 231)
MINT_TINT = (238, 247, 241)
INK = (24, 33, 31)
MUTED = (98, 113, 107)
SAGE = (142, 169, 155)
BLUSH = (244, 221, 216)
PLUM = (28, 43, 39)

WIDTH, HEIGHT = 1200, 630


def find_font(candidates, size):
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


HEADLINE_FONTS = [
    "/System/Library/Fonts/Avenir Next.ttc",
    "/System/Library/Fonts/Supplemental/Avenir.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
]
LABEL_FONTS = [
    "/System/Library/Fonts/Avenir Next.ttc",
    "/System/Library/Fonts/Supplemental/Avenir.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
]


def extract_title(html_text: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
    if not m:
        return ""
    raw = m.group(1).strip()
    # Strip the " | Local Lift Studio" trailing suffix and similar
    for sep in [" | Local Lift Studio", " - Local Lift Studio"]:
        if sep in raw:
            raw = raw.split(sep)[0].strip()
    return raw


def wrap_lines(text: str, font, max_width: int):
    words = text.split()
    lines = []
    cur = []
    for w in words:
        trial = " ".join(cur + [w])
        bbox = font.getbbox(trial)
        if (bbox[2] - bbox[0]) > max_width and cur:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))
    return lines


def draw_gradient_background(img):
    # Soft cream gradient with subtle warm/cool corner tints (mimics CSS radial gradients)
    draw = ImageDraw.Draw(img)
    # Base cream
    draw.rectangle([(0, 0), (WIDTH, HEIGHT)], fill=CREAM)
    # Pink-tint top-left blur (rough approximation via stacked ellipses)
    for r, alpha in [(420, 22), (320, 36), (220, 56)]:
        layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.ellipse((-150, -150, 150 + 2 * r, 150 + 2 * r),
                   fill=(244, 221, 216, alpha))
        img.alpha_composite(layer)
    # Mint-tint top-right
    for r, alpha in [(420, 22), (320, 38), (220, 60)]:
        layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.ellipse((WIDTH - 200 - 2 * r, -150, WIDTH + 200, 150 + 2 * r),
                   fill=(220, 235, 228, alpha))
        img.alpha_composite(layer)
    return img


def render_og(title: str, out_path: Path):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 255))
    img = draw_gradient_background(img)
    draw = ImageDraw.Draw(img)

    # Brand mark + name top-left
    cx, cy = 64, 60
    draw.ellipse((cx, cy, cx + 38, cy + 38), fill=SAGE, outline=None)
    inner = Image.new("RGBA", (28, 28), (0, 0, 0, 0))
    ind = ImageDraw.Draw(inner)
    ind.ellipse((0, 0, 28, 28), fill=(255, 255, 255, 110))
    img.paste(inner, (cx + 5, cy + 5), inner)
    label_font = find_font(LABEL_FONTS, 24)
    draw.text((cx + 52, cy + 5), "Local Lift Studio", font=label_font, fill=INK)

    # Eyebrow chip
    eyebrow_font = find_font(LABEL_FONTS, 18)
    eyebrow_text = "Free guide for med spa owners"
    eb_bbox = eyebrow_font.getbbox(eyebrow_text)
    eb_w = eb_bbox[2] - eb_bbox[0] + 28
    eb_h = 36
    eb_x, eb_y = 64, 144
    draw.rounded_rectangle((eb_x, eb_y, eb_x + eb_w, eb_y + eb_h),
                           radius=18, fill=(255, 255, 255, 220),
                           outline=(0, 0, 0, 32), width=1)
    draw.text((eb_x + 14, eb_y + 8), eyebrow_text, font=eyebrow_font, fill=(67, 86, 79))

    # Headline (auto-fit to width, max 3 lines)
    margin = 64
    max_w = WIDTH - margin * 2
    size = 76
    while size > 36:
        f = find_font(HEADLINE_FONTS, size)
        lines = wrap_lines(title, f, max_w)
        if len(lines) <= 3:
            break
        size -= 4
    line_height = int(size * 1.08)
    y = 220
    for line in lines:
        draw.text((margin, y), line, font=f, fill=INK)
        y += line_height

    # Bottom row: site URL + accent
    site_font = find_font(LABEL_FONTS, 22)
    draw.text((margin, HEIGHT - 80), "tifychau-glitch.github.io/localliftkits", font=site_font, fill=MUTED)

    # Subtle bottom accent bar
    draw.rectangle((0, HEIGHT - 12, WIDTH, HEIGHT), fill=SAGE)

    img.convert("RGB").save(out_path, "PNG", optimize=True)


def main():
    force = "--force" in sys.argv
    built = 0
    skipped = 0
    for html in sorted(DOCS.glob("*.html")):
        if html.name == "thank-you.html":
            continue
        slug = html.stem
        out = OG_DIR / f"{slug}.png"
        if out.exists() and not force:
            skipped += 1
            continue
        title = extract_title(html.read_text(encoding="utf-8"))
        if not title:
            print(f"  skipping {slug} (no title)")
            continue
        render_og(title, out)
        print(f"  built {slug}.png  ({title[:60]}...)")
        built += 1
    print(f"\n  built: {built}, skipped: {skipped}")


if __name__ == "__main__":
    main()
