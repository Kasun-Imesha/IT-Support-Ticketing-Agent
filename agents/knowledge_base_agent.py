import os
import sys
from autogen import AssistantAgent, register_function

sys.path.append(os.path.abspath("../"))
from utils.llm_config import llm_config
from tools.db_search import retrieve_knowledge
# from tools.db_search_faiss import retrieve_knowledge
from utils.prompts import knowledge_base_agent_prompt


def get_knowledge_base_agent():
    knowledge_base_agent = AssistantAgent(
        "KnowledgeBaseAgent", 
        llm_config=llm_config,
        system_message=knowledge_base_agent_prompt,
        code_execution_config={"use_docker": False},
    )
    
    # register tools
    register_function(
        retrieve_knowledge,
        caller=knowledge_base_agent,
        executor=knowledge_base_agent,
        description="Searches for top IT solutions from a knowledge base using a vector similarity search."
    )
    
    # knowledge_base_agent.register_for_llm(
    #     name="retrieve_knowledge",
    #     description="Searches for top IT solutions from a knowledge base using a vector similarity search.",
    # )(retrieve_knowledge)
    
    # knowledge_base_agent.register_for_execution(
    #     name="retrieve_knowledge",
    #     description="Searches for top IT solutions from a knowledge base using a vector similarity search.",
    # )(retrieve_knowledge)
    
    return knowledge_base_agent

if __name__ == "__main__":
    messages = [{"role": "user", "content": "My outlook crashes when I open it"}]
    agent_kb = get_knowledge_base_agent()
    res = None
    for i in range(2):
        if res:
            messages = [res]
        res = agent_kb.generate_reply(messages=messages)
        print(i, res)
