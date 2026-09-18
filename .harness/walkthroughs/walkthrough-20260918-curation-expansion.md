# Walkthrough: Daily Curation Expansion to Top 5 Articles per Publisher

- **Date**: 2026-09-18
- **Task ID**: 20260918-curation-expansion-5-articles
- **Domain**: Content Pipeline / Curation & Architecture
- **Status**: Completed / Ready for CI/CD Deployment

## 1. Scope & Acceptance Criteria
- **A. Centralized Authoritative Configuration**:
  - Defined `ARTICLES_PER_PUBLISHER = 5` and `CANDIDATES_PER_PUBLISHER = 20` in `src/config.py`.
  - Defined canonical publisher registry (The Verge, TechCrunch, Ars Technica, MIT Tech Review, The Information).
- **B. Candidate Retrieval & Sanitization**:
  - Bounded candidate pool (up to 20 candidates per publisher) within a rolling 24-hour window.
  - Stripped tracking parameters (`utm_*`, `oc=5`, etc.) while preserving essential query parameters.
  - Filtered commercial/shopping deals, coupon lists, and trivial login stubs.
- **C. Deterministic Heuristic Importance Ranking**:
  - Evaluated material industry impact (0–35), business/tech relevance (0–25), substantive developments (0–20), recency (0–10), and original reporting (0–10).
  - Deterministic tie-breaking by `(score, timestamp, title_hash)`.
- **D. Analyzer Robustness & Candidate Fallback**:
  - Targets 5 successful analyses per publisher.
  - Automatically falls back to the next ranked eligible candidate if an LLM analysis call fails.
  - Preserved Korean editorial output schema (`korean_title`, `summary_3_lines`, `business_insight`).
- **E. Honest Shortfall Handling & Data-Driven UI**:
  - Preserved approved Discord+Toss hybrid layout without visual redesign.
  - Dynamically calculated reading time from content length (`약 {reading_minutes}분`).
  - Rendered truthful publisher status badges (`5/5건 완료 🟢`, `{cnt}/5건 · 기사 부족 🟡`, `0/5건 · 수집 실패 🔴`).
  - Preserved 100% compatibility with historical 10-article editions.

## 2. Durable Source Changes
- `src/config.py`: Authoritative configuration, publisher registry, and scoring signal keywords.
- `src/fetcher.py`: Candidate pooling, URL canonicalization, eligibility filtering, deterministic scoring, and ranked candidate output.
- `src/analyzer.py`: Multi-model fallback, per-publisher target of 5, candidate replacement on failure, and shortfall reporting.
- `src/generator.py`: Data-driven reading times, dynamic channel counts, honest status badges, and centralized config integration.
- `tests/test_curation_expansion.py`: 7 automated unit and integration tests covering configuration, URL cleaning, eligibility, ranking rubric, 25-article generation, and partial/historical editions.
- `tests/test_ui_integrity.py`: Updated to assert data-driven counts across hero and metadata panels.

## 3. Verification & Validation Outcomes
- **Unit & Pipeline Tests** (`tests/test_curation_expansion.py`):
  - Ran 7 tests in 0.041s — all passed (OK).
- **UI Integrity Regression** (`tests/test_ui_integrity.py`):
  - Passed on both `dist/index.html` and `dist/newsletter-2026-09-18.html`.
- **Git Hygiene**: `git diff --check` passed cleanly with 0 errors and no trailing whitespaces.
- **Local Preview Server**: Omitted per explicit instructions; focused test fixtures used.
