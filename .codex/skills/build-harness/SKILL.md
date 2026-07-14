---
name: build-harness
description: 대상 프로젝트를 분석해 런타임 중립 에이전트 팀·스킬·오케스트레이션·평가·자기개선 하네스를 설계하고 Claude와 Codex 네이티브 어댑터로 생성한다. 사용자가 하네스 구성, 에이전트 팀 생성, /harness:harness 같은 호출형 구성, Claude와 Codex 공용 오케스트레이션을 요청할 때 사용한다.
---

# build-harness

대상 프로젝트에 호출 가능한 실행 하네스를 만들거나 기존 하네스를 점진적으로 개선한다. 고정 역할 묶음을 복사하지 말고, 프로젝트의 실제 경계·기존 규칙·검증 수단을 분석해 공통 명세를 먼저 확정한 뒤 Claude와 Codex 어댑터를 같은 의미로 렌더링한다. 기존 구성이 있으면 전면 재생성보다 보존·흡수·보강을 기본값으로 삼는다.

## 팩토리 확인

1. 이 스킬 폴더의 `scripts/resolve_factory.py`를 실행한다. 이미 팩토리 경로를 알면 `--factory-root <path>`를, 오프라인 요청이면 `--offline`을 사용한다.
2. stdout의 절대 경로를 `FACTORY_ROOT`로 사용한다. 계약 검증이 실패하면 임의 템플릿으로 대체하지 않는다.
3. `FACTORY_ROOT/docs/CONSTRUCTOR-PROTOCOL.md`, `skills/build-harness/references/RUNTIME-CONTRACT.md`, `principles/`, `interview/QUESTION-BANK.md`, `CHECKLIST.md`를 읽는다.
4. 사용한 로컬 경로 또는 자격증명을 제거한 저장소 URL·ref·commit을 생성 하네스의 D-001에 기록한다.

## 입력 해석

- 첫 경로 인자는 대상 프로젝트다. 없으면 현재 작업 디렉터리를 사용한다.
- 나머지 문장은 하네스 목적, 범위, 보존할 기존 구성으로 선반영한다.
- 런타임을 명시하지 않으면 `claude`와 `codex` 어댑터를 모두 만든다.
- 기존 `harness/`가 없으면 `create`, 유효한 runtime-neutral spec이 있으면 `improve`, 부분·레거시 구성이면 `reconcile` 모드로 분류한다. 사용자가 명시하지 않아도 기존 구성이 발견되면 개선 방향으로 잡는다.
- `improve`와 `reconcile`은 `state/`, append-only `ledger/`, 기존 evaluator·gate·사용자 규칙·메모리를 보존한다. 삭제·이름 변경·의미 교체는 자동 수행하지 않는다.

## 생성 절차

