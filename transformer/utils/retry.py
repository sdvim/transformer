import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from transformer.config import settings
from transformer.utils.errors import TransientError


def create_retry_decorator():
    """Create a retry decorator with configured settings."""
    return retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=settings.retry_backoff_multiplier, min=4, max=10),
        retry=retry_if_exception_type((TransientError, httpx.TimeoutException, httpx.ConnectError)),
    )
