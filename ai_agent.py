import json
import os
from openai import OpenAI
import config

client = OpenAI(api_key=config.OPENAI_API_KEY)


def get_comment_syntax(language: str) -> str:
    lang = language.lower()
    if lang in ['python', 'py']:
        return '#'
    elif lang in ['rust', 'rs']:
        return '///'
    else:  # nodejs, go, java, cpp, csharp
        return '//'


def analyze_system_error(error_payload) -> str:
    if isinstance(error_payload, dict):
        log_data = error_payload.get("log", {})
        if isinstance(log_data, dict):
            event_name = log_data.get("event_name", "UNKNOWN_EVENT")
            error_msg = log_data.get("message", "No error log provided")
            timestamp = log_data.get("timestamp", "NOW")
        else:
            event_name = "LOG_EVENT"
            error_msg = str(log_data)
            timestamp = "NOW"

        source_code = error_payload.get("source_code", "")
        language = error_payload.get("language", "python")
    else:
        event_name = "RAW_INTERCEPT"
        error_msg = str(error_payload)
        timestamp = "NOW"
        source_code = ""
        language = "python"

    comment_char = get_comment_syntax(language)

    prompt = f"""
You are SentinelAI, an automated Site Reliability Engineering (SRE) healing agent.
Your task is to analyze an application crash or bug, identify the root cause, and return the fully remediated, production-ready source code.

=== CRASH TELEMETRY ===
Timestamp: {timestamp}
Event Name: {event_name}
Error Details: {error_msg}
Language / Profile: {language}

=== BROKEN SOURCE CODE ===
{source_code}

=== MANDATORY INSTRUCTIONS ===
1. You MUST prepend an SRE Healing Report at the very top of the returned code using appropriate single-line comment syntax ('{comment_char}').
2. The comment block must strictly follow this format:
{comment_char} [AUTONOMOUS HEALING REPORT]
{comment_char} TIMESTAMP: {timestamp}
{comment_char} INTERCEPTED ERROR: <short exception name>
{comment_char} ROOT CAUSE ANALYSIS: <one line summary of the underlying bug>
{comment_char} LINE NUMBER: <line number or 'N/A'>
{comment_char} REMEDIATION DEPLOYED: <one line description of how the bug was resolved>

3. Return ONLY the executable, fully fixed source code (including the required header comment). 
4. DO NOT wrap your output in markdown code blocks (e.g., no ```python or ```go).
5. Ensure the syntax is 100% valid for {language}.
"""

    try:
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert SRE and polyglot software engineer capable of writing pristine code in Python, JavaScript/Node.js, Go, Java, C++, Rust, and C#.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        cleaned_code = response.choices[0].message.content.strip()

        if cleaned_code.startswith("```"):
            lines = cleaned_code.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned_code = "\n".join(lines).strip()

        return cleaned_code

    except Exception as e:
        return f"{comment_char} AI Analysis failed: {str(e)}"