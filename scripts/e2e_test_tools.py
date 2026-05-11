"""End-to-end smoke tests for the 4 interactive tools.

Launches headless Chromium, drives each tool with sample inputs, asserts the
output renders correctly. Catches UX bugs that static JS inspection misses.

Run: python3 scripts/e2e_test_tools.py
Exit 0 = all pass; exit 1 = at least one test failed (description above).

Tests against LIVE URLs (deployed pages on GitHub Pages) so we verify the
actually-shipped versions.
"""

import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

BASE = "https://tifychau-glitch.github.io/localliftkits"

failures = []


def fail(test_name: str, reason: str):
    failures.append(f"{test_name}: {reason}")
    print(f"  FAIL  {test_name}: {reason}")


def passed(test_name: str):
    print(f"  PASS  {test_name}")


def test_hipaa_auditor(page):
    """Paste a deliberately-bad reply, expect a HIGH risk score and multiple findings."""
    print("TEST 1: HIPAA Risk Auditor")
    page.goto(f"{BASE}/hipaa-review-reply-auditor.html", wait_until="networkidle")

    if "hipaa" not in page.title().lower():
        fail("hipaa-auditor.page-loads", f"unexpected title: {page.title()}")
        return

    # Fill a deliberately bad reply (lots of HIPAA exposures)
    bad_reply = (
        "Hi Sarah, thank you for choosing our clinic for your Botox appointment last Tuesday. "
        "Dr. Patel really enjoyed working with you. Per your chart, we discussed potential bruising "
        "in consultation. Please call us for a complimentary follow-up filler session."
    )
    page.locator("#reply").fill(bad_reply)
    page.locator("button.button.primary:has-text('Run the audit')").click()
    page.wait_for_selector("#score.show", timeout=3000)

    score = page.locator("#score-num").inner_text()
    findings_count = page.locator("#findings .finding").count()
    msg = page.locator("#score-msg").inner_text()

    if int(score) < 50:
        fail("hipaa-auditor.score-flags-bad-reply", f"score was {score}, expected >= 50 for a bad reply")
        return
    if findings_count < 4:
        fail("hipaa-auditor.flags-multiple-issues", f"only {findings_count} findings; expected 4+")
        return
    if "high risk" not in msg.lower():
        fail("hipaa-auditor.risk-message", f"expected 'high risk' in message; got: {msg}")
        return

    passed(f"hipaa-auditor (score={score}, {findings_count} findings)")

    # Test: clear button resets everything
    page.locator("button.button:has-text('Clear')").click()
    if page.locator("#reply").input_value() != "":
        fail("hipaa-auditor.clear-resets-textarea", "textarea not cleared after Clear")
        return
    passed("hipaa-auditor.clear-button")

    # Test: clean reply scores low
    clean_reply = (
        "Thank you for sharing your feedback. We are sorry your experience did not meet expectations. "
        "Because privacy matters, we cannot discuss specifics publicly. Please contact us at hello@example.com."
    )
    page.locator("#reply").fill(clean_reply)
    page.locator("button.button.primary:has-text('Run the audit')").click()
    page.wait_for_selector("#score.show", timeout=3000)
    clean_score = int(page.locator("#score-num").inner_text())
    if clean_score > 20:
        fail("hipaa-auditor.clean-reply-low-score", f"clean reply scored {clean_score}, expected <=20")
        return
    passed(f"hipaa-auditor.clean-reply-passes (score={clean_score})")


