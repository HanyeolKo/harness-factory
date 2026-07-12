# harness-factory

프로젝트별·대형 작업별 **LLM 실행 하네스(harness)의 뼈대**를 빠르게 만드는 팩토리입니다.
사용자는 이 레포를 내려받아 Claude Code 또는 GPT/Codex Skills에 `build-harness` 스킬로 연결하고,
대상 프로젝트에서 “하네스 구성해줘”라고 요청해 표준 하네스 구조를 생성합니다.

## 빠른 시작 — 스킬로 내려받아 사용하기

### 1. 레포지토리 내려받기

```bash
git clone <harness-factory-repo-url> harness-factory
cd harness-factory
```

스킬 본문은 이 레포의 `README.md`, `docs/CONSTRUCTOR-PROTOCOL.md`, `principles/`, `interview/`, `templates/`, `CHECKLIST.md`를 읽습니다.
따라서 스킬 파일만 단독 복사하기보다 레포 전체를 런타임이 읽을 수 있는 위치에 두는 방식을 권장합니다.

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
이후 `state/state.json`의 `next_action`과 queue evaluator를 따라 실행·평가·회고 루프를 진행합니다.

## 하네스가 생성하는 표준 구조

```text
<target-project>/harness/
├── HARNESS.md
├── ENVIRONMENT.md
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

## 무엇을 보장하는가

- **뼈대 역할 유지**: 대상 프로젝트의 실제 업무를 대신 구현하지 않고, 실행 규율·평가 기준·기록 구조를 생성합니다.
- **평가 우선**: evaluator 없는 작업 단위는 실행하지 않습니다.
- **검증 기록 필수**: 평가 기록 없는 pass 처리는 없습니다.
- **회복·회고 내장**: 실패는 `RECOVERY-PLAYBOOK.md`로 분류하고, 반복 실패·정기 주기·콜드스타트 fail은 `IMPROVE-LOOP.md`로 환류합니다.
- **콜드스타트 가능성**: 새 LLM 세션이 `HARNESS.md`부터 읽고 목적, 다음 행동, 완료 evaluator를 복원할 수 있어야 합니다.

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
Codex/Claude용 실행·회고 스킬 설치, 산출물 계약, 콜드스타트 필수값, 미치환 플레이스홀더, 레포 내 양쪽 `build-harness` 스킬 배포 경로를 확인합니다.
