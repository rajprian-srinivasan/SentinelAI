import os
import time
import json
import subprocess
import shutil
import signal
from datetime import datetime
import ai_agent
import config

app_process = None
LAST_HEAL_TIMES = {}

def start_application():
    global app_process
    print(f"[Orchestrator] Launching instance via command: {config.RUN_COMMAND}...")
    app_process = subprocess.Popen(config.RUN_COMMAND, start_new_session=True)
    print(f"[Orchestrator] Application running under PID: {app_process.pid} (New Process Group)")

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
        print("[Sandbox] Step 1: Running language syntax validation...")
        syntax_check = subprocess.run(
            config.VALIDATE_COMMAND,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        if syntax_check.returncode != 0:
            print(f"[Sandbox ERROR] Syntax check failed:\n{syntax_check.stderr}")
            return False
            
        print("[Sandbox] Step 2: Running live 3-second application smoke test...")
        
        sandbox_command = list(config.RUN_COMMAND)
        if config.TARGET_FILE in sandbox_command:
            idx = sandbox_command.index(config.TARGET_FILE)
            sandbox_command[idx] = config.TEMP_FILE
            
        initial_log_size = os.path.getsize(config.LOG_FILE) if os.path.exists(config.LOG_FILE) else 0
        
        sandbox_process = subprocess.Popen(
            sandbox_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            sandbox_process.wait(timeout=3)
            print(f"[Sandbox ERROR] Application crashed instantly on boot with code {sandbox_process.returncode}")
            return False
        except subprocess.TimeoutExpired:
            print("[Sandbox] Application survived initial boot sequence window.")
            
            if os.path.exists(config.LOG_FILE):
                with open(config.LOG_FILE, "r") as f:
                    f.seek(initial_log_size)
                    for line in f:
                        try:
                            log_entry = json.loads(line)
                            if log_entry.get("severity") == "CRITICAL":
                                print(f"[Sandbox ERROR] App ran but threw a CRITICAL log: {log_entry.get('message')}")
                                sandbox_process.kill()
                                return False
                        except json.JSONDecodeError:
                            pass
            
            sandbox_process.terminate()
            try:
                sandbox_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                sandbox_process.kill()
                
            return True
            
    except Exception as e:
        print(f"[Sandbox ERROR] Validation pipeline runtime exception: {str(e)}")
        return False

def execute_remediation(corrected_code: str, original_code_backup: str):
    global app_process
    print(f"\n[Executor] Processing incoming patch...")
    
    if config.DRY_RUN:
        print("\n======================= [DRY RUN ACTIVE] =======================")
        print("The AI Agent proposed the following remediation patch:")
        print("----------------------------------------------------------------")
        print(sanitize_ai_output(corrected_code))
        print("----------------------------------------------------------------")
        print("[Dry Run] Skipping code deployment, sandbox testing, and service restart.")
        print("================================================================\n")
        return

    audit_record = {
        "timestamp": datetime.now().isoformat(),
        "error_type": "Unknown",
        "compiled_successfully": False,
        "action_taken": "None",
        "post_fix_verified": "Pending"
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
            raise SyntaxError("AI patch failed deep smoke test sandbox checks.")
            
        audit_record["compiled_successfully"] = True
        
        os.makedirs("patches", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.basename(config.TARGET_FILE)
        backup_path = f"patches/{timestamp}_pre_heal_{base_name}"
        with open(backup_path, "w") as backup_file:
            backup_file.write(original_code_backup)
        print(f"[Executor] Staged historical backup to {backup_path}")

        if app_process and app_process.poll() is None:
            print(f"[Executor] Terminating old process tree (PGID: {app_process.pid})...")
            try:
                os.killpg(os.getpgid(app_process.pid), signal.SIGTERM)
                app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"[Executor] Process tree ignored SIGTERM. Escalating to SIGKILL...")
                os.killpg(os.getpgid(app_process.pid), signal.SIGKILL)
                app_process.wait()
            except ProcessLookupError:
                pass
        
        os.replace(config.TEMP_FILE, config.TARGET_FILE)
        print(f"[Executor] Self-healing complete! {config.TARGET_FILE} atomically swapped.")
        
        audit_record["action_taken"] = "ATOMIC_SWAP_DEPLOYED"
        start_application()

        print("[Verification] Observing live production runtime for 10 seconds...")
        post_fix_success = True
        verification_start_log_size = os.path.getsize(config.LOG_FILE) if os.path.exists(config.LOG_FILE) else 0
        
        for _ in range(100):
            time.sleep(0.1)
            if app_process.poll() is not None:
                print(f"[Verification ERROR] Production application died during the post-fix window with exit code {app_process.returncode}")
                post_fix_success = False
                break
                
            if os.path.exists(config.LOG_FILE):
                with open(config.LOG_FILE, "r") as f:
                    f.seek(verification_start_log_size)
                    for line in f:
                        try:
                            log_entry = json.loads(line)
                            if log_entry.get("severity") == "CRITICAL":
                                print(f"[Verification ERROR] New CRITICAL incident detected: {log_entry.get('message')}")
                                post_fix_success = False
                                break
                        except json.JSONDecodeError:
                            pass
            if not post_fix_success:
                break

        if post_fix_success:
            print("[Verification SUCCESS] No recurring CRITICAL logs detected. Patch verified stable.")
            audit_record["post_fix_verified"] = "SUCCESS"
        else:
            print("[Verification FAILED] Patch did not resolve the underlying systemic failure. Triggering alert state...")
            audit_record["post_fix_verified"] = "FAILED"
        
    except Exception as e:
        print(f"[Executor ERROR] AI patch validation failed: {str(e)}. Rolling back...")
        audit_record["compiled_successfully"] = False
        audit_record["action_taken"] = "ROLLBACK_TO_BACKUP"
        audit_record["post_fix_verified"] = "SKIPPED_FAILED_VALIDATION"
        
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
            try:
                os.killpg(os.getpgid(app_process.pid), signal.SIGTERM)
                app_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(app_process.pid), signal.SIGKILL)
                app_process.wait()
            except ProcessLookupError:
                pass
        if os.path.exists(config.TEMP_FILE):
            os.remove(config.TEMP_FILE)
        print("System stopped cleanly.")