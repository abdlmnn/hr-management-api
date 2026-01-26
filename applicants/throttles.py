from django.conf import settings
from rest_framework.throttling import SimpleRateThrottle


class _DynamicRateIpThrottle(SimpleRateThrottle):
    """
    IP-based throttle that reads rates from Django settings at runtime:
      settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"][scope]

    We do this (instead of DRF api_settings) so tests using override_settings
    behave deterministically and so ops can adjust via env-backed settings.
    """

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}

    def get_rate(self):
        rates = getattr(settings, "REST_FRAMEWORK", {}).get("DEFAULT_THROTTLE_RATES", {})
        return rates.get(self.scope)


class PublicApplicantSubmitThrottle(_DynamicRateIpThrottle):
    scope = "public_applicant_submit"


class PublicApplicantVerifyThrottle(_DynamicRateIpThrottle):
    scope = "public_applicant_verify"


