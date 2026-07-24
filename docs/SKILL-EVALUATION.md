# SKILL-EVALUATION — 0.2.0 평가 계약

기준일: 2026-07-24
대상: 일곱 factory skill, schema 1.1, Claude·Codex·Gemini adapter, event-driven harness evaluation

실제 pass는 자동 검사와 fixture evidence가 있을 때만 기록합니다.

## 수용 기준

| 영역 | 통과 조건 |
|---|---|
| 프로젝트 소유권 | state·ledger·report가 대상에 남고 factory가 중앙 수집하지 않는다. |
| 스킬 surface | 일곱 스킬이 설치 runtime에 노출된다. |
| evaluator link | 모든 `skills[].evaluator`가 존재하고 kind별 scope/type 계약과 일치한다. |
| provider 중립성 | Claude, Codex, Gemini가 같은 의미이며 canonical skill과 byte-identical하다. |
| watched path | exact managed artifact drift·삭제는 검출하고 unrelated user 파일은 무시한다. |
| 저비용 trigger | checker가 읽기 전용이고 `none|targeted|full`만 반환하며 LLM을 호출하지 않는다. |
| 안전 라우팅 | input-invalid는 구조 복구로, adapter/parity는 verify-first로 간다. |
| targeted 제한 | 세 reason만 고정 결정적 suite에 매핑되고 임의 LLM targeted 평가가 없다. |
| ACK | 완료 run만 recorder가 ACK하고 같은 mandatory 신호를 반복하지 않는다. |
| 개선 gate | full regression/하네스 귀속 뒤에만 개선한다. |

## Schema와 스킬별 평가

schema 1.1 매핑:

- entry/evaluation/verification/domain skill → `scope: task`; verification은 구조 validator
- harness-evaluation/improvement skill → `self_evaluation.evaluator`, `scope: harness`, `type: experiment`

### build-harness

- common contract, evaluator links, targeted suite, checker/recorder/state를 생성한다.
- canonical은 별도 hash하고 `watched_paths`에는 선택 provider의 exact root guidance, spec skill projection, namespaced agent wrapper, 생성 config만 둔다.

### build-agent / build-skill / build-evaluator

- 공통 정본을 먼저 바꾸고 모든 선택 provider를 재투영한다.
- skill 변경은 evaluator link를, harness evaluator 변경은 `type: experiment`를 보존한다.
- 변경 event와 exact watched path를 원자적으로 갱신한다.

### verify-harness

- schema, refs, DAG, access, root block, byte parity, watched drift, cold-start를 결정적으로 검사한다.
- cold-start false→true와 parity pass→fail에 pending event를 추가한다.
- effect evaluation이나 improvement를 추론하지 않는다.

### evaluate-harness

- `input-invalid:*`는 effect evaluation/LLM 없이 verify/recovery로 보낸다.
- `adapter-change|parity-fail`은 parity pass 뒤에만 평가한다.
- targeted는 `evaluation/suites/targeted.json`, full은 experiment evaluator를 사용한다.
- 완료된 targeted/full 뒤 recorder를 호출한다.

### improve-harness

- 완료·ACK된 full report의 하네스 귀속 또는 명시적 근거 요청이 필요하다.
- 1~2개 변경 후 task structural evaluator, 원 task evaluator, full experiment를 재실행한다.
- full recorder ACK 뒤 improved 또는 사전 허용 neutral만 수용한다.

## Checker fixture

| 사례 | checker 기대 | runtime route |
|---|---|---|
| 신호 없음 | `none` | 종료, LLM 없음 |
| deterministic sample | `targeted` | fixed sample metric |
| cost regression | `targeted` | fixed cost metric |
| retry pressure | `targeted` | fixed retry metric |
| full interval/success regression | `full` | full experiment |
| canonical/component event | `full`, mandatory | verify 필요 시 선행 |
| adapter/parity event | `full`, mandatory | parity pass 전 평가 금지 |
| cold-start false→true | `full`, mandatory | structural 상태 확인 |
| malformed input | `full`, mandatory, `input-invalid:*` | verify/recovery only; effect/LLM 금지 |
| non-mandatory + budget/cooldown | `none` + deferred | 종료 |

## Targeted suite fixture

- reason key가 `cost-regression|retry-pressure|deterministic-sample` 세 개뿐이다.
- 각 key가 기존 task evidence/rolling state에서 계산할 deterministic metric 목록을 가진다.
- checker에 없는 reason을 suite가 임의 실행하지 않는다.
- targeted 경로에서 blind/LLM judge를 열지 않는다.

## Recorder fixture

완료 run에 대해 다음을 검증합니다.

1. checker JSON을 평가 전 run의 `trigger.json`에 동결
2. malformed decision file, decision mismatch, stale managed hash이면 ACK 거부
3. full이면 처리 시작 pending snapshot과 frozen failure acknowledgement만 ACK
4. full이면 canonical과 선택 provider managed artifact hash, units, cooldown, verdict 갱신
5. targeted이면 last decision/verdict와 cooldown만 갱신하고 mandatory event 보존
6. 평가 중 추가된 pending event와 failure incident 보존
7. full ACK 직후 같은 상태는 동일 mandatory 평가를 다시 열지 않음
8. ACK 뒤 새 cold-start false→true 또는 parity pass→fail은 다시 검출
9. 중단·미완료 run은 state 미변경

## Watched path fixture

- 선택 provider root guidance 수정·삭제 검출
- spec skill projection 수정·삭제 검출
- namespaced agent wrapper와 생성 provider config 수정·삭제 검출
- unrelated user skill/agent 또는 선택하지 않은 provider 변경은 hash 불변

## 교차 오판 방지

다음을 fail로 처리합니다.

1. task fail 하나로 agent 구성을 자동 수정
2. task pass를 harness improved로 간주
3. `input-invalid:*`를 full LLM evaluation으로 전달
4. parity fail을 verify 없이 effect evaluation
5. 모호한 targeted LLM judge 실행
6. evaluator 완화로 treatment 통과
7. recorder 없이 pending event를 수동 clear

## 자동 검증

```powershell
python scripts\test_runtime_neutral_contract.py
python scripts\test_self_evaluation_trigger.py
python scripts\skill_smoke_build_harness.py
python scripts\validate_runtime_neutral.py <target-project>
```

cold-start는 목적, next action, 연결 task evaluator, pending event, 마지막 effect verdict를 파일에서 복원해야 합니다. 과거 대화를 요구하면 fail입니다.
