# Walkthrough: Gemini Quota Repair, Circuit Breaking, and Pipeline Bounding

- **Date**: 2026-09-19
- **Task ID**: 20260919-quota-repair-and-bounds
- **Domain**: Content Pipeline Reliability & CI/CD Safety
- **Status**: Completed & Verified with Mocks

## 1. Incident Root Cause Analysis (Run #19)
- **Primary Root Cause**:
  - `src/analyzer.py` processed articles sequentially (1 request per candidate). For 14-16 candidates, with an active Google Gemini Free Tier daily limit of 20 RPD (`GenerateRequestsPerDayPerProjectPerModel-FreeTier`), single-article queries depleted the remaining daily quota mid-run.
  - When the daily quota 429 was returned, `src/analyzer.py` lacked daily quota classification and treated it as an article-specific failure. It cascaded through all remaining candidates and backups, repeatedly hitting the exhausted quota bucket.
  - The SDK automatically waited ~18 seconds per 429 response. Multiplying across 6 candidates and 4 fallback attempts resulted in the 31m 27s hang.
  - Because `print()` calls lacked unbuffered output and `.github/workflows/daily-pipeline.yml` lacked `timeout-minutes`, intermediate log lines were blocked in memory and the runner had no upper time bound.

## 2. Implemented Architecture & Safety Controls
1. **Publisher-Level Bounded Batching**:
   - Each publisher's candidate pool (up to 5 articles) is batched into a single structured prompt with stable IDs (`art_1` .. `art_5`).
   - Expected inference requests for a 25-article edition reduced from 25 to **exactly 5 requests** (1 per publisher).
   - Maximum requests including single retry: **10 requests**, safely below the 20 RPD daily quota.
   - Exact ID-set validation prevents hallucinations or dropped articles.
2. **Structured Error Classification & Circuit Breaking**:
   - Explicitly distinguishes `DAILY_QUOTA_EXHAUSTED` from transient `TRANSIENT_RATE_LIMIT` (RPM/TPM), `AUTHENTICATION_ERROR`, and `MODEL_UNAVAILABLE`.
   - On daily quota exhaustion: immediately trips the circuit breaker, halts further requests, and records honest shortfall (`status: "daily_quota_exhausted"`). Zero backup candidate cascade.
3. **Execution & Transport Timeouts**:
   - `request_options={"timeout": 45.0}` on LLM calls.
   - `timeout-minutes: 10` configured on GitHub Actions `build` job.
   - `PYTHONUNBUFFERED: "1"` and `sys.stdout.reconfigure(line_buffering=True)` for real-time CI logs.
4. **Publication & Deployment Safety Guard**:
   - In `.github/workflows/daily-pipeline.yml`: `push` events run unit/mock validation tests and static site validation without making live Gemini API calls, protecting exhausted daily quota.
   - Live curation executes exclusively on `schedule` (cron) and manual `workflow_dispatch`.
   - `dist/index.html` non-empty validation ensures a failed run never overwrites a valid edition with an empty page.
5. **Financial News Protection**:
   - Refined `is_eligible_candidate` with `FINANCIAL_MARKET_TOKENS` so titles like "CoreWeave Prices $3.7 Billion Convertible Bond Offering" are properly preserved while true shopping deals ("Save $50", "% off", "promo code") are filtered.

## 3. Verification & Validation Outcomes
- **Automated Test Suite**:
  - `tests/test_quota_and_pipeline_bounds.py` (13 test scenarios covering daily quota precedence, circuit breaking, batch validation, timeout bounds, financial headline protection, checkpointing, and publication safety).
  - `tests/test_curation_expansion.py` (7 tests).
  - Total: 20 tests ran in 0.135s — ALL PASSED (OK).
- **UI Regression Suite**:
  - `tests/test_ui_integrity.py` passed cleanly on `dist/index.html` and `dist/newsletter-2026-09-18.html`.
- **Code Hygiene**:
  - `git diff --check` passed cleanly with 0 errors.
