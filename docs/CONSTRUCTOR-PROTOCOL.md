# CONSTRUCTOR-PROTOCOL — 하네스 구성·수정 규약

이 문서는 factory의 일곱 스킬이 따라야 할 공통 규약입니다. 구성자는 대상 프로젝트를 분석해 프로젝트 내부의 런타임 중립 정본을 만들거나 수정하고, 그 정본에서 Claude·Codex·Gemini 네이티브 어댑터를 투영합니다.

## 0. 소유권 경계

- factory는 프로젝트 하네스를 package, registry, 중앙 state로 흡수하지 않는다.
- `harness/`, state, ledger, evaluation report의 소유자는 대상 프로젝트다.
- 기존 하네스가 있으면 같은 위치에서 점진적으로 변경한다.
- factory checkout에는 재사용 가능한 schema, provider 계약, template, validator, skill만 둔다.
- 프로젝트별 관찰을 factory 템플릿에 환류하는 것은 별도 사용자 승인 작업이다.

각 스킬은 먼저 동봉된 `scripts/resolve_factory.py`로 `FACTORY_ROOT`를 확정합니다. resolver가 필수 계약을 검증한 source만 읽고, 경로 또는 repository/ref/commit을 생성 하네스의 D-001에 기록합니다.

## 1. 스킬 선택

가장 작은 적합 스킬을 선택합니다.

| 상황 | 스킬 |
|---|---|
| 하네스가 없거나 전체 토폴로지 재설계 | `build-harness` |
| agent·권한·handoff 변경 | `build-agent` |
| 실행/domain skill 변경 | `build-skill` |
| task/harness evaluator 변경 | `build-evaluator` |
| 구조와 provider parity 확인 | `verify-harness` |
| 하네스 변경 효과 판정 | `evaluate-harness` |
| 입증된 하네스 결함 수정 | `improve-harness` |

원자적 변경 요청에 `build-harness`를 사용해 전체 state를 재초기화하지 않습니다.

## 2. 조사와 인터뷰

- `README.md`, `principles/`, `interview/QUESTION-BANK.md`, `CHECKLIST.md`를 읽는다.
- 대상의 README/docs, 빌드·테스트·CI, root 규칙, 디렉터리·서비스·데이터 계약, 기존 agent/skill/hook/evaluator를 조사한다.
- 수집 목적은 목적 가설, 결정적 task evaluator, domain graph, 기존 하네스 보존 경계, harness-effect baseline을 찾는 것이다.
- 코드와 문서에서 확인한 사실은 다시 묻지 않는다.
- 확인되지 않은 목적, 승인 gate, 완료 기준, provider 범위만 최대 두 번의 질문 묶음으로 확인한다.
- 사용자가 맡기면 질문 은행의 schema 1.1 기본값과 Claude·Codex·Gemini를 적용하고 인도 보고에 명시한다.

## 3. 공통 설계

### Domain과 agent

- 역할 수와 이름을 고정하지 않고 실제 프로젝트 경계에서 도출한다.
- capability 합집합에 routing, execution, verification, verdict, defect-counting, improvement를 포함한다.
- agent마다 lane, capabilities, domains, access, `fast|balanced|deep` 티어를 지정한다.
- 실제 vendor 모델명은 provider adapter에서 매핑하고 공통 spec에 넣지 않는다.
- 정상 handoff는 DAG다. retry와 improvement 환류는 loop로 표현하고 역방향 edge를 넣지 않는다.

### Skill evaluator 연결

schema 1.1에서는 모든 `skills[].evaluator`가 필수입니다.

- entry/evaluation/verification/domain → `scope: task`; verification은 구조 validator
- harness-evaluation/improvement → `self_evaluation.evaluator`; `scope: harness`, `type: experiment`

실행자와 task evidence runner, task verdict owner를 계약상 분리합니다. harness evaluator는 task fail을 곧바로 하네스 결함으로 간주하지 않습니다.

### 승인 gate

모든 인간 승인 조건을 `approval_gates`의 id, trigger, owner, required_action으로 기록합니다. provider 자유 텍스트에만 별도 gate를 만들지 않습니다.

## 4. build-harness 절차

