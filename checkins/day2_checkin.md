### Day 2 Daily Check-in Note (Project Concierge)

1. What I finished today: Integrated Groq LLM (`openai/gpt-oss-120b`) with source citation, built `OrderService` tool with defensive handling for malformed tracking (`ORD-1004`) and 30-min cancellation checks, built and executed 10-attack adversarial suite (100% defense rate), and ran full 40-question eval benchmark (67.5% accuracy).
2. What I did not finish, and why: Latency/cost ablation and automated regression testing were deferred to Day 3 per the schedule.
3. The biggest problem I hit and how I handled it: In evaluation, several honest refusals on international shipping were caused by BM25 ranking general FAQs over specific memos; documented in `FAILURES.md` as a retrieval-recall bottleneck rather than hallucination.
4. A decision I made that I am unsure about: Strictly returning "I don't know" when documents don't match, which lowered the raw accuracy score but completely eliminated hallucinations (100% on unanswerable queries).
5. Where I need input, if anywhere: Desired trade-off between aggressive retrieval (top_k=5 vs top_k=3) versus prompt context token cost.
6. Hours actually spent: 5.5 focused hours.
7. Plan for tomorrow: Optimize latency and token cost to meet operational constraints, build formal human escalation routing, package CLI, and write the 4-page founder decision memo.

