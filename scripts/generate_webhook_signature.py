r"""
Generate SHA256 signature for the payment webhook payload.

Usage:
  poetry run python scripts/generate_webhook_signature.py \\
    --transaction-id 5eae174f-7cd0-472c-bd36-35660f00132b \\
    --user-id 1 --account-id 1 --amount 100 \\
    --secret-key gfdmhghif38yrf9ew0jkf32

  poetry run python scripts/generate_webhook_signature.py ... --json
"""

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from uuid import UUID

# Add the project root so 'app' module is importable
sys.path.insert(0, str((Path(__file__).parent.parent).resolve()))


from app.services.payments.signature import build_webhook_signature
from app.settings import settings


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate payment webhook SHA256 signature.",
    )
    parser.add_argument(
        "--transaction-id",
        required=True,
        help="External transaction UUID",
    )
    parser.add_argument("--user-id", type=int, required=True, help="User id")
    parser.add_argument("--account-id", type=int, required=True, help="Account id")
    parser.add_argument("--amount", required=True, help="Payment amount")
    parser.add_argument(
        "--secret-key",
        default=None,
        help="Webhook secret (default: PAYMENTS_APP_PAYMENTS_SECRET_KEY from settings)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full webhook JSON including signature",
    )
    parser.add_argument(
        "--signature-only",
        action="store_true",
        help="Print only the signature hash (default when --json is not set)",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point."""
    args = _parse_args()
    secret_key = args.secret_key or settings.payments_secret_key

    try:
        transaction_id = UUID(args.transaction_id)
    except ValueError:
        print(f"Invalid transaction_id UUID: {args.transaction_id}", file=sys.stderr)
        return 1

    try:
        amount = Decimal(args.amount)
    except InvalidOperation:
        print(f"Invalid amount: {args.amount}", file=sys.stderr)
        return 1

    signature = build_webhook_signature(
        account_id=args.account_id,
        amount=amount,
        transaction_id=transaction_id,
        user_id=args.user_id,
        secret_key=secret_key,
    )

    if args.json:
        payload = {
            "transaction_id": str(transaction_id),
            "user_id": args.user_id,
            "account_id": args.account_id,
            "amount": (
                int(amount) if amount == amount.to_integral_value() else float(amount)
            ),
            "signature": signature,
        }
        print(json.dumps(payload, indent=2))
        return 0

    if args.signature_only or not args.json:
        print(signature)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
