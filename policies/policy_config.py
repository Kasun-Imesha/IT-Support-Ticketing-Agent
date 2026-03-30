"""
Policy Configuration
====================
Central place to enable/disable individual policy checks and tune their parameters.
Set a policy's ``enabled`` flag to False to skip it without touching the policy code.
"""

# INPUT POLICY SETTINGS

INPUT_POLICIES = {

    # --- PII Detection ---
    "detect_email_pii": {
        "enabled": True,
        "severity": "block",          # "block" | "warn"
        "description": "Reject or mask email addresses in user input",
    },
    "detect_phone_pii": {
        "enabled": True,
        "severity": "block",
        "description": "Reject or mask phone numbers in user input",
    },
    "detect_credit_card_pii": {
        "enabled": True,
        "severity": "block",
        "description": "Reject messages containing credit/debit card numbers",
    },
    "detect_ssn_pii": {
        "enabled": True,
        "severity": "block",
        "description": "Reject messages containing Social Security Numbers (US)",
    },
    "detect_password_in_input": {
        "enabled": True,
        "severity": "warn",
        "description": "Warn when user pastes what looks like a plaintext password",
    },

    # Content Safety
    "check_min_length": {
        "enabled": True,
        "severity": "block",
        "min_chars": 10,
        "description": "Reject trivially short / empty inputs",
    },
    "check_max_length": {
        "enabled": True,
        "severity": "block",
        "max_chars": 2000,
        "description": "Reject excessively long inputs (potential prompt injection)",
    },
    "check_prompt_injection": {
        "enabled": True,
        "severity": "block",
        "description": "Detect common prompt-injection patterns",
    },
    "check_offensive_language": {
        "enabled": True,
        "severity": "warn",
        "description": "Flag offensive or abusive language in user input",
    },
    "check_it_relevance": {
        "enabled": True,
        "severity": "warn",
        "description": "Warn when the message appears completely unrelated to IT support",
    },
}


# OUTPUT POLICY SETTINGS
OUTPUT_POLICIES = {

    # PII leakage guard
    "prevent_email_leakage": {
        "enabled": True,
        "severity": "redact",         # "block" | "redact"
        "description": "Redact any email addresses that leak into the AI response",
    },
    "prevent_phone_leakage": {
        "enabled": True,
        "severity": "redact",
        "description": "Redact any phone numbers that leak into the AI response",
    },

    # Response quality
    "check_response_min_length": {
        "enabled": True,
        "severity": "warn",
        "min_chars": 20,
        "description": "Warn if AI gives a suspiciously short/empty response",
    },
    "check_hallucination_disclaimer": {
        "enabled": True,
        "severity": "append",         # "append" a disclaimer if hallucination risk phrases found
        "description": "Append a disclaimer when the AI speculates (e.g. 'I think', 'might be')",
    },
    "check_no_harmful_advice": {
        "enabled": True,
        "severity": "block",
        "description": "Block responses that suggest destructive or dangerous commands",
    },
    "check_confidentiality_breach": {
        "enabled": True,
        "severity": "block",
        "description": "Block responses that expose internal system/tool details inappropriately",
    },
}
