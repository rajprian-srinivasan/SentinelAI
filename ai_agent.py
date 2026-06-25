import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def analyze_system_error(log_entry: dict) -> str:
    print(f"\n[AI Agent] Analyzing system failure: {log_entry.get('event_name')}...")

    system_prompt = (
        "You are an automated Site Reliability Engineering (SRE) autonomous agent. "
        "Your task is to review a critical system log and generate a raw Python script "
        "that will programmatically fix the underlying bug in the application source code.\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. Output ONLY executable Python code.\n"
        "2. Do NOT wrap the code in markdown code blocks like ```python ... ```.\n"
        "3. Do NOT include any introductory text, markdown, explanation, or commentary.\n"
        "4. Your code should open the target file, locate the bug, modify the line safely, and save it back."
    )
    
    user_content = (
        f"CRITICAL LOG FOR REPAIR:\n"
        f"Target File: app.py\n"
        f"Event Name: {log_entry.get('event_name')}\n"
        f"Message: {log_entry.get('message')}\n\n"
        f"Generate the raw Python script to fix the code in app.py to prevent this error from happening again."
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