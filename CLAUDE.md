# oh-my-agent

Claude Code plugin that generates standardized operational agents for any component using `langchain-ai/deepagents`.

## Goal

Component owner가 Claude Code에서 대화형 Q&A를 통해 자신의 서비스에 맞는 운영 에이전트를 생성할 수 있도록 한다. 어떤 컴포넌트에서 만들든 동일한 구조의 에이전트가 나온다.

## How It Works

4단계 Skills 기반 워크플로우:

1. **01-analyze-codebase** — 컴포넌트 코드를 읽고 로깅/메트릭/인프라 의존성 파악
2. **02-design-agent** — 분석 결과 기반으로 tool 목록, config, 시스템 프롬프트 설계
3. **03-generate-agent** — templates/ 참조하여 deepagents 기반 에이전트 프로젝트 생성
4. **04-validate-structure** — AST guard로 구조/네이밍/패턴 통일성 검증

## Architecture

```
guard/       AST 구조 검증기 (rules.yaml + checker.py + CLI)
tools/       레퍼런스 도구 구현 (OpenSearch, Prometheus)
templates/   생성될 에이전트 프로젝트 보일러플레이트 (.tmpl)
skills/      Claude Code 스킬 (01~04)
tests/       Guard 테스트
```

## Default Tools

- **OpenSearch** (`tools/opensearch.py`) — 로그 조회
- **Prometheus** (`tools/prometheus.py`) — 메트릭 쿼리

사용자가 Kafka, DB, 대응 API 등을 자유롭게 추가 가능.

## Guard Rules

생성된 에이전트가 반드시 지켜야 하는 규칙 (`guard/rules.yaml`):
- 필수 파일/디렉토리 존재
- tool 파일명/함수명 snake_case
- tool 파일당 public 함수 1개 + docstring 필수
- 하드코딩된 URL 금지 (config 참조 필수)

## Commands

```bash
# Guard 실행
python3 -m guard check <agent-project-path>

# 테스트
python3 -m pytest tests/ -v
```

## Non-Goals (현재)

- 알림 시스템 연동 (회사별 포맷, 추후)
- 중앙 오케스트레이션 플랫폼
- 멀티 에이전트 간 협업

## Tech Stack

- Python 3.10+
- deepagents, opensearch-py, prometheus-api-client, PyYAML
