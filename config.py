import os
import sys

LOG_FILE = "app_system.log"
AUDIT_FILE = "remediation_audit.json"
COOLDOWN_WINDOW = 30  

TARGET_FILE = "app.py" 
TEMP_FILE = f"{TARGET_FILE}.tmp"
BASE_NAME, _ = os.path.splitext(TARGET_FILE)

LANGUAGE_PROFILES = {
    ".py": {
        "run": ["python3", TARGET_FILE],
        "validate": ["python3", "-m", "py_compile", TEMP_FILE]
    },
    ".js": {
        "run": ["node", TARGET_FILE],
        "validate": ["node", "--check", TEMP_FILE]
    },
    ".java": {
        "run": ["java", TARGET_FILE],
        "validate": ["javac", TEMP_FILE]
    },
    ".cpp": {
        "run": [f"./{BASE_NAME}"],
        "validate": ["g++", "-fsyntax-only", TEMP_FILE]
    },
    ".c": {
        "run": [f"./{BASE_NAME}"],
        "validate": ["gcc", "-fsyntax-only", TEMP_FILE]
    },
    ".go": {
        "run": ["go", "run", TARGET_FILE],
        "validate": ["go", "vet", TEMP_FILE]
    },
    ".rs": {
        "run": [f"./{BASE_NAME}"],
        "validate": ["rustc", "--gated-syntax-check", TEMP_FILE]
    },
    ".cs": {
        "run": ["dotnet", "run"],
        "validate": ["dotnet", "build", "--no-incremental"]
    }
}

_, ext = os.path.splitext(TARGET_FILE)
profile = LANGUAGE_PROFILES.get(ext)

if not profile:
    print(f"[FATAL] Unsupported file type extension '{ext}'. Engine shutting down.")
    sys.exit(1)

RUN_COMMAND = profile["run"]
VALIDATE_COMMAND = profile["validate"]