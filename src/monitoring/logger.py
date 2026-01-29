import logging
import json
import datetime
import os
from typing import Dict, Any

class StructuredLogger:
    def __init__(self, log_file: str = "app_logs.json"):
        self.log_file = log_file
        self._setup_logger()

    def _setup_logger(self):
        # Configure standard logging to console and file
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("app.log", mode='a')
            ]
        )

    def log_event(self, service_name: str, event_type: str, data: Dict[str, Any]):
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "service_name": service_name,
            "event_type": event_type,
            **data
        }
        
        # Log to structured local file
        self._write_to_file(log_entry)
        
        # Log to Google Sheets (Mock)
        self._mock_google_sheets_log(log_entry)

    def _write_to_file(self, entry: Dict[str, Any]):
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"Failed to write to log file: {e}")

    def _mock_google_sheets_log(self, entry: Dict[str, Any]):
        # In a real scenario, this would use google-api-python-client
        # We'll just print it for now to simulate the action
        print(f"[MOCK GOOGLE SHEETS] Logging: {entry.get('timestamp')} | {entry.get('service_name')} | {entry.get('event_type')}")

# Global instance
app_logger = StructuredLogger()
