import time,random
from src.llm.errors import UnifiedRateLimitError

def call_llm_with_retry(
    llm_call_fn,
    max_retries=3,
    base_delay=1.0,
    max_delay=30.0,
):
    for attempt in range(max_retries):
        try:
            result = llm_call_fn()
            if result is None:
                raise RuntimeError("LLM returned None")
            return result

        except UnifiedRateLimitError:
            if attempt == max_retries - 1:
                raise

            delay = min(
                max_delay,
                base_delay * (2 ** attempt)
            )
            jitter = random.uniform(0, delay * 0.1)

            time.sleep(delay + jitter)
