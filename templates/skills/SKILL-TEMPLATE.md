# SKILL 템플릿 — 호출형 하네스 노출

하네스를 Codex Skills, Claude Code 등 스킬/슬래시 커맨드 형태로 호출하고 싶을 때 사용한다. 설치했다면 아래 스킬 본문도 하네스의 실행 규율로 취급한다.

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
description: {{TARGET}} 하네스의 실행 팀을 호출한다. 사용자가 "하네스 실행", "하네스 돌려줘", "다음 작업 진행", "이 요청 라우팅해서 처리"를 요청하거나 세션을 하네스 기준으로 재개할 때 사용. 요청 라우팅, 영향분석, 작업 위임, 평가 요청까지 수행한다.
---

# {{SKILL_NAME}}

## 사용 조건

- 이 스킬은 `{{HARNESS_ROOT}}/HARNESS.md`와 `{{HARNESS_ROOT}}/team/TEAM-ARCHITECTURE.md`가 존재할 때만 사용한다.
- 인자가 주어지면 작업 요청 또는 작업 큐 필터로 해석한다.
- 인자가 없으면 `{{HARNESS_ROOT}}/state/state.json`의 `next_action`을 따른다.

## 절차

1. `{{HARNESS_ROOT}}/HARNESS.md`를 먼저 읽고 세션 시작 프로토콜의 읽기 예산을 따른다.
2. `{{HARNESS_ROOT}}/team/TEAM-ARCHITECTURE.md`를 읽고 실행 팀과 평가 레인의 역할을 확인한다.
3. 런타임 위임 모드를 정한다. Claude에서는 `.claude/agents/{{SKILL_NAME}}-*.md` 에이전트를 이름으로 호출한다. 다른 런타임은 지원되는 서브에이전트 도구에 `team/agents/` 정의와 최소 입력을 전달한다. 미지원일 때만 인라인 수행하고 `team_mode:inline`과 사유를 journal에 기록한다.
4. `{{HARNESS_ROOT}}/state/state.json`에서 `phase`, `next_action`, `current`, `queue`, `improve`를 확인한다. 새 단위 착수 전 RETRO-CHECK가 발동했거나 미적용 회고 제안서가 있으면 `{{SKILL_NAME}}-retro` 절차를 먼저 자동 실행한다.
5. 콜드스타트 3문항에 파일 근거로 답한다: 목적과 현재 단계 / 즉시 수행할 다음 행동 / 완료 판정 evaluator.
6. 요청 또는 next_action을 `{{SKILL_NAME}}-request-router`에 위임해 primary/secondary/work_units로 나눈다.
7. 복합·교차 영향 작업이면 `{{SKILL_NAME}}-impact-analyst`에 위임해 리스크 브리프를 만든다. 단순 작업이면 축약 실행 사유를 기록한다.
8. `{{SKILL_NAME}}-task-coordinator`가 기존 규칙·내부 하네스·작업 단위를 확정하고 `{{SKILL_NAME}}-task-worker`에 단일 단위를 위임한다.
9. 작업 직후 사용자 재호출을 기다리지 않고 `{{SKILL_NAME}}-eval` 절차를 자동 실행한다. 평가 증거 없는 pass 처리는 하지 않는다.
10. fail이면 RECOVERY가 사건당 한 번 실패 카운터를 갱신하게 한다. 반복 실패, evaluator 공백, 콜드스타트 fail이면 `{{SKILL_NAME}}-retro`를 자동 개시한다.
11. 종료 시 `{{HARNESS_ROOT}}/recovery/CHECKPOINT.md` 규격으로 state를 갱신하고, `{{HARNESS_ROOT}}/ledger/journal.jsonl`에 append-only로 기록한다.
12. 잔여 fail, 미실행 evaluator, 인라인 폴백, 인간 승인 게이트 대기 상태는 최종 보고에 숨기지 않는다.

## 불변 조건

- evaluator 없는 작업 단위는 실행하지 않는다.
- 평가 기록 없는 pass 처리는 없다.
- 인간 승인 게이트는 승인 없이 통과하지 않는다.
- `state.json`의 `next_action`은 비워두지 않고, `journal.jsonl`은 append-only로만 다룬다.
- fail은 보고에서 숨기지 않는다.
```

---

## 평가 스킬: `{{SKILL_NAME}}-eval`

```markdown
---
name: {{SKILL_NAME}}-eval
description: {{TARGET}} 하네스의 평가 팀 레인을 실행한다. 사용자가 "하네스 평가", "검증 돌려", "완료 판정", "오류검출 집계", "evaluator 확인"을 요청하거나 작업 단위 pass/fail 판정이 필요할 때 사용.
---

# {{SKILL_NAME}}-eval

## 사용 조건

