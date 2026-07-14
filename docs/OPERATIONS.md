# 운영·평가·개선 가이드

생성된 하네스는 “Claude용 구성”과 “Codex용 구성” 두 벌이 아니라, 하나의 공통 계약과 두 개의 native adapter로 운영합니다.

```text
harness/harness-spec.json
├── 공통 team/skills/loops/state/ledger
├── Claude: CLAUDE.md + .claude/skills + .claude/agents
└── Codex:  AGENTS.md + .agents/skills + .codex/agents + .codex/config.toml
```

## 정본

`harness/harness-spec.json`에는 다음이 들어갑니다.

- `domains`: 프로젝트 경계와 담당 coordinator
- `agents`: 역할 ID, lane, capabilities, domain, access, 추상 모델 티어
- `skills`: entry/evaluation/improvement/domain skill, 시작 역할, 공통 instruction 경로
- `orchestration`: 정상 실행 handoff DAG
- `evaluators`: 증거 runner, verdict owner, command, pass condition
- `approval_gates`: 중지 조건, 승인 주체, 승인 후 필요한 행동
- `loops`: 실행·평가·개선 파일, 개선 owner, 실패·회고 임계값
- `runtime_targets`: 생성할 adapter

각 skill 본문 정본은 spec의 `instructions`가 가리키는 `harness/skills/<skill-id>/SKILL.md`입니다. Claude/Codex adapter에는 이 본문을 byte-identical하게 투영합니다. adapter만 직접 바꾸면 다음 재생성 때 사라지거나 두 런타임의 의미가 달라집니다.

## 프로젝트별 팀 구성

역할은 고정 8개가 아닙니다. 작은 프로젝트는 여러 capability를 한 역할에 합칠 수 있고, 복합 workspace는 view/api/batch/import 같은 domain별 coordinator와 전문 worker·evaluator를 둘 수 있습니다.

다만 다음 capability 합집합은 반드시 존재합니다.

- `routing`
- `execution`
- `verification`
- `verdict`
- `defect-counting`
- `improvement`

경계면이 있으면 `impact-analysis`와 `coordination`을 분리하는 것이 기본입니다. 정상 handoff는 DAG로 만들고 재시도·보강 환류는 improvement loop에 둡니다.

## 모델 티어

공통 spec은 vendor model명을 저장하지 않고 다음 세 티어만 사용합니다.

| 티어 | 용도 |
|---|---|
| `fast` | 라우팅, 결정적 명령 실행, 단순 집계 |
| `balanced` | domain coordination, 일반 구현, 개선안 정리 |
| `deep` | 교차 영향 분석, 고비용 판정, 복잡한 설계 |

생성 시 현재 런타임에서 사용 가능한 실제 모델로 매핑하고 D-001에 기록합니다. 모델을 바꿔도 공통 역할 의미와 evaluator 계약은 유지합니다.

## 실행 흐름

```text
요청
  → entry skill
  → routing / domain handoff
  → execution
  → evaluator runner가 원본 증거 생성
  → evaluator owner가 pass condition 대조
  → fail이면 defect-counting
  → 임계값 도달 시 improvement owner
  → spec 선변경 + 전체 adapter 재생성
  → parity + cold-start + 원 evaluator 재검증
```

실행 role은 자기 작업을 스스로 pass 처리하지 않습니다. runner와 owner가 같은 agent로 병합된 작은 구성도 입력·출력·기록 단계는 분리합니다.

## 호출

namespace가 `step-control-tower`인 예:

| 목적 | Claude | Codex |
|---|---|---|
| 새 요청·다음 unit | `/step-control-tower` | `$step-control-tower` |
| 특정 unit 평가 | `/step-control-tower-eval U-003` | `$step-control-tower-eval U-003` |
| 회고·보강 | `/step-control-tower-retro` | `$step-control-tower-retro` |

일반 운영에서는 entry skill만 호출합니다. 평가와 트리거된 회고는 자동 handoff됩니다.

## 상태와 기록

- `state/state.json`: 현재 phase, queue, current, next_action, improve counter의 source of truth
- `ledger/journal.jsonl`: append-only 실행·evidence·verdict·handoff 기록
- `ledger/DECISIONS.md`: schema, evaluator, 역할, 모델 매핑, gate 변경 근거
- `memory/INDEX.md`: 지속 메모리의 경로, 요약, 읽기 시점, 출처, 검증일, 상태를 관리하는 정본 인덱스
- `recovery/CHECKPOINT.md`: 세션 종료·게이트·예산 경계의 복구 정보

`state.next_action`은 비우지 않습니다. 평가 evidence와 journal line이 없으면 수행되지 않은 것으로 간주합니다.

메모리는 생성·이동·이름 변경·대체·보관과 인덱스 행을 같은 변경 단위에서 갱신합니다. 현재 상태나 사건 이력을 메모리에 복제하지 않고, 기존 사용자 메모리는 승인 없이 덮어쓰거나 삭제하지 않습니다.

## 개선 트리거

기본 트리거는 다음 세 종류입니다.

- 같은 안정적 failure key가 `fail_threshold` 이상 누적
- 완료 unit이 `retro_interval`에 도달
- cold-start가 목적·다음 행동·완료 evaluator를 복원하지 못함
- evaluator가 없거나 실행 불가능한 구조적 fail

improvement owner는 읽기 전용 evidence로 안건 1~2개를 제안합니다. entry orchestrator만 spec과 state의 쓰기 주체가 됩니다.

## 개선 적용 순서

1. 직전 개선의 효과와 동일 failure 재발 확인
2. journal evidence에서 실패 원인 추출
3. `harness-spec.json`과 참조된 공통 skill 변경
4. 공통 team/loop 문서 갱신
5. 선택된 모든 Claude/Codex adapter 재생성
6. parity validator
7. cold-start
8. 개선을 촉발한 원 evaluator
9. DECISIONS와 journal 기록
10. 겨냥한 failure key만 reset

최대 3회 보완 후에도 실패하면 잔여 fail과 중단 사유를 보고합니다. evaluator 완화나 gate 우회는 개선으로 취급하지 않습니다.

## 검증

팩토리 저장소 자체:

```powershell
python scripts\test_runtime_neutral_contract.py
python scripts\skill_smoke_build_harness.py
```

생성된 대상 프로젝트:

```powershell
python <factory-root>\scripts\validate_runtime_neutral.py <target-project>
```

검증기는 spec ID·중첩 필드·상대경로·DAG·evaluator·approval gate·memory index·capability backbone, 공통 agent/skill, Claude frontmatter와 access 제한, Codex agent TOML의 name/description/instructions, global limits, 양 runtime skill과 managed block, placeholder와 byte parity를 확인합니다.

## 콜드스타트

새 세션은 다음 순서만 읽습니다.

1. `harness/HARNESS.md`
2. `harness/harness-spec.json`
3. `harness/team/TEAM-ARCHITECTURE.md`
4. `harness/state/state.json`
5. `harness/memory/INDEX.md`
6. 현재 unit의 refs와 인덱스에서 선택한 지속 메모리

그 뒤 파일 근거로 목적과 현재 phase, 즉시 다음 행동, 해당 행동의 evaluator를 답하지 못하면 cold-start fail입니다.

## 승인 게이트

배포, 삭제, 외부 메시지, 비가역 데이터 변경, 보안·비용 경계처럼 사용자가 지정한 gate는 agent가 우회할 수 없습니다. gate 대기는 fail이 아니라 명시적 waiting 상태로 기록합니다.
