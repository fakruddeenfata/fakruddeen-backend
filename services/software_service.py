import os

class SoftwareService:
    def __init__(self, base_dir="generated_software"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def create_software(self, filename: str, code: str):
        """Create a new software file with given code"""
        file_path = os.path.join(self.base_dir, filename)
        try:
            with open(file_path, "w") as f:
                f.write(code)
            return {"status": "success", "message": f"Software {filename} created", "path": file_path}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_generated(self):
        """List all generated software files"""
        try:
            files = os.listdir(self.base_dir)
            return {"status": "success", "files": files}
        except Exception as e:
            return {"status": "error", "message": str(e)}
