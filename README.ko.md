# Harness Factory

[English](README.md) | [한국어](README.ko.md)

Harness Factory는 프로젝트가 직접 소유하는 에이전트 하네스를 만듭니다. 정해진 팀을 그대로 복사하는 대신 프로젝트에 맞는 에이전트, 스킬, 평가기와 네이티브 어댑터를 도출합니다. 생성된 상태와 증거, 개선 이력은 대상 저장소 안에 남습니다.

하나의 `harness/` 정본으로 Claude Code, Codex, Gemini CLI를 함께 지원합니다. 작업 경계에서는 값싼 결정적 검사만 수행하고, 증거가 필요성을 보여줄 때만 더 무거운 평가를 실행합니다.

## 빠른 시작

Git, Python 3.11 이상, 대상 프로젝트 쓰기 권한, 지원 런타임 중 하나 이상이 필요합니다.

### Claude Code

Claude Code 안에서 다음 명령을 실행합니다.

```text
/plugin marketplace add HanyeolKo/harness-factory
/plugin install harness-factory@harness-factory-marketplace
/reload-plugins
```

새 세션을 시작한 뒤 하네스를 생성합니다.

```text
/harness-factory:build-harness "D:\workspace\step_fps"
```

터미널에서도 같은 설치를 수행할 수 있습니다.

```powershell
claude plugin marketplace add HanyeolKo/harness-factory
claude plugin install harness-factory@harness-factory-marketplace
```

### Codex

마켓플레이스를 등록합니다.

```powershell
codex plugin marketplace add HanyeolKo/harness-factory --ref main
codex plugin marketplace list
```

Codex CLI의 `/plugins` 또는 데스크톱 앱의 Plugins 화면에서 `harness-factory`를 설치합니다. 새 작업을 시작한 뒤 다음처럼 호출합니다.

```text
$harness-factory:build-harness "D:\workspace\step_fps"
```

### Gemini CLI

확장 기능을 설치합니다.

```powershell
gemini extensions install https://github.com/HanyeolKo/harness-factory --ref main
```

Gemini CLI를 다시 시작하고 설치 상태를 확인합니다.

```text
/extensions list
```

그다음 Gemini에게 해당 스킬을 사용하도록 요청합니다.

```text
Use the build-harness skill to create a Claude, Codex, and Gemini harness in D:\workspace\step_fps.
```

필요한 런타임을 따로 지정하지 않으면 `build-harness`가 세 런타임의 어댑터를 모두 생성합니다. 먼저 프로젝트를 분석한 뒤, 코드에서 안전하게 추론할 수 없는 목적, 승인 게이트, 완료 기준, 보고 방식, 문서 정리 위치만 짧게 확인합니다.

## 언어와 읽기 비용 계약

하네스 내부 문서는 기본적으로 간결한 영문을 사용합니다. 스킬, 에이전트 지침, 메모리 항목, 실행 루프 계약을 비롯한 런타임용 문서는 같은 규칙을 반복하지 않고 점진적 공개 원칙을 따릅니다. 먼저 인덱스를 읽고 현재 작업에 필요한 참조만 불러옵니다. 생성된 하네스 안에 같은 내부 내용을 여러 언어로 중복 저장하지 않습니다.

새 하네스는 언어 선택을 `harness/harness-spec.json`에 기록합니다.

- `communication.artifact_language`는 `en`으로 고정됩니다.
- `communication.report_language`는 BCP-47 형태의 언어 태그를 받으며 기본값은 `en`입니다.
- `communication.terminology`는 `technical-english` 또는 `localized`입니다.

`report_language`는 사용자가 보는 보고서의 문장 구조를 정합니다. `technical-english`를 선택하면 `harness`, `agent`, `skill`, `evaluator`, `baseline`, `control`, `treatment` 같은 안정된 기술 용어를 영문으로 유지합니다. `localized`를 선택하면 설명용 기술 명사를 관용적인 현지어로 옮깁니다. 예를 들어 `ko + technical-english`는 “`baseline` 대비 `treatment`의 성공률이 높아졌으며 verdict는 `pass`입니다”처럼, `ko + localized`는 “기준선 대비 적용군의 성공률이 높아졌으며 판정은 `pass`입니다”처럼 보고할 수 있습니다.

