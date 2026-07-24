# 인터뷰 질문 은행 — Phase 1 질의 프로토콜

구성자가 사용자에게 던질 질문의 은행입니다. 목적은 심문이 아니라 **빠른 프로젝트 소유 하네스 구성**입니다.

## 운영 규칙

1. **최대 2회 배치**: 1차는 핵심 Q1~Q4, 2차는 필요한 분기만 최대 4문항.
2. **묻기 전에 조사**: README/docs, 빌드·테스트·CI, 기존 규칙·하네스·state를 조사해 확인 가능한 질문을 소거한다.
3. **목적은 사용자 확정**: 수집 자료로 가설을 제시하되 Q1의 목적은 사용자 입력으로 확정한다.
4. **“알아서” 처리**: 아래 기본값을 적용하고 인도 보고에 명시한다.
5. **선택지 우선**: 자유 서술보다 선택지와 짧은 보완 입력을 사용한다.
6. **결정 기록**: 답변과 적용 기본값을 `ledger/DECISIONS.md` D-001에 기록한다.
7. **프로젝트 소유권**: 기존 하네스를 factory package로 옮길지 묻지 않는다. 기본은 대상 프로젝트 안에서 보존·점진 개선이다.
8. **설계 오버라이드**: 사용자 방향이 우선하지만 evaluator 없는 pass, 승인 gate 우회, evidence 삭제, provider 의미 불일치는 허용하지 않는다.

## 1차 배치 — 핵심 4문항

### Q1. 대상·목적·산출물

> 수집한 자료로는 이 하네스가 `<목적 가설>`을 위해 프로젝트 전체 또는 `<범위>`를 관리하는 것으로 보입니다. 맞나요? 주 산출물은 코드, 문서, 데이터, 혼합 중 무엇인가요?

- **기본값**: 대상은 현재 repository. 목적은 기본값 없이 사용자 확정 필요.
- **매핑**: `harness.id`, `harness.purpose`, domain graph, task evaluator 후보.

### Q2. Task 완료 판정

> 개별 작업이 “제대로 됐다”는 무엇으로 판정할까요? (a) 기존 테스트/빌드/린트 (b) 새 결정적 검증 스크립트 (c) 루브릭 기반 판정 (d) 인간 최종 승인과 a~c 중 하나

- **기본값**: 발견된 결정적 수단. 없으면 검증 스크립트를 첫 backlog로 두고 임시 rubric을 사용.
- **매핑**: `evaluators[].scope: task`, command, pass condition, runner, owner와 entry/evaluation/verification/domain `skills[].evaluator`.
- **주의**: 인간 확인은 approval gate이며 evaluator를 대체하지 않는다.

### Q3. 운영 방식

> 하네스는 어떻게 운영되나요? (a) 사용자 상주 세션 (b) 장시간 자율 실행 (c) cron/event 기반 무인 반복

- **기본값**: (a)
- **매핑**: recovery escalation, checkpoint 빈도, self-evaluation full interval/cooldown.

### Q4. 비용과 평가 강도

> 컨텍스트·토큰과 하네스 자체 평가 비용에 얼마나 민감한가요? (a) 타이트 (b) 보통 (c) 느슨

- **기본값**: (b)
- **매핑**: 작업 budget, `self_evaluation.targeted_sample_rate`, `cooldown_units`, `budget_ratio`, `full_interval_units`.
- **안내**: 매 작업 경계에는 결정적 checker만 실행한다. targeted는 고정 metric suite, full은 harness experiment이며 완료 뒤 recorder가 ACK한다. input-invalid와 미해결 parity는 effect evaluation/LLM으로 보내지 않는다.

## 2차 배치 — 필요한 분기만

### Q5. [대형 작업] 작업 단위

> 파일, 모듈, 기능, 데이터 배치 중 어떤 단위가 자연스러우며 대략 몇 개인가요?

- **기본값**: 조사에서 제안하고 확인만 받는다.
- **매핑**: execution loop, state queue, evaluation sampling unit.

### Q6. [파괴적 단계] 승인 gate

> 배포, 삭제, 외부 발신, 마이그레이션 실행처럼 인간 승인이 필요한 단계가 있나요?

- **기본값**: 파괴적·외부 영향 단계 전부 gate.
- **매핑**: `approval_gates`.

### Q7. [자율/무인] 중단·연락 기준

> 어떤 상황이면 자동 처리를 멈추고 사용자에게 물어야 하나요? (scope 불명확 / retry 상한 / 예산 소진 / gate 도달)

- **기본값**: 네 경우 모두 중지·에스컬레이션.
- **매핑**: recovery와 waiting 상태.

### Q8. [루브릭] 품질 기준

> 산출물이 “좋다”의 기준 2~3가지는 무엇인가요? 예: 정확성, 근거, 분량, 성능.

- **기본값**: 산출물 유형 표준 rubric 초안을 제안하고 확인.
- **매핑**: task evaluator rubric.

### Q9. [기존 root 규칙] 통합 방식

> 기존 `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`가 있습니다. 별도 `harness/` 정본을 두고 각 문서에 managed block만 추가해도 될까요?

- **기본값**: 예. 기존 사용자 본문 보존.
- **매핑**: harness root와 provider managed block. `watched_paths`에는 선택 provider의 exact root guidance, spec skill projection, namespaced wrapper, 생성 config만 둔다.

