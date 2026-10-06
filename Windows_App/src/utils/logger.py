"""
Local Offline Audit Logger
Strictly logs actions locally on disk - No network or remote analytics.
"""

import os
import sys
import datetime

class AuditLogger:
    def __init__(self, log_dir: str = None):
        if log_dir is None:
            # Default to local app directory
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            log_dir = os.path.join(base_dir, "logs")
        
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, "offline_audit.log")

    def log(self, level: str, message: str):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level.upper()}] {message}\n"
        
        # Console output
        print(log_entry.strip())
        
        # Local secure disk output
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception:
            pass

    def info(self, message: str):
        self.log("INFO", message)

    def warning(self, message: str):
        self.log("WARNING", message)

    def error(self, message: str):
        self.log("ERROR", message)

    def security(self, message: str):
        self.log("SECURITY", message)

logger = AuditLogger()
