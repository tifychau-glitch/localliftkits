"""Build the third lead-magnet PDF: Med spa Google review reply audit worksheet.

A single-page printable worksheet that lets owners score their last 5 Google
review replies against 10 best-practice criteria, see where they stand, and
fix the gaps.

Run: python3 scripts/build_audit_worksheet_pdf.py
"""

from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

NAVY = HexColor("#1e3a52")
CREAM = HexColor("#faf6ee")
SAGE = HexColor("#7a8c6c")
SAGE_LIGHT = HexColor("#d8e0cf")
DARK = HexColor("#1a1a1a")
MUTED = HexColor("#5a5a5a")
ROSE = HexColor("#b85a4e")

OUT = Path(__file__).resolve().parent.parent / "docs" / "Free Lead Magnet" / "Med Spa Review Reply Audit Worksheet.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)


CRITERIA = [
    "Reply length is 2 to 4 sentences. Not a wall of text.",
    "Reply does NOT confirm the reviewer was a patient.",
    "Reply does NOT name a treatment, condition, or provider.",
    "Reply opens with one short, neutral line of thanks.",
    "Reply acknowledges feeling, not facts (e.g. 'sorry your experience...').",
    "Reply includes a privacy line ('cannot discuss specifics publicly').",
    "Reply offers ONE offline contact path (phone or email).",
    "Reply does NOT argue with the reviewer's account in public.",
    "Reply does NOT offer a refund, discount, or perk in public.",
    "Reply posted within 72 hours of the review going live.",
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
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.55 * 72, page_h - 0.5 * 72, "Med Spa Review Reply Audit Worksheet")
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#cbd5d3"))
    c.drawString(0.55 * 72, page_h - 0.78 * 72,
                 "Audit your last 5 Google review replies. 10 criteria. Score each reply 0 to 10.")

    # Sage accent stripe
    c.setFillColor(SAGE)
    c.rect(0, 0.45 * 72, page_w, 0.05 * 72, fill=1, stroke=0)

    # Grid setup
    left = 0.5 * 72
    right = page_w - 0.5 * 72
    grid_top = page_h - 1.35 * 72

    # Column headers
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(left, grid_top, "Criterion")

    # 5 reply columns
    col_w = 0.45 * 72
    reply_x_start = right - (5 * col_w) - 0.1 * 72
    for i in range(5):
        c.drawCentredString(reply_x_start + i * col_w + col_w / 2, grid_top, f"R{i+1}")

    # Underline
    c.setStrokeColor(SAGE)
    c.setLineWidth(0.8)
    c.line(left, grid_top - 4, right, grid_top - 4)

    # Rows
    y = grid_top - 16
    row_h = 22
    body_size = 8.5
    criterion_w = reply_x_start - left - 6
    c.setFont("Helvetica", body_size)
    c.setFillColor(DARK)

    for idx, crit in enumerate(CRITERIA):
        # Alt-row tint
        if idx % 2 == 0:
            c.setFillColor(SAGE_LIGHT)
            c.rect(left - 4, y - 6, right - left + 8, row_h, fill=1, stroke=0)

        # Criterion text (wrap if needed)
        wrapped = simpleSplit(f"{idx+1}. {crit}", "Helvetica", body_size, criterion_w)
        c.setFillColor(DARK)
        c.setFont("Helvetica", body_size)
        for j, line in enumerate(wrapped[:2]):
            c.drawString(left, y + (5 - j * 9), line)

        # 5 checkboxes per row
        for i in range(5):
            box_x = reply_x_start + i * col_w + col_w / 2 - 5
            box_y = y + 3
            c.setStrokeColor(NAVY)
            c.setLineWidth(0.6)
            c.rect(box_x, box_y, 10, 10, fill=0, stroke=1)

        y -= row_h

    # Totals row
    y -= 4
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(left, y, "Total (out of 10)")
    for i in range(5):
        cx = reply_x_start + i * col_w + col_w / 2
        c.setStrokeColor(NAVY)
        c.setLineWidth(0.8)
        c.line(cx - 12, y - 3, cx + 12, y - 3)
    y -= 18

    # Scoring band
    c.setFillColor(SAGE)
    c.rect(left - 4, y - 38, right - left + 8, 32, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(left, y - 16, "Scoring")
    c.setFont("Helvetica", 8.5)
    c.drawString(left, y - 28,
                 "8 to 10 healthy.  5 to 7 needs targeted fixes.  Below 5 rebuild from templates.")
    y -= 50

    # Fix list
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left, y, "Most common fixes (in order of frequency)")
    y -= 14
    fixes = [
        "Too long. Trim to 2 to 4 sentences. Long replies signal defensiveness.",
        "Implicit patient confirmation ('your visit last Tuesday'). Strip every dated detail.",
        "Treatment named ('the Botox you had'). Never. Strip every clinical noun.",
        "No offline contact path. Add one phone or email line.",
        "Argued in public. Cut every sentence that contradicts the reviewer.",
    ]
    c.setFont("Helvetica", 8.5)
    c.setFillColor(DARK)
    for f in fixes:
        wrapped = simpleSplit(f"- {f}", "Helvetica", 8.5, right - left)
        for j, line in enumerate(wrapped):
            c.drawString(left, y - j * 11, line)
        y -= 11 * len(wrapped) + 2

    # Footer
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.5)
    c.drawString(left, 0.28 * 72,
                 "Local Lift Studio  |  Free download  |  Not legal or compliance advice. Verify with your practice's compliance officer.")
    c.drawString(left, 0.18 * 72,
                 "Full reply templates and the request workflow kit: tifychau-glitch.github.io/localliftkits")

    c.showPage()
    c.save()
    print(f"built {OUT}")
    print(f"size: {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
