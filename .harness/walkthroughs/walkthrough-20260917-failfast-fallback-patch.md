Walkthrough: Multi-Model Fallback & Fail-Fast Governance Patch
Date: 2026-09-17
Domain: DevOps / CI-CD
Status: Completed

Execution Log
Root Cause Discovered: CI/CD 실패 원인은 수집기(fetcher)가 아닌 LLM 분석기(analyzer.py)의 429 Quota Exceeded (gemini-3.8-flash의 무료 쿼터 소진) 및 이를 무조건 catch하여 빈 배열을 반환하던 '에러 삼킴(Silent Failure)' 구조였음.

Multi-Model Fallback Implemented: gemini-3.5-flash-lite, gemini-3.1-flash-lite, gemini-3.6-flash, gemini-3.8-flash 풀을 구성하여 429 에러 발생 시 즉시 잔여 쿼터를 보유한 모델로 자동 전환하는 로직 구축.

Fail-Fast Architecture Enforced: analyzer.py와 generator.py 모두 분석/발행 기사가 0건일 경우 sys.exit(1)로 비정상 종료하여 GitHub Actions가 즉시 실패를 인지하고 가짜 성공(False Positive)을 원천 차단함.

Local Verification Succeeded: 로컬 파이프라인 테스트 결과 10/10개 기사가 gemini-3.5-flash-lite를 통해 전량 정상 분석되었으며 dist/ 산출물(Markdown/HTML) 생성을 완료함.
