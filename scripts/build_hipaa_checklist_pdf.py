"""Build the second lead-magnet PDF: HIPAA-safe Google review reply checklist.

Single page. Brand palette. Hosted on GitHub Pages, linked from articles.

Run: python3 scripts/build_hipaa_checklist_pdf.py
"""

from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

NAVY = HexColor("#1e3a52")
CREAM = HexColor("#faf6ee")
SAGE = HexColor("#7a8c6c")
DARK = HexColor("#1a1a1a")
MUTED = HexColor("#5a5a5a")

OUT = Path(__file__).resolve().parent.parent / "docs" / "Free Lead Magnet" / "HIPAA-safe Google Review Reply Checklist.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)


SECTIONS = [
    ("Before you reply",
     [
        "Wait at least a few hours. Defensive replies happen in the first hour.",
        "Read the review fully. Identify the actual complaint type.",
        "Check whether the reviewer named a treatment, provider, or visit date.",
        "If they did, take a screenshot. You will not reference the detail publicly, but you may need it for internal follow-up.",
     ]),
    ("In the public reply, NEVER",
     [
        "Confirm whether the reviewer was a patient.",
        "Name the treatment, procedure, or service they had.",
        "Reference their appointment date, time, or provider by name.",
        "Mention billing, insurance, or financial details.",
        "Offer a refund or discount in the public reply.",
        "Argue point by point with the reviewer's claims.",
        "Quote any specific HIPAA-protected detail to deny or correct it.",
     ]),
    ("In the public reply, ALWAYS",
     [
        "Open with one short line of thanks for the feedback.",
        "Acknowledge the feeling, not the fact. 'We are sorry your experience did not meet expectations.'",
        "State a privacy line. 'Because patient privacy matters, we cannot discuss specifics publicly.'",
        "Move the conversation private. 'Please contact us at [phone or email] so we can learn more.'",
        "Keep total length to 2 to 4 sentences.",
        "Have a second person read it before posting if the review is emotional or specific.",
     ]),
    ("After posting",
     [
        "Log the reply in your review tracker so it does not sit unanswered.",
        "If it qualifies for Google removal (fake, off-topic, from a non-patient), flag it through Google Business Profile.",
        "If the reviewer responds privately, handle service recovery in writing. Keep emails to factual, kind, and short.",
        "Do not re-engage publicly even if the reviewer escalates. The audience for the public thread is future patients, not the reviewer.",
     ]),
]


def main():
    page_w, page_h = LETTER
    c = canvas.Canvas(str(OUT), pagesize=LETTER)
    # Background
    c.setFillColor(CREAM)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    # Header bar
    c.setFillColor(NAVY)
    c.rect(0, page_h - 1.05 * 72, page_w, 1.05 * 72, fill=1, stroke=0)
    # Title
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(0.6 * 72, page_h - 0.55 * 72, "HIPAA-Safe Google Review Reply Checklist")
    c.setFont("Helvetica", 10.5)
    c.setFillColor(HexColor("#cbd5d3"))
    c.drawString(0.6 * 72, page_h - 0.82 * 72, "For med spas, aesthetic clinics, dental offices, and small medical practices.")

    # Sage accent stripe
    c.setFillColor(SAGE)
    c.rect(0, 0.55 * 72, page_w, 0.05 * 72, fill=1, stroke=0)

    # Body
    x = 0.6 * 72
    y = page_h - 1.4 * 72
    body_size = 9.0
    line_h = 12.5
    body_w = page_w - 1.2 * 72

    for header, items in SECTIONS:
        # Section header
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 12.5)
        c.drawString(x, y, header)
        y -= 14
        # Sage underline
        c.setStrokeColor(SAGE)
        c.setLineWidth(1.2)
        c.line(x, y + 4, x + 38, y + 4)
        y -= 2
        # Items
        for item in items:
            c.setFillColor(SAGE)
            c.setFont("Helvetica-Bold", body_size)
            c.drawString(x, y, "•")
            c.setFillColor(DARK)
            c.setFont("Helvetica", body_size)
            wrapped = simpleSplit(item, "Helvetica", body_size, body_w - 14)
            for j, line in enumerate(wrapped):
                c.drawString(x + 14, y - j * line_h, line)
            y -= line_h * len(wrapped) + 2
        y -= 6

    # Footer
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(0.6 * 72, 0.32 * 72,
                 "Local Lift Studio  |  Free download  |  Not legal or compliance advice. Always verify with your practice's compliance officer.")
    c.drawString(0.6 * 72, 0.20 * 72,
                 "Full reply templates: tifychau-glitch.github.io/localliftkits")

    c.showPage()
    c.save()
    print(f"built {OUT}")
    print(f"size: {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
