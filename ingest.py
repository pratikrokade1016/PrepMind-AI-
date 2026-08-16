# import os
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS

# # -------------------------------
# # 📂 PATHS
# # -------------------------------
# PDF_PATH = "backend/data/books/polity.pdf"
# DB_PATH = "backend/db/faiss_index"


# def ingest_pdf():
#     print("📄 Loading PDF...")

#     loader = PyPDFLoader(PDF_PATH)
#     documents = loader.load()

#     print(f"✅ Loaded {len(documents)} pages")

#     # -------------------------------
#     # ✂️ SPLIT TEXT (IMPROVED)
#     # -------------------------------
#     print("✂️ Splitting text...")

#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=500,      # 🔥 optimized
#         chunk_overlap=120,   # 🔥 better continuity
#     )

#     docs = splitter.split_documents(documents)

#     # Remove empty chunks (IMPORTANT FIX)
#     docs = [doc for doc in docs if doc.page_content.strip()]

#     print(f"✅ Created {len(docs)} chunks")

#     # -------------------------------
#     # 🔢 EMBEDDINGS
#     # -------------------------------
#     print("🔢 Creating embeddings...")

#     embeddings = HuggingFaceEmbeddings(
#         model_name="sentence-transformers/all-MiniLM-L6-v2"
#     )

#     # -------------------------------
#     # 💾 STORE IN FAISS
#     # -------------------------------
#     print("💾 Storing in FAISS...")

#     # Ensure directory exists (IMPORTANT FIX)
#     os.makedirs(DB_PATH, exist_ok=True)

#     db = FAISS.from_documents(docs, embeddings)
#     db.save_local(DB_PATH)

#     print("✅ Ingestion complete!")


# if __name__ == "__main__":
#     ingest_pdf()

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

PDF_FOLDER = "backend/data/books"
DB_PATH = "backend/db/faiss_index"


def ingest_pdf():
    all_documents = []

    print("📄 Loading all PDFs...")

    for file in os.listdir(PDF_FOLDER):
        if file.endswith(".pdf"):
            file_path = os.path.join(PDF_FOLDER, file)
            print(f"Loading: {file}")

            loader = PyPDFLoader(file_path)
            documents = loader.load()

            all_documents.extend(documents)

    print(f"✅ Total pages loaded: {len(all_documents)}")

    print("✂️ Splitting text...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    docs = splitter.split_documents(all_documents)
    docs = [doc for doc in docs if doc.page_content.strip()]

    print(f"✅ Created {len(docs)} chunks")

    print("🔢 Creating embeddings...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("💾 Saving FAISS index...")

    db = FAISS.from_documents(docs, embeddings)
    db.save_local(DB_PATH)

    print("✅ Multi-PDF ingestion complete!")


if __name__ == "__main__":
    ingest_pdf()