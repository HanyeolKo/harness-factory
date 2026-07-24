# 운영·평가·개선 가이드

생성된 하네스는 프로젝트가 직접 소유하는 하나의 공통 계약과 최대 세 개의 네이티브 어댑터로 운영합니다. 팩토리는 중앙 control plane이나 하네스 상태 저장소가 아닙니다.

```text
harness/harness-spec.json
├── 공통 team / skills / loops / evaluation / state / ledger
├── Claude: CLAUDE.md + .claude/skills + .claude/agents
├── Codex:  AGENTS.md + .agents/skills + .codex/agents + .codex/config.toml
└── Gemini: GEMINI.md + .gemini/skills + .gemini/agents
```

## 정본과 쓰기 순서

`harness/harness-spec.json` schema 1.1에는 domain, agent, skill, orchestration, evaluator, approval gate, loop, runtime target, self-evaluation 정책이 들어갑니다. 각 skill 본문은 `skills[].instructions`가 가리키는 `harness/skills/<skill-id>/SKILL.md`가 정본입니다.

의미를 바꾸는 순서는 항상 같습니다.

1. 대상 프로젝트의 spec과 공통 파일 변경
2. 선택된 Claude·Codex·Gemini 어댑터 재투영
3. `verify-harness`로 구조와 parity 검증
4. 변경 이벤트를 self-evaluation state에 기록
5. 필요한 수준만 `evaluate-harness`로 효과 검증

어댑터만 직접 바꾸거나 factory 저장소에 프로젝트 state를 복사하지 않습니다.

## 일곱 스킬의 운영 역할

- `build-harness`: 아직 schema 1.1 정본이 없거나 전체 재설계가 필요한 경우
- `build-agent`: agent, role 문서, handoff, provider wrapper를 원자적으로 변경
- `build-skill`: 공통 SKILL과 각 provider 투영본을 원자적으로 변경
- `build-evaluator`: task 또는 harness-effect evaluator와 계약을 추가·수정
- `verify-harness`: 외부 LLM 없이 schema, 참조, 권한, parity, placeholder를 검증
- `evaluate-harness`: trigger 결과에 따라 targeted/full 효과 평가 수행
- `improve-harness`: full 평가에서 하네스 결함이 입증된 경우에만 개선

기존 하네스의 일부만 바꿀 때 `build-harness`를 다시 호출할 필요는 없습니다.

## 프로젝트별 팀 구성

역할 수와 이름은 고정하지 않습니다. 작은 프로젝트는 capability를 합칠 수 있고, 복합 workspace는 domain별 coordinator와 전문 worker·evaluator를 둘 수 있습니다.

다음 capability 합집합은 유지합니다.

- `routing`
- `execution`
- `verification`
- `verdict`
- `defect-counting`
- `improvement`

실행자는 산출물을 만들고, evaluator runner가 원본 증거를 만들며, verdict owner가 기준과 대조합니다. schema 1.1의 모든 `skills[].evaluator`는 존재하는 evaluator를 참조합니다: entry/evaluation/verification/domain은 `scope: task`, harness-evaluation/improvement는 `scope: harness`, `type: experiment`입니다. 작은 구성에서 한 agent가 여러 역할을 맡더라도 입력·출력·기록 단계는 분리합니다.

## 두 평가 레인

### Task evaluation

개별 작업이 완료됐는지를 판정합니다. 테스트, 빌드, 린트, 정적 검사, 도메인 루브릭이 여기에 속합니다. 작업마다 해당 evaluator를 실행할 수 있고, evidence와 verdict를 journal에 남깁니다.

### Harness-effect evaluation

하네스 변경이 실제 성과를 개선했는지를 판정합니다. 성공률, 비용, 재시도, cold-start, provider parity를 baseline/control/treatment로 비교합니다. task가 실패했다는 이유만으로 하네스 결함이라고 단정하지 않습니다.

