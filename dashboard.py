import os
import json
import config

def generate_report():
    print("==================================================")
    print("      SENTINEL AI SRE TELEMETRY DASHBOARD        ")
    print("==================================================")
    
    if not os.path.exists(config.AUDIT_FILE):
        print(f"\n[!] No telemetry data recorded yet. Run monitor.py to generate logs.")
        print("==================================================")
        return

    with open(config.AUDIT_FILE, "r") as f:
        try:
            records = json.load(f)
        except json.JSONDecodeError:
            print("\n[!] Telemetry audit file is corrupted or empty.")
            return

    total_incidents = len(records)
    successful_swaps = sum(1 for r in records if r["action_taken"] == "ATOMIC_SWAP_DEPLOYED")
    failed_compilations = sum(1 for r in records if not r["compiled_successfully"])
    
    success_rate = (successful_swaps / total_incidents) * 100 if total_incidents > 0 else 0
    
    error_counts = {}
    for r in records:
        err = r.get("error_type", "Unknown")
        error_counts[err] = error_counts.get(err, 0) + 1

    print(f"Total Intercepted Incidents : {total_incidents}")
    print(f"Successful Self-Heals       : {successful_swaps}")
    print(f"Failed AI Code Patches       : {failed_compilations}")
    print(f"System Recovery Success Rate: {success_rate:.1f}%")
    print("--------------------------------------------------")
    print("INCIDENT TYPE DISTRIBUTION:")
    for err_name, count in error_counts.items():
        print(f" - {err_name}: {count} incident(s)")
    print("==================================================")

if __name__ == "__main__":
    generate_report()