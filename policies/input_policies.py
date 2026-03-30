"""
Input Policy Tools
==================
Each function is registered as a tool that the InputEnforcerAgent can call.
Every function returns a dict with the schema:

    {
        "policy": str,          # policy name
        "passed": bool,         # True → OK, False → violation
        "severity": str,        # "block" | "warn"
        "message": str,         # human-readable explanation
    }

The agent collects all results and decides whether to block, warn, or pass
the user input to the main group-chat pipeline.
"""

import re
from policies.policy_config import INPUT_POLICIES


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
# PII checks
# ---------------------------------------------------------------------------

def detect_email_pii(text: str) -> dict:
    """Check if the user input contains email addresses (PII compliance)."""
    policy_name = "detect_email_pii"
    cfg = INPUT_POLICIES.get(policy_name, {})
    if not cfg.get("enabled", True):
        return _disabled(policy_name)

    pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    matches = re.findall(pattern, text)
    if matches:
        return {
            "policy": policy_name,
            "passed": False,
            "severity": cfg.get("severity", "block"),
            "message": (
                f"Input contains {len(matches)} email address(es): {matches}. "
                "Please remove personal email addresses before submitting."
            ),
        }
    return {"policy": policy_name, "passed": True, "severity": "info", "message": "No email PII detected."}


def detect_phone_pii(text: str) -> dict:
    """Check if the user input contains phone numbers (PII compliance)."""
    policy_name = "detect_phone_pii"
    cfg = INPUT_POLICIES.get(policy_name, {})
    if not cfg.get("enabled", True):
        return _disabled(policy_name)

    # Matches international and local formats: +1-800-555-0199, (800) 555 0199, 07911123456, etc.
    pattern = r"(\+?\d[\d\s\-\(\)]{7,}\d)"
    matches = re.findall(pattern, text)
    # Filter out false positives: pure dates, ticket IDs, version numbers (< 8 digits total)
    real_phones = [m for m in matches if len(re.sub(r"\D", "", m)) >= 8]
    if real_phones:
        return {
            "policy": policy_name,
            "passed": False,
            "severity": cfg.get("severity", "block"),
            "message": (
                f"Input appears to contain phone number(s). "
                "Please remove personal phone numbers before submitting."
            ),
        }
    return {"policy": policy_name, "passed": True, "severity": "info", "message": "No phone PII detected."}


def detect_credit_card_pii(text: str) -> dict:
    """Check if the user input contains credit/debit card numbers."""
    policy_name = "detect_credit_card_pii"
    cfg = INPUT_POLICIES.get(policy_name, {})
    if not cfg.get("enabled", True):
        return _disabled(policy_name)

    # Luhn-ish: 13–19 consecutive digits possibly separated by spaces/dashes
    pattern = r"\b(?:\d[ \-]?){13,19}\b"
    matches = re.findall(pattern, text)
    if matches:
        return {
            "policy": policy_name,
            "passed": False,
            "severity": cfg.get("severity", "block"),
            "message": "Input may contain a credit/debit card number. Never share card details in support tickets.",
        }
    return {"policy": policy_name, "passed": True, "severity": "info", "message": "No card number PII detected."}


def detect_ssn_pii(text: str) -> dict:
    """Check if the user input contains US Social Security Numbers."""
    policy_name = "detect_ssn_pii"
    cfg = INPUT_POLICIES.get(policy_name, {})
    if not cfg.get("enabled", True):
        return _disabled(policy_name)

    # Format: 123-45-6789 or 123 45 6789
    pattern = r"\b\d{3}[- ]\d{2}[- ]\d{4}\b"
    if re.search(pattern, text):
        return {
            "policy": policy_name,
            "passed": False,
            "severity": cfg.get("severity", "block"),
            "message": "Input appears to contain a Social Security Number (SSN). Please remove it.",
        }
    return {"policy": policy_name, "passed": True, "severity": "info", "message": "No SSN detected."}


def detect_password_in_input(text: str) -> dict:
    """Warn if the input looks like it contains a plaintext password."""
    policy_name = "detect_password_in_input"
    cfg = INPUT_POLICIES.get(policy_name, {})
    if not cfg.get("enabled", True):
        return _disabled(policy_name)

    # Heuristic: keywords followed by a non-space token
    pattern = r"(?i)\b(password|passwd|pwd|secret|token)\s*[:=]\s*\S+"
    if re.search(pattern, text):
        return {
            "policy": policy_name,
            "passed": False,
            "severity": cfg.get("severity", "warn"),
            "message": (
                "Input appears to contain a plaintext password or secret token. "
                "Remove credentials before submitting – we never need your password."
            ),
        }
    return {"policy": policy_name, "passed": True, "severity": "info", "message": "No plaintext password detected."}


# ---------------------------------------------------------------------------
# Content safety checks
# ---------------------------------------------------------------------------

