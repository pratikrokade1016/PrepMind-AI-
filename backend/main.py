from fastapi import FastAPI, UploadFile, File, Form, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import shutil
import os
from datetime import datetime


# DB
from backend.db.database import get_db, Base, engine

# Models
from backend.models import User, Chat, Message, Note

# Auth
from backend.auth.utils import decode_token
from backend.auth.routes import router as auth_router

# Routes
from backend.chat.routes import router as chat_router
from backend.notes.routes import router as notes_router

# AI
from backend.rag.retrieve import get_relevant_context
from backend.rag.generate import generate_answer
from backend.ocr.ocr import extract_text_from_image

# -------------------------------
# 🚀 APP INIT
# -------------------------------
app = FastAPI()

# ✅ CREATE TABLES
Base.metadata.create_all(bind=engine)

# -------------------------------
# 🔌 ROUTERS
# -------------------------------
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(notes_router)

# -------------------------------
# 🌐 CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# 📦 REQUEST MODEL
# -------------------------------
class QueryRequest(BaseModel):
    question: str
    chat_id: int | None = None

# -------------------------------
# 🔐 GET USER FROM TOKEN
# -------------------------------
def get_current_user(authorization: str = Header(None)):
    if not authorization:
        return None
    try:
        token = authorization.split(" ")[1]
        payload = decode_token(token)
        return payload["user_id"]
    except:
        return None
    
# -------------------------------
# 💬 BASIC CHAT HANDLER
# -------------------------------
def handle_basic_conversation(question: str):
    q = question.lower()

    greetings = ["hi", "hello", "hey", "hii", "good morning", "good evening"]
    thanks = ["thanks", "thank you"]

    if any(q == g or q.startswith(g) for g in greetings):
        return "Hello! 👋 I'm PrepMind AI. How can I help in your studies?", "High"

    if any(t in q for t in thanks):
        return "You're welcome 😊 Keep learning!", "High"

    if len(q) <= 2:
        return "Please ask a complete question.", "Low"

    return None

# -------------------------------
# 🧠 MAIN CHAT API
# -------------------------------
@app.post("/ask")
async def ask_question(
    question: str = Form(None),
    chat_id: int = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    user_id: int | None = Depends(get_current_user)
):
    question = (question or "").strip()

    if not question and not file:
        return {"answer": "Please enter a question or upload an image.", "confidence": "Low"}

    # 🖼️ IMAGE PROCESSING (INSIDE FUNCTION ✅)
    image_text = ""

    if file and file.filename:
        try:
            file_path = f"temp_{file.filename}"

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            image_text = extract_text_from_image(file_path)
            os.remove(file_path)

            print("📷 Extracted:", image_text)

        except Exception as e:
            print("❌ Image error:", e)

    # 👋 BASIC RESPONSE
    # 👋 BASIC RESPONSE (ONLY IF NO IMAGE)
    if not image_text:
        basic = handle_basic_conversation(question)
        if basic:
            answer, confidence = basic
            return {"answer": answer, "confidence": confidence}
        # -------------------------------
    # 📂 GET OR CREATE CHAT (FIXED)
    # -------------------------------
    if chat_id and user_id:
        chat = db.query(Chat).filter_by(id=chat_id, user_id=user_id).first()
    else:
        chat = Chat(user_id=user_id, title=question[:30])
        db.add(chat)
        db.commit()
        db.refresh(chat)

    # -------------------------------
    # 💾 SAVE USER MESSAGE
    # -------------------------------

    # 💾 SAVE USER MESSAGE (FIXED FOR IMAGE)
    user_text = question if question else "[Image uploaded]"

    user_msg = Message(chat_id=chat.id, role="user", text=user_text)
    db.add(user_msg)
    db.commit()

    # 🔥 UPDATE CHAT TIMESTAMP (USER ACTION)
    from datetime import datetime
    chat.updated_at = datetime.utcnow()
    db.commit()

    # -------------------------------
    # 🔍 CONTEXT
    # -------------------------------

    final_question = question or ""

    if image_text:
        final_question += f"\n\nImage Content:\n{image_text}"

    context, sources = get_relevant_context(final_question)

    if not context:
        return {
            "answer": "No relevant context found.",
            "confidence": "Low",
            "chat_id": chat.id
        }

    # -------------------------------
    # 🤖 GENERATE ANSWER
    # -------------------------------
    answer, confidence = generate_answer(final_question, context)

    # -------------------------------
    # 💾 SAVE AI MESSAGE
    # -------------------------------
    ai_msg = Message(chat_id=chat.id, role="ai", text=answer)
    db.add(ai_msg)
    db.commit()

    chat.updated_at = datetime.utcnow()
    db.commit()

    # 🔥 ADD THIS LINE
    from datetime import datetime
    chat.updated_at = datetime.utcnow()
    db.commit()

    return {
        "answer": answer,
        "confidence": confidence,
        "chat_id": chat.id,
        "sources": sources
    }

# -------------------------------
# 🖼️ IMAGE API
# -------------------------------
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_path = f"temp_{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        extracted_text = extract_text_from_image(file_path)
        os.remove(file_path)

        if not extracted_text.strip():
            return {"answer": "Could not extract text from image."}

        context, sources = get_relevant_context(extracted_text)

        if not context:
            return {
                "question": extracted_text,
                "answer": "No relevant context found.",
                "confidence": "Low"
            }

        answer, confidence = generate_answer(extracted_text, context)

        return {
            "question": extracted_text,
            "answer": answer,
            "confidence": confidence
        }

    except Exception:
        return {"answer": "Error processing image."}

# -------------------------------
# 🚀 ROOT
# -------------------------------
@app.get("/")
def root():
    return {"message": "PrepMind AI Backend Running 🚀"}
