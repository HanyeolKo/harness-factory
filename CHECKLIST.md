# CHECKLIST — schema 1.1 인도 전 검증

전 항목 pass가 원칙입니다. 최대 3회 보완 후에도 fail이 남으면 숨기지 말고 잔여 항목과 사유를 인도 보고에 명시합니다.

## 0. 소유권과 보존

- [ ] 하네스 정본, state, ledger, evaluation report가 대상 프로젝트 안에 있다.
- [ ] factory 저장소나 plugin package에 프로젝트별 state/evidence를 복사하지 않았다.
- [ ] 기존 queue, `next_action`, state counter, append-only journal을 보존했다.
- [ ] `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` 관리 블록 밖 사용자 내용을 보존했다.
- [ ] 원자적 변경이면 전체 하네스를 재초기화하지 않고 가장 작은 build 스킬을 사용했다.

## 1. 공통 구조

- [ ] `harness/harness-spec.json`의 `schema_version`이 `1.1`이다.
- [ ] spec이 중첩 required/unsupported key, ID 유일성, 상대경로, 참조 무결성, DAG, limits 계약을 통과한다.
- [ ] domain마다 경로와 coordinator가 있고 agent·skill·evaluator 참조가 모두 존재한다.
- [ ] 모든 `skills[].evaluator`가 kind 계약과 일치한다: entry/evaluation/verification/domain→task, harness-evaluation/improvement→harness experiment.
- [ ] capability 합집합에 routing, execution, verification, verdict, defect-counting, improvement가 있다.
- [ ] spec agent마다 `harness/team/agents/<role-id>.md`가 있다.
- [ ] spec skill마다 `harness/skills/<skill-id>/SKILL.md`가 있다.
- [ ] execution, task evaluation, harness evaluation, improvement loop가 구분된다.
- [ ] `harness/evaluation/EVALUATION-CONTRACT.md`가 있다.
- [ ] `harness/triggers/check_self_evaluation.py`와 `record_self_evaluation.py`가 있다.
- [ ] `harness/evaluation/suites/targeted.json`이 세 targeted reason을 결정적 metric에 매핑한다.
- [ ] `harness/state/state.json`과 `harness/state/self-evaluation.json`이 있다.
- [ ] recovery, budget, ledger 파일과 최초 journal event가 있다.
- [ ] 미치환 `{{...}}` placeholder와 세션 의존 표현이 없다.
- [ ] 템플릿 source/ref/commit과 초기 결정이 D-001에 기록됐다.

## 2. 일곱 factory 스킬

- [ ] `build-harness`가 전체 bootstrap과 schema 1.1 baseline을 만든다.
- [ ] `build-agent`가 canonical agent와 provider wrapper를 원자적으로 변경한다.
- [ ] `build-skill`이 canonical SKILL과 provider별 byte-identical copy를 만든다.
- [ ] `build-evaluator`가 `task|harness` scope를 명시한다.
- [ ] `verify-harness`가 구조만 결정적으로 검사하고 개선을 자동 수행하지 않는다.
- [ ] `evaluate-harness`가 checker의 `none|targeted|full`을 따른다.
- [ ] `improve-harness`가 full evidence 또는 구조 fail 없이는 시작하지 않는다.
- [ ] 각 build 스킬이 알맞은 mandatory change event를 기록한다.

## 3. Provider adapter

### Claude

- [ ] 선택 시 `.claude/skills/<skill-id>/SKILL.md`가 canonical과 byte-identical하다.
- [ ] `.claude/agents/<namespace>-<role-id>.md`의 이름, 설명, 권한이 spec과 일치한다.
- [ ] read-only agent가 쓰기·shell 도구를 허용하지 않는다.
- [ ] `CLAUDE.md` managed block이 정확히 하나다.

### Codex

