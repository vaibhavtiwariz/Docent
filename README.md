# Docent 📚

### An AI-Powered Curation Assistant for Research Repositories

Docent automates metadata curation for scientific documents. Upload a PDF research
paper → the app extracts its title and authors with a large language model →
you review, correct, and save the result. Every correction is persisted, building
a dataset that powers a built-in accuracy benchmark. Intelligent automation with
human oversight, and the numbers to prove it.

*(Formerly Intelli-curate.)*

---

## 🚀 Key Features

* **AI-Powered Metadata Extraction:** Google Gemini (free AI Studio tier) reads
  the opening pages and returns title + authors as structured JSON.
  Hugging Face Inference Providers supported as an optional backend.
* **Human-in-the-Loop UI:** Review, edit, and validate the AI's output in
  Streamlit. Corrections are saved to SQLite via a dedicated API endpoint —
  the feedback loop is closed, not decorative.
* **Built-in Evaluation:** `eval.py` scores title accuracy and author
  precision/recall/F1 against a labeled paper set. Improvements are measurable.
* **Decoupled Architecture:** FastAPI backend + Streamlit frontend, with
  per-file result caching so reruns never burn a repeat LLM call.
* **Sane Engineering:** Upload validation, temp-file lifecycle management,
  API keys redacted from error output, secrets in `.env` (gitignored).

## 📊 Measured Accuracy (10-paper benchmark)

Benchmark set: 8 landmark arXiv papers (Attention Is All You Need, BERT, GPT-3,
ResNet, Adam, Batch Normalization, GAN, Intriguing Properties of Neural
Networks) + 1 real-world paper + 1 non-paper edge case. Ground truth from
arXiv metadata.

* **Title accuracy: 100%** on all evaluated papers (exact match)
* **Author extraction: exact lists** on all evaluated papers — including a
  31-author paper and names with diacritics (Böhm, Łukasz)
* **Edge case:** non-research document correctly returns empty authors

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, Uvicorn, SQLite
* **Frontend:** Streamlit
* **AI Service:** Google AI Studio (Gemini, structured JSON output); Hugging Face optional
* **Utilities:** PyMuPDF, `python-dotenv`, `requests`

## ⚙️ Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/vaibhavtiwariz/Docent.git
    cd Docent
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\Activate.ps1
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Create a `.env` file** in the root directory:
    ```
    # Default provider (free): get a key at https://aistudio.google.com/apikey
    GOOGLE_API_KEY="AIzaXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

    # Optional: use Hugging Face instead (needs paid Inference Providers credits)
    # LLM_PROVIDER="huggingface"
    # HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ```

## ▶️ Usage

Two terminals:

1.  **Terminal 1 — Backend API**
    ```bash
    uvicorn api:app --reload
    ```
2.  **Terminal 2 — Frontend**
    ```bash
    streamlit run frontend_app.py
    ```

Then open the Streamlit URL, upload a PDF, review the extracted metadata,
correct anything, and hit **Save Corrected Metadata**.

## 📊 Evaluation

1. Drop test PDFs into `eval/`.
2. Copy `eval/ground_truth.example.json` → `eval/ground_truth.json` and fill in
   true titles/authors.
3. Run `python eval.py` — per-paper results plus summary title accuracy and
   mean author F1.

## 🔌 API Endpoints

* `POST /curate-document/` — upload a PDF, get `{"title", "authors"}`.
* `POST /save-correction/` — store a human-reviewed correction
  (AI output vs. corrected values) in SQLite.

## 🔭 Future Scope

1. More fields: abstract, venue, year, DOI, keywords, references
2. Batch/folder ingestion with a processing queue
3. Per-field confidence scores + active learning (route low-confidence
   extractions to human review first)
4. Reference parsing and citation-graph construction
5. Multi-language paper support
6. "Ask your papers" — RAG search over the curated corpus
7. One-click export to BibTeX / CSL-JSON / Zotero

## 💼 Where This Pattern Is Used

Intelligent Document Processing (IDP): AWS Textract, Azure Document
Intelligence, UiPath. Scholarly-PDF incumbent: GROBID. Reference managers
(Zotero, Mendeley) and repository ingestion pipelines (arXiv, Semantic
Scholar) do this exact job in production.
