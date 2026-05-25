from pathlib import Path
from typing import List
import shutil
import uuid

from app.embedding_service import create_embeddings_for_chunks
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.database import (
    init_db,
    insert_chunks,
    get_all_chunks,
    get_document_stats,
    delete_all_chunks,
    save_chat_message,
    get_chat_history,
    delete_chat_history,
)
from app.pdf_service import extract_chunks_from_pdf
from app.search_service import retrieve_relevant_chunks
from app.ai_service import generate_answer


BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
UPLOAD_DIR = BASE_DIR / "uploads"
FRONTEND_DIR = PROJECT_DIR / "frontend"

load_dotenv(BASE_DIR / ".env")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="AI PDF Knowledge Base Chatbot",
    description="Upload PDFs, ask questions, and get answers with sources.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_db()


class AskRequest(BaseModel):
    question: str
    top_k: int = 5


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "AI PDF Knowledge Base Chatbot backend is running",
    }


@app.get("/api/documents")
def list_documents():
    documents = get_document_stats()

    return {
        "documents": documents,
        "total_documents": len(documents),
    }


@app.post("/api/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(
            status_code=400,
            detail="No files uploaded.",
        )

    upload_results = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail=f"Only PDF files are allowed: {file.filename}",
            )

        safe_file_name = Path(file.filename).name
        unique_file_name = f"{uuid.uuid4()}_{safe_file_name}"
        saved_path = UPLOAD_DIR / unique_file_name

        try:
            with saved_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            chunks = extract_chunks_from_pdf(saved_path, safe_file_name)

            if not chunks:
                upload_results.append(
                    {
                        "file_name": safe_file_name,
                        "status": "skipped",
                        "message": "No extractable text found in this PDF.",
                        "chunks_count": 0,
                    }
                )
                continue

            chunks = create_embeddings_for_chunks(chunks)

            insert_chunks(safe_file_name, chunks)

            upload_results.append(
                {
                    "file_name": safe_file_name,
                    "status": "uploaded",
                    "chunks_count": len(chunks),
                }
            )

        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process {file.filename}: {error}",
            )

    return {
        "message": "Upload completed.",
        "results": upload_results,
    }


@app.post("/api/ask")
def ask_question(request: AskRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    all_chunks = get_all_chunks()

    if not all_chunks:
        raise HTTPException(
            status_code=400,
            detail="No documents uploaded yet. Please upload at least one PDF first.",
        )

    relevant_chunks = retrieve_relevant_chunks(
        question=question,
        chunks=all_chunks,
        top_k=request.top_k,
    )

    if not relevant_chunks:
        return {
            "answer": "I could not find relevant information in the uploaded documents.",
            "sources": [],
        }

    try:
        answer = generate_answer(question, relevant_chunks)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"AI generation failed: {error}",
        )

    sources = []

    for chunk in relevant_chunks:
        sources.append(
            {
                "file_name": chunk["file_name"],
                "page_number": chunk["page_number"],
                "chunk_index": chunk["chunk_index"],
                "score": round(chunk["score"], 4),
                "preview": chunk["text"][:300] + "...",
            }
        )

    save_chat_message(
        question=question,
        answer=answer,
        sources=sources,
    )

    return {
        "answer": answer,
        "sources": sources,
    }

@app.get("/api/chat-history")
def list_chat_history():
    history = get_chat_history(limit=20)

    return {
        "history": history,
        "total_items": len(history),
    }


@app.delete("/api/chat-history")
def clear_chat_history():
    delete_chat_history()

    return {
        "message": "Chat history was deleted.",
    }


@app.delete("/api/documents")
def clear_documents():
    delete_all_chunks()

    for file_path in UPLOAD_DIR.glob("*"):
        if file_path.is_file():
            file_path.unlink()

    return {
        "message": "All documents and chunks were deleted.",
    }


app.mount(
    "/",
    StaticFiles(directory=str(FRONTEND_DIR), html=True),
    name="frontend",
)