# Tiffany Launch Steps - Local Lift Studio

Status: Gumroad account created. Buttondown account created. Nice. We are close.

## What Nori needs from Tiffany

Please send these values only after you have them:

```text
BUTTONDOWN_USERNAME=localliftkits
GUMROAD_CHECKOUT_URL=https://lifted16.gumroad.com/l/qkpxfz?_gl=1*xd9w6w*_ga*MzQ4OTg3ODYxLjE3NzU1NjkyMDM.*_ga_6LJN6D94N6*czE3Nzc5ODc2NDMkbzUkZzAkdDE3Nzc5ODc2NDMkajYwJGwwJGgw
GOATCOUNTER_CODE=localiftkits
```

Do not send passwords, recovery codes, API keys, payment info, or private tokens.

## Step 1 - Buttondown

Find your Buttondown username/publication slug.

Usually the form action will become something like:

```text
https://buttondown.email/YOUR_USERNAME
```

Send only the public username/slug, not your password.

Example:

```text
BUTTONDOWN_USERNAME=localliftkits
```

## Step 2 - Gumroad

Create the product/listing using the final buyer ZIP:

```text
/Users/tiffanychau/nori-money-project/Google-Reviews-Growth-Kit-for-Med-Spas-v1.zip
```

Use these seller assets:

```text
/Users/tiffanychau/nori-money-project/local-business-review-growth-kit-v1/Seller Assets/Product Listing Copy.md
/Users/tiffanychau/nori-money-project/local-business-review-growth-kit-v1/assets/cover.png
/Users/tiffanychau/nori-money-project/local-business-review-growth-kit-v1/assets/preview-1-dashboard.png
/Users/tiffanychau/nori-money-project/local-business-review-growth-kit-v1/assets/preview-2-copy-builder.png
/Users/tiffanychau/nori-money-project/local-business-review-growth-kit-v1/assets/preview-3-review-tracker.png
```

Price:

```text
$29
```

After Gumroad gives you the public product/checkout URL, send it like:

```text
GUMROAD_CHECKOUT_URL=https://...
```

## Step 3 - GoatCounter

Create a free GoatCounter site and send the public site code/subdomain.

Example:

```text
GOATCOUNTER_CODE=locallift
```

Do not send passwords or private account settings.

## Step 4 - Nori applies launch values

Once you send the three values, Nori will run:

```text
/Users/tiffanychau/nori-money-project/apply_launch_values.py
```

That script will:

- replace `YOUR_BUTTONDOWN_USERNAME`
- replace `YOUR_GOATCOUNTER_CODE`
- replace `CHECKOUT_LINK_GOES_HERE`
- check that no launch placeholders remain
- verify deploy asset paths still use `assets/...`

## Step 5 - Deploy

Only deploy this folder after placeholders are replaced:

```text
/Users/tiffanychau/nori-money-project/landing-page-deploy
```

Do not deploy this source template directly:

```text
/Users/tiffanychau/nori-money-project/local-business-review-growth-kit-v1/Seller Assets/landing-page-template-NEEDS-SETUP.html
```

## Step 6 - First 14 days after launch

Do not change:

- offer
- price
- headline
- main copy
- preview order

Only fix real bugs like broken links, broken images, checkout failure, analytics failure, or email capture failure.

Reason: GoatCounter data is only useful if the page holds still long enough to measure.
