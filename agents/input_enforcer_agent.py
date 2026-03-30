"""
Input Enforcer Agent
====================
A lightweight AutoGen AssistantAgent that runs every enabled input policy
check (as registered tools) before the user message enters the main
group-chat pipeline.

Usage
-----
    from agents.input_enforcer_agent import run_input_enforcement

    result = run_input_enforcement(user_text)
    # result["allowed"]  → bool
    # result["warnings"] → list[str]
    # result["errors"]   → list[str]

Design notes
------------
* The agent is given all policy functions as tools so it can call them
  autonomously and reason about the combined outcome.
* After tool calls complete, it returns a structured JSON verdict.
* A parallel *direct* evaluation path (no LLM) is also provided for speed:
  use ``run_input_enforcement_fast()`` to skip the LLM loop entirely.
"""
import os
import re
import sys
import json
from autogen import AssistantAgent, UserProxyAgent, register_function
sys.path.append(os.path.abspath("../"))

from utils.llm_config import llm_config
from policies.input_policies import (
    detect_email_pii,
    detect_phone_pii,
    detect_credit_card_pii,
    detect_ssn_pii,
    detect_password_in_input,
    check_min_length,
    check_max_length,
    check_prompt_injection,
    check_offensive_language,
    check_it_relevance,
)
from utils.prompts import input_policy_enforcer_agent_prompt


# Policy tool registry
ALL_INPUT_POLICY_TOOLS = [
    (detect_email_pii,        "Checks for email addresses in user input"),
    (detect_phone_pii,        "Checks for phone numbers in user input"),
    (detect_credit_card_pii,  "Checks for credit/debit card numbers in user input"),
    (detect_ssn_pii,          "Checks for Social Security Numbers in user input"),
    (detect_password_in_input,"Checks for plaintext passwords/secrets in user input"),
    (check_min_length,        "Checks that input meets the minimum character length"),
    (check_max_length,        "Checks that input does not exceed the maximum character length"),
    (check_prompt_injection,  "Detects prompt-injection attack patterns in user input"),
    (check_offensive_language,"Flags offensive or abusive language in user input"),
    (check_it_relevance,      "Checks that the input is related to IT support"),
]


# Agent factory
def get_input_enforcer_agent():
    """
    Build and return the InputEnforcerAgent together with its proxy executor.
    Returns (enforcer_agent, executor_proxy).
    """
    enforcer = AssistantAgent(
        name="InputEnforcerAgent",
        llm_config=llm_config,
        system_message=input_policy_enforcer_agent_prompt,
        code_execution_config=False,
    )

    executor = UserProxyAgent(
        name="InputEnforcerExecutor",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: (
            isinstance(msg, dict)
            # and bool(re.search(r'"allowed"\s*:', msg.get("content") or ""))
            and bool(re.findall(r'"allowed"\s*:', msg.get("content") or "" ))
        ),
    )

    for fn, desc in ALL_INPUT_POLICY_TOOLS:
        register_function(
            fn,
            caller=enforcer,
            executor=executor,
            description=desc,
        )

    return enforcer, executor


# High-level convenience: LLM-assisted enforcement
def run_input_enforcement(user_text: str) -> dict:
    """
    Run all input policy checks via the LLM agent.

    Returns
    -------
    dict with keys:
        allowed   : bool
        warnings  : list[str]
        errors    : list[str]   (block-level violations)
        raw_verdict: dict       (full agent JSON response)
    """
    enforcer, executor = get_input_enforcer_agent()

    executor.initiate_chat(
        recipient=enforcer,
        message=f"Run all input policy checks on this user text:\n\n{user_text}",
        max_turns=15,   # enough rounds for all tool calls + verdict
        silent=True,
    )

    # Extract the last message from the enforcer that contains valid JSON
    verdict_raw = {}
    for msg in reversed(executor.chat_messages.get(enforcer, [])):
        content = msg.get("content", "")
        # Try to parse JSON from the message
        try:
            # Strip markdown code fences if present
            clean = re.sub(r"```(?:json)?", "", content).strip().rstrip("```").strip()
            verdict_raw = json.loads(clean)
            break
        except (json.JSONDecodeError, AttributeError):
            continue

    return {
        "allowed": verdict_raw.get("allowed", True),
        "warnings": verdict_raw.get("warnings", []),
        "errors": verdict_raw.get("block_reasons", []),
        "raw_verdict": verdict_raw,
    }


# Fast path: direct Python evaluation (no LLM round-trip)
def run_input_enforcement_fast(user_text: str) -> dict:
    """
    Run all input policy tools directly in Python — no LLM, instant results.
    Use this when latency matters or for unit testing.

    Returns the same dict schema as ``run_input_enforcement``.
    """
    errors = []
    warnings = []
    policy_results = []

    all_fns = [fn for fn, _ in ALL_INPUT_POLICY_TOOLS]
    for fn in all_fns:
        try:
            result = fn(user_text)
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
            else:
                warnings.append(msg)

    return {
        "allowed": len(errors) == 0,
        "warnings": warnings,
        "errors": errors,
        "raw_verdict": {"policy_results": policy_results},
    }