- [ ] 선택 시 `.agents/skills/<skill-id>/SKILL.md`가 canonical과 byte-identical하다.
- [ ] `.codex/agents/<namespace>-<role-id>.toml`이 파싱되고 name/description/instructions가 spec과 일치한다.
- [ ] `.codex/config.toml` limits가 spec 이상이며 unrelated 설정을 보존한다.
- [ ] `AGENTS.md` managed block이 정확히 하나다.

### Gemini

- [ ] 선택 시 `.gemini/skills/<skill-id>/SKILL.md`가 canonical과 byte-identical하다.
- [ ] `.gemini/agents/<namespace>-<role-id>.md`가 파싱되고 역할·권한 의미가 spec과 일치한다.
- [ ] entry/main orchestrator가 DAG sequencing을 소유한다.
- [ ] `GEMINI.md` managed block이 정확히 하나다.

### Parity

- [ ] 선택된 모든 provider의 agent/skill/evaluator/gate ID 집합과 handoff 의미가 같다.
- [ ] adapter는 thin wrapper이며 공통 역할 의미를 별도 정본으로 복제하지 않는다.
- [ ] `watched_paths`가 선택 provider의 exact root guidance, spec skill projection, namespaced agent wrapper, 생성 config만 포함한다.
- [ ] unrelated user skill/agent와 선택하지 않은 provider 변경은 watched hash를 바꾸지 않는다.
- [ ] 한 provider만 변경된 상태가 없다.

## 4. Task evaluation

- [ ] 모든 실행 unit에 task evaluator가 있다.
- [ ] evaluator runner가 원본 evidence를 만들고 verdict owner가 pass condition과 대조한다.
- [ ] evaluator command 또는 rubric을 실제로 1회 실행했다.
- [ ] evidence와 journal event 없는 pass가 없다.
- [ ] fail 사건을 중복 계상하지 않는다.
- [ ] 인간 승인은 gate이며 task evaluator를 대체하지 않는다.

## 5. Harness-effect evaluation

- [ ] task evaluator와 별도 `scope: harness`, `type: experiment` evaluator가 있다.
- [ ] baseline/control/treatment가 같은 evaluator와 지표를 사용한다.
- [ ] verdict가 `improved|neutral|regressed|inconclusive` 중 하나다.
- [ ] checker의 `minimum_samples`는 success/cost 회귀 비교에만 적용하며 retry·deterministic sample 신호를 막지 않는다.
- [ ] full experiment 자체의 표본이 부족하면 `inconclusive`로 처리한다.
- [ ] task 실패를 자동으로 하네스 결함에 귀속하지 않는다.
- [ ] task pass를 자동으로 하네스 improved로 처리하지 않는다.
- [ ] 평가 기준을 완화해 treatment를 통과시키지 않는다.

## 6. Event-driven trigger

- [ ] `self_evaluation.mode`가 `event-driven`이다.
- [ ] checker, recorder, state, evaluation loop, harness evaluator, targeted suite 참조가 유효하다.
- [ ] sample rate, full interval, cooldown, budget ratio, 성공률·비용·retry 임계값, minimum sample이 확정됐다.
- [ ] mandatory event 목록에 canonical, agent, skill, evaluator, adapter 변경과 cold-start/parity fail이 포함된다.
- [ ] checker는 읽기 전용 결정적 프로그램이며 LLM을 호출하지 않는다.
- [ ] checker stdout은 compact JSON이고 결과가 `none|targeted|full`뿐이다.
- [ ] checker가 `improve`를 반환하거나 파일을 수정하지 않는다.
- [ ] 동일 입력은 동일 결과를 낸다.
- [ ] malformed input은 fail-closed `full`, mandatory이지만 effect evaluation/LLM이 아니라 verify/recovery로 라우팅한다.
- [ ] `adapter-change|parity-fail`은 parity verify pass 전 effect evaluation을 열지 않는다.
- [ ] cold-start false→true와 parity pass→fail 전환이 pending event를 중복 없이 추가한다.
- [ ] targeted는 `targeted.json` reason 매핑만 실행하며 임의 LLM judge를 열지 않는다.

### Trigger fixture