1. schema 1.1 spec 생성과 모든 skill evaluator 링크 검증
2. JSON key, ID, 상대경로, 참조, DAG 검증
3. 공통 team/agent/skill/loop/recovery/state/ledger 렌더링
4. task evaluator와 `scope:harness,type:experiment` evaluator 렌더링
5. `evaluation/suites/targeted.json`에 세 reason의 결정적 metric 렌더링
6. checker, recorder, self-evaluation state 렌더링
7. canonical은 별도 hash하고 `watched_paths`에는 선택 provider의 exact managed artifact만 등록
8. 선택 provider adapter 투영
9. validator와 CHECKLIST 수행
10. baseline full evaluation을 수행하고 recorder로 ACK하거나, 초기 mandatory event를 pending으로 명시

초기 state에는 빈 managed hash와 `canonical-contract-change` pending event를 둡니다. provider root 전체나 unrelated user skill/agent는 watched path에 넣지 않습니다.

## 5. 원자적 build 절차

`build-agent`, `build-skill`, `build-evaluator`는 다음 transaction을 따릅니다.

1. 현재 spec, state, ledger, provider 목록 읽기
2. 변경 전 `verify-harness`
3. 충돌 ID와 영향 handoff/evaluator 분석
4. spec과 공통 정본 변경; skill 변경이면 evaluator 링크도 갱신
5. 선택 provider의 exact managed artifact 재투영
6. 새 projection/wrapper/config의 exact path만 `watched_paths`에 반영
7. 해당 mandatory event를 pending events에 중복 없이 추가
8. 변경 후 `verify-harness`; parity pass→fail이면 `parity-fail` 추가 후 구조 복구
9. checker를 다시 실행하고 유효한 decision만 라우팅

이벤트는 agent→`agent-change`, skill→`skill-change`, evaluator→`evaluator-change`, 공통 계약→`canonical-contract-change`, provider artifact→`adapter-change`입니다. 기존 queue, append-only ledger, evaluation run을 재초기화하지 않습니다.

## 6. provider 렌더링

provider ID와 경로는 `providers/<id>/contract.json`에서 읽습니다.

### Claude

- 기존 `CLAUDE.md` 관리 블록 밖 보존
- 공통 skill을 `.claude/skills/<skill-id>/SKILL.md`에 byte-identical copy
- `.claude/agents/<namespace>-<role-id>.md` 생성
- `read-only`는 읽기 도구만 허용하고 쓰기·shell 도구 금지

### Codex

- 기존 `AGENTS.md` 관리 블록 밖 보존
- 공통 skill을 `.agents/skills/<skill-id>/SKILL.md`에 byte-identical copy
- `.codex/agents/<namespace>-<role-id>.toml` 생성
- `.codex/config.toml`의 관련 agent limits만 구조적 병합

### Gemini

- 기존 `GEMINI.md` 관리 블록 밖 보존
- 공통 skill을 `.gemini/skills/<skill-id>/SKILL.md`에 byte-identical copy
- `.gemini/agents/<namespace>-<role-id>.md` 생성
- 전체 DAG sequencing은 entry/main orchestrator가 소유하고 agent wrapper는 공통 역할 계약을 참조

어댑터는 thin wrapper입니다. 역할 의미를 복제해 별도 정본을 만들지 않습니다.

## 7. event-driven self-evaluation

schema 1.1은 checker/state/evaluation loop/evaluator/targeted suite path, sampling·interval·cooldown·budget·threshold, mandatory events와 `watched_paths`를 확정합니다. canonical은 별도 hash하며 watched path는 선택 provider의 root guidance 파일, spec 각 skill projection, namespaced agent wrapper, 생성 config처럼 exact managed artifact만 포함합니다.

작업 경계 라우팅은 다음 순서를 고정합니다.

1. checker `reasons`에 `input-invalid:*`가 있으면 effect evaluation/LLM을 열지 않고 `verify-harness`와 구조 복구 후 재실행합니다.
2. `adapter-change|parity-fail`이면 provider parity verify가 pass해야 다음 단계로 갑니다. cold-start false→true와 parity pass→fail은 각각 pending event를 추가합니다.
3. 자동 경로의 `none`은 종료합니다. 사용자 명시 full 요청은 raw checker JSON 전체를 `override.original`에 보존하고 top-level effective `decision: full`, `mandatory: false`, `override.kind: explicit-user-request`, original reasons 뒤 marker, 동일한 deferred reasons·hashes·`acknowledgement`를 기록합니다. 이 구조화된 override만 budget·cooldown을 우회하며 input-invalid/parity 검증은 우회하지 않습니다.
4. `targeted`는 `evaluation/suites/targeted.json`에서 `cost-regression|retry-pressure|deterministic-sample` reason과 연결된 결정적 metric만 실행합니다. 임의 LLM targeted 평가는 금지합니다.
5. `full`은 harness experiment evaluator를 실행합니다.

