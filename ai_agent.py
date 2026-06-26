import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def analyze_system_error(payload: dict) -> str:
    log_entry = payload.get("log", {})
    current_source_code = payload.get("source_code", "")

    print(f"\n[AI Agent] Analyzing system failure: {log_entry.get('event_name')}...")

    system_prompt = (
        "You are an automated Site Reliability Engineering (SRE) autonomous agent.\n"
        "Your task is to review a critical system log alongside the application's current source code, "
        "fix the bug, and output the entire, corrected source code file.\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. At the absolute TOP of the file, you MUST include a Python comment block acting as an Incident Report. "
        "It must explicitly state:\n"
        "   # [AUTONOMOUS HEALING REPORT]\n"
        "   # TIMESTAMP: [Insert event timestamp]\n"
        "   # INTERCEPTED ERROR: [State the raw error message]\n"
        "   # ROOT CAUSE ANALYSIS: [Explain why it happened in 1-2 clear sentences]\n"
        "   # REMEDIATION DEPLOYED: [Explain how your code fix resolves the issue]\n"
        "   # LINE NUMBER: [Insert the line number of the error]\n"
        "2. Output ONLY the raw, executable Python code containing this header comment and the rest of the script.\n"
        "3. Do NOT wrap the file in markdown code blocks like ```python ... ```.\n"
        "4. Do NOT include conversational text outside of the Python code file."
    )
    
    user_content = (
        f"CRITICAL LOG FOR REPAIR:\n"
        f"Event Name: {log_entry.get('event_name')}\n"
        f"Message: {log_entry.get('message')}\n"
        f"Timestamp: {log_entry.get('timestamp')}\n\n"
        f"CURRENT SOURCE CODE OF APP.PY:\n"
        f"----------------------------------------\n"
        f"{current_source_code}\n"
        f"----------------------------------------\n\n"
        f"Generate the full, updated source code for app.py with the explanation header and the code fix applied."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Analysis failed due to an error: {str(e)}"