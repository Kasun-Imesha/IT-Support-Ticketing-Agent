import os
from dotenv import load_dotenv
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

_DEFAULT_DB_PATH = os.path.join(_PROJECT_ROOT, "vector_store")

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


def retrieve_knowledge(query: str, k: int=3, db_path: str=_DEFAULT_DB_PATH, category: str=""):
    """get the best matching 'k' documents for the query

    Args:
        query (str): query
        k (int): number of top matching documents to retrieve
        category (str, optional): search filter value for `category`. Defaults to "".

    Returns:
        str: concatenated context from the retrieved documents
        List[str]: sources of the retrieved content
    """
    embeddings = OpenAIEmbeddings()
    db = FAISS.load_local(db_path, embeddings=embeddings, allow_dangerous_deserialization=True)  # allow_dangerous_deserialization for loading from pkl
    docs = db.similarity_search(
        query=query, 
        k=k,
        filter={"category": category} if category else None
    )
    
    return "\n\n".join([f"Category: {doc.metadata.get('category', '')}\nContent: {doc.page_content}" for doc in docs]), [doc.metadata.get("source") for doc in docs]


if __name__ == "__main__":
    # print(retrieve_knowledge("My laptop is not turning on.", category="Hardware Issue"))
    print(retrieve_knowledge("My laptop is not turning on.", category="Other"))
    # print(retrieve_knowledge("My laptop is not turning on."))