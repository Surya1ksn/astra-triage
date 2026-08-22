# Stage 2: Classification, LLM Client, and RAG Retrieval (~45 min)

## Files in scope

- `astra/config.py` — hardcoded secret + string-typed thresholds (bug #1)
- `astra/classifier.py` — broken ranking + unnormalized confidence (bug #2)
- `astra/llm_client.py` — stub proxy call to implement
- `astra/retrieval.py` — TF-IDF retrieval to implement
- `data/knowledge_base/*.md` — already provided, don't need changes

Each file has a `STAGE 2 TODO` docstring at the top explaining exactly
what's wrong and what "done" looks like. Work through them in this order:

1. **Config first.** Nothing else can be tested sensibly until
   `CLASSIFICATION_THRESHOLD` / `RETRIEVAL_THRESHOLD` are real floats and
   the hardcoded key is gone. Read secrets from env, keep the offline
   fallback working with no `.env` at all.

2. **Classifier.** Fix the ranking comparison and normalize confidence
   into `[0, 1]`. Sanity check by hand: a ticket that says "my card was
   charged twice, please refund" should classify as `billing` with a
   confidence clearly above `ASTRA_CLASSIFICATION_THRESHOLD`.

3. **Retrieval.** Implement `load_documents()`, build a TF-IDF index in
   `KnowledgeBase.__init__`, implement `search()` and `search_relevant()`.
   Sanity check: querying "I was charged twice for my subscription"
   should surface `billing-refunds.md` above the relevance threshold, and
   a nonsense query like "purple giraffe skateboard" should return nothing
   relevant.

4. **LLM client.** Implement `_call_proxy` (plain `urllib` POST is fine —
   don't add a new dependency for this). Make sure `complete()` still
   works with no key/base URL set (offline stub path).

## Quick manual smoke test

```bash
python -c "
from astra.classifier import classify
from astra.retrieval import KnowledgeBase

c = classify('Overcharged on my invoice', 'I was charged twice this month, please refund the extra charge.')
print(c)

kb = KnowledgeBase()
for doc, score in kb.search_relevant('I was charged twice for my subscription'):
    print(doc.title, score)
"
```

## Acceptance criteria for this stage

- [ ] No secrets in source. `git grep -i "sk-astra"` returns nothing.
- [ ] Thresholds are floats, validated in `[0, 1]`.
- [ ] `classify()` returns the true highest-scoring category with a
      normalized confidence.
- [ ] `KnowledgeBase.search()` / `search_relevant()` work and return
      sensible results on the smoke test above.
- [ ] `search_relevant()` returns `[]` when nothing clears the threshold
      (used later for escalation routing).
- [ ] `llm_client.complete()` works with and without proxy config set.
- [ ] Committed incrementally, not as one blob.
