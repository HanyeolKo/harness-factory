---
name: build-harness
description: 대상 프로젝트를 분석해 런타임 중립 에이전트 팀·스킬·오케스트레이션·평가·자기개선 하네스를 설계하고 Claude와 Codex 네이티브 어댑터로 생성한다. 사용자가 하네스 구성, 에이전트 팀 생성, /harness:harness 같은 호출형 구성, Claude와 Codex 공용 오케스트레이션을 요청할 때 사용한다.
---

# build-harness

대상 프로젝트에 호출 가능한 실행 하네스를 만든다. 고정 역할 묶음을 복사하지 말고, 프로젝트의 실제 경계·기존 규칙·검증 수단을 분석해 공통 명세를 먼저 확정한 뒤 Claude와 Codex 어댑터를 같은 의미로 렌더링한다.

## 팩토리 확인

1. 이 스킬 폴더의 `scripts/resolve_factory.py`를 실행한다. 이미 팩토리 경로를 알면 `--factory-root <path>`를, 오프라인 요청이면 `--offline`을 사용한다.
2. stdout의 절대 경로를 `FACTORY_ROOT`로 사용한다. 계약 검증이 실패하면 임의 템플릿으로 대체하지 않는다.
3. `FACTORY_ROOT/docs/CONSTRUCTOR-PROTOCOL.md`, `skills/build-harness/references/RUNTIME-CONTRACT.md`, `principles/`, `interview/QUESTION-BANK.md`, `CHECKLIST.md`를 읽는다.
4. 사용한 로컬 경로 또는 자격증명을 제거한 저장소 URL·ref·commit을 생성 하네스의 D-001에 기록한다.

## 입력 해석

- 첫 경로 인자는 대상 프로젝트다. 없으면 현재 작업 디렉터리를 사용한다.
- 나머지 문장은 하네스 목적, 범위, 보존할 기존 구성으로 선반영한다.
- 런타임을 명시하지 않으면 `claude`와 `codex` 어댑터를 모두 만든다.
- 기존 `harness/`가 있으면 `state/`와 append-only `ledger/`를 보존한 채 마이그레이션한다.

## 생성 절차

1. **DISCOVER** — 대상의 규칙 파일, README/docs, 모듈 경계, 빌드·테스트·CI, 기존 skills/agents/hooks를 읽는다. 코드로 알 수 없는 목적·승인 게이트·완료 기준만 최대 2회 배치로 질문한다.
2. **DESIGN** — 프로젝트에 필요한 역할과 스킬을 도출한다. 역할 ID는 프로젝트 의미를 드러내는 lower-kebab-case로 정하고, 각 역할에 lane, 책임, 입력/출력, 권한, `fast|balanced|deep` 모델 티어, handoff를 부여한다. 라우팅·실행·증거수집·판정·실패계상·개선 역량은 빠뜨리지 않되 별도 역할 수는 프로젝트 복잡도에 맞춘다.
3. **SPECIFY** — `templates/harness-spec.json.tmpl`과 `schema/harness-spec.schema.json`을 사용해 `<target>/harness/harness-spec.json`을 정본으로 만든다. 각 skill은 `instructions` 공통 경로를, 승인 조건은 `approval_gates`를 갖는다. orchestration은 참조가 유효한 DAG로, 재시도·보강 환류는 DAG 밖 improvement 계약으로 기록한다.
4. **BUILD COMMON** — 공통 `harness/` 문서·상태·ledger·동적 `team/agents/<role-id>.md`와 `harness/skills/<skill-id>/SKILL.md`를 렌더링한다. 모든 실행 단위에는 evaluator와 pass 조건을 연결한다.
5. **ADAPT CLAUDE** — 선택된 경우 `CLAUDE.md` 관리 블록, 공통 skill과 byte-identical한 `.claude/skills/<skill-id>/SKILL.md`, `.claude/agents/<namespace>-<role-id>.md`를 만든다. agent access를 tools·disallowedTools·permissionMode로 제한하고, 기존 파일은 관리 블록 밖을 보존하며 실제 namespaced agent 이름으로 위임한다.
6. **ADAPT CODEX** — 선택된 경우 `AGENTS.md` 관리 블록, 공통 skill과 byte-identical한 `.agents/skills/<skill-id>/SKILL.md`, name·description·developer_instructions를 가진 `.codex/agents/<namespace>-<role-id>.toml`, 전역 limits를 담은 `.codex/config.toml`을 만든다. 기존 TOML 설정은 구조적으로 병합한다.
7. **VALIDATE** — `python <FACTORY_ROOT>/scripts/validate_runtime_neutral.py <target>`와 `CHECKLIST.md`를 실행한다. 중첩 spec 키, 공통 참조, DAG, evaluator, 승인 게이트, access, 양쪽 역할·스킬 byte parity, TOML/frontmatter, 미치환 placeholder, 콜드스타트를 확인한다.
8. **REPAIR** — fail을 최대 3회 보완한다. 공통 의미 변경은 `harness-spec.json`과 참조된 공통 skill에 먼저 반영하고 모든 선택 어댑터를 재생성한다. 원 evaluator와 parity 검증을 다시 실행하며 잔여 fail은 숨기지 않는다.

## 인도

생성 트리, 공통 역할/스킬 표, Claude와 Codex 호출명, 모델 티어 매핑, 적용한 기본값, 검증 결과, 보존한 기존 상태, 잔여 위험을 보고한다. 생성된 기본 호출명은 `<namespace>`, `<namespace>-eval`, `<namespace>-retro`다.

## 불변 조건

- 런타임 어댑터가 공통 명세와 다른 역할·스킬·평가 의미를 갖게 하지 않는다.
- evaluator와 원본 증거 및 journal 기록 없는 pass는 허용하지 않는다.
- 인간 승인 게이트를 우회하지 않는다.
- 어댑터를 정본으로 삼지 않는다. 의미 변경은 공통 명세에 먼저 반영한다.
- 인라인 폴백, 미실행 evaluator, 잔여 fail을 보고에서 숨기지 않는다.