- [ ] 신호 없음 → `none`
- [ ] deterministic sample 또는 제한 지표 회귀 → `targeted`
- [ ] full interval 도달 → `full`
- [ ] canonical hash 또는 mandatory event → `full`, mandatory
- [ ] 반복 failure threshold → `full`, mandatory
- [ ] non-mandatory + budget 초과 → `none` + deferred reason
- [ ] non-mandatory + cooldown → `none` + deferred reason
- [ ] mandatory event가 budget/cooldown 때문에 누락되지 않음

### Recorder/ACK fixture

- [ ] 완료된 targeted/full마다 recorder를 호출한다.
- [ ] checker JSON을 평가 전에 run의 `trigger.json`에 동결한다.
- [ ] malformed decision file, decision mismatch, stale managed hash는 ACK를 거부한다.
- [ ] full ACK가 처리 시작 pending event와 frozen failure snapshot만 ACK하고 평가 중 생긴 새 event·failure를 보존한다.
- [ ] full ACK가 canonical/provider managed hashes, units, cooldown, verdict를 갱신한다.
- [ ] targeted ACK는 last decision/cooldown만 갱신하고 mandatory event를 소비하지 않는다.
- [ ] full ACK 직후 같은 mandatory 신호가 반복 평가되지 않는다.
- [ ] ACK 이후 새 cold-start/parity incident가 다시 검출된다.
- [ ] 미완료 run은 state를 변경하지 않는다.
## 7. 개선 gate

- [ ] full 평가의 regression 또는 결정적 구조 fail이 하네스에 귀속됐다.
- [ ] 개선 안건이 1~2개이고 예상 효과와 rollback 조건이 있다.
- [ ] spec과 공통 파일을 adapter보다 먼저 변경했다.
- [ ] 모든 선택 provider를 재투영했다.
- [ ] verify, cold-start, 원 task evaluator, full effect evaluation을 재실행했다.
- [ ] improved 또는 사전 허용된 neutral만 수용했다.
- [ ] regression이면 안전한 rollback과 근거 기록을 수행했다.
- [ ] 승인 gate 우회, evidence 삭제, 평가 기준 완화를 개선으로 취급하지 않았다.

## 8. 콜드스타트

컨텍스트 없는 세션이 다음을 파일 근거로 답해야 합니다.

- [ ] 하네스 목적과 현재 phase
- [ ] 지금 즉시 수행할 다음 행동
- [ ] 그 행동의 task evaluator
- [ ] domain별 실행 순서와 handoff
- [ ] pending self-evaluation event와 마지막 harness verdict
- [ ] 개선이 허용되는 조건

대화 기억이 필요하거나 `next_action`이 비어 있으면 fail입니다. `coldstart_fail` false→true 전환은 `coldstart-fail` pending event를 추가합니다.

## 9. 저장소·대상 검증

팩토리 저장소:

```powershell
python scripts\test_runtime_neutral_contract.py
python scripts\test_self_evaluation_trigger.py
python scripts\skill_smoke_build_harness.py
```

대상 프로젝트:

```powershell
python scripts\validate_runtime_neutral.py <target-project>
python <target-project>\harness\triggers\check_self_evaluation.py <target-project>\harness
```

- [ ] 모든 명령의 실제 결과를 기록했다.
- [ ] 미실행 명령은 pass로 표기하지 않았다.

## 10. 인도 보고

- [ ] 생성·수정 파일과 보존한 state/ledger를 요약했다.
- [ ] domain/agent/skill/evaluator topology와 provider를 요약했다.
- [ ] task eval과 harness eval의 차이와 호출법을 안내했다.
- [ ] sampling, cooldown, budget, mandatory event 값을 안내했다.
- [ ] 검증·보완 회전 수와 각 변경을 기록했다.
- [ ] 잔여 fail이 없으면 “없음”, 있으면 항목과 사유를 명시했다.
- [ ] 첫 실행과 rollback 방법을 안내했다.
