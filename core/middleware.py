"""Per-response diagnostics; no learner code or private data is logged."""
from time import perf_counter
from django.conf import settings
from django.utils.cache import patch_cache_control


class ResponseTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = perf_counter()
        response = self.get_response(request)
        timing = f'app;dur={(perf_counter() - start) * 1000:.2f}'
        previous = response.get('Server-Timing')
        response['Server-Timing'] = f'{previous}, {timing}' if previous else timing
        response['X-App-Revision'] = settings.APP_REVISION
        # WhiteNoise serves public static assets before this middleware.
        patch_cache_control(response, private=True, no_store=True)
        return response
