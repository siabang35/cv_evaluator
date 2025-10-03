from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from openai import RateLimitError, APIError, APITimeoutError
from app.config import settings


def create_llm_retry_decorator():
    """
    Create a retry decorator for LLM API calls with exponential backoff.
    
    Retries on:
    - Rate limit errors
    - API errors
    - Timeout errors
    
    Strategy:
    - Max 3 attempts
    - Exponential backoff: 2^x * 1 second (2s, 4s, 8s)
    """
    return retry(
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((RateLimitError, APIError, APITimeoutError)),
        reraise=True
    )


# Decorator instance
retry_llm_call = create_llm_retry_decorator()
