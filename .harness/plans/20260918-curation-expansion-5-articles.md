# [Plan] Expand Daily Curation to Top 5 Articles per Publisher

- **Task ID**: 20260918-curation-expansion-5-articles
- **Domain**: software
- **Target Deliverables**:
  - `src/config.py` (Centralized pipeline configuration & canonical publisher registry)
  - `src/fetcher.py` (Candidate pooling, URL canonicalization, deterministic importance ranking)
  - `src/analyzer.py` (Batching, candidate fallback replacement on LLM failure, honest shortfall handling)
  - `src/generator.py` (Data-driven counts, dynamic reading-time, status badges, historical edition compatibility)
  - `tests/test_curation_expansion.py` (Comprehensive focused tests for ranking, deduplication, shortfall, and generation)
  - `.harness/walkthroughs/walkthrough-20260918-curation-expansion.md` (Verification evidence)

## 1. Objective & Scope
Transition the Zero-Capital Newsletter daily curation pipeline from 2 articles per publisher to the top 5 most important eligible articles per publisher across the 5 canonical tech media outlets:
1. The Verge (`verge`)
2. TechCrunch (`techcrunch`)
3. Ars Technica (`arstechnica`)
4. MIT Technology Review (`mit`)
5. The Information (`theinformation`)

Target capacity:
- Up to 5 selected articles per publisher.
- Up to 25 articles per daily edition.
- Exactly 5 per publisher when sufficient valid candidates and successful analyses exist.
- Honest shortfall reporting when candidates or analyses fall short.

## 2. Architecture & Design Principles
- **Centralized Configuration**: `ARTICLES_PER_PUBLISHER = 5`, `CANDIDATES_PER_PUBLISHER = 20`, `FRESHNESS_HOURS = 24`.
- **Durable Source Only**: All pipeline behavior lives in `src/`.
- **Approved UI Preservation**: Retain 100% of the approved Discord macro + Toss micro visual layout, CSS tokens, and interaction models. Make counts and reading time data-driven.
- **Deterministic Heuristic Importance Ranking**:
  - Material industry, market, or public impact: 0–35
  - Relevance to technology and business decisions: 0–25
  - Substantive developments supported by evidence: 0–20
  - Recency within 24h rolling window: 0–10
  - Original reporting / distinctive evidence: 0–10
  - Promotional / shopping exclusions (-100 / filter)
  - Deterministic tie-breaking by `(score, timestamp, title_hash)`
- **Analyzer Robustness**:
  - Process candidates per publisher up to the target of 5.
  - If an individual candidate fails LLM analysis, draw the next ranked eligible candidate from that publisher's pool.
  - Maintain bounded rate limiting (4s delay) and fallback model pool.
- **Zero Hallucination / Honest Shortfall**:
  - Never fabricate articles to fill a quota.
  - Display actual counts (`5/5건`, `3/5건`, etc.).

## 3. Step-by-Step Action Plan
- [ ] Phase 1: Create `src/config.py` with authoritative parameters and publisher metadata.
- [ ] Phase 2: Refactor `src/fetcher.py` to extract up to 20 candidates per publisher, strip tracking URLs, apply deterministic ranking rubric, and output ranked candidate pool with backups.
- [ ] Phase 3: Update `src/analyzer.py` to target 5 successful analyses per publisher using backup candidates on failures.
- [ ] Phase 4: Update `src/generator.py` for data-driven reading time and dynamic publisher status badges.
- [ ] Phase 5: Implement `tests/test_curation_expansion.py` and verify all tests pass.
- [ ] Phase 6: Commit, push to `origin/main`, monitor GitHub Actions CI/CD run, and verify live deployment.
