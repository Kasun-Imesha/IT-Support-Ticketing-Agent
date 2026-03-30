"""
Output Policy Tools
===================
Each function is registered as a tool that the OutputEnforcerAgent can call.
Return schema is the same as input policies:

    {
        "policy": str,
        "passed": bool,
        "severity": str,       # "block" | "warn" | "redact" | "append"
        "message": str,
        "modified_text": str,  # present only when severity == "redact" or "append"
    }
"""

import re
from policies.policy_config import OUTPUT_POLICIES


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _disabled(policy_name: str) -> dict:
    return {
        "policy": policy_name,
        "passed": True,
        "severity": "info",
        "message": f"Policy '{policy_name}' is disabled – skipped.",
    }


# ---------------------------------------------------------------------------
# PII leakage guards
# ---------------------------------------------------------------------------

def prevent_email_leakage(text: str) -> dict:
    """Redact any email addresses that appear in the AI response."""
    policy_name = "prevent_email_leakage"
    cfg = OUTPUT_POLICIES.get(policy_name, {})
    if not cfg.get("enabled", True):
        return _disabled(policy_name)

    pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    redacted, count = re.subn(pattern, "[EMAIL REDACTED]", text)
    if count:
        return {
            "policy": policy_name,
            "passed": False,
            "severity": cfg.get("severity", "redact"),
            "message": f"Email address(es) found in output and redacted ({count} occurrence(s)).",
            "modified_text": redacted,
        }
    return {"policy": policy_name, "passed": True, "severity": "info", "message": "No email leakage detected."}


def prevent_phone_leakage(text: str) -> dict:
    """Redact any phone numbers that appear in the AI response."""
    policy_name = "prevent_phone_leakage"
    cfg = OUTPUT_POLICIES.get(policy_name, {})
    if not cfg.get("enabled", True):
        return _disabled(policy_name)

    pattern = r"(\+?\d[\d\s\-\(\)]{7,}\d)"
    matches = re.findall(pattern, text)
    real_phones = [m for m in matches if len(re.sub(r"\D", "", m)) >= 8]
    if real_phones:
        redacted = text
        for phone in real_phones:
            redacted = redacted.replace(phone, "[PHONE REDACTED]")
        return {
            "policy": policy_name,
            "passed": False,
            "severity": cfg.get("severity", "redact"),
            "message": f"Phone number(s) found in output and redacted ({len(real_phones)} occurrence(s)).",
            "modified_text": redacted,
        }
    return {"policy": policy_name, "passed": True, "severity": "info", "message": "No phone leakage detected."}


# ---------------------------------------------------------------------------
# Response quality checks
# ---------------------------------------------------------------------------

def check_response_min_length(text: str) -> dict:
    """Warn if the AI response is suspiciously short."""
    policy_name = "check_response_min_length"
    cfg = OUTPUT_POLICIES.get(policy_name, {})
    if not cfg.get("enabled", True):
        return _disabled(policy_name)

    min_chars = cfg.get("min_chars", 20)
    if len(text.strip()) < min_chars:
        return {
            "policy": policy_name,
            "passed": False,
            "severity": cfg.get("severity", "warn"),
            "message": (
                f"AI response is very short ({len(text.strip())} chars). "
                "The response quality may be low."
            ),
        }
    return {"policy": policy_name, "passed": True, "severity": "info", "message": "Response length OK."}


def check_hallucination_disclaimer(text: str) -> dict:
    """Append a disclaimer if the AI uses speculative or uncertain language."""
    policy_name = "check_hallucination_disclaimer"
    cfg = OUTPUT_POLICIES.get(policy_name, {})
    if not cfg.get("enabled", True):
        return _disabled(policy_name)

    speculation_patterns = [
        r"(?i)\bi\s+think\b",
        r"(?i)\bi\s+believe\b",
        r"(?i)\bmight\s+be\b",
        r"(?i)\bcould\s+be\b",
        r"(?i)\bprobably\b",
        r"(?i)\bpossibly\b",
        r"(?i)\bnot\s+(entirely\s+)?sure\b",
        r"(?i)\bI('m|\s+am)\s+not\s+(100%\s+)?certain\b",
    ]
    matched = [pat for pat in speculation_patterns if re.search(pat, text)]
    if matched:
        disclaimer = (
            "\n\n---\n⚠️ *Disclaimer: This response contains uncertain language. "
            "If this solution does not resolve your issue, please escalate to the IT support team.*"
        )
        return {
            "policy": policy_name,
            "passed": False,
            "severity": cfg.get("severity", "append"),
            "message": "Speculative language detected in AI output; disclaimer appended.",
            "modified_text": text + disclaimer,
        }
    return {"policy": policy_name, "passed": True, "severity": "info", "message": "No speculation language detected."}


def check_no_harmful_advice(text: str) -> dict:
    """Block responses that suggest destructive or dangerous system commands."""
    policy_name = "check_no_harmful_advice"
    cfg = OUTPUT_POLICIES.get(policy_name, {})
    if not cfg.get("enabled", True):
        return _disabled(policy_name)

    dangerous_patterns = [
        r"(?i)\brm\s+-rf\b",
        r"(?i)\bformat\s+c:\b",
        r"(?i)\bdel\s+/[qfsq]\b",
        r"(?i)\bshutdown\s+/[rfs]\b",
        r"(?i)\b(drop|truncate)\s+(table|database)\b",
        r"(?i)\bsudo\s+rm\b",
        r"(?i):(){ :|:& };:",       # fork bomb
        r"(?i)\bchmod\s+777\s+/\b",
        r"(?i)\bkill\s+-9\s+-1\b",
    ]
    for pat in dangerous_patterns:
        if re.search(pat, text):
            return {
                "policy": policy_name,
                "passed": False,
                "severity": cfg.get("severity", "block"),
                "message": "AI response contains a potentially harmful/destructive command and has been blocked.",
            }
    return {"policy": policy_name, "passed": True, "severity": "info", "message": "No harmful advice detected."}


def check_confidentiality_breach(text: str) -> dict:
    """Block responses that expose internal system/infrastructure details."""
    policy_name = "check_confidentiality_breach"
    cfg = OUTPUT_POLICIES.get(policy_name, {})
    if not cfg.get("enabled", True):
        return _disabled(policy_name)

    breach_patterns = [
        r"(?i)\bOPENAI_API_KEY\b",
        r"(?i)\bapi[_\s]?key\s*[:=]\s*sk-[A-Za-z0-9]{10,}",   # OpenAI key format
        r"(?i)\bprivate[_\s]?key\b",
        r"(?i)\bconnection[_\s]?string\b",
        r"(?i)\bpassword\s*[:=]\s*\S+",
        r"(?i)\bsecret\s*[:=]\s*\S+",
        r"(?i)\bSENDER_PASSWORD\b",
        r"(?i)\bsmtp\s*(server|login|password)\b",
    ]
    for pat in breach_patterns:
        if re.search(pat, text):
            return {
                "policy": policy_name,
                "passed": False,
                "severity": cfg.get("severity", "block"),
                "message": "AI response may expose confidential system credentials or infrastructure details and has been blocked.",
            }
    return {"policy": policy_name, "passed": True, "severity": "info", "message": "No confidentiality breach detected."}
