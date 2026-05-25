import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(
    "Upload a PDF and ask a question to see the answer here."
  );
  const [sources, setSources] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);

  const [uploadStatus, setUploadStatus] = useState("");
  const [error, setError] = useState("");

  const [isUploading, setIsUploading] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [isClearingDocuments, setIsClearingDocuments] = useState(false);
  const [isClearingHistory, setIsClearingHistory] = useState(false);

  useEffect(() => {
    loadDocuments();
    loadChatHistory();
  }, []);

  async function loadDocuments() {
    try {
      const response = await fetch(`${API_URL}/api/documents`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Could not load documents.");
      }

      setDocuments(data.documents || []);
    } catch (error) {
      setError(error.message);
    }
  }

  async function loadChatHistory() {
    try {
      const response = await fetch(`${API_URL}/api/chat-history`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Could not load chat history.");
      }

      setChatHistory(data.history || []);
    } catch (error) {
      setError(error.message);
    }
  }

  async function handleUpload() {
    setError("");
    setUploadStatus("");

    if (!selectedFiles || selectedFiles.length === 0) {
      setError("Please select at least one PDF file.");
      return;
    }

    const formData = new FormData();

    selectedFiles.forEach((file) => {
      formData.append("files", file);
    });

    try {
      setIsUploading(true);
      setUploadStatus("Processing PDF files...");

      const response = await fetch(`${API_URL}/api/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed.");
      }

      setUploadStatus(data.message || "Upload completed.");
      setSelectedFiles([]);

      const fileInput = document.getElementById("pdfInput");

      if (fileInput) {
        fileInput.value = "";
      }

      await loadDocuments();
    } catch (error) {
      setError(error.message);
      setUploadStatus("");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleAsk() {
    setError("");

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      setError("Please enter a question.");
      return;
    }

    try {
      setIsAsking(true);
      setAnswer("Generating answer...");
      setSources([]);

      const response = await fetch(`${API_URL}/api/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: trimmedQuestion,
          top_k: 5,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to generate answer.");
      }

      setAnswer(data.answer || "No answer generated.");
      setSources(data.sources || []);

      await loadChatHistory();
    } catch (error) {
      setError(error.message);
      setAnswer("No answer generated.");
      setSources([]);
    } finally {
      setIsAsking(false);
    }
  }

  async function handleClearDocuments() {
    const confirmed = window.confirm("Delete all uploaded documents and chunks?");

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setIsClearingDocuments(true);

      const response = await fetch(`${API_URL}/api/documents`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to clear documents.");
      }

      setUploadStatus(data.message || "Documents were deleted.");
      setDocuments([]);
      setAnswer("Upload a PDF and ask a question to see the answer here.");
      setSources([]);
    } catch (error) {
      setError(error.message);
    } finally {
      setIsClearingDocuments(false);
    }
  }

  async function handleClearHistory() {
    const confirmed = window.confirm("Delete chat history?");

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setIsClearingHistory(true);

      const response = await fetch(`${API_URL}/api/chat-history`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to clear chat history.");
      }

      setUploadStatus(data.message || "Chat history was deleted.");
      setChatHistory([]);
    } catch (error) {
      setError(error.message);
    } finally {
      setIsClearingHistory(false);
    }
  }

  function openHistoryItem(item) {
    setQuestion(item.question);
    setAnswer(item.answer);
    setSources(item.sources || []);
    setError("");
  }

  return (
    <div className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">Portfolio Project</p>
          <h1>AI PDF Knowledge Base Chatbot</h1>
          <p className="subtitle">
            Upload PDF documents, ask business questions, and get AI answers
            with sources.
          </p>
        </div>
      </header>

      <main className="layout">
        <section className="card">
          <div className="card-header">
            <h2>1. Upload PDF documents</h2>
            <p>Add one or more PDF files to build your knowledge base.</p>
          </div>

          <div className="upload-box">
            <input
              id="pdfInput"
              type="file"
              accept="application/pdf"
              multiple
              onChange={(event) =>
                setSelectedFiles(Array.from(event.target.files))
              }
            />

            <button onClick={handleUpload} disabled={isUploading}>
              {isUploading ? "Uploading..." : "Upload PDFs"}
            </button>
          </div>

          {uploadStatus && <div className="status">{uploadStatus}</div>}

          <div className="documents-header">
            <h3>Uploaded documents</h3>
            <button
              className="secondary-button"
              onClick={handleClearDocuments}
              disabled={isClearingDocuments}
            >
              {isClearingDocuments ? "Clearing..." : "Clear all"}
            </button>
          </div>

          <div className="documents-list">
            {documents.length === 0 ? (
              <div className="empty-state">No documents uploaded yet.</div>
            ) : (
              documents.map((document) => (
                <div className="document-item" key={document.file_name}>
                  <div className="document-name">{document.file_name}</div>
                  <div className="document-meta">
                    {document.chunks_count} chunks · pages{" "}
                    {document.first_page}-{document.last_page}
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="documents-header">
            <h3>Chat history</h3>
            <button
              className="secondary-button"
              onClick={handleClearHistory}
              disabled={isClearingHistory}
            >
              {isClearingHistory ? "Clearing..." : "Clear history"}
            </button>
          </div>

          <div className="documents-list">
            {chatHistory.length === 0 ? (
              <div className="empty-state">No questions asked yet.</div>
            ) : (
              chatHistory.map((item) => (
                <button
                  className="history-item"
                  key={item.id}
                  onClick={() => openHistoryItem(item)}
                >
                  <span className="history-question">{item.question}</span>
                  <span className="history-date">{item.created_at}</span>
                </button>
              ))
            )}
          </div>
        </section>

        <section className="card">
          <div className="card-header">
            <h2>2. Ask a question</h2>
            <p>The chatbot answers only from uploaded PDF content.</p>
          </div>

          <textarea
            value={question}
            placeholder="Example: What is the refund policy?"
            onChange={(event) => setQuestion(event.target.value)}
          />

          <button onClick={handleAsk} disabled={isAsking}>
            {isAsking ? "Thinking..." : "Ask AI"}
          </button>

          {error && <div className="error-box">{error}</div>}

          <div className="answer-section">
            <h3>Answer</h3>
            <div className="answer-box">{answer}</div>
          </div>

          <div className="sources-section">
            <h3>Sources</h3>

            <div className="sources-box">
              {sources.length === 0 ? (
                <div>Sources will appear here.</div>
              ) : (
                sources.map((source, index) => (
                  <div className="source-item" key={index}>
                    <div className="source-title">
                      {source.file_name} — page {source.page_number}
                    </div>
                    <div className="document-meta">
                      Relevance score: {source.score}
                    </div>
                    <div className="source-preview">{source.preview}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;