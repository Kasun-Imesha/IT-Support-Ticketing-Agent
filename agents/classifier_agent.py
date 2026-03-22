import os
import sys
from pathlib import Path
from autogen import AssistantAgent

sys.path.append(os.path.abspath("../"))
from utils.llm_config import llm_config
from utils.prompts import classifier_agent_prompt


def get_classifier_agent():
    agent_cls = AssistantAgent(
        name="ClassifierAgent",
        llm_config=llm_config,
        system_message=classifier_agent_prompt,
    )
    
    return agent_cls


if __name__ == "__main__":
    agent_clf = get_classifier_agent()
    print(agent_clf.generate_reply(messages=[{"role": "user", "content": "My outlook crashes when I open it."}]))