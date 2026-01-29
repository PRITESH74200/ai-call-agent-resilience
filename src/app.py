import time
import logging
from typing import List, Dict, Any
from src.services.elevenlabs_service import ElevenLabsService
from src.services.llm_service import LLMService
from src.monitoring.health_check import HealthCheckManager
from src.monitoring.alerts import alerts
from src.monitoring.logger import app_logger
from src.core.exceptions import AppError, TransientError, PermanentError
from src.core.resilience.circuit_breaker import CircuitBreakerOpenError

logger = logging.getLogger(__name__)

class AICallAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize Services
        self.eleven_labs = ElevenLabsService(
            retry_config=config['services']['eleven_labs']['retry'],
            cb_config=config['services']['eleven_labs']['circuit_breaker']
        )
        self.llm = LLMService(
            retry_config=config['services']['llm']['retry'],
            cb_config=config['services']['llm']['circuit_breaker']
        )
        
        # Initialize Health Monitoring
        self.health_manager = HealthCheckManager(check_interval=5.0)
        self.health_manager.register_service("ElevenLabs", self.eleven_labs.health_check)
        self.health_manager.register_service("LLMProvider", self.llm.health_check)
        
        # Register alerting for CB state changes
        self.eleven_labs.circuit_breaker.on_state_change = self._handle_cb_state_change
        self.llm.circuit_breaker.on_state_change = self._handle_cb_state_change

    def _handle_cb_state_change(self, service_name: str, state: Any):
        if state.value == "OPEN":
            alerts.send_alert(
                f"Circuit Breaker OPEN for {service_name}",
                f"The service {service_name} has hit the failure threshold and is now disabled.",
                severity="CRITICAL"
            )
        elif state.value == "CLOSED":
            alerts.send_alert(
                f"Circuit Breaker CLOSED for {service_name}",
                f"The service {service_name} has recovered.",
                severity="INFO"
            )

    def start(self):
        self.health_manager.start()
        logger.info("AI Call Agent Started")

    def stop(self):
        self.health_manager.stop()
        logger.info("AI Call Agent Stopped")

    def process_call_queue(self, contacts: List[str]):
        logger.info(f"Starting to process {len(contacts)} contacts...")
        for contact in contacts:
            try:
                self.process_single_call(contact)
            except Exception as e:
                logger.error(f"Critical failure processing call for {contact}: {e}")
                # Graceful degradation: Move to next contact in queue
                logger.info(f"Skipping contact {contact} and moving to next...")

    def process_single_call(self, contact_name: str):
        logger.info(f"--- Processing Call for: {contact_name} ---")
        
        try:
            # 1. Get LLM Response
            response_text = self.llm.get_response(f"Hello {contact_name}")
            logger.info(f"LLM Response: {response_text}")
            
            # 2. Generate Speech
            audio = self.eleven_labs.generate_speech(response_text)
            logger.info(f"Audio Generated: {audio}")
            
            logger.info(f"Call successfully completed for {contact_name}")
            
        except CircuitBreakerOpenError as e:
            logger.warning(f"Service unavailable due to open circuit: {e}")
            alerts.send_alert("Call Blocked", f"Circuit is open. Skipping call for {contact_name}", severity="WARNING")
            raise e
        except PermanentError as e:
            logger.error(f"Permanent error for {contact_name}: {e}")
            alerts.send_alert("Permanent Call Failure", f"Call for {contact_name} failed permanently: {e}")
            raise e
        except TransientError as e:
            # If it reaches here, retries have failed
            logger.error(f"Transient error persisted after retries for {contact_name}: {e}")
            alerts.send_alert("Call Failed after Retries", f"Service issues prevented call for {contact_name}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise e
