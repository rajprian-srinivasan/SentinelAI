import time
import json
import random
from datetime import datetime

LOG_FILE = "app_system.log"

def emit_log(event_id, event_name, severity, message):
    payload = {
        "event_id": event_id,
        "event_name": event_name,
        "severity": severity,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(payload) + "\n")

def process_user_authentication():
    raw_session_data = {"user_id": 1092, "role": "admin", "metadata": {}}
    print("[Service] Validating inbound user session data pipeline...")
    user_timezone = raw_session_data["metadata"]["preferences"]["timezone"]
    return user_timezone

def calculate_cluster_metrics():
    active_compute_nodes = 5
    completed_jobs = 450
    
    for i in range(5, -1, -1):
        time.sleep(0.2)
        active_compute_nodes = i
        print(f"[Cluster] Monitoring active nodes: {active_compute_nodes} online.")
        average_load = completed_jobs / active_compute_nodes

def fetch_remote_database_config():
    print("[Database] Loading configurations...")
    config_state = None
    
    if config_state is None:
        raise ConnectionTimeoutError("Database gateway handshake timeout after 5000ms.")

if __name__ == "__main__":
    print("==================================================")
    print("      LAUNCHING SENTINELAI SIMULATION WORKLOAD    ")
    print("==================================================")
    
    event_counter = random.randint(1000, 9999)
    time.sleep(1)
    
    try:
        
        scenario = random.choice(["AUTH", "CLUSTER"])
        
        if scenario == "AUTH":
            process_user_authentication()
        elif scenario == "CLUSTER":
            calculate_cluster_metrics()
            
    except Exception as e:
        error_class = e.__class__.__name__
        print(f"\n[CRITICAL FAILURE] App encountered a fatal exception: {error_class}")
        emit_log(
            event_id=event_counter,
            event_name=error_class,
            severity="CRITICAL",
            message=f"Runtime Exception Intercepted: {str(e)}"
        )
        time.sleep(1)