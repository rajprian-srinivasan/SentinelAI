import os
from openai import OpenAI
from dotenv import load_dotenv
import config

load_dotenv()
client = OpenAI()

def analyze_system_error(payload: dict) -> str:
    # Safely handle both structured logs and plain text string logs from the UI
    raw_log = payload.get("log", {})
    if isinstance(raw_log, dict):
        event_name = raw_log.get("event_name", "Interactive Incident")
        message = raw_log.get("message", "User Submitted Error Log")
        timestamp = raw_log.get("timestamp", "N/A")
    else:
        event_name = "Interactive UI Submission"
        message = str(raw_log)
        timestamp = "N/A"

    current_source_code = payload.get("source_code", "")

    print(f"\n[AI Agent] Analyzing system failure using {config.OPENAI_MODEL}...")

    target_filename = config.TARGET_FILE if os.path.exists(config.TARGET_FILE) else "user_submission.py"
    _, ext = os.path.splitext(target_filename)
    if ext in [".js", ".java", ".cpp", ".c", ".cs", ".go"]:
        comment_char = "//"
    elif ext in [".rs"]:
        comment_char = "///"
    else:
        comment_char = "#"

    system_prompt = (
        "You are an automated Site Reliability Engineering (SRE) autonomous agent.\n"
        f"Your task is to review a critical system log alongside the application's current source code ({target_filename}), "
        "fix the bug, and output the entire, corrected source code file.\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        f"1. At the absolute TOP of the file, you MUST include a comment block (using '{comment_char}' syntax) acting as an Incident Report. "
        "It must explicitly state:\n"
        f"   {comment_char} [AUTONOMOUS HEALING REPORT]\n"
        f"   {comment_char} TIMESTAMP: [Insert event timestamp]\n"
        f"   {comment_char} INTERCEPTED ERROR: [State the raw error message]\n"
        f"   {comment_char} ROOT CAUSE ANALYSIS: [Explain why it happened in 1-2 clear sentences]\n"
        f"   {comment_char} LINE NUMBER: [Insert the line number where the code was modified]\n"
        f"   {comment_char} REMEDIATION DEPLOYED: [Explain how your code fix resolves the issue]\n"
        f"2. Output ONLY the raw, executable code containing this header comment and the rest of the script.\n"
        "3. Do NOT wrap the file in markdown code blocks like ```python or ```javascript.\n"
        "4. Do NOT include conversational text outside of the code file."
    )
    
    user_content = (
        f"CRITICAL LOG FOR REPAIR:\n"
        f"Event Name: {event_name}\n"
        f"Message: {message}\n"
        f"Timestamp: {timestamp}\n\n"
        f"CURRENT SOURCE CODE OF {target_filename.upper()}:\n"
        f"----------------------------------------\n"
        f"{current_source_code}\n"
        f"----------------------------------------\n\n"
        f"Generate the full, updated source code for {target_filename} with the explanation header and the code fix applied."
    )

    try:
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.0
        )
        
        usage = response.usage
        print(f"[Cost Control] Tokens Used -> Prompt: {usage.prompt_tokens} | Completion: {usage.completion_tokens} | Total: {usage.total_tokens}")
        
        patched_code = response.choices[0].message.content.strip()

        # Extra safety check to strip markdown block ticks if LLM includes them
        if patched_code.startswith("```"):
            lines = patched_code.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            patched_code = "\n".join(lines).strip()

        return patched_code
    except Exception as e:
        return f"AI Analysis failed due to an error: {str(e)}"