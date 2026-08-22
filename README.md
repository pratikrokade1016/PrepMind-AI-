PrepMind AI — RAG-Based Intelligent Learning Assistant

PrepMind AI is an AI-powered learning assistant designed to help students prepare for competitive examinations such as UPSC and MPSC.

The platform allows students to ask questions using text or images. Image-based questions are processed using OCR, while relevant study material is retrieved using a Retrieval-Augmented Generation (RAG) pipeline before generating the final response using an LLM.

The goal is to provide context-aware, syllabus-oriented answers instead of relying only on the LLM’s general knowledge.

⸻

✨ Features

* 📝 Text-based Questions — Ask questions directly using text.
* 📷 Image-based Questions — Upload an image containing a question and extract its text using OCR.
* 🔎 Semantic Retrieval — Retrieve relevant study material using embeddings and vector similarity search.
* 🧠 RAG-based Question Answering — Generate answers using retrieved context.
* 🤖 LLM Integration — Use an LLM to generate contextual responses.
* 📚 Syllabus-oriented Learning — Ground responses using competitive-exam study material.
* 📝 Quiz Generation — Generate practice questions based on the learning content.
* 🎯 Personalized Learning — Support adaptive learning workflows based on student interactions.

⸻

🏗️ System Architecture

                         ┌────────────────────┐
                         │       Student      │
                         └─────────┬──────────┘
                                   │
                         Text / Image Question
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                  Text                           Image
                    │                             │
                    │                            OCR
                    │                             │
                    └──────────────┬──────────────┘
                                   │
                            Extracted Question
                                   │
                                   ▼
                         ┌──────────────────┐
                         │ Text Processing  │
                         │ & Chunking       │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    Embeddings    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Vector Store    │
                         │      FAISS       │
                         └────────┬─────────┘
                                  │
                           Similarity Search
                                  │
                                  ▼
                         Relevant Context
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   LLM / AI API   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         Contextual Answer
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     Student      │
                         └──────────────────┘

⸻

🔍 How the RAG Pipeline Works

PrepMind uses Retrieval-Augmented Generation (RAG) to improve the relevance of generated answers.

1. Document Processing

Study material is collected from relevant competitive-examination resources.

The documents are:

* Loaded
* Cleaned
* Split into smaller chunks
* Converted into vector embeddings

2. Embedding Generation

Each document chunk is converted into a numerical vector representation using an embedding model.

These vectors represent the semantic meaning of the content.

3. Vector Storage

The generated embeddings are stored in a FAISS vector index.

This allows the system to perform efficient similarity searches.

4. Question Processing

When a student asks a question, the question is converted into an embedding.

For image-based questions, OCR is performed before generating the embedding.

5. Retrieval

The question embedding is compared against the stored document embeddings.

The most relevant chunks are retrieved as contextual information.

6. Generation

The retrieved context and the student’s question are provided to the LLM.

The LLM generates an answer based on the retrieved information.

Question
   ↓
Embedding
   ↓
Similarity Search
   ↓
Relevant Context
   ↓
Prompt + Context
   ↓
LLM
   ↓
Final Answer

This approach helps keep generated answers grounded in the available study material.

⸻

📷 OCR Workflow

PrepMind supports image-based questions.

Image Upload
     ↓
Image Processing
     ↓
OCR
     ↓
Extracted Text
     ↓
RAG Pipeline
     ↓
Relevant Study Material
     ↓
LLM
     ↓
Answer

This allows students to take a question from a textbook, question paper, or image and directly use it with the learning assistant.

⸻

🧠 AI Workflow

The overall AI workflow combines OCR, retrieval, embeddings, and LLM generation.

                 User Question
                      │
             ┌────────┴────────┐
             │               								              │
           Text              							        Image
             │                 							              │
             │               						                      OCR
             │                  						                    │
             └────────┬────────┘
                      │
                Question Text
                      │
                      ▼
                 Embeddings
                      │
                      ▼
                 FAISS Search
                      │
                      ▼
              Relevant Documents
                      │
                      ▼
               Context Building
                      │
                      ▼
                  LLM API
                      │
                      ▼
               Generated Answer

⸻

🛠️ Tech Stack

Frontend

* JavaScript
* HTML
* CSS

Backend

* Python
* FastAPI
* REST APIs

AI / Generative AI

* Large Language Models
* Retrieval-Augmented Generation (RAG)
* Prompt Engineering
* Embeddings
* Semantic Search
* OCR

AI Frameworks / Libraries

* LangChain
* FAISS
* Hugging Face

Database / Storage

* MongoDB
* Firebase

Development Tools

* Git
* GitHub
* Postman
* Cursor

⸻

🎯 Project Goals

PrepMind was developed to explore how modern AI technologies can be applied to education and personalized learning.

The project focuses on combining:

OCR
 +
Embeddings
 +
Vector Search
 +
RAG
 +
LLMs
 +
Personalized Learning

into a single learning workflow.

⸻

🔮 Future Improvements

* Improve OCR accuracy for complex question papers.
* Add citation and source references for retrieved answers.
* Implement conversation memory.
* Add hybrid search combining keyword and semantic retrieval.
* Add retrieval evaluation and answer-quality metrics.
* Introduce AI agents for multi-step learning workflows.
* Add personalized study-plan generation.
* Add student performance analytics.
* Deploy the application using cloud infrastructure.

⸻

📌 What We Learned

Through this project, we gained practical experience with:

* Building REST APIs with FastAPI
* Integrating AI/LLM APIs
* Implementing Retrieval-Augmented Generation
* Working with embeddings and vector databases
* Processing image-based questions using OCR
* Designing AI-assisted learning workflows
* Connecting frontend applications with AI backends
* Structuring an end-to-end AI application

⸻

👨‍💻 Authors

Varad Gorwadkar

Bachelor of Engineering — Information Technology

Pratik Rokade

Bachelor of Engineering — Information Technology

⸻

⭐ Project

PrepMind AI combines OCR, embeddings, vector search, RAG, and LLMs to create a contextual and personalized learning assistant for competitive exam preparation.
