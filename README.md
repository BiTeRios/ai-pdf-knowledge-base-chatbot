# AI PDF Knowledge Base Chatbot

A full-stack Retrieval-Augmented Generation application that allows users to upload PDF documents, ask questions, and receive AI-generated answers based only on the uploaded content.

The application extracts text from PDF files, divides it into overlapping chunks, generates vector embeddings, retrieves the most relevant content using cosine similarity, and sends that context to an AI model to generate a grounded answer with source references.

---

## Overview

Companies often store important information inside large PDF documents, including:

* Internal policies
* Product documentation
* User manuals
* Employee onboarding materials
* Reports and contracts
* Frequently asked questions
* Training materials

Finding specific information manually can be slow and inconvenient.

This project demonstrates how an AI-powered knowledge base can help users quickly search through PDF documents using natural-language questions.

---

## Features

* Upload multiple PDF documents
* Validate uploaded file types
* Extract text page by page
* Split extracted text into overlapping chunks
* Generate vector embeddings for every chunk
* Store documents, embeddings, and metadata in SQLite
* Search document content using semantic similarity
* Generate answers using an OpenAI model
* Restrict answers to the uploaded document context
* Display source file names and page numbers
* Show relevance scores and source previews
* Save previous questions and answers
* Reopen previous conversations from chat history
* Clear uploaded documents
* Clear chat history
* Responsive React interface
* Loading, validation, empty, and error states
* Interactive FastAPI documentation
* Complete Docker Compose setup
* Persistent local storage for uploaded files and database data
* No hardcoded API keys

---

## Application Workflow

```text
PDF Upload
    ↓
Text Extraction with PyMuPDF
    ↓
Text Chunking with Overlap
    ↓
Embedding Generation
    ↓
SQLite Storage
    ↓
User Question
    ↓
Question Embedding
    ↓
Cosine Similarity Search
    ↓
Relevant Context Retrieval
    ↓
AI Answer Generation
    ↓
Answer, Sources and Chat History
```

### 1. Document processing

When a user uploads a PDF, the backend:

1. Validates that the uploaded file is a PDF.
2. Saves it using a unique generated filename.
3. Extracts text from every page with PyMuPDF.
4. Cleans and divides the text into overlapping chunks.
5. Generates an embedding vector for every chunk.
6. Saves the text, embedding, page number, and document metadata in SQLite.

### 2. Semantic search

When a user asks a question:

1. The question is converted into an embedding.
2. Its embedding is compared with stored document embeddings.
3. Cosine similarity is used to calculate relevance.
4. The most relevant chunks are selected.
5. Irrelevant chunks below the configured relevance threshold are excluded.

### 3. AI answer generation

The retrieved chunks are provided to the AI model as context.

The system prompt instructs the model to:

* Answer only from the supplied context
* Avoid using unsupported external knowledge
* Clearly state when the answer cannot be found in the uploaded documents

The final response includes the answer and the document sources used to generate it.

---

## Tech Stack

### Frontend

* React
* Vite
* JavaScript
* CSS
* Fetch API
* Nginx

### Backend

* Python 3.11
* FastAPI
* Uvicorn
* Pydantic
* PyMuPDF
* NumPy
* OpenAI Python SDK
* Python Multipart

### Data and AI

* SQLite
* OpenAI text embeddings
* Cosine similarity
* Retrieval-Augmented Generation
* OpenAI Responses API

### Infrastructure

* Docker
* Docker Compose
* Multi-stage frontend build
* Nginx reverse proxy
* Persistent bind-mounted storage

---

## Architecture

```text
┌──────────────────────────────┐
│        React Frontend        │
│                              │
│  PDF Upload                  │
│  Document List               │
│  Question Form               │
│  Answer and Sources          │
│  Chat History                │
└──────────────┬───────────────┘
               │ HTTP / REST
               ▼
┌──────────────────────────────┐
│      Nginx Reverse Proxy     │
│                              │
│  Serves React application    │
│  Proxies /api requests       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│        FastAPI Backend       │
│                              │
│  PDF Processing              │
│  Embedding Generation        │
│  Semantic Search             │
│  AI Answer Generation        │
│  Chat History Management     │
└───────┬──────────────┬───────┘
        │              │
        ▼              ▼
┌──────────────┐  ┌──────────────┐
│    SQLite    │  │  OpenAI API  │
│              │  │              │
│ Chunks       │  │ Embeddings   │
│ Embeddings   │  │ AI Answers   │
│ Chat History │  │              │
└──────────────┘  └──────────────┘
```

