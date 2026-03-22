import os
import sys
from dotenv import load_dotenv


load_dotenv("../")


llm_config = {
    "config_list": [
        {
            # "model": "gpt-4",
            # "model": "gpt-5-mini",
            "model": "gpt-4.1",
            "api_key": os.environ.get("OPENAI_API_KEY")
        }
    ]
}
