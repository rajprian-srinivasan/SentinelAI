import os
import time
import json
import subprocess
import signal
import ai_agent
from datetime import datetime, timezone

LOG_FILE = "app_system.log"
TARGET_FILE = "app.py"
TEMP_FILE = "app.py.tmp"

app_process = None

def start_application():
    global app_process
    print(f"[Orchestrator] Launching fresh instance of {TARGET_FILE}...")
    app_process = subprocess.Popen(["python3", TARGET_FILE])
    print(f"[Orchestrator] {TARGET_FILE} running under PID: {app_process.pid}")

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
                
        compile(clean_code, TARGET_FILE, "exec")
        audit_record["compiled_successfully"] = True
        
        if app_process and app_process.poll() is None:
            print(f"[Executor] Terminating old process (PID: {app_process.pid})...")
            app_process.terminate()
            app_process.wait()
        
        with open(TEMP_FILE, "w") as tmp_file:
            tmp_file.write(clean_code)
            
        os.replace(TEMP_FILE, TARGET_FILE)
        print("[Executor] Self-healing complete! app.py has been atomically swapped on disk.")
        
        audit_record["action_taken"] = "ATOMIC_SWAP_DEPLOYED"
        start_application()
        
    except Exception as e:
        print(f"[Executor ERROR] AI patch failed validation: {str(e)}. Restoring backup...")
        audit_record["compiled_successfully"] = False
        audit_record["action_taken"] = "ROLLBACK_TO_BACKUP"
        
        if os.path.exists(TEMP_FILE):
            os.remove(TEMP_FILE)
            
        with open(TARGET_FILE, "w") as src_file:
            src_file.write(original_code_backup)
            
        if app_process and app_process.poll() is not None:
            start_application()
            
    finally:
        audit_log_file = "remediation_audit.json"
        records = []
        if os.path.exists(audit_log_file):
            try:
                with open(audit_log_file, "r") as rf:
                    records = json.load(rf)
            except json.JSONDecodeError:
                records = []
                
        records.append(audit_record)
        with open(audit_log_file, "w") as wf:
            json.dump(records, wf, indent=4)

def monitor_logs():
    print("Starting autonomous log monitoring & orchestration...")

    if not os.path.exists(LOG_FILE):
        print(f"Log file {LOG_FILE} is waiting to be initialized.")
        start_application()
        
    with open(LOG_FILE, "r") as file:
        file.seek(0, 2)
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)
                continue
            try:
                log_entry = json.loads(line)
                if log_entry.get("severity") == "CRITICAL":
                    print("\n" + "="*50)
                    print(f"[ALARM] Intercepted {log_entry['event_name']}!")
                    print(f"   Timestamp: {log_entry.get('timestamp')}")
                    print(f"   Message:   {log_entry.get('message')}")
                    print(f"   Status:    SRE Agent is generating code patch now...")
                    print("="*50)
                    
                    source_code_context = ""
                    if os.path.exists(TARGET_FILE):
                        with open(TARGET_FILE, "r") as src:
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
                print(f"Error parsing log entry: {line}")

if __name__ == "__main__":
    try:
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w") as f:
                pass
        
        if app_process is None:
            start_application()
            
        monitor_logs()
    except KeyboardInterrupt:
        print("\n[Orchestrator] Stopping monitor and shutting down child processes...")
        if app_process and app_process.poll() is None:
            app_process.terminate()
        if os.path.exists(TEMP_FILE):
            os.remove(TEMP_FILE)
        print("System stopped cleanly.")