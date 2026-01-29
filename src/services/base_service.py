from abc import ABC, abstractmethod
import logging
from typing import Any
from src.core.resilience.circuit_breaker import CircuitBreaker
from src.core.resilience.retry import retry_with_backoff
from src.monitoring.logger import app_logger

class BaseService(ABC):
    def __init__(self, name: str, retry_config: dict, cb_config: dict):
        self.name = name
        self.retry_config = retry_config
        self.circuit_breaker = CircuitBreaker(
            service_name=name,
            **cb_config
        )

    def execute(self, func_name: str, *args, **kwargs) -> Any:
        """Execute a service function with retry and circuit breaker logic."""
        func = getattr(self, f"_{func_name}")
        
        # Log CBA state before call
        app_logger.log_event(
            self.name, 
            "REQUEST_START", 
            {"circuit_state": self.circuit_breaker.state.value}
        )

        try:
            # We wrap the circuit breaker call INSIDE the retry logic.
            # This way, each retry attempt is governed by and informs the circuit breaker.
            # If the circuit breaker opens during retries, it will fail fast for subsequent attempts.
            
            def attempt_with_cb():
                return self.circuit_breaker.call(lambda: func(*args, **kwargs))

            result = retry_with_backoff(
                func=attempt_with_cb,
                service_name=self.name,
                **self.retry_config
            )
            
            app_logger.log_event(
                self.name, 
                "REQUEST_SUCCESS", 
                {"circuit_state": self.circuit_breaker.state.value}
            )
            return result

        except Exception as e:
            app_logger.log_event(
                self.name, 
                "REQUEST_FAILURE", 
                {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "circuit_state": self.circuit_breaker.state.value
                }
            )
            raise e

    @abstractmethod
    def health_check(self) -> bool:
        pass
