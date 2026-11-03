# SwiftCart Support Assistant (Project Concierge)
> **3-Day Build Intern Challenge:** Production-grade RAG & Tool-Calling Support System with Grounding, Adversarial Defenses, and Human Escalation.

---

## 🚀 Quickstart (Clean Checkout in Under 2 Minutes)

### 1. Clone & Set Up Virtual Environment
```bash
cd Task
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b    # or openai/gpt-oss-20b for ultra-fast mode
```

---

## 💻 Running the System

### Interactive Support Assistant CLI:
Run the interactive customer support terminal:
```bash
python run.py
```
Or ask a single question directly:
```bash
python run.py --query "Where is my order ORD-1001?"
python run.py --query "What is the restocking fee for electronics?"
```

---

## 🧪 Test & Evaluation Suites

### 1. Run Automated PyTest Regression Suite (7 Tests)
Verifies obsolete document exclusion, cancellation window math, safety guardrails, and safe refusal:
```bash
pytest tests/test_regression.py -v
```

### 2. Run Adversarial Attack Benchmark (10 Vectors)
Tests prompt injections, admin code theft (`SC-OVR-7741`), and coercive refund demands:
```bash
python tests/test_adversarial.py
```
*(Result: 10/10 Defended - 100% Defense Rate)*

### 3. Run Full 40-Question Evaluation Benchmark
Scores factual accuracy, contradiction handling, unanswerable refusals, and source citations:
```bash
python tests/score_eval.py
```

### 4. Run Architecture Latency & Cost Comparison
Benchmarks Design A (120B) vs. Design B (20B) with millisecond latency timings:
```bash
python tests/compare_designs.py
```

### 5. Run Day 1 Retrieval Benchmark
Measures BM25 Hit Rate @ 1 and Hit Rate @ 3 across document passages:
```bash
python tests/test_retrieval.py
```

---

## 📁 Repository Structure

```text
├── data/
│   ├── docs/                   # 8 Knowledge base markdown files (with intentional flaws)
│   ├── orders.json             # Mock order service database (10 orders with edge cases)
│   └── eval_set.json           # 40 Ground-truth evaluation test questions
├── src/
│   ├── chunker.py              # Structural Markdown header chunker with metadata tagging
│   ├── retriever.py            # BM25 search engine with obsolete/confidential filtering
│   ├── order_service.py        # Order lookup tool with 30-min cancellation window logic
│   ├── assistant.py            # Core Groq LLM agent with grounded citations & tool calling
│   └── guardrails.py           # Pre-LLM safety & legal escalation router
├── tests/
│   ├── test_retrieval.py       # Day 1 retrieval accuracy baseline (Hit@3 = 75%)
│   ├── test_adversarial.py     # Day 2 10-attack security suite (100% defense)
│   ├── score_eval.py           # Full 40-question end-to-end benchmark evaluator
│   ├── compare_designs.py      # Day 3 latency & cost comparison (Design A vs B)
│   └── test_regression.py      # Automated pytest regression test suite (7/7 passed)
├── checkins/
│   ├── day1_checkin.md         # Official Day 1 check-in note (7-question format)
│   ├── day2_checkin.md         # Official Day 2 check-in note (7-question format)
│   └── day3_checkin.md         # Official Day 3 check-in note (7-question format)
├── notes/
│   └── plan_day2_day3.md       # Day 1 risk assessment and 2-day engineering roadmap
├── run.py                      # Production-ready CLI interface
├── FAILURES.md                 # Mandatory running log of failures, false assumptions & lessons
├── REPORT.md                   # 4-Page Executive Decision Memo for the Founder
├── requirements.txt            # Python dependencies
└── README.md                   # Complete reproduction instructions
```

---

## 📑 Core Submission Deliverables

- **`REPORT.md`**: 4-page founder decision memo strictly following Section 8 of the brief.
- **`FAILURES.md`**: 5 detailed failure & recovery log entries detailing key technical pivots.
- **`checkins/`**: Three daily check-in notes strictly adhering to Section 7 guidelines.