1. **DISCOVER** — 대상의 규칙 파일, README/docs, 모듈 경계, 빌드·테스트·CI, 기존 harness/skills/agents/hooks를 읽는다. 기존 하네스가 있으면 원 validator와 evaluator를 먼저 실행해 기준선을 남기고, 관리 주체·보존 대상·충돌·메모리 인덱스를 inventory한다. 코드로 알 수 없는 목적·승인 게이트·완료 기준만 최대 2회 배치로 질문한다.
2. **DESIGN** — 모드를 `create|improve|reconcile`로 확정하고 변경 없음/추가/수정 제안/충돌/승인 필요로 나눈 delta plan을 만든다. 기존 역할·스킬이 프로젝트 경계와 맞으면 재사용하고, 부족한 capability만 추가·병합한다. 새 역할에는 lower-kebab-case ID, lane, 책임, 입력/출력, 권한, `fast|balanced|deep` 모델 티어, handoff를 부여한다.
3. **SPECIFY** — `templates/harness-spec.json.tmpl`과 `schema/harness-spec.schema.json`을 사용해 `<target>/harness/harness-spec.json`을 정본으로 만든다. 기존 spec은 구조적으로 병합하고 알 수 없는 필드나 충돌을 임의로 버리지 않는다. 각 skill은 `instructions` 공통 경로를, 승인 조건은 `approval_gates`를 갖는다. orchestration은 참조가 유효한 DAG로, 재시도·보강 환류는 DAG 밖 improvement 계약으로 기록한다.
4. **BUILD COMMON** — `create`는 공통 `harness/`를 렌더링한다. `improve|reconcile`은 delta plan에 포함된 관리 파일만 갱신하고 나머지는 보존한다. 동적 `team/agents/<role-id>.md`, `harness/skills/<skill-id>/SKILL.md`, `memory/INDEX.md`를 정본과 동기화하며 모든 실행 단위에 evaluator와 pass 조건을 연결한다.
5. **ADAPT CLAUDE** — 선택된 경우 `CLAUDE.md` 관리 블록, 공통 skill과 byte-identical한 `.claude/skills/<skill-id>/SKILL.md`, `.claude/agents/<namespace>-<role-id>.md`를 만든다. agent access를 tools·disallowedTools·permissionMode로 제한하고, 기존 파일은 관리 블록 밖을 보존하며 실제 namespaced agent 이름으로 위임한다.
6. **ADAPT CODEX** — 선택된 경우 `AGENTS.md` 관리 블록, 공통 skill과 byte-identical한 `.agents/skills/<skill-id>/SKILL.md`, name·description·developer_instructions를 가진 `.codex/agents/<namespace>-<role-id>.toml`, 전역 limits를 담은 `.codex/config.toml`을 만든다. 기존 TOML 설정은 구조적으로 병합한다.
7. **VALIDATE** — `python <FACTORY_ROOT>/scripts/validate_runtime_neutral.py <target>`와 `CHECKLIST.md`를 실행한다. 중첩 spec 키, 공통 참조, DAG, evaluator, 승인 게이트, memory index, access, 양쪽 역할·스킬 byte parity, TOML/frontmatter, 미치환 placeholder, 콜드스타트를 확인한다. 기존 하네스에서는 기준선 evaluator와 보존 manifest의 전후 diff도 확인한다.
8. **REPAIR** — fail을 최대 3회 보완한다. 공통 의미 변경은 `harness-spec.json`과 참조된 공통 skill에 먼저 반영하고 모든 선택 어댑터를 재생성한다. 원 evaluator와 parity 검증을 다시 실행하며 잔여 fail은 숨기지 않는다.

## 인도

생성 트리, 적용 모드와 delta plan, 공통 역할/스킬 표, Claude와 Codex 호출명, 모델 티어 매핑, 적용한 기본값, 검증 결과, 보존·흡수·충돌한 기존 상태, memory index 상태, 잔여 위험을 보고한다. 생성된 기본 호출명은 `<namespace>`, `<namespace>-eval`, `<namespace>-retro`다.

## 기존 하네스 융화 규칙

- 같은 호출을 다시 실행하면 새 하네스를 덮어쓰지 않고 현재 spec·state·ledger·평가 결과를 입력으로 개선 후보를 도출한다.
- 사용자 소유 파일, 출처 불명 파일, 기존 ID는 보존 우선이다. 충돌은 exact field/path와 선택지를 보고하고 승인 전까지 기존 값을 유지한다.
- 관리 블록·생성 어댑터는 namespace 단위로만 upsert한다. stale 후보는 검증 완료 뒤 정리 목록으로 제시하며 자동 삭제하지 않는다.
- 전후 보존 manifest와 원 evaluator가 통과해야 개선 완료다. 기준선부터 실패했다면 새 회귀와 기존 실패를 구분해 보고한다.

## 메모리 인덱스 관리

- spec `1.1`의 `memory.index`는 `harness/memory/INDEX.md`를 가리키며 `preserve-and-reconcile` 정책을 사용한다. 기존 spec `1.0`은 읽을 수 있고, 개선 시 인덱스를 추가하는 호환 업그레이드를 제안한다.
- 지속 메모리는 `경로 | 한 줄 요약 | 언제 읽나 | 출처 | 마지막 검증 | 상태`로 색인한다. 상태·작업 큐는 `state.json`, 사건 이력은 `journal.jsonl`에 남겨 중복 저장하지 않는다.
- 메모리 생성·이동·이름 변경·대체·보관과 인덱스 갱신은 같은 변경 단위에서 수행한다. 기존 사용자 메모리는 승인 없이 삭제하거나 덮어쓰지 않는다.

## 불변 조건

- 런타임 어댑터가 공통 명세와 다른 역할·스킬·평가 의미를 갖게 하지 않는다.
- evaluator와 원본 증거 및 journal 기록 없는 pass는 허용하지 않는다.
- 인간 승인 게이트를 우회하지 않는다.
- 어댑터를 정본으로 삼지 않는다. 의미 변경은 공통 명세에 먼저 반영한다.
- 기존 사용자 구성과 지속 메모리를 명시적 승인 없이 삭제·덮어쓰기·이름 변경하지 않는다.
- 인라인 폴백, 미실행 evaluator, 잔여 fail을 보고에서 숨기지 않는다.