### Q10. [기록량] 기록 수준

> 기록은 (a) 판정·실패·결정만 (b) unit 시작/종료 포함 (c) 최대 상세 중 어느 수준인가요?

- **기본값**: (b)
- **매핑**: journal event와 evaluation report 상세도.

### Q11. [복합 프로젝트] 팀과 provider

> domain별 coordinator·worker가 필요한가요? evidence runner와 verdict owner는 누가 맡고 Claude, Codex, Gemini 중 어떤 adapter가 필요한가요?

- **기본값**: 역할 수는 고정하지 않고 routing, execution, verification, verdict, defect-counting, improvement capability를 배치한다. 경계면에서는 impact-analysis·coordination을 분리하고 세 provider를 모두 생성한다.
- **매핑**: domains, agents, skills, orchestration, evaluators, runtime targets, provider adapters.
- **주의**: 한 agent가 여러 역할을 맡더라도 산출물·evidence·verdict 단계는 분리한다.

### Q12. [기존 하네스 또는 효과 평가] baseline

> 최근 안정 구간에서 작업 성공률, 평균 비용, retry 수를 계산할 수 있나요? 새 하네스 변경이 유지해야 할 지표는 무엇인가요?

- **기본값**: 최근 결정적 task evaluator 기록에서 가능한 지표를 계산. 자료가 없으면 baseline 수집 전 verdict를 `inconclusive`로 제한.
- **매핑**: `scope: harness`, `type: experiment` evaluator와 harness-evaluation/improvement skill 링크, baseline, success/cost/retry threshold, minimum samples.

## 기본값 일괄표

| 필드 | 기본값 |
|---|---|
| TARGET | 현재 repository |
| HARNESS_OWNERSHIP | 대상 프로젝트가 정본·state·ledger·evidence 소유 |
| SCHEMA_VERSION | 1.1 |
| TASK_EVALUATOR | 발견된 결정적 수단, 없으면 검증 스크립트 신설 |
| HARNESS_EVALUATOR | `scope: harness`, `type: experiment`; harness-evaluation/improvement skill이 참조 |
| PASS_CONDITION | command exit 0 또는 rubric 전 기준 pass |
| OPERATION_MODE | 사용자 상주 세션 |
| WORK_BUDGET | 80% 경고, 100% checkpoint 후 중지/교체 |
| WORK_UNIT | 조사 기반 제안 |
| PARALLELISM | 안전한 독립 경계만 병렬, spec limit 명시 |
| DETERMINISTIC_BOUNDARY | 검증·집계·trigger는 스크립트, 의미 판단만 LLM |
| GATES | 파괴적·외부 영향 단계 전부 |
| JOURNAL_LEVEL | unit 시작/종료 + evidence + verdict + 결정 |
| HARNESS_ROOT | `<대상>/harness/` |
| SELF_EVALUATION_MODE | event-driven; input-invalid→verify/recovery, adapter/parity→verify-first |
| TARGETED_SAMPLE_RATE | 0.05; 프로젝트 baseline으로 조정 |
| TARGETED_SUITE | `self_evaluation.targeted_suite` 경로의 cost/retry/sample 결정적 metric |
| EVALUATION_ACK | checker JSON을 run trigger.json에 동결하고 완료 targeted/full마다 recorder |
| FULL_INTERVAL_UNITS | 10 units |
| COOLDOWN_UNITS | 직전 평가 후 2 units |
| EVALUATION_BUDGET_RATIO | 전체 작업 예산의 10% 이하 |
| SUCCESS_RATE_DROP_POINTS | 5 percentage points |
| COST_INCREASE_RATIO | 0.20 |
| FAIL_THRESHOLD | 같은 failure key 3회 |
| RETRY_THRESHOLD | unit당 3회 |
| MINIMUM_SAMPLES | 5 units |
| MANDATORY_EVENTS | canonical/agent/skill/evaluator/adapter 변경, cold-start/parity fail |
| TEAM_ARCHITECTURE | capability backbone + 프로젝트 경계별 동적 역할 |
| RUNTIME_TARGETS | Claude + Codex + Gemini, 사용자 명시 시 축소 |
| WATCHED_PATHS | canonical은 별도 hash; 선택 provider exact managed artifact만 포함 |

수치 기본값은 시작점입니다. 기존 기록이 충분하면 관측 baseline으로 조정하고 근거를 D-001에 남깁니다.

## 질문 없이 채우는 필드

| 필드 | 출처 |
|---|---|
| BUILD/RUN/LINT/TEST command | repository 조사. 없으면 “없음”을 명시하고 backlog 생성 |
| PROJECT_TREE / EXISTING_SCRIPTS / FORBIDDEN | repository, CI, root 규칙 조사 |
| EXISTING_HARNESS_STATE | 대상 프로젝트의 현재 state/ledger. 보존 대상 |
| PROVIDER_NATIVE_PATHS | `providers/<id>/contract.json` |
| SKILL_EVALUATOR_LINKS | skill kind과 evaluator scope/type에서 결정 |
| WATCHED_EXACT_ARTIFACTS | spec과 선택 provider projection에서 계산; 사용자 질문 불필요 |
| CREATED_DATE | 생성 시점 |
| INTERVIEW_SUMMARY / VERIFY_ROUND | 결정 기록 / 실제 검증 결과 |
