from autogen import UserProxyAgent

from tools.db_search import retrieve_knowledge
# from tools.db_search_faiss import retrieve_knowledge
from agents.classifier_agent import get_classifier_agent
from agents.knowledge_base_agent import get_knowledge_base_agent

def get_user_agent():
    agent_user = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
    )
    return agent_user

def run_clf_test():
    user = get_user_agent()
    classifier = get_classifier_agent()
    
    for ticket in sample_tickets:
        print(f"\nTicket: {ticket}")
        user.initiate_chat(
            recipient=classifier,
            message=f"Classify this ticket: {ticket}",
            max_turns=1,
        )

def run_kb_test():
    agent_user = get_user_agent()
    agent_user.register_for_execution(
        name="retrieve_knowledge"
    )(retrieve_knowledge)
    
    agent_kb = get_knowledge_base_agent()
    
    agent_user.initiate_chat(
        agent_kb,
        # message="Use the tool retrieve_knowledge to find the fix for: My outlook crashes when I open it. Select the category from [Network Issue, Hardware Issue, Software Bug, Access Request, Password Reset, Other]",
        message="My outlook crashes when I open it. Select the category from [Network Issue, Hardware Issue, Software Bug, Access Request, Password Reset, Other]",
        max_turns=2,
    )
    
    
if __name__ == "__main__":
    sample_tickets = [
        "My laptop is not turining on since morning"
    ]
    # run_clf_test()
    run_kb_test()
    