---

## Project Structure

```text
ai-pdf-knowledge-base-chatbot/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── pdf_service.py
│   │   ├── embedding_service.py
│   │   ├── search_service.py
│   │   └── ai_service.py
│   │
│   ├── data/
│   │   └── knowledge_base.db
│   │
│   ├── uploads/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .dockerignore
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   │
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
```

---

## Backend Modules

### `main.py`

Defines the FastAPI application, API endpoints, request validation, CORS configuration, startup logic, and document processing workflow.

### `pdf_service.py`

Opens PDF documents with PyMuPDF, extracts text page by page, cleans the text, and divides it into overlapping chunks.

### `embedding_service.py`

Creates embedding vectors through the OpenAI API and calculates cosine similarity between vectors.

Embeddings are generated in batches to avoid sending an excessive amount of text in a single request.

### `search_service.py`

Creates an embedding for the user's question, compares it with stored chunk embeddings, sorts chunks by relevance, and returns the best matches.

### `ai_service.py`

Builds the context from retrieved chunks and sends it to the configured AI model using the OpenAI Responses API.

### `database.py`

Manages the SQLite database, including:

* Database initialization
* Document chunk storage
* Embedding serialization
* Document statistics
* Chat history storage
* Document deletion
* Chat history deletion

---

## API Endpoints

| Method   | Endpoint            | Description                              |
| -------- | ------------------- | ---------------------------------------- |
| `GET`    | `/api/health`       | Check whether the backend is running     |
| `GET`    | `/api/documents`    | Get uploaded document statistics         |
| `POST`   | `/api/upload`       | Upload and process one or more PDF files |
| `POST`   | `/api/ask`          | Ask a question about uploaded documents  |
| `DELETE` | `/api/documents`    | Delete all documents and stored chunks   |
| `GET`    | `/api/chat-history` | Get recent questions and answers         |
| `DELETE` | `/api/chat-history` | Delete the complete chat history         |

Interactive API documentation is available through Swagger UI:

```text
http://localhost:8000/docs
```

---

## Getting Started with Docker

Docker Compose is the recommended way to run the application.

### Prerequisites

Install:

* Docker
* Docker Compose

### 1. Clone the repository

```bash
git clone <repository-url>
cd ai-pdf-knowledge-base-chatbot
```

### 2. Create the environment file

Linux or macOS:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### 3. Configure the API key

Open `.env` and provide your API settings:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

Do not commit the `.env` file to Git.

### 4. Build and start the containers

```bash
docker compose up --build
```

### 5. Open the application

```text
Frontend: http://localhost:3000
Backend:  http://localhost:8000
API Docs: http://localhost:8000/docs
```

### 6. Stop the application

```bash
docker compose down
```

The SQLite database and uploaded files remain available locally through the mounted `backend/data` and `backend/uploads` directories.

---

## Running Without Docker

### Backend

Create a backend environment file:

Linux or macOS:

```bash
cp .env.example backend/.env
```

Windows PowerShell:

```powershell
Copy-Item .env.example backend/.env
```

Create and activate a virtual environment:

```bash
cd backend
python -m venv .venv
```

