#!/usr/bin/env python3
"""Apply public launch values to Local Lift Studio deploy files.

Usage:
  python3 apply_launch_values.py \
    --buttondown USERNAME \
    --checkout-url https://gumroad.com/l/... \
    --goatcounter CODE

Do not put passwords, private tokens, API keys, or payment info here.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path('/Users/tiffanychau/nori-money-project')
DEPLOY_INDEX = ROOT / 'landing-page-deploy' / 'index.html'
SELLER_TEMPLATE = ROOT / 'local-business-review-growth-kit-v1' / 'Seller Assets' / 'landing-page-template-NEEDS-SETUP.html'
SETUP_DOC = ROOT / 'local-business-review-growth-kit-v1' / 'Seller Assets' / 'Landing Page Email and Analytics Setup.md'

PLACEHOLDERS = [
    'YOUR_BUTTONDOWN_USERNAME',
    'YOUR_GOATCOUNTER_CODE',
    'CHECKOUT_LINK_GOES_HERE',
]


def die(msg: str) -> None:
    print(f'ERROR: {msg}', file=sys.stderr)
    sys.exit(1)


def validate_buttondown(value: str) -> str:
    value = value.strip()
    if value.startswith('http://') or value.startswith('https://'):
        value = value.rstrip('/').split('/')[-1]
    if not re.fullmatch(r'[A-Za-z0-9_-]{2,80}', value):
        die('Buttondown username should be a public slug like localliftkits, not an email/password/token.')
    return value


def validate_goatcounter(value: str) -> str:
    value = value.strip()
    value = value.replace('https://', '').replace('http://', '')
    value = value.replace('.goatcounter.com', '').strip('/ ')
    if not re.fullmatch(r'[A-Za-z0-9-]{2,80}', value):
        die('GoatCounter code should be the public site code/subdomain, like locallift.')
    return value


def validate_checkout_url(value: str) -> str:
    value = value.strip()
    if not re.match(r'^https://', value):
        die('Checkout URL must start with https://')
    if any(secret_word in value.lower() for secret_word in ['password', 'token=', 'apikey', 'api_key', 'secret=']):
        die('Checkout URL looks like it may contain a secret/token. Do not use it.')
    return value


def replace_in_file(path: Path, buttondown: str, goatcounter: str, checkout_url: str) -> None:
    if not path.exists():
        die(f'Missing file: {path}')
    text = path.read_text(encoding='utf-8')
    text = text.replace('YOUR_BUTTONDOWN_USERNAME', buttondown)
    text = text.replace('YOUR_GOATCOUNTER_CODE', goatcounter)
    text = text.replace('CHECKOUT_LINK_GOES_HERE', checkout_url)
    path.write_text(text, encoding='utf-8')


def verify(path: Path, is_deploy: bool = False) -> None:
    text = path.read_text(encoding='utf-8')
    remaining = [p for p in PLACEHOLDERS if p in text]
    if remaining:
        die(f'Placeholders still remain in {path}: {remaining}')
    if is_deploy:
        if '../assets/' in text:
            die('Deploy index still contains ../assets/ paths. It should use assets/... when deployed as site root.')
        required_assets = [
            'assets/cover.png',
            'assets/preview-1-dashboard.png',
            'assets/preview-2-copy-builder.png',
            'assets/preview-3-review-tracker.png',
        ]
        missing = [asset for asset in required_assets if asset not in text]
        if missing:
            die(f'Deploy index is missing expected asset refs: {missing}')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--buttondown', required=True, help='Public Buttondown username/slug')
    parser.add_argument('--checkout-url', required=True, help='Public Gumroad/Payhip checkout URL')
    parser.add_argument('--goatcounter', required=True, help='Public GoatCounter site code/subdomain')
    args = parser.parse_args()

    buttondown = validate_buttondown(args.buttondown)
    goatcounter = validate_goatcounter(args.goatcounter)
    checkout_url = validate_checkout_url(args.checkout_url)

    replace_in_file(DEPLOY_INDEX, buttondown, goatcounter, checkout_url)
    replace_in_file(SELLER_TEMPLATE, buttondown, goatcounter, checkout_url)

    verify(DEPLOY_INDEX, is_deploy=True)
    verify(SELLER_TEMPLATE, is_deploy=False)

    print('Launch values applied successfully.')
    print(f'Updated deploy page: {DEPLOY_INDEX}')
    print(f'Updated seller template: {SELLER_TEMPLATE}')
    print('Verified: no launch placeholders remain in updated HTML files.')
    print('Verified: deploy index uses site-root asset paths: assets/...')


if __name__ == '__main__':
    main()
