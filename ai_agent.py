import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def analyze_system_error(log_entry: dict) -> str:
    print(f"\n[AI Agent] Analyzing system failure: {log_entry.get('event_name')}...")

    system_prompt = (
        "You are an automated Site Reliability Engineering (SRE) autonomous agent. "
        "Your job is to analyze incoming critical system logs, diagnose the root cause, "
        "and provide a concise recommendation for an automated fix."
    )
    
    user_content = (
        f"CRITICAL LOG INTERCEPTED:\n"
        f"Event ID: {log_entry.get('event_id')}\n"
        f"Event Name: {log_entry.get('event_name')}\n"
        f"Severity: {log_entry.get('severity')}\n"
        f"Message: {log_entry.get('message')}\n"
        f"Timestamp: {log_entry.get('timestamp')}\n\n"
        f"Please provide a 2-3 sentence analysis of the failure and state the immediate remediation step required."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Analysis failed due to an error: {str(e)}"

if __name__ == "__main__":
    mock_log = {
        "event_id": 999,
        "event_name": "MOCK_DISK_SPACE_EXHAUSTED",
        "severity": "CRITICAL",
        "message": "Partition /var/log is at 99% capacity. Write operations suspended.",
        "timestamp": "2026-06-23T12:00:00Z"
    }
    print("Running quick standalone AI test...")
    analysis = analyze_system_error(mock_log)
    print("\n=== AI Analysis Result ===")
    print(analysis)