두 방식 모두 식별자, 명령, 경로, 증거, JSON 키, reason·status 값, `pass`·`fail` 같은 저장 판정은 번역하지 않습니다. 같은 내용을 두 언어로 반복하지 않고 선택한 방식으로 자연스럽게 한 번만 작성합니다. 영문 정본에 정확한 비영문 프로젝트명이나 기계 토큰을 넣어야 할 때는 해당 값만 백틱으로 감싸고 주변 설명은 영문으로 작성합니다. 이 표시 설정만 바뀌어도 full 하네스 성과평가가 열리지는 않습니다. 기존 schema 1.0과 1.1 하네스와의 호환성을 위해 `communication` 객체는 선택 사항이며, 없으면 위의 영문 기본값 세 가지를 적용합니다. 새로 생성되는 하네스에는 항상 포함됩니다.

## 변경 보고서와 Learning Assist

완료된 작업은 기본적으로 `harness/reports/<change-id>/CHANGE-REPORT.md`에 짧은 변경 보고서를 남깁니다. 이 문서는 설계 문서를 다시 만드는 용도가 아니라, 무엇을 바꿨는지, 왜 바꿨는지, 중요한 처리 흐름, 핵심 파일, 실제로 수행한 검증, 이후 알아둘 점만 빠르게 확인하기 위한 문서입니다.

새 하네스를 구성할 때 사용자가 읽을 보고서와 학습 문서를 어디에 정리할지 묻습니다. 선택값은 `harness/policies/reporting.json`에 저장합니다.

- `file`이 기본값이며 프로젝트 내부 파일을 그대로 사용합니다.
- `notion`은 사용자가 지정한 Notion 페이지나 데이터베이스에 읽기용 사본을 게시합니다.
- `slack`은 사용자가 지정한 Slack 채널이나 대화에 읽기용 사본을 게시합니다.

Notion이나 Slack을 선택하면 대상 위치는 사용자가 직접 지정해야 하며 agent가 임의로 추측하지 않습니다. 외부 사본을 사용하더라도 Git 파일이 검증 정본입니다.

Learning Assist는 단독으로 사용할 때 작업 흐름을 막지 않습니다. 더 자세한 설명이나 이해도 확인을 요청하면 실제 diff와 관련 소스만 읽어 설명을 확장합니다. 문서는 **실제 동작 → 이유 → 처리 흐름 → 관련 코드 → 필요할 때 기술용어** 순서로 설명하고, 동료 개발자에게 구두로 설명할 때 잘 쓰지 않을 번역투·추상 표현은 피합니다.

현지화된 보고를 선택하면 설명 문장은 자연스러운 현지어를 우선합니다. 코드에서 다시 찾아야 하는 식별자·경로·명령·설정 키는 그대로 두되, 일반 설명까지 영문 절차 용어로 채우지 않습니다. 정확한 기술 용어가 필요하면 먼저 동작을 쉬운 말로 설명한 뒤 한 번만 괄호나 코드 표기로 소개합니다.

이해도 퀴즈는 용어 암기보다 구현의 원인·결과와 흐름을 확인합니다. 오답이면 바로 정답을 공개하지 않고 **방향 힌트 → 구체적인 상황/반례 → 마지막 실패 기록 후 개념 설명** 순서로 보정합니다. 문장이 애매하거나 정의되지 않은 용어 때문에 틀린 경우에는 이해 실패로 세기 전에 설명이나 문제를 다시 작성합니다.

## 선택형 Learning Gate

새 하네스에는 Learning Gate 정책이 항상 설치되며 기본값은 그대로 `enabled: false`입니다.

- `enabled`는 사용자의 명시적 지시로만 바꿀 수 있습니다. agent는 활성화나 비활성화를 제안할 수 있지만 직접 전환할 수 없습니다.
- OFF 상태에서는 Gate 때문에 추가 학습 작업을 강제하거나 리뷰 요청·PR 생성·병합을 막지 않습니다.
- ON 상태에서는 설정된 위험 기반 범위에 해당하는 변경만 적용하며, 일치하는 risk tag는 저위험 exemption보다 우선합니다.
- Gate 적용 대상에서는 구현·검증 후 짧은 Change Report를 먼저 만들고, **Learning Assist가 같은 쉬운 문체로 실제 diff를 설명한 뒤 사용자가 그 설명을 읽고 Gate 퀴즈를 푸는 흐름**을 사용합니다.
- Gate에서도 오답에 정답을 곧바로 공개하지 않고 단계적 힌트를 사용합니다. 어려운 어휘나 애매한 문제 때문에 틀린 경우는 곧바로 이해 실패로 처리하지 않습니다.
- 통과 증거는 기존과 동일하게 commit된 source snapshot, quiz/answers hash, `verification.json`에 묶입니다. Notion이나 Slack의 읽기용 사본은 이 Git 증거를 대체하지 않습니다.
- 기존 하네스를 improve 또는 reconcile할 때 사용자가 정한 ON/OFF 값과 기존 학습 증거, reporting 정책을 보존합니다.

