import time
import json
import random
from datetime import datetime, timezone

LOG_FILE = "app_system.log"

def simulate_traffic():
    print("Traffic simulator active. Writing to logs...")
    event_id = 100

    while True:
        event_id += 1
        timestamp = datetime.now(timezone.utc).isoformat()
        failure_trigger = random.choice([0, 1, 2, 3, 4, 5])
        try:
            if failure_trigger == 0:
                active_nodes = 0
                node_load = 500 / active_nodes    
            
            elif failure_trigger == 1:
                system_config = {"host": "localhost", "port": 8080}
                token_auth = system_config["api_key"]
            
            else:
                log_entry = {
                    "event_id": event_id,
                    "severity": "INFO",
                    "event_name": "STATE_NORMAL",
                    "timestamp": timestamp,
                    "message": "System node health check reporting nominal status."
                }
                with open(LOG_FILE, "a") as f:
                    f.write(json.dumps(log_entry) + "\n")
                    
        except Exception as e:
            error_name = type(e).__name__
            log_entry = {
                "event_id": event_id,
                "severity": "CRITICAL",
                "event_name": "STATE_PROCESSING_EXCEPTION",
                "timestamp": timestamp,
                "message": f"{error_name}: {str(e)} during operational runtime execution step."
            }
            with open(LOG_FILE, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
            
            time.sleep(2)

        time.sleep(1)

if __name__ == "__main__":
    simulate_traffic()