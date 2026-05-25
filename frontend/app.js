const pdfInput = document.getElementById("pdfInput");
const uploadButton = document.getElementById("uploadButton");
const uploadStatus = document.getElementById("uploadStatus");

const historyList = document.getElementById("historyList");
const clearHistoryButton = document.getElementById("clearHistoryButton");

const documentsList = document.getElementById("documentsList");
const clearButton = document.getElementById("clearButton");

const questionInput = document.getElementById("questionInput");
const askButton = document.getElementById("askButton");

const answerBox = document.getElementById("answerBox");
const sourcesBox = document.getElementById("sourcesBox");
const errorBox = document.getElementById("errorBox");


function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}


function clearError() {
    errorBox.textContent = "";
    errorBox.classList.add("hidden");
}


async function loadDocuments() {
    try {
        const response = await fetch("/api/documents");
        const data = await response.json();

        documentsList.innerHTML = "";

        if (!data.documents || data.documents.length === 0) {
            documentsList.innerHTML = `
                <div class="empty-state">
                    No documents uploaded yet.
                </div>
            `;
            return;
        }

        data.documents.forEach((document) => {
            const item = window.document.createElement("div");

            item.className = "document-item";
            item.innerHTML = `
                <div class="document-name">${document.file_name}</div>
                <div class="document-meta">
                    ${document.chunks_count} chunks · pages ${document.first_page}-${document.last_page}
                </div>
            `;

            documentsList.appendChild(item);
        });

    } catch (error) {
        documentsList.innerHTML = `
            <div class="empty-state">
                Could not load documents.
            </div>
        `;
    }
}

async function loadChatHistory() {
    try {
        const response = await fetch("/api/chat-history");
        const data = await response.json();

        historyList.innerHTML = "";

        if (!data.history || data.history.length === 0) {
            historyList.innerHTML = `
                <div class="empty-state">
                    No questions asked yet.
                </div>
            `;
            return;
        }

        data.history.forEach((item) => {
            const historyItem = window.document.createElement("div");
            historyItem.className = "history-item";

            historyItem.innerHTML = `
                <div class="history-question">${item.question}</div>
                <div class="history-date">${item.created_at}</div>
            `;

            historyItem.addEventListener("click", () => {
                questionInput.value = item.question;
                answerBox.textContent = item.answer;
                renderSources(item.sources);
            });

            historyList.appendChild(historyItem);
        });

    } catch (error) {
        historyList.innerHTML = `
            <div class="empty-state">
                Could not load chat history.
            </div>
        `;
    }
}

uploadButton.addEventListener("click", async () => {
    clearError();

    const files = pdfInput.files;

    if (!files || files.length === 0) {
        showError("Please select at least one PDF file.");
        return;
    }

    const formData = new FormData();

    for (const file of files) {
        formData.append("files", file);
    }

    uploadButton.disabled = true;
    uploadButton.textContent = "Uploading...";
    uploadStatus.textContent = "Processing PDF files...";

    try {
        const response = await fetch("/api/upload", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Upload failed.");
        }

        uploadStatus.textContent = data.message;
        pdfInput.value = "";

        await loadDocuments();

    } catch (error) {
        showError(error.message);
        uploadStatus.textContent = "";
    } finally {
        uploadButton.disabled = false;
        uploadButton.textContent = "Upload PDFs";
    }
});


askButton.addEventListener("click", async () => {
    clearError();

    const question = questionInput.value.trim();

    if (!question) {
        showError("Please enter a question.");
        return;
    }

    askButton.disabled = true;
    askButton.textContent = "Thinking...";

    answerBox.textContent = "Generating answer...";
    sourcesBox.textContent = "Searching relevant sources...";

    try {
        const response = await fetch("/api/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                question: question,
                top_k: 5,
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Failed to generate answer.");
        }

        answerBox.textContent = data.answer;

        renderSources(data.sources);

        await loadChatHistory();

    } catch (error) {
        showError(error.message);
        answerBox.textContent = "No answer generated.";
        sourcesBox.textContent = "No sources available.";
    } finally {
        askButton.disabled = false;
        askButton.textContent = "Ask AI";
    }
});

clearHistoryButton.addEventListener("click", async () => {
    clearError();

    const confirmed = confirm("Delete chat history?");

    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch("/api/chat-history", {
            method: "DELETE",
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Failed to clear chat history.");
        }

        uploadStatus.textContent = data.message;

        await loadChatHistory();

    } catch (error) {
        showError(error.message);
    }
});

clearButton.addEventListener("click", async () => {
    clearError();

    const confirmed = confirm("Delete all uploaded documents and chunks?");

    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch("/api/documents", {
            method: "DELETE",
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Failed to clear documents.");
        }

        uploadStatus.textContent = data.message;
        answerBox.textContent = "Upload a PDF and ask a question to see the answer here.";
        sourcesBox.textContent = "Sources will appear here.";

        await loadDocuments();

    } catch (error) {
        showError(error.message);
    }
});


function renderSources(sources) {
    sourcesBox.innerHTML = "";

    if (!sources || sources.length === 0) {
        sourcesBox.textContent = "No sources found.";
        return;
    }

    sources.forEach((source) => {
        const item = window.document.createElement("div");
        item.className = "source-item";

        item.innerHTML = `
            <div class="source-title">
                ${source.file_name} — page ${source.page_number}
            </div>
            <div class="document-meta">
                Relevance score: ${source.score}
            </div>
            <div class="source-preview">
                ${source.preview}
            </div>
        `;

        sourcesBox.appendChild(item);
    });
}


loadDocuments();
loadChatHistory();