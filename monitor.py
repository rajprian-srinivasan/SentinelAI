import os
import time
import json
import subprocess
import shutil
from datetime import datetime
import ai_agent
import config

app_process = None
LAST_HEAL_TIMES = {}

def start_application():
    global app_process
    print(f"[Orchestrator] Launching instance via command: {config.RUN_COMMAND}...")
    app_process = subprocess.Popen(config.RUN_COMMAND)
    print(f"[Orchestrator] Application running under PID: {app_process.pid}")

def sanitize_ai_output(raw_code: str) -> str:
    cleaned = raw_code.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned

def verify_code_behavior() -> bool:
    try:
        result = subprocess.run(
            config.VALIDATE_COMMAND,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("[Executor ERROR] Validation command timed out.")
        return False
    except Exception as e:
        print(f"[Executor ERROR] Structural validation failed: {str(e)}")
        return False

def execute_remediation(corrected_code: str, original_code_backup: str):
    global app_process
    print(f"\n[Executor] Processing incoming patch...")
    
    audit_record = {
        "timestamp": datetime.now().isoformat(),
        "error_type": "Unknown",
        "compiled_successfully": False,
        "action_taken": "None"
    }
    
    try:
        clean_code = sanitize_ai_output(corrected_code)
        if not clean_code or "AI Analysis failed" in clean_code:
            raise ValueError("Invalid or empty code received from AI agent.")
        
        for line in clean_code.splitlines():
            if "INTERCEPTED ERROR:" in line:
                audit_record["error_type"] = line.split(":", 1)[1].strip()
                break

        with open(config.TEMP_FILE, "w") as tmp_file:
            tmp_file.write(clean_code)

        if not verify_code_behavior():
            raise SyntaxError("AI patch failed language validation check.")
            
        audit_record["compiled_successfully"] = True
        
        if app_process and app_process.poll() is None:
            print(f"[Executor] Terminating old process (PID: {app_process.pid})...")
            app_process.terminate()
            try:
                app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"[Executor] Process ignored SIGTERM. Escalating to SIGKILL...")
                app_process.kill()
                app_process.wait()
        
        os.replace(config.TEMP_FILE, config.TARGET_FILE)
        print(f"[Executor] Self-healing complete! {config.TARGET_FILE} atomically swapped.")
        
        audit_record["action_taken"] = "ATOMIC_SWAP_DEPLOYED"
        start_application()
        
    except Exception as e:
        print(f"[Executor ERROR] AI patch validation failed: {str(e)}. Rolling back...")
        audit_record["compiled_successfully"] = False
        audit_record["action_taken"] = "ROLLBACK_TO_BACKUP"
        
        if os.path.exists(config.TEMP_FILE):
            os.remove(config.TEMP_FILE)
            
        with open(config.TARGET_FILE, "w") as src_file:
            src_file.write(original_code_backup)
            
        if app_process and app_process.poll() is not None:
            start_application()
            
    finally:
        records = []
        if os.path.exists(config.AUDIT_FILE):
            try:
                with open(config.AUDIT_FILE, "r") as rf:
                    records = json.load(rf)
            except json.JSONDecodeError:
                records = []
                
        records.append(audit_record)
        with open(config.AUDIT_FILE, "w") as wf:
            json.dump(records, wf, indent=4)

def monitor_logs():
    print("Starting autonomous log monitoring & orchestration...")
    
    with open(config.LOG_FILE, "r") as file:
        file.seek(0, 2)
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)
                continue
            try:
                log_entry = json.loads(line)
                if log_entry.get("severity") == "CRITICAL":
                    error_msg = log_entry.get("message", "")
                    current_time = time.time()
                    
                    if error_msg in LAST_HEAL_TIMES and (current_time - LAST_HEAL_TIMES[error_msg] < config.COOLDOWN_WINDOW):
                        print(f"\n[MONITOR] Rate-limiting active: Blocked duplicate AI payload call for error: '{error_msg}'")
                        continue
                        
                    LAST_HEAL_TIMES[error_msg] = current_time
                    
                    print("\n" + "="*50)
                    print(f"[ALARM] Intercepted {log_entry['event_name']}!")
                    print(f"   Message:   {error_msg}")
                    print("="*50)
                    
                    source_code_context = ""
                    if os.path.exists(config.TARGET_FILE):
                        with open(config.TARGET_FILE, "r") as src:
                            source_code_context = src.read()
                    
                    payload = {
                        "log": log_entry,
                        "source_code": source_code_context
                    }
                    
                    corrected_code = ai_agent.analyze_system_error(payload)
                    execute_remediation(corrected_code, source_code_context)
                    
                    print("\nMonitoring system resuming vigilance...")
                    print("-" * 50)
                else:
                    print(f"[Heartbeat] Event {log_entry.get('event_id')} parsed successfully.", end="\r")
            except json.JSONDecodeError:
                pass

if __name__ == "__main__":
    try:
        primary_runtime_executable = config.RUN_COMMAND[0]
        if not shutil.which(primary_runtime_executable):
            print(f"[FATAL CRITICAL ERROR] The configured executable '{primary_runtime_executable}' was not found in the system PATH.")
            print(f"Please check your environment installation or modify config.py to match your local setup.")
            exit(1)
            
        if not os.path.exists(config.LOG_FILE):
            with open(config.LOG_FILE, "w") as f:
                pass
        
        if app_process is None:
            start_application()
            
        monitor_logs()
    except KeyboardInterrupt:
        print("\n[Orchestrator] Shutting down child processes cleanly...")
        if app_process and app_process.poll() is None:
            app_process.terminate()
            try:
                app_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                app_process.kill()
        if os.path.exists(config.TEMP_FILE):
            os.remove(config.TEMP_FILE)
        print("System stopped cleanly.")