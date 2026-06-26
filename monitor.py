import os
import time
import json
import ai_agent

LOG_FILE = "app_system.log"
TARGET_FILE = "app.py"

def execute_remediation(corrected_code: str, original_code_backup: str):
    print(f"\n[Executor] Overwriting '{TARGET_FILE}' directly with the AI fix...")
    try:
        if not corrected_code or "AI Analysis failed" in corrected_code:
            raise ValueError("Invalid code received from AI agent.")
            
        compile(corrected_code, TARGET_FILE, "exec")
        
        with open(TARGET_FILE, "w") as src_file:
            src_file.write(corrected_code)
        print("[Executor] Self-healing complete! app.py has been modified directly on disk.")
        
    except Exception as e:
        print(f"[Executor ERROR] AI patch failed validation: {str(e)}. Restoring backup...")
        with open(TARGET_FILE, "w") as src_file:
            src_file.write(original_code_backup)

def monitor_logs():
    print("Starting autonomous log monitoring...")

    if not os.path.exists(LOG_FILE):
        print(f"Log file {LOG_FILE} is waiting to be initialized.")
        while not os.path.exists(LOG_FILE):
            time.sleep(1)
            
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
        monitor_logs()
    except KeyboardInterrupt:
        print("\nAutonomous Monitor stopped by user.")