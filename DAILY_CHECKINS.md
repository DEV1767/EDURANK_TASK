# SwiftCart Support Assistant - Daily Check-in Notes

### Day 1 Daily Check-in Note (Project Concierge)

1. What I finished today: Audited 8 knowledge docs, built header-based chunker with metadata tagging, implemented BM25 retriever with obsolete/internal filtering, and created a 40-question eval set with baseline benchmark (Hit@3 = 75.0%).
2. What I did not finish, and why: LLM answer generation and tool integration were intentionally deferred to Day 2 to focus on measurement and data quality first, per Day 1 goal.
3. The biggest problem I hit and how I handled it: Naive retrieval fetched obsolete 2022 policies; solved by enriching chunks with `status: ACTIVE` metadata and filtering out obsolete files before indexing.
4. A decision I made that I am unsure about: Excluding `Internal_support_handbook.md` from the customer retriever causes legal-escalation eval questions to miss document retrieval, though it ensures zero confidential leakage.
5. Where I need input, if anywhere: Confirming whether Tier 1 agents/bots should ever quote discretionary exceptions or strictly maintain public return rules.
6. Hours actually spent: 5.5 focused hours.
7. Plan for tomorrow: Integrate Groq LLM with source citation, connect mock order API with timeout/retry wrappers, and run the 10-case adversarial attack test suite.



---

### Day 2 Daily Check-in Note (Project Concierge)

1. What I finished today: Integrated Groq LLM (`openai/gpt-oss-120b`) with source citation, built `OrderService` tool with defensive handling for malformed tracking (`ORD-1004`) and 30-min cancellation checks, built and executed 10-attack adversarial suite (100% defense rate), and ran full 40-question eval benchmark (67.5% accuracy).
2. What I did not finish, and why: Latency/cost ablation and automated regression testing were deferred to Day 3 per the schedule.
3. The biggest problem I hit and how I handled it: In evaluation, several honest refusals on international shipping were caused by BM25 ranking general FAQs over specific memos; documented in `FAILURES.md` as a retrieval-recall bottleneck rather than hallucination.
4. A decision I made that I am unsure about: Strictly returning "I don't know" when documents don't match, which lowered the raw accuracy score but completely eliminated hallucinations (100% on unanswerable queries).
5. Where I need input, if anywhere: Desired trade-off between aggressive retrieval (top_k=5 vs top_k=3) versus prompt context token cost.
6. Hours actually spent: 5.5 focused hours.
7. Plan for tomorrow: Optimize latency and token cost to meet operational constraints, build formal human escalation routing, package CLI, and write the 4-page founder decision memo.



---

### Day 3 Daily Check-in Note (Project Concierge)

1. What I finished today: Evaluated Design A (120B) vs Design B (20B) measuring 40.9% speedup and 80% cost reduction, built `EscalationGuardrail` for immediate safety/legal handoffs, created 7-test automated pytest regression suite (100% pass), packaged interactive CLI (`run.py`), and completed the 4-page founder report (`REPORT.md`).
2. What I did not finish, and why: Hybrid dense-sparse reranking was scoped for future 2-week roadmap to prioritize defensibility and complete system packaging within the 5-6 hour daily timebox.
3. The biggest problem I hit and how I handled it: Evaluating model trade-offs without sacrificing factual accuracy; solved by benchmarking latency and grounding across identical support scenarios on Groq.
4. A decision I made that I am unsure about: Recommending 20B model for production to maximize speed and cost efficiency over the 120B model's slightly richer stylistic synthesis.
5. Where I need input, if anywhere: Feedback on the proposed 20% phased pilot rollout outlined in the executive report.
6. Hours actually spent: 5.0 focused hours.
7. Plan for tomorrow: Conduct final clean-checkout verification, record the 5-8 minute walkthrough video demo, and prepare for the 30-minute live defense.


