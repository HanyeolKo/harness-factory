# harness-factory

**프로젝트별·대형 작업별 하네스(harness)의 뼈대를 빠르게 구축해주는 하네스 팩토리.**

이 레포지토리는 사람이 읽는 문서이기 이전에, **하네스를 구성하는 LLM(이하 "구성자")을 위한 가이드북**이다.
사용자가 *"이 레포지토리를 참고해서 하네스 구성해줘"* 라고 요청하면, 구성자는 이 README와 하위 문서를 읽고
아래 프로토콜에 따라 사용자에게 필요한 최소한의 질의를 던진 뒤, 대상 프로젝트에 하네스 뼈대를 인스턴스화한다.

---

## 1. 하네스란 무엇인가

여기서 하네스란 **LLM 에이전트가 프로젝트 또는 큰 단위 작업을 수행할 때 따르는 실행 규율의 집합**이다.
구체적으로는 다음을 담은 파일 구조와 루프 정의다.

| 축 | 역할 | 산출 템플릿 |
|---|---|---|
| **실행 (Execution)** | 작업을 어떤 단위로 쪼개고, 어떤 순서와 규율로 수행하는가 | `templates/loops/EXECUTION-LOOP.md.tmpl` |
| **평가 (Evaluation)** — *1급 구성요소* | 각 실행 단위의 완료를 무엇으로 판정하는가. 실행보다 먼저 정의된다 | `templates/loops/EVAL-LOOP.md.tmpl` |
| **회복 (Recovery)** | 실패·중단 시 어떻게 분류하고, 재시도하고, 재개하는가 | `templates/recovery/` |
| **보완 (Improvement)** | 평가·회복 이벤트를 근거로 하네스 자신을 어떻게 개정하는가 | `templates/loops/IMPROVE-LOOP.md.tmpl` |
| **기록 (Ledger)** | 무엇을, 어떤 규격으로, 어디에 남기는가 | `templates/ledger/` |
| **코스트 (Budget)** | 컨텍스트·토큰·턴을 예산으로 선언하고 소진을 추적한다 | `templates/budget/` |

실행·회복·보완이 3대 축이고, **평가 루프가 세 축 모두의 입력을 만든다.**
기록과 코스트는 여섯 축 전체를 떠받치는 기반 계층이다.

## 2. 핵심 원칙 (요약)

상세는 `principles/`의 각 문서를 읽는다. 구성자는 하네스를 생성하기 전에 반드시 전부 읽어야 한다.

1. **평가 루프는 1급 구성요소다** — 완료 판정 기준(evaluator)이 정의되지 않은 작업 단위는 실행할 수 없다. → `principles/01-evaluation-first.md`
2. **모든 컨텍스트는 예산이다** — 작업 단위별로 컨텍스트 예산을 명시적으로 선언하고 소진을 기록한다. → `principles/02-context-budget.md`
3. **결정적 오프로딩 규율** — 기계적으로 반복 가능한 것은 스크립트와 파일로 내리고, LLM 추론은 판단이 필요한 곳에만 쓴다. 상태는 파일에 산다. → `principles/03-deterministic-offloading.md`
4. **실패 회복은 설계에 내장된다** — 체크포인트, 실패 분류, 재시도 정책, 에스컬레이션 기준을 사후가 아니라 뼈대에 넣는다. → `principles/04-failure-recovery.md`
5. **환경 가독성** — 아무 맥락 없는 새 세션이 파일만 읽고 5분 안에 현재 상태를 복원하고 다음 행동을 결정할 수 있어야 한다. → `principles/05-environment-readability.md`
6. **점진적 자기 보완** — 하네스는 고정된 산출물이 아니라, 평가 실패와 회복 이벤트를 연료로 스스로를 개정하는 기초 틀이다. → `principles/06-self-improvement.md`

## 3. 구성자 수행 프로토콜

사용자로부터 하네스 구성 요청을 받으면 아래 5단계를 순서대로 수행한다.

### Phase 0 — 원칙 로드
- `principles/` 전체와 `interview/QUESTION-BANK.md`를 읽는다.
- 대상 프로젝트가 이미 존재하면 그 구조(빌드/테스트 수단, 디렉토리, 기존 규칙 파일)를 훑어 **결정적 evaluator 후보**를 미리 찾는다. 인터뷰 질문 수를 줄이는 재료다.

### Phase 1 — 인터뷰
- `interview/QUESTION-BANK.md`의 프로토콜대로 질의한다. **질문은 최대 2회 배치**(1차 핵심 4문항, 필요 시 2차 보완)로 끝낸다. 빠른 구성이 목적이므로 심문하지 않는다.
- 사용자가 "알아서 해줘"라고 하면 질문 은행의 **기본값 열**을 그대로 적용하고, 적용한 기본값을 인도 시 명시한다.
- 코드베이스에서 이미 답을 확인할 수 있는 것(테스트 러너 존재 여부 등)은 묻지 않는다.