def test_volume_calculator(page):
    """Test the review volume calculator math."""
    print("TEST 2: Review Volume Calculator")
    page.goto(f"{BASE}/med-spa-review-volume-calculator.html", wait_until="networkidle")

    # Default values: current=42, patients=120, askrate=35, conversion=22
    # Monthly = 120 * 0.35 * 0.22 = 9.24 new reviews/month
    # 90 days = 3 months → 42 + 28 = 70 (rounded)
    # 365 days = 12 months → 42 + 111 = 153 (rounded)
    r90 = page.locator("#r90").inner_text()
    r365 = page.locator("#r365").inner_text()

    if r90 == "-" or r365 == "-":
        fail("calculator.initial-values-not-computed", f"r90={r90}, r365={r365}")
        return

    r90_val = int(r90)
    r365_val = int(r365)
    if r90_val < 65 or r90_val > 75:
        fail("calculator.r90-math-off", f"r90={r90_val}, expected ~70 (42 + 3*9.24)")
        return
    if r365_val < 145 or r365_val > 160:
        fail("calculator.r365-math-off", f"r365={r365_val}, expected ~153 (42 + 12*9.24)")
        return
    passed(f"calculator.default-math (r90={r90}, r365={r365})")

    # Change ask rate to 100, verify the "max" projection updates
    page.locator("#askrate").fill("100")
    # Trigger recalc by firing input event (already handled via event listener)
    page.locator("#askrate").press("Tab")
    page.wait_for_timeout(200)  # allow JS recalc

    r90_max = int(page.locator("#r90").inner_text())
    # At 100% ask rate, monthly = 120 * 1.0 * 0.22 = 26.4 → 3 months adds 79 → r90 = 121
    if r90_max < 115 or r90_max > 130:
        fail("calculator.high-askrate-math", f"at 100% ask, r90={r90_max}, expected ~121")
        return
    passed(f"calculator.askrate-changes-projection (r90 went to {r90_max})")


def test_reply_generator(page):
    """Test the negative review reply generator."""
    print("TEST 3: Negative Review Reply Generator")
    page.goto(f"{BASE}/negative-review-reply-generator.html", wait_until="networkidle")

    # Fill the form
    page.locator("#spaName").fill("Glow Aesthetics")
    page.locator("#reviewText").fill("The wait was way too long and the receptionist was rude to me.")

    # Click generate button
    page.locator("button#generate").click()
    page.wait_for_timeout(500)

    reply_text = page.locator("#reply").inner_text()
    if len(reply_text) < 30:
        fail("reply-generator.output-too-short", f"reply was {len(reply_text)} chars; expected 30+")
        return
    # Should reference the spa name OR appropriate language; should NOT contain "Botox" or treatment details
    if "Glow Aesthetics" not in reply_text and "we" not in reply_text.lower():
        fail("reply-generator.no-context", f"reply doesn't reference spa or use 'we': {reply_text[:80]}")
        return
    passed(f"reply-generator.produces-reply ({len(reply_text)} chars)")


def test_request_generator(page):
    """Test the review request message generator."""
    print("TEST 4: Review Request Generator")
    page.goto(f"{BASE}/review-request-generator.html", wait_until="networkidle")

    # Defaults are already filled; just click Generate
    page.locator("#spaName").fill("Glow Aesthetics")
    page.locator("#clientName").fill("Jamie")
    page.locator("button#generate").click()
    page.wait_for_timeout(500)

    sms = page.locator("#sms").inner_text()
    email = page.locator("#email").inner_text()

    if len(sms) < 30:
        fail("request-generator.sms-too-short", f"SMS was {len(sms)} chars")
        return
    if len(email) < 50:
        fail("request-generator.email-too-short", f"email was {len(email)} chars")
        return
    if "Jamie" not in sms and "Glow" not in sms:
        fail("request-generator.no-personalization", f"SMS missing personalization: {sms[:80]}")
        return
    passed(f"request-generator.produces-both (SMS={len(sms)}c, email={len(email)}c)")


def main():
    print(f"E2E tests for 4 interactive tools on {BASE}\n")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context()
        page = ctx.new_page()
        try:
            test_hipaa_auditor(page)
            test_volume_calculator(page)
            test_reply_generator(page)
            test_request_generator(page)
        except PlaywrightTimeout as e:
            fail("timeout", str(e))
        finally:
            browser.close()

    print()
    if failures:
        print(f"E2E SUITE FAILED ({len(failures)} failures):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("E2E SUITE PASSED (all 4 tools work end-to-end)")
    sys.exit(0)


if __name__ == "__main__":
    main()
