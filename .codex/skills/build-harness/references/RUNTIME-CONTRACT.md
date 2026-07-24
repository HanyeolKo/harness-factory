# Runtime-neutral contract

정본과 운영 상태는 생성 프로젝트의 `harness/` 아래에 있다. 팩토리는 제작 도구이며 Claude, Codex, Gemini 파일은 발견·위임용 adapter다.

## 정본 계층

1. schema 1.1 `harness/harness-spec.json`이 provider, 역할, skill, DAG, evaluator, gate, limits, self-evaluation을 정의한다.
2. `harness/team/agents/<role-id>.md`와 `harness/skills/<skill-id>/SKILL.md`가 provider-neutral 의미를 보유한다.
3. `harness/loops/`는 task evaluation, harness effect evaluation, improvement를 분리한다.
4. `harness/state/`, append-only `harness/ledger/`, `harness/evaluation/`은 대상 프로젝트가 소유하며 팩토리로 전송하지 않는다.
5. `providers/<id>/contract.json`이 provider 투영 위치와 capability를 선언한다.

## 공통 의미

- ID는 lower-kebab-case이고 agent model은 `fast|balanced|deep` 추상 tier다.
- 정상 orchestration graph는 DAG다. retry와 improvement feedback은 DAG 밖 loop 계약이다.
- schema 1.1의 모든 `skills[].evaluator`는 존재하는 evaluator를 참조한다.
  - entry/evaluation/verification/domain → `scope: task`; verification은 구조 validator
  - harness-evaluation/improvement → `self_evaluation.evaluator`, `scope: harness`, `type: experiment`
- 인간 승인은 evaluator가 아니라 stable ID approval gate다.
- 의미 변경은 공통 spec을 먼저 바꾸고 선택 adapter 전체를 다시 투영한다.

## Provider adapter

| Provider | root guidance | skill projection | agent projection |
|---|---|---|---|
| Claude | `CLAUDE.md` managed block | `.claude/skills/<skill-id>/SKILL.md` | `.claude/agents/<namespace>-<role-id>.md` |
| Codex | `AGENTS.md` managed block | `.agents/skills/<skill-id>/SKILL.md` | `.codex/agents/<namespace>-<role-id>.toml` |
| Gemini | `GEMINI.md` managed block | `.gemini/skills/<skill-id>/SKILL.md` | `.gemini/agents/<namespace>-<role-id>.md` |

skill projection은 canonical과 byte-identical하다. Agent wrapper는 최소 도구와 공통 역할 경로만 담는다. Gemini main orchestrator가 DAG 순서를 소유하며 subagent 간 재귀 위임을 전제하지 않는다.

## Watched artifact

checker는 `harness/` canonical을 별도 hash한다. `self_evaluation.watched_paths`는 선택 provider의 다음 exact managed artifact만 나열한다.

- 선택 provider의 root guidance 파일
- spec의 각 skill에 대응하는 projection 파일
- spec의 각 role에 대응하는 namespaced agent wrapper
- factory가 생성·관리한 provider config

provider 디렉터리 전체, unrelated user skill/agent, 선택하지 않은 provider, factory 저장소는 감시하지 않는다. 이 계약은 adapter 삭제·drift를 검출하면서 무관한 사용자 변경이 full 평가를 여는 것을 막는다.

## 이벤트 기반 self-evaluation

1. task boundary에서는 읽기 전용 `check_self_evaluation.py`만 실행한다. 출력은 compact JSON `none|targeted|full`이며 LLM 호출·state write·`improve` 반환을 금지한다.
2. `input-invalid:*`는 평가 요청이 아니다. effect evaluation/LLM을 열지 않고 `verify-harness`·구조 복구 후 checker를 다시 실행한다.
3. `adapter-change|parity-fail`은 parity verify pass 전 effect evaluation을 금지한다. cold-start가 false→true이면 `coldstart-fail`, parity가 pass→fail이면 `parity-fail`을 pending events에 중복 없이 추가한다.
4. targeted는 `self_evaluation.targeted_suite`가 가리키는 `evaluation/suites/targeted.json`의 reason 매핑만 실행한다.
   - `cost-regression` → 고정 cost metric
   - `retry-pressure` → 고정 retry metric
   - `deterministic-sample` → 고정 sample fixture/metric
   모호한 임의 LLM targeted 평가는 금지한다.
5. full은 `scope: harness`, `type: experiment` evaluator로 baseline/control/treatment를 같은 조건에서 비교한다.
6. `minimum_samples`는 success/cost 비교에만 적용한다. `targeted_sample_rate`는 독립적인 결정적 sample 신호를 만들고 budget·cooldown은 모든 비필수 신호를 유예한다. canonical/agent/skill/evaluator/adapter 변경, cold-start/parity fail, 반복 failure는 mandatory full이다.

## Recorder와 ACK

완료된 targeted/full 뒤에 반드시 실행한다.

```text
python harness/triggers/record_self_evaluation.py harness --decision <targeted|full> --decision-file harness/evaluation/runs/<run-id>/trigger.json --verdict <improved|neutral|regressed|inconclusive>
```

평가 전에 checker JSON을 `harness/evaluation/runs/<run-id>/trigger.json`에 동결한다. 명시적 full 요청은 raw checker JSON 전체를 `override.original`에 보존한다. top-level은 evaluator와 recorder가 공유하는 effective `decision: full`, `mandatory: false`이고, `override.kind: explicit-user-request`, original reasons 뒤의 marker, 동일한 deferred reasons·managed hashes·`acknowledgement`를 기록한다. raw checker full은 wrapper 없이 허용하지만 단순 decision 변조나 구조화되지 않은 budget·cooldown 우회는 거부한다. recorder는 frozen decision/reasons, managed hashes, failure snapshot이 유효한지 확인한 뒤 원자 갱신한다. ACK decision/reasons는 평가 중 바뀐 rolling-metric decision으로 대체하지 않는다.

- full: 처리 시작 때의 pending-event/reason과 frozen `acknowledgement` failure snapshot만 ACK하고 canonical/provider hashes, units-since-full, cooldown, last decision/verdict를 갱신한다.
- targeted: last decision/verdict와 cooldown만 갱신하고 mandatory event를 소비하지 않는다.
- 평가 중 들어온 새 pending event와 failure incident는 보존한다.
- 미완료·중단·stale run은 ACK하지 않는다.

따라서 이미 처리한 mandatory signal은 다음 checker에서 반복되지 않고, ACK 이후 새 cold-start/parity incident는 transition event로 다시 검출된다.

## 개선 원자성

full 평가가 regression 또는 하네스 원인을 확인한 경우에만 improvement 후보를 만든다. 공통 spec·canonical component·선택 adapter·결정 기록을 한 transaction으로 바꾸고 `verify targeted → verify full → 동일 full suite`로 확인한다. improved 또는 명시적으로 허용한 neutral만 채택하며 state, ledger, evaluation run을 보존한다.

## 호환성

validator는 schema 1.0과 1.1을 읽는다. 1.0 하네스는 migration 전까지 새 self-evaluation 파일과 skill evaluator link를 강제하지 않는다. 신규 생성은 1.1을 사용한다.
