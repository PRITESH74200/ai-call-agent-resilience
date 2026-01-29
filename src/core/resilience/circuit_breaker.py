import time
import logging
from enum import Enum
from typing import Callable, Any, Optional
from src.core.exceptions import TransientError, PermanentError

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreakerOpenError(Exception):
    """Raised when the circuit breaker is open."""
    pass

class CircuitBreaker:
    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 3,
        recovery_timeout: float = 30.0,
        on_state_change: Optional[Callable[[str, CircuitState], None]] = None
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.on_state_change = on_state_change
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None

    def _set_state(self, new_state: CircuitState):
        if self.state != new_state:
            logger.info(f"Circuit Breaker for {self.service_name} changed state: {self.state} -> {new_state}")
            self.state = new_state
            if self.on_state_change:
                self.on_state_change(self.service_name, new_state)

    def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self._set_state(CircuitState.HALF_OPEN)
            else:
                raise CircuitBreakerOpenError(f"Circuit Breaker for {self.service_name} is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except PermanentError:
            # Permanent errors don't trip the circuit breaker as they are usually client-side/logic issues
            # though some might argue they should if they indicate a major misconfiguration.
            # For this assignment, let's keep it to TransientErrors tripping the circuit.
            raise
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self._set_state(CircuitState.CLOSED)
        self.failure_count = 0

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
            self._set_state(CircuitState.OPEN)

    def get_status(self):
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time
        }
