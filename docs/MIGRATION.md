# 기존 하네스 개선·융화 가이드

기존 standalone `.claude/skills/build-harness` 또는 `.codex/skills/build-harness`, 고정 역할 기반 `harness/`, Claude 전용 control tower를 런타임 중립 구성과 융화하는 절차입니다. 기존 하네스에서 다시 호출하면 전면 재생성이 아니라 개선을 기본값으로 사용합니다.

## 모드 결정

- `create`: 기존 하네스 자산이 없을 때만 새로 생성
- `improve`: 유효한 runtime-neutral `harness-spec.json`이 있을 때 현재 정본을 기준으로 부족한 부분만 보강
- `reconcile`: 부분 구성·과거 형식·런타임 전용 control tower를 inventory한 뒤 공통 정본에 점진적으로 흡수

사용자가 명시하지 않아도 기존 자산이 발견되면 `improve` 또는 `reconcile`을 선택합니다. 삭제·이름 변경·기존 의미 교체가 필요하면 자동 적용하지 않고 정확한 경로·필드와 선택지를 보고합니다.

## 보존 원칙

다음은 새로 만들지 말고 기존 기록을 보존합니다.

- `harness/state/`
- `harness/ledger/journal.jsonl`
- `harness/ledger/DECISIONS.md`
- 기존 메모리 문서와 `harness/memory/INDEX.md`
- 사용자 작성 `CLAUDE.md`, `AGENTS.md`
- 기존 프로젝트별 evaluator와 승인 gate

특히 journal은 append-only입니다. 새 schema로 바꾼다는 이유로 이전 event를 재작성하지 않습니다.

## 1. 현재 구성 확인

- standalone `build-harness` 사본 위치
- 기존 실행·평가·회고 skill 이름
- `.claude/agents/`의 역할과 handoff
- `.codex/skills/` 같은 과거 비표준 출력
- root rules와 `.codex/config.toml`
- 진행 중 queue, next_action, fail counter
- 실제로 통과해야 하는 evaluator

변경 전에 현재 ref, 원 validator/evaluator 결과, 파일별 관리 주체, state/ledger backup 위치를 기록합니다. 이 목록이 전후 보존 manifest가 됩니다.

## 2. plugin 설치 확인

Claude:

```text
/harness-factory:build-harness
```

Codex:

```text
$harness-factory:build-harness
```

namespaced skill이 보이지 않으면 마이그레이션을 시작하지 말고 [설치 가이드](SETUP.md)를 먼저 확인합니다.

## 3. 자연어로 마이그레이션 요청

별도 플래그를 가정하지 말고 보존할 상태와 원하는 adapter를 호출에 명시합니다.

Claude 예:

```text
/harness-factory:build-harness "D:\workspace\step_fps"의 기존 harness와 Claude control tower를 분석해줘.
state와 append-only ledger, 기존 evaluator를 보존하고 runtime-neutral spec으로 전환한 뒤
Claude와 Codex adapter를 모두 생성해줘.
```

Codex 예:

```text
$harness-factory:build-harness 기존 fixed-team harness를 마이그레이션해줘.
진행 중 queue와 failure count는 유지하고, 프로젝트 경계에서 역할을 다시 도출해.
```

## 4. delta plan으로 공통 spec에 흡수

전체 템플릿을 다시 렌더링하지 않고 항목을 `unchanged`, `add`, `modify-proposed`, `conflict`, `approval-required`로 분류합니다. 기존 ID와 의미가 현재 프로젝트 경계에 맞으면 재사용하고 부족한 capability만 추가합니다.

- 기존 project/router/coordinator 관계 → `domains`, `agents`, `orchestration.handoffs`
- 실행·평가·회고·도메인 skill → `skills`와 `harness/skills/<skill-id>/SKILL.md`
- 검증 명령과 판정 기준 → `evaluators`
- fail threshold와 retro 주기 → `loops`
- Claude/Codex별 모델명 → agent의 추상 `model_tier` + adapter 매핑
- 기존 승인 조건 → `approval_gates`와 waiting 상태
- 기존 메모리·조사 요약·외부 프로젝트 문서 → `memory/INDEX.md`에 원래 경로·요약·읽기 시점·출처·검증일·상태로 색인

역할 이름이 기존 8개와 같더라도 자동으로 유지할 이유는 없습니다. 실제 domain과 capability가 같은 경우에만 보존하고, 병합·분리 근거를 D-001에 기록합니다.

spec `1.0`은 그대로 읽을 수 있습니다. 개선 시 spec `1.1`의 `memory` 계약과 `harness/memory/INDEX.md`를 추가하는 호환 업그레이드를 제안하되, 기존 메모리 파일을 강제로 이동하거나 덮어쓰지 않습니다.

## 5. native adapter 재생성

Claude:

- 기존 `CLAUDE.md` 보존 + 관리 블록 upsert
- `.claude/skills/<skill-id>/SKILL.md`
- `.claude/agents/<namespace>-<role-id>.md`

Codex:

- 기존 `AGENTS.md` 보존 + 관리 블록 upsert
- `.agents/skills/<skill-id>/SKILL.md`
- name/description/developer_instructions를 가진 `.codex/agents/<namespace>-<role-id>.toml`
- 기존 `.codex/config.toml` 보존 + 전역 agent limits 병합

과거 `.codex/skills/<generated-skill>`은 새 표준 출력이 아닙니다. 새 Codex skill이 `.agents/skills`에서 확인될 때까지 삭제하지 않습니다.

## 6. 검증

다음이 모두 pass한 뒤에만 기존 bootstrap 사본을 제거합니다.

1. spec parse·참조·DAG
2. 공통 agent와 두 adapter의 agent/skill parity
3. Claude namespaced 호출
4. Codex `$` namespaced 호출
5. cold-start 목적·next_action·evaluator 복원
6. 기존 원 evaluator
7. state queue와 fail counter 보존
8. ledger append-only 보존
9. root 사용자 규칙과 unrelated TOML 설정 보존
10. memory index 필수 열·active 경로·중복 ID/경로 검사
11. 전후 보존 manifest 비교와 기준선 대비 새 회귀 없음

## 7. 정리

검증 후 제거 후보:

- 프로젝트에 복사했던 standalone `.claude/skills/build-harness`
- 과거 bootstrap용 `.codex/skills/build-harness`
- spec에 없는 stale namespaced agent
- 새 `.agents/skills`와 중복되는 과거 generated skill

삭제 전에 새 plugin 호출과 rollback ref를 인도 보고에 기록합니다.

## 롤백

1. 생성된 managed block과 adapter만 이전 상태로 복원
2. 보존한 `state/`와 `ledger/` 유지
3. 기존 standalone skill을 다시 enable
4. 기존 factory ref 또는 commit으로 고정
5. 원 evaluator와 cold-start 재실행
6. 실패 원인을 새 journal event와 DECISIONS에 기록

롤백에서도 기존 memory index 행과 사용자 메모리를 삭제하지 않습니다. 새 항목이 무효화됐다면 `superseded` 또는 `archived`로 표시하고 근거를 남깁니다.

롤백에서도 journal line을 삭제하거나 fail counter를 임의로 낮추지 않습니다.