- `{{HARNESS_ROOT}}/team/TEAM-ARCHITECTURE.md`와 `{{HARNESS_ROOT}}/loops/EVAL-LOOP.md`가 존재할 때만 사용한다.
- 인자가 주어지면 unit id 또는 평가 대상 파일/범위로 해석한다.
- 인자가 없으면 `{{HARNESS_ROOT}}/state/state.json`의 `current` 또는 첫 번째 `todo` unit을 평가 대상으로 삼는다.

## 절차

1. `{{HARNESS_ROOT}}/HARNESS.md`, `{{HARNESS_ROOT}}/team/TEAM-ARCHITECTURE.md`, `{{HARNESS_ROOT}}/loops/EVAL-LOOP.md`를 읽는다.
2. 평가 대상 unit의 evaluator와 pass 조건을 확인한다. 없으면 실행하지 않고 `fail(structural:no-evaluator)`로 보고한다.
3. `{{SKILL_NAME}}-verification-runner`에 위임해 `{{EVALUATOR_COMMANDS}}` 또는 unit evaluator를 실행하고 명령·cwd·exit code·핵심 출력을 보존한다.
4. 원본 증거를 `{{SKILL_NAME}}-evaluation-lead`에 넘겨 pass 조건과 대조한 verdict를 받는다. 실행자의 설명만으로 pass 처리하지 않는다.
5. fail이면 `{{SKILL_NAME}}-defect-counter`에 위임해 실패 키와 유형을 확정한다.
6. fail 사건을 RECOVERY에 넘겨 `state/state.json`의 `improve.fail_counts[키]`를 사건당 정확히 한 번 올린다. 반복 실패·평가 공백·콜드스타트 fail이면 `{{SKILL_NAME}}-retro`를 자동 개시한다.
7. `{{HARNESS_ROOT}}/ledger/journal.jsonl`에 append-only eval·count·handoff 기록을 남긴다.

## 불변 조건

- evaluator 없는 작업 단위는 pass 처리하지 않는다.
- 원본 실행 증거 없는 pass는 없다.
- evaluator 약화는 평가 결과가 아니라 하네스 변경이며, `DECISIONS.md` 기록이 필요하다.
```

---

## 회고 스킬: `{{SKILL_NAME}}-retro`

```markdown
---
name: {{SKILL_NAME}}-retro
description: {{TARGET}} 하네스의 보강 루프를 개시한다. 사용자가 "하네스 회고", "하네스 개선", "반복 실패 분석", "팀 구조 보강"을 요청하거나 RETRO-CHECK 트리거가 발동했을 때 사용.
---

# {{SKILL_NAME}}-retro

## 사용 조건

- `{{HARNESS_ROOT}}/loops/IMPROVE-LOOP.md`와 `{{HARNESS_ROOT}}/ledger/journal.jsonl`이 존재할 때만 사용한다.
- 인자가 주어지면 회고 범위로 해석한다. 예: 실패 키, unit id, 기간, 특정 evaluator, 팀 역할.

## 절차

1. `{{HARNESS_ROOT}}/HARNESS.md`의 설계 방향과 파일 맵을 확인한다.
2. `{{HARNESS_ROOT}}/team/TEAM-ARCHITECTURE.md`에서 실행 팀과 평가 레인의 현재 책임 경계를 확인한다.
3. `{{HARNESS_ROOT}}/state/state.json`의 `improve` 카운터와 `next_action`을 읽는다.
4. `{{HARNESS_ROOT}}/ledger/journal.jsonl`에서 인자 또는 트리거에 해당하는 최소 범위만 읽는다.
5. `{{SKILL_NAME}}-improvement-coordinator`에 읽기 전용 입력을 넘겨 반복 실패·평가 공백·라우팅/위임 누락을 겨냥한 보강안 1~2개를 제안서로 받는다.
6. 오케스트레이터가 다음 태스크 경계에서 제안서를 자동 적용한다. 인간 승인 게이트에 해당할 때만 적용 전 사용자 승인을 기다린다.
7. 하네스 문서를 고치면 관련 파일 맵, `team/`, `ledger/DECISIONS.md`, `state/state.json`을 같은 변경 단위에서 갱신한다.
8. 적용 후 콜드스타트와 원 evaluator를 다시 실행한다. fail이면 최대 3회까지 보완하고, 3회 후 잔여 fail은 숨기지 않는다. pass한 경우 이번에 겨냥한 실패 키만 리셋한다.
9. evaluator 완화, 게이트 우회, fail 은폐를 개선안으로 제안하지 않는다. 필요한 경우 대체 evaluator 또는 사용자 승인 대기 상태를 제안한다.
10. 회고 결과는 최종 보고에 적용 변경, 검증 결과, 남은 위험으로 나눠 기록한다.
```
