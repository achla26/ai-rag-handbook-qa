# 📚 Handbook Q&A - Production RAG with Guardrails

> AI-powered Q&A system with **citations**, **hallucination detection**, and **confidence scoring**

## 🎯 Key Metrics

| Metric | Value |
|--------|-------|
| ✅ **Accuracy** | **100%** (10/10 tests) |
| 📝 **Citation Rate** | **100%** |
| ⚡ **Avg Latency** | **1.01s** |
| 🛡️ **Guardrails** | 3 Active |

---

## 🚀 Features

- ✅ **Cited Answers** - Every answer includes `[Source X]` references
- ✅ **Hallucination Detection** - Flags ungrounded statements
- ✅ **Confidence Scoring** - LOW confidence → "I don't know"
- ✅ **Citation Validation** - Verifies citations are real
- ✅ **FastAPI Backend** - Production-ready REST API
- ✅ **Streamlit UI** - Interactive chat interface
- ✅ **Eval Pipeline** - Automated regression testing

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Groq (llama-3.3-70b) |
| Vector DB | Qdrant |
| Embeddings | sentence-transformers |
| Backend | FastAPI |
| Frontend | Streamlit |
| Eval | Custom pipeline |

---

## 📁 Project Structure

```
├── src/
│   ├──app/
│   │   ├── core/       # Embeddings, LLM, Vector Store
│   │   ├── guardrails  # Citation, hallucination, confidence
│   │   ├── retrieval   # RAG chain, retriever
│   │   ├── ingestion   # Document loading, chunking
│   │   └── tests       # Related Tests   
│   ├── config/         # Settings management
│   ├── api/            # FastAPI routes
│   ├── evals/          # Test cases + metrics
│   ├── data/documents/ # Source documents
│   └── utils           # utils , logger
├── main.py             # API entry point
└── app.py           # Streamlit UI
```

---

## 🏃 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start Qdrant (Docker)
docker run -p 6333:6333 qdrant/qdrant

# Run API
uvicorn main:app --reload --port 8000

# Run UI (separate terminal)
streamlit run app.py

# Run Evals
python evals/run_evals.py
```

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/ingest` | Ingest documents |
| POST | `/api/v1/query` | Ask questions |
| GET | `/api/v1/stats` | Collection stats |

---

## 🛡️ Guardrails Explained

### 1. Citation Validator
Checks if `[Source X]` in answer points to real retrieved sources.

### 2. Hallucination Detector
Compares each sentence against context using semantic similarity.

### 3. Confidence Scorer
- **HIGH** (>0.6): Answer confidently
- **MEDIUM** (0.3-0.6): Answer with warning
- **LOW** (<0.3): Abstain - "I don't know"

---

## 🔮 What I'd Do Next

- [ ] Add Reranker (Cross-encoder) for better precision
- [ ] Implement hybrid search (Dense + BM25)
- [ ] Add user feedback loop for continuous improvement
- [ ] Deploy on cloud (AWS/GCP)
- [ ] Add authentication layer

---

## 👨‍💻 Author

Built as part of AI Engineering portfolio project.

---

## 📄 License

MIT
