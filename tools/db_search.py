import os
from dotenv import load_dotenv

# Always load .env from the project root (two levels up from this file: tools/ -> project root)
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

_DEFAULT_DB_PATH = os.path.join(_PROJECT_ROOT, "vector_store")

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


def retrieve_knowledge(query: str, k: int=3, db_path: str=_DEFAULT_DB_PATH, collection_name: str="it_issues", category: str=""):
    """get the best matching 'k' documents for the query
    
    Args:
        query (str): query
        k (int, optional): number of top matching documents to retrieve (use more than 1 for enhanced correct retrievals). Defaults to 3
        db_path (str, optional): path to the vector db. Defaults to "../vector_store".
        collection_name (str, optional): name of the db collection. Defaults to "it_issues".
        category (str, optional): search filter value for `category`. Defaults to "".

    Returns:
        str: concatenated context from the retrieved documents
        List[str]: sources of the retrieved content
    """
    embeddings = OpenAIEmbeddings()
    db = Chroma(
        persist_directory=db_path, 
        embedding_function=embeddings, 
        collection_name=collection_name,
        
    )
    print(f"{db=} {query=} {k=} {category=}")
    docs = db.similarity_search(
        query=query, 
        k=k,
        filter={"category": category} if category else None
    )
    
    return "\n\n".join([f"Category: {doc.metadata.get('category', '')}\nContent: {doc.page_content}" for doc in docs]), [doc.metadata.get("source") for doc in docs]


if __name__ == "__main__":
    # print(retrieve_knowledge("My laptop is not turning on.", category="Hardware Issue"))
    print(retrieve_knowledge("My laptop is not turning on."))
    