### Phase 2 — 설계 결정 확정
- 인터뷰 답변을 `templates/`의 치환 필드에 매핑한다. 매핑 규칙은 질문 은행의 각 질문에 명시되어 있다.
- 확정한 결정과 근거를 생성될 하네스의 `ledger/DECISIONS.md`에 첫 번째 결정(D-001)으로 기록한다.

### Phase 3 — 뼈대 인스턴스화
- `templates/` 이하의 `.tmpl` 파일들을 대상 프로젝트의 `harness/` 디렉토리(또는 사용자가 지정한 위치)로 복사하며 `{{PLACEHOLDER}}`를 전부 치환한다.
- 표준 산출 구조는 §4를 따른다. 대상 프로젝트 성격상 불필요한 축은 파일을 빼는 게 아니라 **해당 파일 안에 "미사용 — 사유"를 기록**한다 (환경 가독성 원칙).

### Phase 4 — 검증과 인도
- `CHECKLIST.md`의 전 항목을 수행한다. 핵심은 **콜드스타트 테스트**: 하네스의 `HARNESS.md`만 읽고 다음 행동 하나를 결정할 수 있는지 스스로 검증한다.
- 남은 `{{`가 있는지 전수 검색한다. 남아 있으면 인도 불가.
- 사용자에게 생성 파일 목록, 적용한 결정(질문 답변 + 기본값), 첫 실행 방법을 요약해 인도한다.

## 4. 산출물 계약 — 생성되는 하네스의 표준 구조

```
<대상 프로젝트>/harness/
├── HARNESS.md                 # 단일 진입점. 새 세션은 반드시 이 파일부터 읽는다
├── ENVIRONMENT.md             # 실행·검증 커맨드, 디렉토리 맵, 금지사항
├── loops/
│   ├── EXECUTION-LOOP.md      # 실행 루프 규율
│   ├── EVAL-LOOP.md           # 평가 루프 — evaluator 정의와 판정 규격
│   └── IMPROVE-LOOP.md        # 보완 루프 — 하네스 자기 개정 절차
├── recovery/
│   ├── RECOVERY-PLAYBOOK.md   # 실패 분류표·재시도 정책·에스컬레이션 기준
│   └── CHECKPOINT.md          # 체크포인트 규격과 재개 절차
├── ledger/
│   ├── JOURNAL-FORMAT.md      # journal.jsonl 라인 스키마
│   ├── journal.jsonl          # 실행 기록 (append-only)
│   └── DECISIONS.md           # 설계 결정 기록 (ADR-lite)
├── budget/
│   └── CONTEXT-BUDGET.md      # 예산 선언표 + 소진 장부 + 초과 시 행동
└── state/
    └── state.json             # 재개 가능한 현재 상태 (체크포인트 대상)
```

이 구조는 계약이다. 파일명과 위치를 임의로 바꾸지 않는다. 바꿔야 할 사유가 있으면 `DECISIONS.md`에 기록하고 `HARNESS.md`의 파일 맵을 갱신한다.

## 5. 이 레포지토리의 디렉토리 맵

```
harness-factory/
├── README.md                  # (이 문서) 구성자 가이드북 — 진입점
├── CHECKLIST.md               # Phase 4 인도 전 검증 체크리스트
├── principles/                # 핵심 원칙 6편 — Phase 0 필독
├── interview/
│   └── QUESTION-BANK.md       # Phase 1 질의 프로토콜: 질문 은행·기본값·매핑 규칙
├── templates/                 # Phase 3 인스턴스화 대상 (.tmpl)
│   ├── HARNESS.md.tmpl
│   ├── ENVIRONMENT.md.tmpl
│   ├── loops/
│   ├── recovery/
│   ├── ledger/
│   ├── budget/
│   └── skills/SKILL-TEMPLATE.md   # 하네스 루프를 스킬로 노출할 때 사용
├── examples/
│   └── minimal/               # 치환 완료된 최소 예시 — 톤과 밀도의 기준
└── .claude/skills/build-harness/  # Claude Code에서 /build-harness 로 이 프로토콜 실행
```

## 6. 구성자가 지켜야 할 톤

- 생성되는 하네스 문서는 **미래의 LLM 세션이 읽는 실행 지시문**이다. 사람용 설명문이 아니라 명령형·판정형으로 쓴다.
- 짧고 결정적으로. "가급적", "적절히" 같은 판단 유보 표현은 기본값이나 수치로 바꾼다.
- 예시가 필요하면 `examples/minimal/`의 밀도를 기준으로 삼는다.