| 구분 | Task evaluation | Harness-effect evaluation |
|---|---|---|
| 질문 | 이 작업이 완료됐는가? | 하네스 변경이 더 나은가? |
| 대상 | 작업 산출물 | agent·skill·evaluator·adapter 변경 |
| 빈도 | 작업 계약에 따름 | trigger checker가 선택 |
| 결과 | pass/fail/blocked | improved/neutral/regressed/inconclusive |
| 후속 | defect 기록 또는 작업 재시도 | 입증된 결함만 개선 후보 |

## 저비용 trigger checker

매 작업 경계에서 읽기 전용 `harness/triggers/check_self_evaluation.py`만 실행합니다. 출력은 `none|targeted|full`이며 LLM 호출, state write, `improve` 반환을 금지합니다.

완료 task를 기록하는 기존 transaction에서만 `current_unit`을 갱신하고 `units_since_full += 1`, `cooldown_remaining_units = max(0, n-1)`을 정확히 한 번 적용하며 recent/rolling 원시 evidence를 반영합니다. 이는 추가 LLM 호출이 아닌 결정적 산술입니다.

### 라우팅 우선순위

1. `input-invalid:*`이면 effect evaluation과 LLM을 열지 않습니다. `verify-harness`와 구조 복구 후 checker를 다시 실행합니다.
2. `adapter-change|parity-fail`이면 선택 provider parity가 pass하기 전 effect evaluation을 실행하지 않습니다. parity가 pass→fail로 바뀌면 `pending_events`에 `parity-fail`을 중복 없이 추가합니다.
3. 자동 경로의 `none`이면 종료합니다. 사용자가 명시한 full 평가는 raw checker JSON 전체를 `override.original`에 보존하고 top-level effective `decision: full`, `mandatory: false`, `override.kind: explicit-user-request`, original reasons 뒤 marker, 동일한 deferred reasons·hashes·`acknowledgement`를 기록합니다. evaluator와 recorder는 같은 top-level decision을 해석하며 단순 decision 변조와 구조화되지 않은 budget·cooldown 우회는 거부합니다. input-invalid와 parity 검증은 우회하지 않습니다.
4. `targeted`이면 `evaluation/suites/targeted.json`에서 reason과 정확히 연결된 결정적 metric만 실행합니다.
5. `full`이면 `scope: harness`, `type: experiment` evaluator로 baseline/control/treatment를 비교합니다.

`targeted.json`의 허용 매핑은 `cost-regression`, `retry-pressure`, `deterministic-sample`입니다. 임의 범위나 LLM targeted judge는 허용하지 않습니다.

### Mandatory와 비용 제한

canonical/agent/skill/evaluator/adapter 변경, cold-start/parity fail, 반복 failure는 mandatory full로 올립니다. success regression은 full 신호지만 비필수 평가 예산·cooldown 정책의 적용을 받습니다. cold-start가 false→true이면 `coldstart-fail`, parity가 pass→fail이면 `parity-fail`을 pending events에 기록합니다. ACK 뒤 동일 incident가 반복되지 않지만, 이후의 새 전환은 다시 검출됩니다.

`minimum_samples`는 success-rate와 cost regression 비교가 활성화되는 표본 하한일 뿐 retry나 sampling 신호를 막지 않습니다. `targeted_sample_rate`는 unit ID의 결정적 hash로 독립적인 `deterministic-sample` targeted 신호를 만듭니다. cooldown과 budget ratio는 cost/retry/sample/full-interval을 포함한 모든 비필수 신호를 유예하며 사유를 `deferred_reasons`에 남깁니다. mandatory는 유예하지 않습니다.

### 완료 ACK

평가 전에 checker JSON을 `<target-project>\harness\evaluation\runs\<run-id>\trigger.json`에 동결합니다. 완료된 targeted/full마다 그 decision file로 recorder를 호출합니다.

```powershell
python <target-project>\harness\triggers\record_self_evaluation.py <target-project>\harness --decision <targeted|full> --decision-file <target-project>\harness\evaluation\runs\<run-id>\trigger.json --verdict <improved|neutral|regressed|inconclusive>
```