Linux or macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies and start the server:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://localhost:8000
```

### Frontend

Open another terminal:

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

Start the development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

## Environment Variables

| Variable                 | Required | Description                                       |
| ------------------------ | -------: | ------------------------------------------------- |
| `OPENAI_API_KEY`         |      Yes | API key used for embeddings and answer generation |
| `OPENAI_BASE_URL`        |       No | Custom OpenAI-compatible API base URL             |
| `OPENAI_MODEL`           |       No | Model used to generate document-based answers     |
| `OPENAI_EMBEDDING_MODEL` |       No | Model used to create vector embeddings            |
| `VITE_API_URL`           |       No | Backend URL used by the frontend outside Docker   |

---

## Example Usage

1. Open the application.
2. Select one or more PDF files.
3. Click **Upload PDFs**.
4. Wait for document processing to finish.
5. Enter a question related to the uploaded documents.
6. Click **Ask AI**.
7. Review the generated answer.
8. Check the source file, page number, relevance score, and text preview.
9. Reopen previous answers from the chat history when needed.

Example questions:

```text
What is the refund policy?
```

```text
What requirements are described in the document?
```

```text
Summarize the main responsibilities mentioned in the uploaded files.
```

```text
Which documents mention payment conditions?
```

---

## Database Structure

### `chunks`

Stores processed document content.

| Column        | Description                       |
| ------------- | --------------------------------- |
| `id`          | Unique chunk identifier           |
| `file_name`   | Original PDF filename             |
| `page_number` | Source page number                |
| `chunk_index` | Position of the chunk on the page |
| `text`        | Extracted document text           |
| `embedding`   | Serialized embedding vector       |
| `created_at`  | Record creation timestamp         |

### `chat_history`

Stores previous questions and generated answers.

| Column         | Description                    |
| -------------- | ------------------------------ |
| `id`           | Unique history item identifier |
| `question`     | User question                  |
| `answer`       | Generated AI answer            |
| `sources_json` | Serialized source information  |
| `created_at`   | Record creation timestamp      |

---

## Design Decisions

### SQLite

SQLite was selected because the project is a compact, single-instance portfolio application.

It provides:

* Simple local setup
* No separate database server
* Persistent document and chat data
* Easy integration with Python
* Sufficient performance for a small knowledge base

### Overlapping chunks

Document text is divided into chunks with overlap so information located near chunk boundaries is less likely to lose its surrounding context.

### Embedding-based retrieval

Semantic embeddings allow the application to find conceptually relevant content even when the user's question does not contain the exact words used in the PDF.

### Source references

Every retrieved chunk keeps its document name and page number. This allows users to verify where the generated answer came from.

### Docker Compose

The frontend and backend run in separate containers:

* React is compiled in a Node build stage.
* Nginx serves the production frontend.
* Nginx proxies API requests to FastAPI.
* FastAPI processes PDFs and communicates with the AI API.
* Local directories preserve uploaded files and database content.

---

## Error Handling

The application handles common errors such as:

* No file selected
* Unsupported file type
* PDF with no extractable text
* Empty question
* No uploaded documents
* Missing API key
* PDF processing failure
* Embedding generation failure
* AI generation failure
* Backend connection errors

Errors are returned by the backend and displayed in the frontend interface.

---

## Current Limitations

This project is designed as a local portfolio prototype rather than a production SaaS application.

Current limitations include:

* No user authentication
* No separate user workspaces
* No OCR for scanned image-only PDFs
* SQLite instead of a dedicated vector database
* Embeddings stored as serialized JSON
* No streaming AI responses
* No background processing queue
* No individual document deletion
* No automated test suite
* No cloud deployment configuration

---

## Possible Future Improvements

* Add user authentication and authorization
* Add individual document deletion
* Add OCR support for scanned PDFs
* Stream AI responses to the frontend
* Add drag-and-drop PDF upload
* Add document upload progress
* Add conversation threads
* Add automated backend and frontend tests
* Add rate limiting
* Add structured logging
* Add background document processing
* Add support for DOCX and TXT files
* Replace SQLite search storage with PostgreSQL and pgvector
* Add cloud object storage
* Deploy the application to a cloud platform

---

## Skills Demonstrated

This project demonstrates practical experience with:

* Python backend development
* FastAPI REST API design
* React frontend development
* PDF text extraction
* Retrieval-Augmented Generation
* Vector embeddings
* Cosine similarity
* Prompt construction
* OpenAI API integration
* SQLite database design
* File upload handling
* Input validation
* Error handling
* Environment variable management
* Docker containerization
* Docker Compose
* Multi-stage Docker builds
* Nginx configuration
* Reverse proxy configuration
* Full-stack application architecture

---

## Use Cases

The same architecture can be adapted for:

* Internal company knowledge bases
* Employee policy assistants
* Customer support systems
* Product documentation search
* Legal document exploration
* Educational material assistants
* Technical manual search
* Contract analysis prototypes
* Research document assistants
* Employee onboarding systems

---

## License

This project was created as a portfolio and educational project.
