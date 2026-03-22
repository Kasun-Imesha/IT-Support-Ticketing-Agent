import os
import faiss
from uuid import uuid4
from dotenv import load_dotenv
load_dotenv("../")

from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
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
    
def build_index_from_document(file_path: str, persist_dir: str="../vector_store_faiss"):
    """build vector store from a given document

    Args:
        file_path (str): file path of the document
        persist_dir (str, optional): vector store save path. Defaults to "./vector_store".
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
    db = FAISS.from_documents(splitted_documents, embeddings, ids=uuids)
    db.save_local(persist_dir)


if __name__ == "__main__":
    file_path = "../data/knowledge_base.json"
    db_path = "../vector_store_faiss"
    print(f"[INFO] Building the vector store from {file_path}")
    build_index_from_document(file_path, db_path)
    print("[INFO] DB built..")
    
    print("[INFO] Checking similarity")
    embeddings = OpenAIEmbeddings()
    db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    res = db.similarity_search("My mouse is not working", k=3)
    for doc in res:
        print(doc)
