import os
from openai import OpenAI
from dotenv import load_dotenv
import config

load_dotenv()
client = OpenAI()


def get_comment_syntax(language_or_file: str) -> str:
    val = str(language_or_file).lower()
    
    if val in ['rust', 'rs', '.rs']:
        return '///'
    elif val in ['nodejs', 'javascript', 'go', 'java', 'cpp', 'csharp', 'js', 'go', 'java', 'cpp', 'cs', '.js', '.go', '.java', '.cpp', '.cs']:
        return '//'
    else:
        return '#'


def analyze_system_error(error_payload) -> str:
    if isinstance(error_payload, dict):
        log_data = error_payload.get("log", {})
        if isinstance(log_data, dict):
            event_name = log_data.get("event_name", "Interactive Incident")
            error_msg = log_data.get("message", "User Submitted Error Log")
            timestamp = log_data.get("timestamp", "N/A")
        else:
            event_name = "Interactive UI Submission"
            error_msg = str(log_data)
            timestamp = "N/A"

        source_code = error_payload.get("source_code", "")
        language = error_payload.get("language", "")
    else:
        event_name = "RAW_INTERCEPT"
        error_msg = str(error_payload)
        timestamp = "N/A"
        source_code = ""
        language = "python"

    if not language:
        target_file = config.TARGET_FILE if os.path.exists(config.TARGET_FILE) else "user_submission.py"
        _, ext = os.path.splitext(target_file)
        language = ext if ext else "python"

    comment_char = get_comment_syntax(language)

    print(f"\n[AI Agent] Analyzing system failure using {config.OPENAI_MODEL} ({language})...")

    system_prompt = (
        "You are an automated Site Reliability Engineering (SRE) autonomous agent.\n"
        f"Your task is to review a critical system log alongside the application's source code ({language}), "
        "fix the bug, and output the entire, corrected source code file.\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        f"1. At the absolute TOP of the file, you MUST include a comment block (using '{comment_char}' syntax) acting as an Incident Report. "
        "It must explicitly state:\n"
        f"   {comment_char} [AUTONOMOUS HEALING REPORT]\n"
        f"   {comment_char} TIMESTAMP: {timestamp}\n"
        f"   {comment_char} INTERCEPTED ERROR: {error_msg}\n"
        f"   {comment_char} ROOT CAUSE ANALYSIS: [Explain why it happened in 1-2 clear sentences]\n"
        f"   {comment_char} LINE NUMBER: [Insert line number where the code was modified]\n"
        f"   {comment_char} REMEDIATION DEPLOYED: [Explain how your code fix resolves the issue]\n"
        f"2. Output ONLY the raw, executable code containing this header comment and the rest of the script.\n"
        f"3. Do NOT wrap the file in markdown code blocks like ```python or ```go.\n"
        f"4. Do NOT include conversational text outside of the code file."
    )

    user_content = (
        f"CRITICAL LOG FOR REPAIR:\n"
        f"Event Name: {event_name}\n"
        f"Message: {error_msg}\n"
        f"Timestamp: {timestamp}\n\n"
        f"CURRENT SOURCE CODE ({language}):\n"
        f"----------------------------------------\n"
        f"{source_code}\n"
        f"----------------------------------------\n\n"
        f"Generate the full, updated source code with the explanation header and code fix applied."
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

        if patched_code.startswith("```"):
            lines = patched_code.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            patched_code = "\n".join(lines).strip()

        return patched_code

    except Exception as e:
        return f"{comment_char} AI Analysis failed due to an error: {str(e)}"