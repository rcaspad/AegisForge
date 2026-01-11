import logging
from typing import Any, List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_core.messages import BaseMessage

try:
    # google.api_core is used by langchain-google-genai exceptions
    from google.api_core.exceptions import ResourceExhausted
    RETRIABLE_EXCEPTIONS = (ResourceExhausted, Exception)
except Exception as e:
    logging.warning(f"ResourceExhausted import failed: {e}")
    RETRIABLE_EXCEPTIONS = (Exception,)

logger = logging.getLogger(__name__)


def _log_retry(retry_state):
    logger.warning(
        "LLM invoke retry %s due to %s",
        retry_state.attempt_number,
        getattr(retry_state.outcome, "exception", lambda: None)(),
    )


def _default_wait():
    return wait_exponential(multiplier=1, min=1, max=16)


def _default_stop():
    return stop_after_attempt(3)


@retry(
    wait=_default_wait(),
    stop=_default_stop(),
    retry=retry_if_exception_type(RETRIABLE_EXCEPTIONS),
    reraise=True,
    after=_log_retry,
)
def invoke_with_retry(model: Any, messages: List[BaseMessage]):
    """Invoke LangChain chat model with retries and exponential backoff."""
    return model.invoke(messages)
