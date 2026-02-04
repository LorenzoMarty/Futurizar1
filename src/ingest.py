import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_documents_by_subject(base_dir: str, subject: str):
    docs_dir = os.path.join(base_dir, subject.lower())
    if not os.path.isdir(docs_dir):
        raise FileNotFoundError(f"Pasta da matéria não encontrada: {docs_dir}")

    docs = []
    for filename in os.listdir(docs_dir):
        path = os.path.join(docs_dir, filename)

        if filename.lower().endswith(".pdf"):
            loaded = PyPDFLoader(path).load()
        elif filename.lower().endswith(".txt"):
            loaded = TextLoader(path, encoding="utf-8").load()
        else:
            continue

        # marca a matéria no metadata (crítico para filtro)
        for d in loaded:
            d.metadata["subject"] = subject.lower()
            d.metadata["source"] = path.replace("\\", "/")
        docs.extend(loaded)

    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    return splitter.split_documents(docs)
