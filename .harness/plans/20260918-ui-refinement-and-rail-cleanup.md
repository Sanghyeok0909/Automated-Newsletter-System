# [Plan] End-to-End UI Refinement and Far-Left Rail Cleanup

- **Task ID**: 20260918-ui-refinement-and-rail-cleanup
- **Domain**: software
- **Target Deliverables**:
  - `src/generator.py` (Durable template engine source)
  - `dist/index.html` (Regenerated production entry point)
  - `dist/newsletter-2026-09-18.html` (Regenerated archive HTML)
  - `.harness/walkthroughs/walkthrough-20260918-ui-refinement.md` (Verification evidence)

## 1. Objective & Scope
Execute an end-to-end user interface overhaul of the Zero-Capital Newsletter web application:
1. **Far-Left Rail Cleanup**: Remove the five redundant circular publisher icons (phone, unicorn, gear, microscope, newspaper) beneath the home control in the far-left rail. Retain solely the primary home control (`⚡`) with a deterministic briefing reset action.
2. **Publisher Navigation Preservation**: Retain all 5 publisher channels (The Verge, TechCrunch, Ars Technica, MIT Tech Review, The Information) in the context sidebar navigation with accurate dynamic counts.
3. **Design System & Layout Upgrade**:
   - Compact, information-dense editorial dashboard inspired by Discord macro-navigation and Toss micro-interactions.
   - Consolidated CSS tokens (neutral slate dark theme, crisp light theme, responsive surface elevation, typography hierarchy).
   - Concise reader-oriented briefing header (replaces oversized demo hero).
   - Real-time client-side search composable with publisher filters.
   - Honest and accurate metadata indicators (Zero-Capital design target label, dynamic article count, reading time estimate, non-misleading status badges).
   - Mobile-first responsive accessibility (slide-over drawer with Escape key support, touch targets >= 44px, no horizontal scroll at 360px).
4. **Zero Data Loss**: Preserve all 10 curated articles, summaries, AI insights, and source URLs.

## 2. Core Invariants & Engineering Constraints
- **Durable Source Invariant**: All layout and markup changes MUST be implemented in `src/generator.py` so that automated scheduled pipeline executions (`python src/generator.py`) reliably persist the redesign.
- **Data Integrity**: 100% preservation of article payload (`src/translated_articles.json` -> `dist/`). Zero truncation or dropping of publisher articles (specifically verifying Ars Technica and multi-word publisher names).
- **Zero Cost & Zero Dependency**: Pure Vanilla CSS3 and ES6 JavaScript. No paid fonts, no runtime CDNs, no tracking scripts.
- **Workflow Stability**: Preserve GitHub Actions continuous deployment (`.github/workflows/daily-pipeline.yml`).

## 3. Step-by-Step Action Plan
- [ ] Phase 1: Baseline inspection and data capture of existing article payload.
- [ ] Phase 2: Refactor `src/generator.py` template engine:
  - Remove unwanted 5 rail buttons, tooltips, and divider; streamline home control.
  - Implement cohesive CSS token architecture (dark/light, focus rings, reduced motion).
  - Implement concise briefing hero and typography hierarchy.
  - Integrate client-side instant search bar and empty state.
  - Upgrade metadata panel with honest zero-capital metrics and per-source status badges.
  - Add mobile responsive navigation drawer and toggle button.
- [ ] Phase 3: Execute `python src/generator.py` to regenerate `dist/index.html` and `dist/newsletter-2026-09-18.html`.
- [ ] Phase 4: Local HTTP server verification, multi-viewport inspection, and data integrity test script.
- [ ] Phase 5: Commit, push to `origin/main`, monitor CI/CD deployment, and record .harness walkthrough.

## 4. Verification & Validation Protocol
- Run Python compilation and execution: `python src/generator.py`.
- Run automated verification script validating article counts (10/10), publisher channel presence, search functionality, and absence of removed rail icons.
- Verify HTTP preview serving at `localhost:8080`.
- Verify Git status and push to GitHub remote.
