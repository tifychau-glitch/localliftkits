# Local Lift Kits

Public landing-page repo for Local Lift Studio / Local Lift Kits.

Current first product:

Google Reviews Growth Kit for Med Spas

## What is in this repo

- `landing-page-deploy/` - deploy-ready static landing page folder.
- `TIFFANY-LAUNCH-STEPS.md` - simple launch checklist for Buttondown, Gumroad, and GoatCounter values.
- `apply_launch_values.py` - helper script that safely replaces public launch placeholders.

## What is intentionally not in this repo

The paid customer product ZIP and buyer package are intentionally ignored so they do not accidentally become public if this repo is used for GitHub Pages.

Final buyer ZIP lives locally at:

`/Users/tiffanychau/nori-money-project/Google-Reviews-Growth-Kit-for-Med-Spas-v1.zip`

Upload that ZIP directly to Gumroad/Payhip, not GitHub.

## Launch placeholders

Do not deploy publicly until these are replaced in `landing-page-deploy/index.html`:

- `YOUR_BUTTONDOWN_USERNAME`
- `YOUR_GOATCOUNTER_CODE`
- `CHECKOUT_LINK_GOES_HERE`

Use:

```bash
python3 apply_launch_values.py \
  --buttondown YOUR_PUBLIC_BUTTONDOWN_USERNAME \
  --checkout-url https://YOUR_GUMROAD_OR_PAYHIP_URL \
  --goatcounter YOUR_GOATCOUNTER_CODE
```

## Post-launch rule

After launch, hold the offer, price, headline, main copy, and preview order steady for 14 days so analytics are interpretable.
