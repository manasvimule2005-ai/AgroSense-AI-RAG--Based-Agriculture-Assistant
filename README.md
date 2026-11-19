# AgroSense AI: RAG-Based Agriculture Assistant 🌱

AgroSense AI is a full-stack, enterprise-grade agricultural intelligence application built with **Streamlit**, **LangChain**, **FAISS**, and **SQLite**. It empowers farmers, agronomists, extension workers, and agriculture researchers to query verified agronomic documents with strict source citations, analyze crop health, manage pests and diseases, and evaluate soil health.

---

## 🌾 Features & Architecture

- **Dashboard**: Real-time operational metrics (indexed documents, vector chunks, queries answered, system health).
- **AI Assistant**: Grounded RAG conversational engine with strict source attribution, chunk previews, and suggested prompt chips.
- **Crop Guide**: Interactive directory of staple crops (Rice, Wheat, Tomato, Maize, Cotton) with agronomic parameters (sowing, harvest, soil, water).
- **Pest & Disease**: Symptom-based diagnostic matching with biological, cultural, and chemical controls.
- **Soil Health Evaluator**: Multi-parameter NPK, pH, EC, and organic carbon calculator based on ICAR Soil Health Card standards.
- **Knowledge Base Manager**: In-app document manager supporting PDF, TXT, DOCX, and MD with automated chunking and FAISS re-indexing.
- **Chat History**: Full transcript persistence in SQLite with search, export, and session continuation.
- **Usage Analytics**: Visualized telemetry covering queries over time, response latency, and source citation distribution.
- **Settings**: Modular LLM configuration (Google Gemini, OpenAI, Anthropic Claude, Ollama) and vector retrieval tuning.

---

## 🚀 Quick Start Guide (Windows)

### 1. Prerequisites
- Python 3.10 - 3.12 installed (ensure "Add python.exe to PATH" was checked during setup).
- Open VS Code in this directory (`C:\Users\Manasvi\.gemini\antigravity\scratch\AgroSenseAI`).

### 2. Environment Setup
In PowerShell (`Ctrl + ~`):
```powershell
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure API Keys
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```
Open `.env` and set your preferred provider and key (e.g., `GEMINI_API_KEY=your_key_here`).

### 4. Run the Application
```powershell
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.