정책 파일은 `harness/policies/reporting.json`과 `harness/policies/learning-gate.json`에 생성됩니다. 세부 흐름은 [Learning Assist](docs/LEARNING-ASSIST.md), [Reporting Contract](docs/REPORTING-CONTRACT.md), [Learning Gate](docs/LEARNING-GATE.md)를 참고합니다.

## 역할이 분명한 일곱 스킬

변경 범위에 맞는 가장 작은 skill을 사용합니다.

| Skill | 용도 |
|---|---|
| `build-harness` | 새 하네스를 생성하거나 기존 하네스를 융화하고 전체 토폴로지를 마이그레이션 |
| `build-agent` | 프로젝트 역할 하나를 추가하거나 수정 |
| `build-skill` | 프로젝트가 소유하는 실행 스킬 하나를 추가하거나 수정 |
| `build-evaluator` | 작업 평가기 또는 하네스 효과 평가기를 추가하거나 수정 |
| `verify-harness` | 스키마, 참조, DAG, 권한, 어댑터 동등성을 결정적으로 검증 |
| `evaluate-harness` | baseline, control, treatment 증거를 비교 |
| `improve-harness` | 입증된 하네스 결함을 한두 건만 수정하고 결과를 재평가 |

원자적 build 스킬은 공통 명세를 먼저 수정하고 선택한 런타임 어댑터에 다시 투영한 뒤 동등성을 검증합니다. 에이전트, 스킬, 평가기 하나를 바꾸기 위해 전체 하네스를 다시 만들 필요는 없습니다.

## 프로젝트 소유와 점진적 변경

Harness Factory는 설치된 하네스를 중앙에서 운영하는 제어면이나 패키지 레지스트리가 아닙니다. 각 대상 프로젝트가 정본 명세, 상태, 추가 전용 원장, 평가 증거, 학습 증거, 변경 보고서와 메모리를 직접 소유합니다.

`build-harness`는 대상을 `create`, `improve`, `reconcile` 중 하나로 분류합니다. 기존 하네스에서는 기준선, 파일 소유권, 보존 목록을 먼저 기록한 뒤 필요한 변경분만 적용합니다. 기존 ID, 상태, 원장, 평가기, 승인 게이트, 사용자 규칙, Learning Gate 상태, 학습 증거, reporting 정책, 소유권을 알 수 없는 파일은 승인 없이 삭제하거나 이름을 바꾸거나 의미를 교체하지 않습니다.

의미의 정본은 `harness/harness-spec.json`과 프로젝트가 소유하는 공통 문서·정책입니다. 공통 정본을 먼저 수정해야 하며, 런타임 어댑터만 직접 고치면 다음 투영에서 변경이 사라질 수 있습니다.

## LLM을 매번 호출하지 않는 평가

작업 완료 판정과 하네스 효과 평가는 서로 분리됩니다. 각 작업은 연결된 작업 평가기로 완료 여부를 판정하고, 읽기 전용 결정적 검사기가 하네스 자체에 추가 평가가 필요한지 결정합니다.

```text
task boundary
  → deterministic checker
  → input-invalid:*: verify and repair structure; do not open effect evaluation
  → adapter-change|parity-fail: restore provider parity first
  → none: stop
  → targeted: run only the fixed deterministic metrics for the reason
  → full: compare baseline, control, and treatment
  → completed targeted/full: acknowledge the frozen decision
  → attributed harness defect: consider improve-harness
```

재실행 대기 기간, 표본 하한, 평가 예산은 필수가 아닌 작업을 유예합니다. 일반 메모리 변경은 결정적으로 검사할 뿐 그 자체로 full 실험을 일으키지 않습니다. 따라서 평소 작업 경계의 비용은 낮게 유지하면서 계약 변경, 회귀, 콜드 스타트 실패, 어댑터 드리프트에는 더 강한 평가를 적용할 수 있습니다.

