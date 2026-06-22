import os
import time
import json

LOG_FILE = "app_system.log"

def monitor_logs():
    print("Starting log monitoring...")

    if not os.path.exists(LOG_FILE):
        print(f"Log file {LOG_FILE} is waiting to be intialized.")
        while not os.pathl.exists(LOG_FILE):
            time.sleep(1)
    with open(LOG_FILE, "r") as file:
        file.seek(0,2)
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)
                continue
            try:
                log_entry = json.loads(line)
                if log_entry.get("severity") == "CRITICAL":
                    print(f"\n[ALARM] Intercepted {log_entry['event_name']}!")
                    print(f"   Message: {log_entry['message']}")
                    print(f"   Timestamp: {log_entry['timestamp']}")
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