
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

import pandas as pd
import json
import os
import re

load_dotenv()

#=============================================================================#

root_folder           = "./doc_md"
collection_name       = "doc_db"
persist_directory     = "./doc_db"
embeddings_model_name = "bge-m3:latest"

#=============================================================================#

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

embeddings = OllamaEmbeddings(model=embeddings_model_name)
# embeddings = GoogleGenerativeAIEmbeddings(model=embeddings_model_name, api_key=os.getenv("GOOGLE_API_KEY"))

vector_store = Chroma(
    collection_name    = collection_name,
    embedding_function = embeddings,
    persist_directory  = persist_directory
)

#=============================================================================#

def read_all_md_files(root_dir: str):
    md_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith(".md"):
                file_path = os.path.join(dirpath, filename)

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                md_files.append({
                    "path": file_path,
                    "filename": filename,
                    "content": content
                })

    return md_files

#-----------------------------------------------------------------------------#

def clean_md_content(md_text: str) -> str:

    text = md_text

    # 1. 移除 Markdown 圖片 ![](xxx)
    text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)

    # 2. 移除 <br> / <br/>
    text = re.sub(r'<br\s*/?>', '', text, flags=re.IGNORECASE)

    # 3. 只移除「頭尾」的換行與空白，保留中間段落
    return text.strip()

#-----------------------------------------------------------------------------#

def create_doc_db():

    md_files = read_all_md_files(root_folder)

    for md_file in md_files:

        filename = md_file["filename"].split('.')[0]

        print(filename)

        documents = []
        ids = []

        md_header_splits = md_splitter.split_text(md_file["content"])

        for index, split in enumerate(md_header_splits):

            metadata = split.metadata

            metadata["product_model"] = filename

            clean_content = clean_md_content(split.page_content)

            documents.append(Document(page_content=clean_content, metadata=metadata))

            ids.append(str(f"{filename}_{index+1}"))

        vector_store.add_documents(documents=documents, ids=ids)

    print("Done")

#-----------------------------------------------------------------------------#

def search_doc_db(query_text, product_model, k_num):

    try:
        result = vector_store.similarity_search(
            query_text,
            filter={"product_model": product_model},
            k=k_num
        )

    except:
        result = vector_store.similarity_search(
            query_text,
            k=k_num
        )

    return result

#=============================================================================#

if __name__ == '__main__':

    create_doc_db()

    """
    query_text = "請問註冊鍵在哪？,我的型號是AS701"
    product_model = "AS701"
    result = search_doc_db(query_text, product_model, 5)
    page_contents = [doc.page_content for doc in result]
    print(page_contents)
    """
