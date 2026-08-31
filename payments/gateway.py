"""Razorpay integration.

Implemented against Razorpay's REST API with the standard library rather than
the `razorpay` SDK, so the project gains no new dependency and the code runs
as-is. Two calls are involved:

  1. Create a Razorpay Order (server side) and hand its id to the browser.
  2. Verify the signature the browser returns, then mark the Payment paid.

The signature check is the security boundary: never trust the browser's word
that a payment succeeded. Razorpay signs `<order_id>|<payment_id>` with the key
secret, so recomputing that HMAC is what proves the callback is genuine.

With no keys configured the gateway reports itself disabled and the app falls
back to manual reconciliation on the admin payments screen.
"""

import base64
import hashlib
import hmac
import json
import urllib.error
import urllib.request
from decimal import Decimal

from django.conf import settings

RAZORPAY_API = "https://api.razorpay.com/v1"


class GatewayError(Exception):
    """Raised when Razorpay rejects a request or is unreachable."""


def is_enabled() -> bool:
    return bool(getattr(settings, "RAZORPAY_KEY_ID", "") and getattr(settings, "RAZORPAY_KEY_SECRET", ""))


def _auth_header() -> str:
    raw = f"{settings.RAZORPAY_KEY_ID}:{settings.RAZORPAY_KEY_SECRET}".encode()
    return "Basic " + base64.b64encode(raw).decode()


def to_paise(amount) -> int:
    """Razorpay bills in the smallest currency unit."""
    return int((Decimal(str(amount)) * 100).quantize(Decimal("1")))


def create_order(amount, receipt: str, notes: dict | None = None) -> dict:
    """Create a Razorpay Order and return its JSON."""
    if not is_enabled():
        raise GatewayError("Razorpay is not configured.")

    body = json.dumps(
        {
            "amount": to_paise(amount),
            "currency": getattr(settings, "RAZORPAY_CURRENCY", "INR"),
            "receipt": receipt,
            "notes": notes or {},
        }
    ).encode()

    request = urllib.request.Request(
        f"{RAZORPAY_API}/orders",
        data=body,
        headers={"Authorization": _auth_header(), "Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise GatewayError(f"Razorpay rejected the order request: {detail}") from exc
    except urllib.error.URLError as exc:
        raise GatewayError(f"Could not reach Razorpay: {exc.reason}") from exc


def verify_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """Constant-time check of Razorpay's callback signature."""
    if not is_enabled():
        return False
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        f"{order_id}|{payment_id}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature or "")
