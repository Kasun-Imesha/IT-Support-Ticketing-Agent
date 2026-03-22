import os
import faiss
from uuid import uuid4
from dotenv import load_dotenv
load_dotenv("../")

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain_community.docstore import InMemoryDocstore
from langchain_community.document_loaders import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def metadata_func(record: dict, metadata: dict) -> dict:
    """the metadata insertion/augmentation function

    Args:
        record (dict): json record
        metadata (dict): initial metadata object

    Returns:
        dict: modified metadata object
    """
    metadata["id"] = record.get("id", "")
    metadata["category"] = record.get("category", "")
    return metadata
    
def build_index_from_document(file_path: str, persist_dir: str="../vector_store", collection_name: str="it_issues"):
    """build vector store from a given document

    Args:
        file_path (str): file path of the document
        persist_dir (str, optional): vector store save path. Defaults to "./vector_store".
        collection_name (str, optional): 
    """
    loader = JSONLoader(
        file_path=file_path,
        jq_schema=".[]",
        content_key='.problem + ": " + .solution',
        metadata_func=metadata_func,
        is_content_key_jq_parsable=True,
    )
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splitted_documents = splitter.split_documents(documents)
    
    embeddings = OpenAIEmbeddings()
    
    uuids = [str(uuid4()) for _ in range(len(documents))]
    print(f"[INFO] Building the vector store from {file_path}")
    Chroma.from_documents(
        documents=splitted_documents, 
        embedding=embeddings,
        ids=uuids,
        persist_directory=persist_dir,
        collection_name="it_issues", # optional
    )
    print(f"[INFO] DB built at {persist_dir}")


if __name__ == "__main__":
    file_path = "../data/knowledge_base.json"
    db_path = "../vector_store"
    collection_name = "it_issues"
    
    build_index_from_document(file_path, db_path, collection_name)
    
    print("[INFO] Checking similarity")
    embeddings = OpenAIEmbeddings()
    db = Chroma(
        persist_directory=db_path, 
        embedding_function=embeddings, 
        collection_name=collection_name,
    )
    res = db.similarity_search(
        "My mouse is not working", 
        k=3,
        # filter={"category": "Hardware Issue"}
        filter={"category": "Other"}
    )
    for doc in res:
        print(doc)
