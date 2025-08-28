# 🧰 LangGraph Support Ticket Resolution Agent (Multi‑Step Review Loop)

This project implements a production‑style support agent using **LangGraph**. It takes a support ticket (`subject`, `description`), **classifies** it, performs **RAG retrieval** per category, **drafts** a response, runs a **policy/quality review**, and if needed **refines & retries** (up to 2 review cycles). If still not compliant, it **escalates** and logs into a CSV for human follow‑up.

## ✅ Features
- Classification into **Billing**, **Technical**, **Security**, **General** (LLM‑driven w/ offline fallback)
- Category‑aware **RAG** using lightweight **TF‑IDF** over local knowledge base files
- Draft generation via LLM (or template fallback)
- Automated **policy review** (LLM or rules fallback) that can **reject** and return actionable feedback
- **Retry loop** (max **2** attempts) that refines retrieval using reviewer feedback
- **Escalation path** writes to `data/escalation_log.csv` with full trace
- Built for **LangGraph CLI dev server** (checkpoints via SQLite)

---

## 🗂 Project Structure

```
support-agent-langgraph/
├─ graph.py                     # LangGraph entrypoint used by `langgraph dev`
├─ client.py                    # Simple CLI runner without dev UI
├─ app/
│  ├─ __init__.py
│  ├─ state.py                  # Typed state
│  ├─ classifier.py             # Classification node
│  ├─ retriever.py              # Category-aware RAG node
│  ├─ drafter.py                # Draft generation node
│  ├─ reviewer.py               # Review & policy check node
│  ├─ escalation.py             # Finalize / Escalate nodes
│  ├─ policies.py               # Support guidelines for reviewer
│  └─ utils/
│     ├─ __init__.py
│     └─ rag_index.py          # TF-IDF index per category
├─ data/
│  ├─ knowledge/
│  │  ├─ Billing/*.md
│  │  ├─ Technical/*.md
│  │  ├─ Security/*.md
│  │  └─ General/*.md
│  └─ escalation_log.csv
├─ demo/
│  ├─ tickets.jsonl             # Example tickets (happy path, retry, escalation)
│  ├─ demo_script.md            # What to show in the video
│  └─ run_demo.sh               # Quick demo script
├─ requirements.txt
├─ .env.example
└─ README.md
```

---

## 🚀 Quickstart

> **Prereqs:** Python 3.10+ recommended.

1) **Clone / open** this folder and create a virtual env:
```bash
cd support-agent-langgraph
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

2) **Install dependencies:**
```bash
pip install -r requirements.txt
```

3) Create a `.env` file (copy from `.env.example`) and set your **OpenAI** key:
```bash
cp .env.example .env
# edit .env and set OPENAI_API_KEY=...  (and optionally OPENAI_MODEL=gpt-4o-mini)
```

> ✅ You can run with no LLM by setting `DRY_RUN_NO_LLM=1` in `.env`, but reviewers expect an LLM-backed run.

4) **Start the LangGraph dev server:**
```bash
langgraph dev
```
- The dev UI should open in your browser.
- It uses a local SQLite checkpoint in `checkpoints.sqlite` to persist state.
- The CLI automatically discovers the compiled `graph` object in `graph.py`.

5) **Run a sample ticket via the dev UI** or with the CLI runner:
```bash
python client.py --subject "Login failure on mobile" --description "App shows 403 after 2FA on iOS 17"
```

---

## 🧪 Demo Scenarios

We include 3 tickets in `demo/tickets.jsonl`:
- **Happy path**: passes review on first attempt
- **Retry path**: first draft rejected, refined retrieval, second draft approved
- **Escalation**: fails twice → escalates to CSV

Use:
```bash
bash demo/run_demo.sh
```

---

## 🧱 Design Notes

- **Graph**: `START → classify → retrieve → draft → review → (finalize | refine | escalate) → END`
- **Retry loop**: On reject, reviewer feedback is injected into a refined retrieval query, and we try again. After `attempts >= 2`, route to `escalate`.
- **RAG**: Lightweight TF‑IDF (scikit‑learn) over local markdown files under `data/knowledge/<Category>`. This keeps deps minimal and avoids an external vector DB. You can swap `rag_index.py` for FAISS/chroma easily.
- **LLM Abstractions**: Each node handles both LLM and offline fakes (so the app still runs without keys).
- **Logging/Traceability**: State carries drafts, feedback, and attempt counts; escalation logs complete context to CSV.

---

## 📹 Recording Your Demo Video

Open `demo/demo_script.md` and follow the step‑by‑step flow to record a short screencast (happy path, retry, escalation). Submit the video file or a link alongside your repo.

---

## 🧯 Troubleshooting

- **`langgraph: command not found`** → Ensure `pip install -r requirements.txt` in the active venv.
- **OpenAI auth errors** → Set `OPENAI_API_KEY` in `.env`, confirm billing/access, try a smaller model (e.g., `gpt-4o-mini`).
- **No LLM output / timeouts** → Temporarily set `DRY_RUN_NO_LLM=1` to validate the graph logic.
- **Nothing retrieved** → Ensure the knowledge files exist under `data/knowledge/*`.

---

## 📜 License
MIT (for assessment submission convenience)
