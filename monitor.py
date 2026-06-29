import os
import time
import json
import subprocess
from datetime import datetime, timezone
import ai_agent

TARGET_FILE = "app.py"
LOG_FILE = "app_system.log"

def get_last_critical_log():
    if not os.path.exists(LOG_FILE):
        return None
        
    critical_logs = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                log_data = json.loads(line)
                if log_data.get("severity") == "CRITICAL":
                    critical_logs.append(log_data)
            except json.JSONDecodeError:
                continue
                
    return critical_logs[-1] if critical_logs else None

def get_source_code():
    with open(TARGET_FILE, "r") as f:
        return f.read()

def run_pipeline():
    print("==================================================")
    print("[MONITOR] Starting SRE Autonomous Orchestrator...")
    print("==================================================")
    
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        
    app_process = subprocess.Popen(["python3", TARGET_FILE])
    print(f"[MONITOR] Subprocess spawned: {TARGET_FILE} (PID: {app_process.pid})")
    
    try:
        while True:
            time.sleep(1)
            
            if app_process.poll() is not None:
                print("[MONITOR] Warning: Target app stopped unexpectedly. Restarting...")
                app_process = subprocess.Popen(["python3", TARGET_FILE])
                continue

            last_crit = get_last_critical_log()
            if last_crit:
                print(f"\n[CRITICAL ALERT DETECTED]: {last_crit['message']}")
                print(f"[MONITOR] Freezing target process (PID: {app_process.pid})...")
                
                app_process.terminate()
                app_process.wait()
                
                source_code = get_source_code()
                error_context = last_crit["message"]
                
                print("[MONITOR] Querying AI agent for remediation patch...")
                fixed_code = ai_agent.generate_fix(source_code, error_context)
                
                if fixed_code:
                    print("[MONITOR] Patch received. Implementing Atomic Swap...")
                    
                    temp_file = f"{TARGET_FILE}.tmp"
                    with open(temp_file, "w") as f:
                        f.write(fixed_code)
                        
                    os.replace(temp_file, TARGET_FILE)
                    print("[MONITOR] Atomic file swap successful. Live code updated safely.")
                    
                    if os.path.exists(LOG_FILE):
                        os.remove(LOG_FILE)
                        
                    print("[MONITOR] Rebooting microservice with deployed fix...")
                    app_process = subprocess.Popen(["python3", TARGET_FILE])
                else:
                    print("[MONITOR] Error: AI agent failed to provide a valid code patch. Retrying...")
                    app_process = subprocess.Popen(["python3", TARGET_FILE])
                    
    except KeyboardInterrupt:
        print("\n[MONITOR] Shutting down orchestrator loop.")
        if app_process.poll() is None:
            app_process.terminate()

if __name__ == "__main__":
    run_pipeline()