checker는 읽기 전용이고 `none|targeted|full`만 반환합니다. trigger는 개선 명령이 아닙니다. 완료 task의 기존 state transaction이 `current_unit`, `units_since_full += 1`, `cooldown_remaining_units = max(0, n-1)`, recent/rolling evidence를 정확히 한 번 갱신하며 추가 LLM 호출은 하지 않습니다.

## 8. evaluate-harness 계약

- full은 같은 evaluator와 pass condition으로 baseline/control/treatment를 비교합니다.
- 표본 미달, arm 조건 불일치, 미실행 evaluator는 `inconclusive`입니다.
- 평가 전 checker JSON을 `<target>\harness\evaluation\runs\<run-id>\trigger.json`에 동결하고 완료된 targeted/full마다 다음 recorder를 호출합니다.

```powershell
python <target>\harness\triggers\record_self_evaluation.py <target>\harness --decision <targeted|full> --decision-file <target>\harness\evaluation\runs\<run-id>\trigger.json --verdict <improved|neutral|regressed|inconclusive>
```

recorder는 frozen trigger의 decision/reasons, current managed hashes, `acknowledgement` failure snapshot을 확인합니다. ACK decision/reasons는 변화한 rolling-metric decision으로 대체하지 않습니다. full은 처리 시작 pending/reason과 frozen failure snapshot만 ACK하고 managed canonical/provider hashes, units, cooldown을 갱신합니다. 평가 중 생긴 새 event·failure는 보존합니다. targeted는 last decision·cooldown만 갱신합니다. 이 상태 전이로 같은 mandatory signal이 반복 평가되지 않습니다.

full report가 regression 또는 하네스 결함을 귀속한 경우에만 `improve-harness`로 전달합니다.

## 9. improve-harness 계약

1. 하네스 귀속 근거와 겨냥 지표 확인
2. 예상 효과와 rollback 조건 기록
3. 변경 1~2개 선택
4. 공통 spec/문서 선변경
5. 모든 선택 provider adapter 재투영
6. `verify-harness`, cold-start, 원 task evaluator 실행
7. checker JSON을 run의 `trigger.json`에 동결하고 full harness-effect evaluation 실행
8. completed full recorder ACK
9. improved 또는 사전 허용된 neutral만 수용
10. regression이면 안전한 rollback 후 근거 기록

평가 기준 완화, gate 우회, evidence 삭제, unrelated state 초기화는 금지합니다.

## 10. 검증·인도

다음을 수행합니다.

```powershell
python <FACTORY_ROOT>\scripts\validate_runtime_neutral.py <target>
python <target>\harness\triggers\check_self_evaluation.py <target>\harness
# completed targeted/full 이후 recorder는 §8의 명령으로 실행
```

CHECKLIST의 구조, provider, 평가, trigger fixture, cold-start를 최대 3회 보완합니다. 잔여 fail은 숨기지 않고 인도 보고에 명시합니다.

인도 보고에는 다음을 포함합니다.

- 생성·수정 파일과 보존한 state/ledger
- 적용 기본값과 domain/agent/skill/evaluator 토폴로지
- provider 목록과 모델 티어 매핑
- task evaluation과 harness-effect evaluation 호출법
- trigger 정책, budget/cooldown/sampling 값
- 검증 회전과 잔여 fail

## 11. 불변 조건

1. task evaluator 없는 작업 단위를 실행하지 않는다.
2. 원본 evidence와 기록 없는 pass는 없다.
3. 인간 승인 gate는 승인 없이 통과하지 않는다.
4. `state.json.next_action`은 비우지 않고 journal은 append-only다.
5. fail과 인라인 폴백을 숨기지 않는다.
6. adapter 의미 변경은 공통 spec에 먼저 반영한다.
7. 선택 provider 간 역할·skill·evaluator·gate 의미를 동일하게 유지한다.
8. trigger 발생만으로 하네스를 자동 수정하지 않는다.
9. factory가 프로젝트 state를 중앙 소유하지 않는다.
