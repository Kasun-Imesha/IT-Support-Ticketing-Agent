import os
from autogen import UserProxyAgent, GroupChat, GroupChatManager

from utils.llm_config import llm_config
from tools.send_email import escalate_with_email
from agents.classifier_agent import get_classifier_agent
from agents.notification_agent import get_notification_agent
from agents.knowledge_base_agent import get_knowledge_base_agent
from agents.input_enforcer_agent import run_input_enforcement_fast, run_input_enforcement
from agents.output_enforcer_agent import run_output_enforcement_fast, run_output_enforcement


def is_termination_msg(msg):
    return isinstance(msg, dict) and msg.get("content", "").strip().upper() == "TERMINATE"


clf_agent = get_classifier_agent()
kb_agent = get_knowledge_base_agent()
notification_agent = get_notification_agent()

## Bind notification agent directly to send email (bypasses LLM)
notification_agent.generate_reply = lambda messages, sender: escalate_with_email(issue=messages[0]["content"])

user_agent = UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    code_execution_config=False,
    is_termination_msg=is_termination_msg,
)

# In AutoGen, GroupChat maintains the full message history between agents.
# The messages=[] parameter initializes that history
group_chat = GroupChat(
    agents=[user_agent, clf_agent, kb_agent],
    messages=[],
    speaker_selection_method="auto",
    allow_repeat_speaker=False,
    max_round=6,
)
chat_manager_agent = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config,
    is_termination_msg=is_termination_msg,
)


# Policy-guarded conversation runner
class PolicyViolationError(Exception):
    """Raised when a blocking input policy is violated."""
    def __init__(self, errors: list[str], warnings: list[str]):
        self.errors = errors
        self.warnings = warnings
        super().__init__("\n".join(errors))


def run_with_policy_enforcement(user_text: str) -> dict:
    """
    Full policy-guarded pipeline:
      1. Input enforcement  → block/warn on PII, injections, etc.
      2. Main group-chat    → classifier + knowledge-base agents
      3. Output enforcement → redact/append/block on the final response

    Parameters
    ----------
    user_text : str
        Raw text submitted by the user.

    Returns
    -------
    dict with keys:
        success         : bool
        final_response  : str   (cleaned AI response, or "" if blocked/no response)
        input_warnings  : list[str]
        output_warnings : list[str]
        blocked_by      : str   (which stage blocked: "input" | "output" | "")
        block_reasons   : list[str]
    """

    # 1. Input enforcement
    # input_result = run_input_enforcement_fast(user_text)
    input_result = run_input_enforcement(user_text)

    if not input_result["allowed"]:
        return {
            "success": False,
            "final_response": "",
            "input_warnings": input_result["warnings"],
            "output_warnings": [],
            "blocked_by": "input",
            "block_reasons": input_result["errors"],
        }

    # 2. Main group-chat pipeline
    responses = []
    original_receive = user_agent.receive

    def receive_and_capture(*args, **kwargs):
        if len(args) >= 2:
            message = args[0]
            if isinstance(message, dict):
                content = message.get("content", "").replace("TERMINATE", "").strip()
                if content:
                    responses.append(content)
        return original_receive(*args, **kwargs)

    user_agent.receive = receive_and_capture
    user_agent.initiate_chat(recipient=chat_manager_agent, message=user_text)
    user_agent.receive = original_receive

    raw_response = responses[-1] if responses else ""

    # 3. Output enforcement
    output_result = run_output_enforcement_fast(raw_response)

    if not output_result["allowed"]:
        return {
            "success": False,
            "final_response": "",
            "input_warnings": input_result["warnings"],
            "output_warnings": output_result["warnings"],
            "blocked_by": "output",
            "block_reasons": output_result["errors"],
        }

    return {
        "success": True,
        "final_response": output_result["final_text"],
        "input_warnings": input_result["warnings"],
        "output_warnings": output_result["warnings"],
        "blocked_by": "",
        "block_reasons": [],
    }


if __name__ == "__main__":
    # user_msg = "I cannot connect to my wifi. Please call or wapp me on +94710847726"
    user_msg = "Please help me resolve, my laptop is not turning on"
    
    # res = user_agent.initiate_chat(
    #     recipient=chat_manager_agent,
    #     # message="Please help me resolve, my laptop is not turning on"
    #     # message="I cannot connect to my wifi"
    #     message=user_msg
    # )
    
    res = run_with_policy_enforcement(user_msg)
    
    print(res)
    