# HARNESS — harness-factory 레포 지속 개선

> schema 1.1 이벤트 기반 흐름의 문서 예시다. 전체 생성 fixture나 validator 정본은 아니다.

## 소유권과 경계

이 하네스의 상태·기록·평가 결과·개선 이력은 대상 프로젝트가 소유한다. harness-factory는 최초 생성과 명시적으로 요청된 구성 변경을 돕지만 설치된 하네스를 흡수하거나 원격 운영하지 않는다.

이 예제는 `harness-spec.json`, 두 trigger script, runtime adapter를 의도적으로 생략한다. 포함·생략 범위는 `../README.md`가 정본이다.

## 목적과 판정 분리

harness-factory 레포의 문서·템플릿·검증 계약을 지속 개선한다.

| 판정 | 실행 시점 | evaluator | 결과 |
|---|---|---|---|
| task evaluation | 모든 작업 단위 | `loops/EVAL-LOOP.md` | `pass|fail` |
| harness effect evaluation | checker가 요청할 때만 | `loops/HARNESS-EVAL-LOOP.md` | `improved|neutral|regressed|inconclusive` |

## 세션 시작

1. 이 파일을 읽는다.
2. `state/state.json`에서 현재 작업·다음 행동을 확인한다.
3. `budget/CONTEXT-BUDGET.md`의 마지막 소진 기록을 읽는다.
4. `state.json.current.refs`에 명시된 파일만 추가로 읽는다.
5. 목적·다음 행동·완료 evaluator 중 하나라도 복원할 수 없으면 `improve.coldstart_fail = true`로 기록하고 `coldstart-fail` pending event를 중복 없이 추가한다.
6. `loops/EXECUTION-LOOP.md`를 시작한다.

## 태스크 경계 라우팅

완전한 생성물에서는 read-only checker를 실행한다.

```text
python harness/triggers/check_self_evaluation.py harness
```

결정값보다 `reasons`를 먼저 검사한다.

- `input-invalid:*`: effect evaluation과 LLM judge를 열지 않는다. `verify-harness`로 schema·참조·파일·adapter parity만 복구한 뒤 checker를 다시 실행한다.
- `adapter-change|parity-fail`: 선택 provider parity가 pass할 때까지 effect evaluation을 열지 않는다.
- `none`: 평가·개선 문서를 추가로 읽지 않는다.
- `targeted`: `evaluation/suites/targeted.json`의 연결 metric만 실행한다.
- `full`: frozen `trigger.json`을 입력으로 baseline/control/treatment를 비교한다.

완료된 targeted/full은 `HARNESS-EVAL-LOOP.md`의 recorder로 ACK한다. checker 결과만으로 improvement를 시작하지 않는다.

## provider 감시 artifact

실제 spec의 `watched_paths`는 선택 provider별 root guidance, 각 managed skill 파일, 각 namespaced agent 파일, 선택 config의 정확한 파일 집합이다. skill/agent root 디렉터리 전체는 감시하지 않는다.

## 축 구성

| 축 | 문서 | 계약 |
|---|---|---|
| 실행 | `loops/EXECUTION-LOOP.md` | 작업 1건씩 수행 |
| 작업 평가 | `loops/EVAL-LOOP.md` | 매 작업 완료 전 필수 |
| 하네스 평가 | `loops/HARNESS-EVAL-LOOP.md` | checker가 `targeted|full`일 때만 |
| 개선 | `loops/IMPROVE-LOOP.md` | full 평가의 회귀·하네스 결함 근거 필요 |
| 회복 | `recovery/RECOVERY-PLAYBOOK.md` | task fail 분류·회복 |
| 상태 | `state/` | 작업 상태와 자기평가 상태 분리 |
| 기록·비용 | `ledger/`, `budget/` | 평가 비용과 운영 비용 분리 |

## 세션 종료

1. `state/state.json`과 `state/self-evaluation.json`을 갱신한다.
2. `ledger/journal.jsonl`에 `session_end`를 기록한다.
3. 운영 비용과 평가 비용을 분리해 기록한다.
4. task evaluator와 필요한 구조 검증을 통과한 작업 단위만 커밋한다.

## 파일 맵

```text
examples/self-improve/harness/
├── HARNESS.md
├── ENVIRONMENT.md
├── loops/
│   ├── EXECUTION-LOOP.md
│   ├── EVAL-LOOP.md
│   ├── HARNESS-EVAL-LOOP.md
│   └── IMPROVE-LOOP.md
├── evaluation/
│   ├── EVALUATION-CONTRACT.md
│   ├── suites/targeted.json
│   └── runs/EXAMPLE-001/trigger.json
├── recovery/
├── ledger/
├── budget/
└── state/
    ├── state.json
    └── self-evaluation.json
```

`evaluation/runs/EXAMPLE-001/trigger.json`은 형식 설명용 동결 입력이다. 실행 가능한 spec·checker·recorder·adapter는 이 예제에 포함하지 않는다.
