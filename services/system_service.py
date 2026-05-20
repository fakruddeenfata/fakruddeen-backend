import os
import subprocess
import platform

class SystemService:
    def __init__(self):
        self.os_type = platform.system().lower()

    def open_application(self, app_name: str):
        """Open an application based on OS"""
        try:
            if self.os_type == "windows":
                subprocess.Popen(["start", app_name], shell=True)
            elif self.os_type == "darwin":  # macOS
                subprocess.Popen(["open", "-a", app_name])
            elif self.os_type == "linux":
                subprocess.Popen([app_name])
            return {"status": "success", "message": f"{app_name} opened"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def run_command(self, command: str):
        """Run a system command"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return {"status": "success", "output": result.stdout}
        except Exception as e:
            return {"status": "error", "message": str(e)}
