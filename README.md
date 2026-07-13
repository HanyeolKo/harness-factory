# harness-factory

프로젝트별·대형 작업별 **호출형 LLM 실행 하네스(harness)** 를 빠르게 만드는 팩토리입니다.
사용자는 이 레포를 Claude Code 또는 GPT/Codex Skills에 `build-harness` 스킬로 연결하고,
대상 프로젝트에서 “하네스 구성해줘”라고 요청해 실행 팀 + 평가 레인 기반 하네스 구조를 생성합니다.

## 빠른 시작 — 스킬로 내려받아 사용하기

### 1. 레포지토리 내려받기

```bash
git clone <harness-factory-repo-url> harness-factory
cd harness-factory
```

레포 전체 설치는 오프라인·고정 버전 운용에 가장 단순합니다. 스킬 폴더만 설치한 경우에도 동봉된 resolver가 로컬 팩토리, `HARNESS_FACTORY_HOME`, 캐시를 순서대로 찾고, 없으면 공식 GitHub 저장소에서 템플릿을 가져옵니다.

GitHub 폴백 기본값은 `https://github.com/HanyeolKo/harness-factory.git`의 `main`입니다. 재현 가능한 설치는 `HARNESS_FACTORY_REF`에 태그나 커밋을 지정합니다. resolver는 내려받은 경로의 필수 템플릿 계약을 검증하고, 실제 commit은 생성 하네스의 D-001에 기록됩니다. 오프라인 요청에서는 네트워크 폴백을 사용하지 않습니다.

### 2. Codex/GPT Skills에 설치

```bash
mkdir -p "$CODEX_HOME/skills"
cp -R .codex/skills/build-harness "$CODEX_HOME/skills/build-harness"
```

Codex 세션에서 대상 프로젝트를 열고 다음처럼 요청합니다.

```text
build-harness 스킬로 이 프로젝트 하네스 구성해줘.
```

### 3. Claude Code Skills에 설치

프로젝트 단위로 사용할 때:

```bash
mkdir -p <target-project>/.claude/skills
cp -R .claude/skills/build-harness <target-project>/.claude/skills/build-harness
```

Claude Code에서 대상 프로젝트를 열고 다음처럼 요청합니다.

```text
build-harness 스킬로 이 프로젝트 하네스 구성해줘.
```

### 4. 생성 후 시작 방법

스킬이 대상 프로젝트에 `<HARNESS_ROOT>/HARNESS.md`를 만들면, 새 세션은 항상 그 파일부터 읽습니다.
이후 `team/TEAM-ARCHITECTURE.md`의 실행 팀과 평가 레인을 따라 실행·평가·회고 루프를 진행합니다.

- 실행 팀: `request-router` → `impact-analyst` → `task-coordinator` → `task-worker`
- 평가 레인: `verification-runner` → `evaluation-lead` → `defect-counter` → `improvement-coordinator`

Claude에서는 같은 역할이 `<target-project>/.claude/agents/<skill-name>-<role>.md`에 실제 서브에이전트로 설치됩니다. 실행·평가·회고 스킬은 이 에이전트를 이름으로 위임 호출합니다. 다른 런타임은 지원되는 서브에이전트 기능을 사용하고, 기능이 없을 때만 사유를 기록한 인라인 폴백을 사용합니다.

## 하네스가 생성하는 표준 구조

```text
<target-project>/harness/
├── HARNESS.md
├── ENVIRONMENT.md
├── team/
│   ├── TEAM-ARCHITECTURE.md
│   └── agents/
│       ├── 01-request-router.md
│       ├── 02-impact-analyst.md
│       ├── 03-task-coordinator.md
│       ├── 04-task-worker.md
│       ├── 05-evaluation-lead.md
│       ├── 06-verification-runner.md
│       ├── 07-defect-counter.md
│       └── 08-improvement-coordinator.md
├── loops/
│   ├── EXECUTION-LOOP.md
│   ├── EVAL-LOOP.md
│   └── IMPROVE-LOOP.md
├── recovery/
│   ├── RECOVERY-PLAYBOOK.md
│   └── CHECKPOINT.md
├── ledger/
│   ├── JOURNAL-FORMAT.md
│   ├── journal.jsonl
│   └── DECISIONS.md
├── budget/
│   └── CONTEXT-BUDGET.md
└── state/
    └── state.json
```

이 구조는 계약입니다. 프로젝트 특성상 축을 쓰지 않더라도 파일을 삭제하지 않고 “미사용 — 사유”를 기록합니다.

호출형 런타임 어댑터를 설치하면 대상 루트에 다음 구조도 생깁니다.

```text
<target-project>/
├── .claude/agents/<skill-name>-{request-router,...,improvement-coordinator}.md
├── .claude/skills/<skill-name>/SKILL.md
├── .claude/skills/<skill-name>-eval/SKILL.md
└── .claude/skills/<skill-name>-retro/SKILL.md
```

