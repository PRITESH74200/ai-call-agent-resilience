import time
import random
import logging
from typing import Callable, Type, Tuple, Any
from src.core.exceptions import TransientError

logger = logging.getLogger(__name__)

def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = (TransientError,),
    service_name: str = "Unknown"
) -> Any:
    """
    Retry a function with exponential backoff.
    
    Args:
        func: The function to execute.
        max_retries: Maximum number of retry attempts.
        initial_delay: Starting delay in seconds.
        backoff_factor: Multiplier for the delay after each failure.
        retryable_exceptions: Exceptions that trigger a retry.
        service_name: Name of the service for logging.
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return func()
        except retryable_exceptions as e:
            last_exception = e
            if attempt == max_retries:
                logger.error(f"Service {service_name} failed after {max_retries} retries. Final error: {str(e)}")
                raise e
            
            # Add some jitter to avoid thundering herd if multiple instances retry at same time
            jitter = random.uniform(0, 0.1 * delay)
            sleep_time = delay + jitter
            
            logger.warning(
                f"Attempt {attempt + 1} for {service_name} failed: {str(e)}. "
                f"Retrying in {sleep_time:.2f} seconds..."
            )
            
            time.sleep(sleep_time)
            delay *= backoff_factor
        except Exception as e:
            # Permanent errors or non-retryable exceptions skip retries
            logger.error(f"Non-retryable error in {service_name}: {str(e)}")
            raise e

    raise last_exception
