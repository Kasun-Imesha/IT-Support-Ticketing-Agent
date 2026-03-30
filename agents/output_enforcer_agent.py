"""
Output Enforcer Agent
=====================
A lightweight AutoGen AssistantAgent that runs every enabled output policy
check (as registered tools) on the final AI response BEFORE it is shown
to the user.

Usage
-----
    from agents.output_enforcer_agent import run_output_enforcement_fast

    result = run_output_enforcement_fast(ai_response_text)
    # result["allowed"]       → bool
    # result["final_text"]    → str   (may be redacted/appended)
    # result["warnings"]      → list[str]
    # result["errors"]        → list[str]

Design notes
------------
* Same dual-path design as InputEnforcerAgent:
    - LLM-assisted path  : run_output_enforcement()       ← agent reasons over checks
    - Fast direct path   : run_output_enforcement_fast()  ← pure Python, no LLM
* "redact" severity → the modified_text is propagated to final_text.
* "append" severity → disclaimer is appended to final_text.
* "block"  severity → allowed=False, original text suppressed.
"""
import os
import re
import sys
import json
from autogen import AssistantAgent, UserProxyAgent, register_function
sys.path.append(os.path.abspath("../"))

from utils.llm_config import llm_config
from policies.output_policies import (
    prevent_email_leakage,
    prevent_phone_leakage,
    check_response_min_length,
    check_hallucination_disclaimer,
    check_no_harmful_advice,
    check_confidentiality_breach,
)
from utils.prompts import output_policy_enforcer_agent_prompt


# Policy tool registry
ALL_OUTPUT_POLICY_TOOLS = [
    (prevent_email_leakage,          "Redacts email addresses that appear in the AI response"),
    (prevent_phone_leakage,          "Redacts phone numbers that appear in the AI response"),
    (check_response_min_length,      "Warns if the AI response is suspiciously short"),
    (check_hallucination_disclaimer, "Appends a disclaimer when speculative language is detected"),
    (check_no_harmful_advice,        "Blocks responses containing dangerous/destructive commands"),
    (check_confidentiality_breach,   "Blocks responses that expose credentials or system secrets"),
]


# Agent factory
def get_output_enforcer_agent():
    """
    Build and return the OutputEnforcerAgent together with its proxy executor.
    Returns (enforcer_agent, executor_proxy).
    """
    enforcer = AssistantAgent(
        name="OutputEnforcerAgent",
        llm_config=llm_config,
        system_message=output_policy_enforcer_agent_prompt,
        code_execution_config=False,
    )

    executor = UserProxyAgent(
        name="OutputEnforcerExecutor",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: (
            isinstance(msg, dict)
            # and bool(re.search(r'"allowed"\s*:', msg.get("content") or ""))
            and bool(re.findall(r'"allowed"\s*:', msg.get("content") or ""))
        ),
    )

    for fn, desc in ALL_OUTPUT_POLICY_TOOLS:
        register_function(
            fn,
            caller=enforcer,
            executor=executor,
            description=desc,
        )

    return enforcer, executor


# High-level convenience: LLM-assisted enforcement
def run_output_enforcement(ai_text: str) -> dict:
    """
    Run all output policy checks via the LLM agent.

    Returns
    -------
    dict with keys:
        allowed    : bool
        final_text : str    (cleaned text; empty string if blocked)
        warnings   : list[str]
        errors     : list[str]   (block-level violations)
        raw_verdict: dict
    """
    enforcer, executor = get_output_enforcer_agent()

    executor.initiate_chat(
        recipient=enforcer,
        message=f"Run all output policy checks on this AI response text:\n\n{ai_text}",
        max_turns=15,
        silent=True,
    )

    verdict_raw = {}
    for msg in reversed(executor.chat_messages.get(enforcer, [])):
        content = msg.get("content", "")
        try:
            clean = re.sub(r"```(?:json)?", "", content).strip().rstrip("```").strip()
            verdict_raw = json.loads(clean)
            break
        except (json.JSONDecodeError, AttributeError):
            continue

    allowed = verdict_raw.get("allowed", True)
    return {
        "allowed": allowed,
        "final_text": verdict_raw.get("final_text", ai_text) if allowed else "",
        "warnings": verdict_raw.get("warnings", []),
        "errors": verdict_raw.get("block_reasons", []),
        "raw_verdict": verdict_raw,
    }


# Fast path: direct Python evaluation (no LLM round-trip)
def run_output_enforcement_fast(ai_text: str) -> dict:
    """
    Run all output policy tools directly in Python — no LLM, instant results.
    Handles redact/append chaining correctly.

    Returns the same dict schema as ``run_output_enforcement``.
    """
    errors = []
    warnings = []
    policy_results = []
    current_text = ai_text    # may be mutated by redact/append policies
    blocked = False

    all_fns = [fn for fn, _ in ALL_OUTPUT_POLICY_TOOLS]
    for fn in all_fns:
        try:
            result = fn(current_text)
        except Exception as exc:
            result = {
                "policy": fn.__name__,
                "passed": True,
                "severity": "info",
                "message": f"Policy check error (skipped): {exc}",
            }
        policy_results.append(result)

        if not result.get("passed", True):
            severity = result.get("severity", "warn")
            msg = result.get("message", "")

            if severity == "block":
                errors.append(msg)
                blocked = True

            elif severity in ("redact", "append"):
                # Apply text modification and keep running
                modified = result.get("modified_text")
                if modified:
                    current_text = modified
                warnings.append(msg)

            else:  # warn
                warnings.append(msg)

    return {
        "allowed": not blocked,
        "final_text": "" if blocked else current_text,
        "warnings": warnings,
        "errors": errors,
        "raw_verdict": {"policy_results": policy_results},
    }