recorder는 frozen trigger의 decision/reasons, current managed hashes, `acknowledgement` failure snapshot을 확인합니다. ACK decision/reasons는 변화한 rolling-metric decision으로 대체하지 않습니다. full은 처리 시작 snapshot의 pending events와 failures만 ACK하고 exact managed artifact hashes, units, cooldown, last verdict를 원자 갱신합니다. 평가 중 생긴 새 event·failure는 다음 boundary에 남습니다. targeted는 last decision·cooldown만 갱신합니다. 미완료 run에는 recorder를 호출하지 않습니다.

canonical은 별도 hash합니다. `self_evaluation.watched_paths`는 선택 provider의 root guidance 파일, spec 각 skill projection, namespaced agent wrapper, 생성 config만 나열합니다. provider root 전체와 unrelated user skill/agent는 제외합니다.

## 작업 경계 흐름

```text
entry → execution → linked task evaluator → verdict/state 기록
                                             ↓
                                   deterministic checker
                 input-invalid ─→ verify/structural recovery ─→ recheck
                 adapter/parity ─→ parity verify ─────────────→ recheck/pass
                 none ───────────→ 종료
                 targeted ───────→ fixed deterministic suite ─→ recorder ACK
                 full ───────────→ experiment evaluator ──────→ recorder ACK
                                                          └──→ attributed regression only → improve
```

`full`은 평가 강도이며 개선 명령이 아닙니다.
## 개선 적용 규칙

1. baseline과 직전 변경의 예상 효과를 명시
2. evidence에서 하네스 귀속 근거 확인
3. 한 번에 1~2개 변경만 선택
4. spec과 공통 파일을 먼저 변경
5. 선택된 모든 provider adapter 재투영
6. `verify-harness`, cold-start, 원 task evaluator 실행
7. full harness-effect evaluation으로 treatment 비교
8. improved 또는 사전 허용된 neutral만 수용
9. regression이면 rollback 가능한 변경을 되돌리고 근거 기록

평가 기준 완화, 승인 gate 우회, evidence 삭제는 개선이 아닙니다.

## 상태와 기록

- `state/state.json`: phase, queue, current, next_action의 source of truth
- `state/self-evaluation.json`: managed artifact hashes, pending/ACK snapshot, 최근 decision/verdict, baseline/recent 지표, budget·cooldown
- `ledger/journal.jsonl`: append-only 작업·evidence·verdict·trigger·evaluation 기록
- `ledger/DECISIONS.md`: schema, evaluator, 역할, provider 매핑, gate, 개선 수용 근거
- `recovery/CHECKPOINT.md`: 세션 종료·게이트·예산 경계의 복구 정보

`state.next_action`은 비우지 않습니다. 원본 evidence와 journal event가 없으면 수행되지 않은 것으로 간주합니다.

## 수동 운영

구조 검사:

```powershell
python <factory-root>\scripts\validate_runtime_neutral.py <target-project>
```

trigger 확인:

```powershell
python <target-project>\harness\triggers\check_self_evaluation.py <target-project>\harness
```

checker 출력이 `none`이면 종료합니다. `input-invalid:*`는 구조 복구, adapter/parity reason은 parity 검증으로 라우팅합니다. 유효한 `targeted|full` 평가를 완료한 뒤에는 위 recorder를 호출합니다.

## 콜드스타트

새 세션은 다음 순서만 읽습니다.

1. `harness/HARNESS.md`
2. `harness/harness-spec.json`
3. `harness/team/TEAM-ARCHITECTURE.md`
4. `harness/state/state.json`
5. `harness/state/self-evaluation.json`
6. 현재 unit refs

목적, 현재 단계, 즉시 다음 행동, 연결 task evaluator, pending harness evaluation을 복원하지 못해 `coldstart_fail`이 false→true가 되면 pending events에 `coldstart-fail`을 중복 없이 추가합니다.

## 승인 게이트

배포, 삭제, 외부 메시지, 비가역 데이터 변경, 보안·비용 경계처럼 사용자가 지정한 gate는 agent가 우회할 수 없습니다. gate 대기는 fail이 아니라 명시적 waiting 상태로 기록합니다.
