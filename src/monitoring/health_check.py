import threading
import time
import logging
from typing import Dict, List, Callable, Optional

logger = logging.getLogger(__name__)

class HealthCheckManager:
    def __init__(self, check_interval: float = 10.0):
        self.check_interval = check_interval
        self.services: Dict[str, Callable[[], bool]] = {}
        self.health_status: Dict[str, bool] = {}
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def register_service(self, name: str, health_func: Callable[[], bool]):
        self.services[name] = health_func
        self.health_status[name] = True
        logger.info(f"Registered health check for {name}")

    def start(self):
        if self._thread is None:
            self._thread = threading.Thread(target=self._run_checks, daemon=True)
            self._thread.start()
            logger.info("Health check monitoring started.")

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()

    def _run_checks(self):
        while not self._stop_event.is_set():
            for name, check_func in self.services.items():
                try:
                    is_healthy = check_func()
                    if is_healthy != self.health_status[name]:
                        state = "HEALTHY" if is_healthy else "UNHEALTHY"
                        logger.warning(f"Health status changed for {name}: {state}")
                        self.health_status[name] = is_healthy
                except Exception as e:
                    logger.error(f"Health check failed for {name}: {e}")
                    self.health_status[name] = False
            
            time.sleep(self.check_interval)

    def is_service_healthy(self, name: str) -> bool:
        return self.health_status.get(name, False)
