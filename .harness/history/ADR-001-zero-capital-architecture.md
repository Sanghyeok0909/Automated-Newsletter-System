ADR 001: Zero-Capital 인프라 및 기술 스택 선정
Date: 2026-09-16
Status: Accepted
Context:
초기 자본금 $0.00의 제약 하에서 매일 대량의 영문 텍스트를 처리하는 자율형 뉴스레터 비즈니스를 설계해야 함. 비용이 발생하는 클라우드 컴퓨팅(AWS EC2)이나 유료 API(OpenAI Pro) 구독은 핵심 지침에 위배됨.

Decision:

AI Model: 월 고정 비용 없이 충분한 추론 및 번역 성능을 제공하는 Google AI Studio의 Gemini Flash 무료 티어를 채택함.

Automation: 상시 구동되는 VM 호스팅 대신 매일 1회 실행되는 서버리스 GitHub Actions를 채택함.

CMS: 별도의 데이터베이스, 웹 호스팅, 이메일 발송 비용을 100% 제거하기 위해 Substack을 채택함.

Consequences:

(Positive) 인프라 비용이 $0로 고정되어 비즈니스 런웨이(Runway)가 무한대로 확보됨.

(Negative) 트래픽 밀집 시간대에 GitHub Actions cron 스케줄러의 지연이 발생할 수 있음.

(Mitigation) 지연 시간을 흡수하기 위해 파이프라인 실행 시작 시간을 목표 발행 시간보다 30분 앞당겨 스케줄링함.
