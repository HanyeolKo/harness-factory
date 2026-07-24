---
name: build-agent
description: 생성된 런타임 중립 하네스에 프로젝트 역할 기반 agent를 추가하거나 수정하고 공통 명세·역할 파일·Claude/Codex/Gemini adapter를 원자적으로 동기화한다. 사용자가 agent, coordinator, worker, reviewer, evaluator 역할이나 권한·handoff를 만들거나 바꾸려 할 때 사용한다.
---

# build-agent

생성된 하네스의 agent 한 역할을 공통 정본에서 변경한다. 대상에 `harness/harness-spec.json`이 없으면 이 스킬 대신 `build-harness`를 사용한다.

## 팩토리 확인

1. `scripts/resolve_factory.py`를 실행해 `FACTORY_ROOT`를 확정한다.
2. `FACTORY_ROOT/skills/build-harness/references/RUNTIME-CONTRACT.md`와 대상의 `harness/harness-spec.json`을 읽는다.
3. 첫 경로 인자를 대상으로, 나머지를 역할 목적과 제약으로 해석한다. 경로가 없으면 현재 작업 디렉터리를 사용한다.

## 절차

1. **DISCOVER** — 대상 domain, 기존 agent, handoff, evaluator, root 규칙을 확인한다. 같은 책임이 이미 있으면 중복 역할보다 기존 역할 확장을 우선 검토한다.
2. **DEFINE** — lower-kebab-case ID, lane, capabilities, domains, access, `fast|balanced|deep` tier, 입력·출력·handoff를 확정한다.
3. **GUARD** — 쓰기 권한 확대, 파괴적 동작, 외부 발신이 생기면 기존 또는 신규 approval gate를 연결한다.
4. **SPEC FIRST** — `harness-spec.json`의 agents/domains/orchestration을 먼저 변경한다. 정상 handoff DAG에 개선·재시도 역방향 edge를 넣지 않는다.
5. **BUILD COMMON** — `harness/team/agents/<role-id>.md`와 `TEAM-ARCHITECTURE.md`를 갱신한다.
6. **ADAPT PREFLIGHT** — provider adapter를 쓰기 전에 `python <FACTORY_ROOT>/scripts/validate_runtime_neutral.py <target> --provider-path-preflight`를 실행하고 exit 0을 확인한다. provider 경로가 절대 경로·lexical traversal·symlink escape로 target 밖을 가리키면 실패하며, 그때는 provider 디렉터리·파일을 생성·쓰기·이동하거나 우회 경로를 사용하지 않는다.
7. **ADAPT** — 선택 runtime 모두에 thin wrapper를 생성한다: Claude `.claude/agents`, Codex `.codex/agents`, Gemini `.gemini/agents`. 공통 역할 의미를 adapter에 복제하지 않는다.
8. **RECORD** — `ledger/DECISIONS.md`에 역할 변경 이유와 영향 범위를 남기고 `pending_events`에 `agent-change`와 필요한 `adapter-change`를 중복 없이 추가한다. 진행 상태와 append-only journal은 보존한다.
9. **VERIFY** — `verify-harness`를 실행하고 영향받은 원 evaluator를 재실행한다. parity가 pass→fail로 바뀌면 `parity-fail`을 중복 없이 추가한다.

## 원자성

spec, 공통 역할, 모든 선택 adapter, 문서 투영, 결정 기록을 한 변경 단위로 취급한다. 일부만 성공하면 완료로 보고하지 말고 잔여 불일치를 명시한다. adapter만 직접 수정하거나 evaluator·gate를 약화하지 않는다.
