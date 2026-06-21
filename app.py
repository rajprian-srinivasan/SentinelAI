import time
import random
import json
from datetime import datetime

LOG_FILE = "app_system.log"

ERROR_TEMPLATES = [
    {
        "severity": "CRITICAL",
        "event_name": "DATABASE_CONNECTION_TIMEOUT",
        "message": "OperationalError: database connection lost. Timeout after 30000ms."
    },
    {
        "severity": "CRITICAL",
        "event_name": "API_GATEWAY_FAILURE",
        "message": "HTTP 504 Gateway Timeout: Upstream authentication server failed to respond."
    },
    {
        "severity": "CRITICAL",
        "event_name": "STATE_PROCESSING_EXCEPTION",
        "message": "ZeroDivisionError: division by zero in metric calculation."
    }
]

def generate_background_logs():
    print("Starting Bug Simulator. Generating traffic...")
    event_id = 1000
    while True:
        timestamp = datetime.utcnow().isoformat() + "Z"
        event_id += 1
        
        if random.random() > 0.20:
            log_entry = {
                "timestamp": timestamp,
                "event_id": event_id,
                "severity": "INFO",
                "event_name": "API_REQUEST_SUCCESSFUL",
                "message": "HTTP 200 OK. Processed secure payload checkout routine."
            }
        else:
            template = random.choice(ERROR_TEMPLATES)
            log_entry = {
                "timestamp": timestamp,
                "event_id": event_id,
                "severity": template["severity"],
                "event_name": template["event_name"],
                "message": template["message"]
            }
            
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        time.sleep(2)

if __name__ == "__main__":
    try:
        generate_background_logs()
    except KeyboardInterrupt:
        print("Bug Simulator stopped by user.")