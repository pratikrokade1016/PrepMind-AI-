import os
from dotenv import load_dotenv
import google.generativeai as genai

# -------------------------------
# 🔐 LOAD ENV & CONFIGURE GEMINI
# -------------------------------
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel(model_name="gemini-2.5-flash")


# -------------------------------
# 🔥 MODE DETECTION (KEEP YOURS)
# -------------------------------
def detect_mode(question: str):
    q = question.lower()

    if "mcq" in q or "quiz" in q or "questions" in q:
        return "quiz"

    if "short" in q or "notes" in q or "revision" in q:
        return "notes"

    if "exam" in q or "upsc" in q or "answer writing" in q:
        return "exam"

    return "normal"


# -------------------------------
# 🤖 GEMINI CALL
# -------------------------------
def call_gemini(prompt: str):
    response = model.generate_content(prompt)
    return response.text


# -------------------------------
# 🔥 GENERATE ANSWER
# -------------------------------
def generate_answer(question: str, context: str):

    if not context.strip():
        return ("Answer not found in provided books.", "Low")

    mode = detect_mode(question)

    # -------------------------------
    # 🧠 COMMON STRICT RULE
    # -------------------------------
    strict_rule = """
IMPORTANT STRICT RULE:
- Use ONLY the provided context
- Do NOT use outside knowledge
- If the answer is not clearly present in the context,
  strictly reply only:
  "Answer not found in provided books."
"""

    # -------------------------------
    # 🧠 PROMPT BASED ON MODE
    # -------------------------------

    if mode == "quiz":
        prompt = f"""
You are a competitive exam tutor.

{strict_rule}

Generate 5 multiple-choice questions (MCQs).

Rules:
- Each must have 4 options (A, B, C, D)
- Clearly mention correct answer

Context:
{context}

Topic:
{question}
"""

    elif mode == "notes":
        prompt = f"""
You are a competitive exam tutor.

{strict_rule}

Give SHORT REVISION NOTES.

Rules:
- Only bullet points
- No paragraphs
- Crisp and fast revision
- Include keywords

Context:
{context}

Topic:
{question}
"""

    elif mode == "exam":
        prompt = f"""
You are a UPSC Mains answer writing expert.

{strict_rule}

FORMAT:

📘 Topic

🔹 Definition (2-3 lines, precise)

🔹 Key Points:
• Include Articles if present
• Use keywords
• 4-6 crisp points

🔹 Value Addition:
• Example / Case (1 line)

🔹 Conclusion:
• Forward-looking

Context:
{context}

Question:
{question}
"""

    else:  # normal mode
        prompt = f"""
You are a helpful teacher for competitive exam students.

{strict_rule}

Explain clearly in simple language.

Rules:
- Keep it exam-oriented (UPSC/MPSC)
- Clean structured answer (no ** symbols)

Include:
- Easy explanation
- Key points
- Example (if possible)

Context:
{context}

Question:
{question}
"""

    # -------------------------------
    # 🤖 CALL GEMINI
    # -------------------------------
    try:
        output = call_gemini(prompt).strip()

        # Cleanup
        output = output.replace("Answer:", "").strip()

        # -------------------------------
        # 📊 CONFIDENCE LOGIC
        # -------------------------------
        if "answer not found" in output.lower():
            confidence = "Low"
        elif len(output) > 300:
            confidence = "High"
        else:
            confidence = "Medium"

        return output, confidence

    except Exception as e:
        return (f"Error generating answer: {str(e)}", "Low")