import os
from openai import OpenAI
from dotenv import load_dotenv
import config

load_dotenv()
client = OpenAI()

def analyze_system_error(payload: dict) -> str:
    log_entry = payload.get("log", {})
    current_source_code = payload.get("source_code", "")

    print(f"\n[AI Agent] Analyzing system failure using {config.OPENAI_MODEL}...")

    _, ext = os.path.splitext(config.TARGET_FILE)
    if ext in [".js", ".java", ".cpp", ".c", ".cs", ".go"]:
        comment_char = "//"
    elif ext in [".rs"]:
        comment_char = "///"
    else:
        comment_char = "#"

    system_prompt = (
        "You are an automated Site Reliability Engineering (SRE) autonomous agent.\n"
        f"Your task is to review a critical system log alongside the application's current source code ({config.TARGET_FILE}), "
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
        f"Event Name: {log_entry.get('event_name')}\n"
        f"Message: {log_entry.get('message')}\n"
        f"Timestamp: {log_entry.get('timestamp')}\n\n"
        f"CURRENT SOURCE CODE OF {config.TARGET_FILE.upper()}:\n"
        f"----------------------------------------\n"
        f"{current_source_code}\n"
        f"----------------------------------------\n\n"
        f"Generate the full, updated source code for {config.TARGET_FILE} with the explanation header and the code fix applied."
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
        
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Analysis failed due to an error: {str(e)}"