Learning Gate 검증은 이 하네스 효과 평가 루프와 별개입니다. 적용 대상 변경에 대해 개발자가 코드를 이해했다는 증거를 확인할 뿐, 하네스 자체의 성능이 개선됐다고 판정하지 않습니다. Learning Assist 단독 사용은 설명 보조이며 비차단입니다.

## 생성되는 구조

```text
<target>/
├── harness/                              # Runtime-neutral source of truth
│   ├── harness-spec.json                 # Schema 1.1
│   ├── HARNESS.md
│   ├── team/agents/<role-id>.md
│   ├── skills/<skill-id>/SKILL.md
│   ├── policies/
│   │   ├── reporting.json                # file|notion|slack 읽기 위치
│   │   ├── learning-gate.json            # enabled=false로 설치
│   │   └── LEARNING-GATE.md
│   ├── reports/
│   │   └── <change-id>/CHANGE-REPORT.md
│   ├── learning-assist/
│   │   ├── _templates/
│   │   └── <change-id>/                  # 사용자가 요청한 세션 산출물
│   ├── learning/
│   │   ├── _templates/
│   │   └── <change-id>/                  # Gate ON + 적용 대상 증거
│   ├── loops/
│   │   └── HARNESS-EVAL-LOOP.md
│   ├── evaluation/
│   │   ├── EVALUATION-CONTRACT.md
│   │   └── suites/targeted.json
│   ├── triggers/
│   │   ├── check_self_evaluation.py
│   │   ├── record_self_evaluation.py
│   │   └── verify_learning_gate.py
│   ├── state/
│   │   ├── state.json
│   │   └── self-evaluation.json
│   ├── memory/INDEX.md
│   └── ledger/
├── CLAUDE.md
├── .claude/{skills,agents}/
├── AGENTS.md
├── .agents/skills/
├── .codex/{agents,config.toml}
├── GEMINI.md
└── .gemini/{skills,agents}/
```

## 로컬 체크아웃

아직 배포하지 않은 변경을 시험하거나 오프라인에서 사용하려면 저장소를 복제합니다.

```powershell
git clone https://github.com/HanyeolKo/harness-factory.git
cd harness-factory
```

로컬 체크아웃을 사용할 런타임에 연결합니다.

```powershell
claude --plugin-dir D:\workspace\harness-factory
codex plugin marketplace add D:\workspace\harness-factory
codex plugin marketplace list
gemini extensions link D:\workspace\harness-factory
```

Codex에서는 로컬 체크아웃을 등록한 뒤 Plugins에서 `harness-factory`를 설치하거나 활성화하고 새 작업을 시작합니다.

완전한 오프라인 첫 실행에는 체크아웃 안에 `schema/`, `providers/`, `templates/`, `scripts/`, `skills/`가 모두 있어야 합니다. 자동 소스 탐색을 사용할 수 없으면 `HARNESS_FACTORY_HOME`이 저장소 루트를 가리키도록 설정합니다. 버전 고정, 업데이트, 리졸버 설정은 설치 가이드를 참고하세요.

## 문서

- [설치, 업데이트, 버전 고정](docs/SETUP.md)
- [운영, 평가, 개선](docs/OPERATIONS.md)
- [Learning Assist](docs/LEARNING-ASSIST.md)
- [Reporting Contract](docs/REPORTING-CONTRACT.md)
- [Learning Gate](docs/LEARNING-GATE.md)
- [plugin 0.1 또는 schema 1.0에서 마이그레이션](docs/MIGRATION.md)
- [구성자 프로토콜](docs/CONSTRUCTOR-PROTOCOL.md)
- [평가 계약](docs/SKILL-EVALUATION.md)
- [인도 체크리스트](CHECKLIST.md)

## 저장소 검사

변경을 배포하기 전에 저장소 계약을 검사합니다.

```powershell
python scripts\test_runtime_neutral_contract.py
python scripts\test_self_evaluation_trigger.py
python scripts\test_learning_gate_contract.py
python scripts\skill_smoke_build_harness.py
python scripts\validate_runtime_neutral.py <target-project>
```

이 검사는 플러그인 0.2.1 매니페스트, 일곱 스킬, Claude/Codex/Gemini 어댑터, 스키마 1.1, 투영 동등성, 결정적 trigger 정책, Learning Assist/reporting 계약, Learning Gate의 OFF/ON 무결성 계약을 확인합니다. 마지막 명령은 실제 대상 프로젝트에 생성된 하네스를 검증합니다.