## 기본 설계 방향

기본값은 **코스트 기반 자동검증·보완**입니다. 작업 단위마다 evaluator를 먼저 확정하고, 실행 후 평가 레인이 원본 증거로 완료를 판정합니다. fail은 사건당 한 번 계상하며 반복 실패·정기 주기·콜드스타트 fail이 임계값에 닿으면 별도 보강 에이전트가 제안서를 만들고 오케스트레이터가 적용·재검증합니다.

프로젝트 특성에 따라 팀 크기, 모델 비용, 회고 주기와 evaluator는 바꿀 수 있습니다. 변경 근거와 영향은 `ledger/DECISIONS.md`에 기록하며 아래 불변 조건은 오버라이드하지 않습니다.

## 무엇을 보장하는가

- **호출형 팀 구조 생성**: 대상 프로젝트의 실제 업무를 대신 구현하지 않고, 라우팅·영향분석·위임·평가·보강을 수행할 실행 팀 뼈대를 생성합니다.
- **실제 에이전트 위임**: Claude에서는 8개 역할을 `.claude/agents/`에 설치하고, 호출형 스킬이 실제 위임합니다. 미지원 런타임만 인라인 폴백합니다.
- **실행/평가 분리**: 실행자는 산출물을 만들고, 평가 레인이 증거 기반으로 pass/fail을 판정합니다.
- **평가 우선**: evaluator 없는 작업 단위는 실행하지 않습니다.
- **검증 기록 필수**: 평가 기록 없는 pass 처리는 없습니다.
- **회복·회고 내장**: 실패는 `RECOVERY-PLAYBOOK.md`로 분류하고, 반복 실패·정기 주기·콜드스타트 fail은 `IMPROVE-LOOP.md`로 환류합니다.
- **자동 보완 연결**: 실행 후 평가, fail 계상, 회고 개시, 제안 적용, 콜드스타트·원 evaluator 재검증을 사용자 재호출 없이 연결합니다.
- **최초 설치 폴백**: 로컬 템플릿이 없으면 동봉 resolver가 공식 GitHub ref를 캐시하고 계약을 검증합니다.
- **콜드스타트 가능성**: 새 LLM 세션이 `HARNESS.md`부터 읽고 목적, 다음 행동, 완료 evaluator와 팀 흐름을 복원할 수 있어야 합니다.

## 불변 조건

1. evaluator 없는 작업 단위는 실행하지 않습니다.
2. 원본 평가 증거와 journal 기록 없는 pass는 허용하지 않습니다.
3. 인간 승인 게이트는 승인 없이 통과하지 않습니다.
4. `state.json.next_action`은 비우지 않고 `journal.jsonl`은 append-only로 다룹니다.
5. fail, 미실행 evaluator, 인라인 폴백은 검증과 인도 보고에서 숨기지 않습니다.

## 사용자용 문서와 구성자용 문서

| 독자 | 문서 | 용도 |
|---|---|---|
| 사용자 | `README.md` | 설치, 스킬 호출, 생성 결과 이해 |
| 구성자(LLM) | `docs/CONSTRUCTOR-PROTOCOL.md` | Phase 0~4 하네스 생성 절차 |
| 구성자(LLM) | `principles/` | 평가·예산·회복·회고·문서 규율 원칙 |
| 구성자(LLM) | `interview/QUESTION-BANK.md` | 사용자 질의와 템플릿 매핑 |
| 검증자 | `CHECKLIST.md` | 인도 전 구조·루프·콜드스타트 검증 |
| 운영자 | `docs/SKILL-EVALUATION.md` | 현재 스킬 평가와 남은 운영 권고 |

## 레포지토리 맵

```text
harness-factory/
├── README.md
├── CHECKLIST.md
├── docs/
│   ├── CONSTRUCTOR-PROTOCOL.md
│   └── SKILL-EVALUATION.md
├── principles/
├── interview/
├── scripts/
│   └── skill_smoke_build_harness.py
├── templates/
│   ├── HARNESS.md.tmpl
│   ├── ENVIRONMENT.md.tmpl
│   ├── team/
│   ├── loops/
│   ├── recovery/
│   ├── ledger/
│   ├── budget/
│   └── skills/SKILL-TEMPLATE.md
├── examples/
├── .claude/skills/build-harness/
└── .codex/skills/build-harness/
```

## 검증

스킬 템플릿 또는 `build-harness` 스킬 프로토콜을 바꾸면 아래 검증을 실행합니다.

```bash
python3 scripts/skill_smoke_build_harness.py
```

이 검증은 disposable 대상 프로젝트를 만들고, `build-harness` 스킬의 Phase 0~4 흐름에 맞춰 템플릿을 치환한 뒤,
Codex/Claude용 실행·평가·회고 스킬, Claude 에이전트 8종, 자동 보완 연결, resolver 로컬·오프라인 경로, 산출물 계약과 미치환 플레이스홀더를 확인합니다.
