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
        
        total_requests = 500
        active_nodes = random.choice([5, 4, 2, 1, 0]) 
        
        try:
            node_load = total_requests / active_nodes
            
            log_entry = {
                "event_id": event_id,
                "severity": "INFO",
                "message": f"System processing healthy. Current average node load: {node_load:.2f}",
                "timestamp": timestamp
            }
        except ZeroDivisionError as e:
            log_entry = {
                "event_id": event_id,
                "event_name": "STATE_PROCESSING_EXCEPTION",
                "severity": "CRITICAL",
                "message": f"ZeroDivisionError: {str(e)} during system node load calculation balance step.",
                "timestamp": timestamp
            }
            
        with open(LOG_FILE, "a") as file:
            file.write(json.dumps(log_entry) + "\n")
            
        time.sleep(1)

if __name__ == "__main__":
    simulate_traffic()