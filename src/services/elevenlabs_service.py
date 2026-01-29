import random
from src.services.base_service import BaseService
from src.core.exceptions import ServiceUnavailableError, PermanentError

class ElevenLabsService(BaseService):
    def __init__(self, retry_config: dict, cb_config: dict):
        super().__init__("ElevenLabs", retry_config, cb_config)
        self.is_down = False # For simulation

    def generate_speech(self, text: str):
        return self.execute("generate_speech_call", text)

    def _generate_speech_call(self, text: str):
        if self.is_down:
            raise ServiceUnavailableError("ElevenLabs is currently down (Simulated 503)", service_name=self.name)
        
        # Simulate occasional random failures
        if random.random() < 0.1:
            raise ServiceUnavailableError("Random ElevenLabs failure", service_name=self.name)
            
        return f"Speech audio for: {text}"

    def health_check(self) -> bool:
        return not self.is_down
