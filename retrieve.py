from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

DB_PATH = "backend/db/faiss_index"

# -------------------------------
# 🔥 LOAD EMBEDDINGS + DB
# -------------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.load_local(
    DB_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

# -------------------------------
# 🔍 BETTER RETRIEVER
# -------------------------------
retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 8}   # more candidate chunks
)

# -------------------------------
# 🧠 IMPROVED STOPWORDS
# -------------------------------
STOPWORDS = {
    "what", "is", "the", "a", "an", "of", "in", "on", "for",
    "to", "with", "and", "or", "explain", "define", "about",
    "limitations", "powers", "government", "tell", "me",
    "write", "short", "note", "notes", "describe"
}

# -------------------------------
# 🔍 GET CONTEXT + SOURCE INFO
# -------------------------------
def get_relevant_context(question: str):
    question = question.lower().strip()

    docs = retriever.invoke(question)

    if not docs:
        return "", []

    # -------------------------------
    # 🧠 CLEAN QUESTION WORDS
    # -------------------------------
    question_words = [
        word.strip(".,?!:;()[]")
        for word in question.split()
        if word not in STOPWORDS and len(word) > 2
    ]

    filtered_docs = []

    # -------------------------------
    # 🔥 BETTER KEYWORD MATCHING
    # -------------------------------
    for doc in docs:
        content = doc.page_content.lower()

        match_count = 0

        for word in question_words:
            if word in content:
                match_count += 1

        # Keep docs only if enough meaningful matches found
        if match_count >= 2:
            filtered_docs.append(doc)

    # -------------------------------
    # ⚠️ FALLBACK
    # -------------------------------
    if not filtered_docs:
        filtered_docs = docs

    # -------------------------------
    # 🔥 TAKE TOP 3 (BETTER THAN 2)
    # -------------------------------
    filtered_docs = filtered_docs[:3]

    # -------------------------------
    # 📘 BUILD CONTEXT
    # -------------------------------
    context = "\n\n".join([
        doc.page_content for doc in filtered_docs
    ])

    # Limit context size for Gemini efficiency
    context = context[:2000]

    # -------------------------------
    # 📄 SOURCE INFO
    # -------------------------------
    sources = []

    for doc in filtered_docs:
        metadata = doc.metadata

        file_path = metadata.get("source", "Unknown File")
        file_name = os.path.basename(file_path)

        page_number = metadata.get("page", "Unknown")

        source_data = {
            "file": file_name,
            "page": page_number
        }

        if source_data not in sources:
            sources.append(source_data)

    # -------------------------------
    # 🧪 DEBUG PRINT (VERY USEFUL)
    # -------------------------------
    print("\n========== RETRIEVED CONTEXT ==========")
    print(context)
    print("=======================================\n")

    print("📘 Sources:", sources)

    return context, sources