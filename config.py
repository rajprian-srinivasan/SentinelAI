import os
import sys


LOG_FILE = "app_system.log"
AUDIT_FILE = "remediation_audit.json"
COOLDOWN_WINDOW = 30  


TARGET_FILE = os.getenv("TARGET_FILE", "app.py")
TEMP_FILE = f"{TARGET_FILE}.tmp"
BASE_NAME, _ = os.path.splitext(TARGET_FILE)


OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DRY_RUN = False


LANGUAGE_PROFILES = {
    ".py": {
        "name": "Python",
        "comment": "#",
        "run": ["python3", TARGET_FILE],
        "validate": ["python3", "-m", "py_compile", TEMP_FILE]
    },
    ".js": {
        "name": "Node.js / JavaScript",
        "comment": "//",
        "run": ["node", TARGET_FILE],
        "validate": ["node", "--check", TEMP_FILE]
    },
    ".ts": {
        "name": "TypeScript",
        "comment": "//",
        "run": ["npx", "ts-node", TARGET_FILE],
        "validate": ["npx", "tsc", "--noEmit", TEMP_FILE]
    },
    ".go": {
        "name": "Go",
        "comment": "//",
        "run": ["go", "run", TARGET_FILE],
        "validate": ["go", "vet", TEMP_FILE]
    },
    ".java": {
        "name": "Java",
        "comment": "//",
        "run": ["java", TARGET_FILE],
        "validate": ["javac", TEMP_FILE]
    },
    ".cpp": {
        "name": "C++",
        "comment": "//",
        "run": [f"./{BASE_NAME}"],
        "validate": ["g++", "-fsyntax-only", TEMP_FILE]
    },
    ".c": {
        "name": "C",
        "comment": "//",
        "run": [f"./{BASE_NAME}"],
        "validate": ["gcc", "-fsyntax-only", TEMP_FILE]
    },
    ".rs": {
        "name": "Rust",
        "comment": "///",
        "run": [f"./{BASE_NAME}"],
        "validate": ["rustc", "--gated-syntax-check", TEMP_FILE]
    },
    ".cs": {
        "name": "C#",
        "comment": "//",
        "run": ["dotnet", "run"],
        "validate": ["dotnet", "build", "--no-incremental"]
    },
    ".sh": {
        "name": "Shell / Bash",
        "comment": "#",
        "run": ["bash", TARGET_FILE],
        "validate": ["bash", "-n", TEMP_FILE]
    },
    ".rb": {
        "name": "Ruby",
        "comment": "#",
        "run": ["ruby", TARGET_FILE],
        "validate": ["ruby", "-c", TEMP_FILE]
    },
    ".php": {
        "name": "PHP",
        "comment": "//",
        "run": ["php", TARGET_FILE],
        "validate": ["php", "-l", TEMP_FILE]
    }
}


_, ext = os.path.splitext(TARGET_FILE)
profile = LANGUAGE_PROFILES.get(ext)

if not profile:
    print(f"[WARN] Target file extension '{ext}' not in strict matrix. Falling back to default Python profile.")
    profile = LANGUAGE_PROFILES[".py"]

RUN_COMMAND = profile["run"]
VALIDATE_COMMAND = profile["validate"]