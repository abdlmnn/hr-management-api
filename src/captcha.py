import os
from typing import Optional, Tuple

import requests
from rest_framework.exceptions import ValidationError


def verify_captcha(response_token: Optional[str], remoteip: Optional[str] = None) -> Tuple[bool, str]:
    """
    Server-side CAPTCHA verification.

    This is intentionally provider-agnostic:
    - Set CAPTCHA_VERIFY_URL to your provider's siteverify endpoint
      - reCAPTCHA: https://www.google.com/recaptcha/api/siteverify
      - hCaptcha:  https://hcaptcha.com/siteverify
    - Set CAPTCHA_SECRET_KEY to enable enforcement.

    Returns: (is_valid, message)
    Raises ValidationError when CAPTCHA is required but missing/invalid.
    """

    secret = os.getenv("CAPTCHA_SECRET_KEY")
    if not secret:
        # CAPTCHA not enforced (dev or not configured)
        return True, "captcha_not_configured"

    if not response_token:
        raise ValidationError({"captcha_token": ["CAPTCHA is required."]})

    verify_url = os.getenv("CAPTCHA_VERIFY_URL") or "https://www.google.com/recaptcha/api/siteverify"

    data = {
        "secret": secret,
        "response": response_token,
    }
    if remoteip:
        data["remoteip"] = remoteip

    try:
        r = requests.post(verify_url, data=data, timeout=5)
        r.raise_for_status()
        payload = r.json()
    except Exception:
        # Avoid leaking provider/network errors; treat as invalid
        raise ValidationError({"captcha_token": ["CAPTCHA verification failed. Please try again."]})

    if payload.get("success") is True:
        return True, "captcha_ok"

    raise ValidationError({"captcha_token": ["Invalid CAPTCHA. Please try again."]})