def check_min_length(text: str) -> dict:
    """Reject trivially short or empty inputs."""
    policy_name = "check_min_length"
    cfg = INPUT_POLICIES.get(policy_name, {})
    if not cfg.get("enabled", True):
        return _disabled(policy_name)

    min_chars = cfg.get("min_chars", 10)
    if len(text.strip()) < min_chars:
        return {
            "policy": policy_name,
            "passed": False,
            "severity": cfg.get("severity", "block"),
            "message": (
                f"Input is too short ({len(text.strip())} chars). "
                f"Please describe your IT issue in at least {min_chars} characters."
            ),
        }
    return {"policy": policy_name, "passed": True, "severity": "info", "message": "Input length OK."}


def check_max_length(text: str) -> dict:
    """Reject excessively long input to guard against prompt-injection dumps."""
    policy_name = "check_max_length"
    cfg = INPUT_POLICIES.get(policy_name, {})
    if not cfg.get("enabled", True):
        return _disabled(policy_name)

    max_chars = cfg.get("max_chars", 2000)
    if len(text) > max_chars:
        return {
            "policy": policy_name,
            "passed": False,
            "severity": cfg.get("severity", "block"),
            "message": (
                f"Input is too long ({len(text)} chars, limit {max_chars}). "
                "Please shorten your description."
            ),
        }
    return {"policy": policy_name, "passed": True, "severity": "info", "message": "Input length within limit."}


def check_prompt_injection(text: str) -> dict:
    """Detect common prompt-injection attack patterns."""
    policy_name = "check_prompt_injection"
    cfg = INPUT_POLICIES.get(policy_name, {})
    if not cfg.get("enabled", True):
        return _disabled(policy_name)

    injection_patterns = [
        r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
        r"(?i)you\s+are\s+now\s+(a|an)\s+",
        r"(?i)disregard\s+(your|all)\s+(previous|prior|system)\s+",
        r"(?i)act\s+as\s+(if\s+you\s+are|a)\s+",
        r"(?i)forget\s+everything\s+(you\s+know|above)",
        r"(?i)new\s+instructions?:",
        r"(?i)system\s+prompt\s*:",
        r"(?i)jailbreak",
        r"(?i)developer\s+mode",
    ]
    for pat in injection_patterns:
        if re.search(pat, text):
            return {
                "policy": policy_name,
                "passed": False,
                "severity": cfg.get("severity", "block"),
                "message": "Input contains a suspected prompt-injection pattern and has been blocked.",
            }
    return {"policy": policy_name, "passed": True, "severity": "info", "message": "No prompt injection detected."}


def check_offensive_language(text: str) -> dict:
    """Flag obviously offensive or abusive language."""
    policy_name = "check_offensive_language"
    cfg = INPUT_POLICIES.get(policy_name, {})
    if not cfg.get("enabled", True):
        return _disabled(policy_name)

    # Basic word-list; in production replace with a proper moderation API call
    offensive_terms = [
        r"\bfuck\b", r"\bshit\b", r"\basshole\b", r"\bbastard\b",
        r"\bidiot\b", r"\bstupid\b", r"\bmoron\b",
    ]
    found = [pat for pat in offensive_terms if re.search(pat, text, re.IGNORECASE)]
    if found:
        return {
            "policy": policy_name,
            "passed": False,
            "severity": cfg.get("severity", "warn"),
            "message": "Input contains potentially offensive language. Please keep submissions professional.",
        }
    return {"policy": policy_name, "passed": True, "severity": "info", "message": "No offensive language detected."}


def check_it_relevance(text: str) -> dict:
    """Warn if the question appears completely unrelated to IT support."""
    policy_name = "check_it_relevance"
    cfg = INPUT_POLICIES.get(policy_name, {})
    if not cfg.get("enabled", True):
        return _disabled(policy_name)

    # Must contain at least one IT-related keyword
    it_keywords = [
        r"\b(computer|laptop|desktop|monitor|keyboard|mouse|printer|scanner)\b",
        r"\b(network|wifi|wi-fi|vpn|internet|ethernet|router|firewall|dns)\b",
        r"\b(password|login|access|account|permission|authentication|2fa|mfa)\b",
        r"\b(software|application|app|program|install|update|crash|error|bug)\b",
        r"\b(email|outlook|teams|zoom|office|windows|mac|linux|browser)\b",
        r"\b(server|database|backup|cloud|storage|disk|drive|usb)\b",
        r"\b(ticket|issue|problem|support|help|fix|broken|slow|freeze)\b",
        r"\b(hardware|device|cable|port|connection|screen|display)\b",
    ]
    if not any(re.search(pat, text, re.IGNORECASE) for pat in it_keywords):
        return {
            "policy": policy_name,
            "passed": False,
            "severity": cfg.get("severity", "warn"),
            "message": (
                "Your message does not appear to be related to IT support. "
                "This system is designed for IT issues only."
            ),
        }
    return {"policy": policy_name, "passed": True, "severity": "info", "message": "Input appears IT-relevant."}
