import os

LOG_FILE = "app_system.log"
TARGET_FILE = "app.py"
TEMP_FILE = "app.py.tmp"
AUDIT_FILE = "remediation_audit.json"


RUN_COMMAND = ["python3", TARGET_FILE]
VALIDATE_COMMAND = ["python3", "-m", "py_compile", TEMP_FILE]
COOLDOWN_WINDOW = 30