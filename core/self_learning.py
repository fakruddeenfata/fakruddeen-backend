import json
import os
from datetime import datetime

class SelfLearningEngine:
    def __init__(self, log_file="self_learning_log.json"):
        self.log_file = log_file
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

    def log_error(self, service: str, error_message: str):
        """Log errors for future learning"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "error": error_message
        }
        logs = self._read_logs()
        logs.append(entry)
        self._write_logs(logs)
        return {"status": "logged", "entry": entry}

    def suggest_improvement(self):
        """Suggest improvements based on logged errors"""
        logs = self._read_logs()
        suggestions = {}
        for log in logs:
            service = log["service"]
            if service not in suggestions:
                suggestions[service] = 0
            suggestions[service] += 1

        improvements = []
        for service, count in suggestions.items():
            if count > 3:
                improvements.append(f"Service '{service}' has {count} errors. Consider retraining or debugging.")
        return {"status": "success", "improvements": improvements}

    def _read_logs(self):
        with open(self.log_file, "r") as f:
            return json.load(f)

    def _write_logs(self, logs):
        with open(self.log_file, "w") as f:
            json.dump(logs, f, indent=4)
