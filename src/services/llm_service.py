import random
from src.services.base_service import BaseService
from src.core.exceptions import ServiceTimeoutError, AuthenticationError

class LLMService(BaseService):
    def __init__(self, retry_config: dict, cb_config: dict):
        super().__init__("LLMProvider", retry_config, cb_config)
        self.is_down = False

    def get_response(self, prompt: str):
        return self.execute("get_response_call", prompt)

    def _get_response_call(self, prompt: str):
        if self.is_down:
            raise ServiceTimeoutError("LLM Provider timed out (Simulated)", service_name=self.name)
            
        return f"AI response to: {prompt}"

    def health_check(self) -> bool:
        return not self.is_down
