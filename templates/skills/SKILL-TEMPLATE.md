# SKILL 템플릿 — 하네스 루프 노출

하네스를 Codex Skills, Claude Code 등 스킬/슬래시 커맨드 형태로 호출하고 싶을 때 사용한다.
대상 프로젝트에 설치하는 것은 선택 사항이지만, 설치했다면 아래 스킬 본문도 하네스의 실행 규율로 취급한다.

## 설치 위치

| 런타임 | 권장 위치 |
|---|---|
| Codex | `$CODEX_HOME/skills/{{SKILL_NAME}}/SKILL.md` 또는 프로젝트가 정한 skills 디렉토리 |
| Claude Code | `.claude/skills/{{SKILL_NAME}}/SKILL.md` |

설치 후 `{{HARNESS_ROOT}}/HARNESS.md`의 파일 맵 또는 대상 프로젝트의 규칙 파일에 스킬 위치를 한 줄로 등재한다.

---

## 실행 스킬: `{{SKILL_NAME}}`

```markdown
---
name: {{SKILL_NAME}}
description: {{TARGET}} 하네스의 세션 시작 프로토콜과 실행 루프를 개시한다. 사용자가 "하네스 실행", "하네스 돌려줘", "다음 작업 진행"을 요청하거나 세션을 하네스 기준으로 재개할 때 사용.
---

# {{SKILL_NAME}}

## 사용 조건

- 이 스킬은 `{{HARNESS_ROOT}}/HARNESS.md`가 존재할 때만 사용한다.
- 인자가 주어지면 작업 큐 필터로 해석한다. 예: 특정 unit id, 파일 경로, 평가 대상 이름.
- 인자가 없으면 `{{HARNESS_ROOT}}/state/state.json`의 `next_action`을 따른다.

## 절차

1. `{{HARNESS_ROOT}}/HARNESS.md`를 먼저 읽고, 세션 시작 프로토콜의 읽기 예산을 따른다.
2. `{{HARNESS_ROOT}}/state/state.json`에서 `phase`, `next_action`, `current`, `queue`, `improve`를 확인한다.
3. 콜드스타트 3문항에 파일 근거로 답한다: 목적과 현재 단계 / 즉시 수행할 다음 행동 / 완료 판정 evaluator.
4. 하나라도 답할 수 없으면 실행하지 않는다. `improve.coldstart_fail = true`로 기록하고 `{{HARNESS_ROOT}}/loops/IMPROVE-LOOP.md`를 따른다.
5. 실행 전 현재 작업 단위에 evaluator가 있는지 확인한다. evaluator 없는 작업 단위는 실행하지 않는다.
6. `{{HARNESS_ROOT}}/loops/EXECUTION-LOOP.md`의 단위 선택 → 실행 → 평가 → 기록 → RETRO-CHECK 순서를 그대로 수행한다.
7. 종료 시 `{{HARNESS_ROOT}}/recovery/CHECKPOINT.md` 규격으로 state를 갱신하고, `{{HARNESS_ROOT}}/ledger/journal.jsonl`에 append-only로 기록한다.
8. 잔여 fail, 미실행 evaluator, 인간 승인 게이트 대기 상태는 최종 보고에 숨기지 않는다.

## 불변 조건

- evaluator 없는 작업 단위는 실행하지 않는다.
- 평가 기록 없는 pass 처리는 없다.
- 인간 승인 게이트는 승인 없이 통과하지 않는다.
- `state.json`의 `next_action`은 비워두지 않고, `journal.jsonl`은 append-only로만 다룬다.
- fail은 보고에서 숨기지 않는다.
```

---

## 회고 스킬: `{{SKILL_NAME}}-retro`

```markdown
---
name: {{SKILL_NAME}}-retro
description: {{TARGET}} 하네스의 보완 루프를 개시한다. 사용자가 "하네스 회고", "하네스 개선", "반복 실패 분석"을 요청하거나 RETRO-CHECK 트리거가 발동했을 때 사용.
---

# {{SKILL_NAME}}-retro

## 사용 조건

- `{{HARNESS_ROOT}}/loops/IMPROVE-LOOP.md`와 `{{HARNESS_ROOT}}/ledger/journal.jsonl`이 존재할 때만 사용한다.
- 인자가 주어지면 회고 범위로 해석한다. 예: 실패 키, unit id, 기간, 특정 evaluator.

## 절차

1. `{{HARNESS_ROOT}}/HARNESS.md`의 설계 방향과 파일 맵을 확인한다.
2. `{{HARNESS_ROOT}}/state/state.json`의 `improve` 카운터와 `next_action`을 읽는다.
3. `{{HARNESS_ROOT}}/ledger/journal.jsonl`에서 인자 또는 트리거에 해당하는 최소 범위만 읽는다.
4. `{{HARNESS_ROOT}}/loops/IMPROVE-LOOP.md`의 트리거 판정 → 원인 분류 → 개정안 작성 → 검증 계획 순서를 따른다.
5. 하네스 문서를 고치면 관련 파일 맵, `ledger/DECISIONS.md`, `state/state.json`을 같은 변경 단위에서 갱신한다.
6. evaluator 완화, 게이트 우회, fail 은폐를 개선안으로 제안하지 않는다. 필요한 경우 대체 evaluator 또는 사용자 승인 대기 상태를 제안한다.
7. 회고 결과는 최종 보고에 적용 변경, 검증 결과, 남은 위험으로 나눠 기록한다.
```
