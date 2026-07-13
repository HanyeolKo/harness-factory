# harness-factory

Claude Code의 `/harness:harness`처럼 한 번 호출해 프로젝트별 에이전트 팀과 스킬을 구성하되, 결과를 Claude에 종속시키지 않고 Codex에서도 같은 의미로 실행할 수 있게 만드는 하네스 팩토리입니다.

대상 프로젝트를 분석해 공통 `harness/` 명세를 먼저 만들고, 그 명세에서 Claude와 Codex의 네이티브 skills·agents·root 규칙을 각각 생성합니다. 역할 수와 이름은 고정하지 않으며 프로젝트의 서비스·모듈·데이터 경계와 실제 evaluator에서 도출합니다.

## 바로 호출하기

Claude Code:

```text
/harness-factory:build-harness "D:\workspace\step_fps"
```

Codex:

```text
$harness-factory:build-harness "D:\workspace\step_fps"
```

목적까지 한 번에 전달할 수 있습니다.

```text
/harness-factory:build-harness "D:\workspace\step_fps"의 기존 control tower를 보존하면서
프로젝트별 coordinator, 전문 skill, 평가·자기개선 루프를 Claude와 Codex 양쪽으로 구성해줘.
```

런타임을 따로 지정하지 않으면 Claude와 Codex 어댑터를 모두 생성합니다. 코드와 문서로 확인할 수 없는 목적·승인 게이트·완료 기준만 최대 두 번의 질문 묶음으로 확인합니다.

## 설치 요약

### Claude Code

Claude Code 안에서 marketplace를 추가하고 플러그인을 설치합니다.

```text
/plugin marketplace add HanyeolKo/harness-factory
/plugin install harness-factory@harness-factory-marketplace
/reload-plugins
```

로컬 checkout을 바로 시험하려면 다음처럼 실행합니다.

```powershell
claude --plugin-dir D:\workspace\harness-factory
```

### Codex

marketplace를 등록합니다.

```powershell
codex plugin marketplace add HanyeolKo/harness-factory --ref main
codex plugin marketplace list
```

그다음 Codex CLI에서는 `/plugins`, ChatGPT 데스크톱 앱에서는 Plugins 화면을 열어 `harness-factory-marketplace`의 `harness-factory`를 설치하고 새 작업을 시작합니다. 새 작업에서 `$` 선택기에 `harness-factory:build-harness`가 나타나면 준비가 끝난 것입니다.

버전 고정, 로컬 개발, Windows/Bash 환경변수, 업데이트와 오프라인 설정은 [설치 가이드](docs/SETUP.md)를 참고하세요.

## 생성 결과

```text
<target>/
├── harness/                         # 런타임 중립 정본
│   ├── harness-spec.json            # domains, agents, skills, DAG, evaluators, gates, loops
│   ├── HARNESS.md
│   ├── team/agents/<role-id>.md
│   ├── skills/<skill-id>/SKILL.md   # 모든 runtime skill의 공통 정본
│   ├── loops/
│   ├── state/
│   └── ledger/
├── CLAUDE.md                        # 기존 내용 + harness-factory 관리 블록
├── .claude/
│   ├── skills/<skill-id>/SKILL.md
│   └── agents/<namespace>-<role-id>.md
├── AGENTS.md                        # 기존 내용 + harness-factory 관리 블록
├── .agents/skills/<skill-id>/SKILL.md
└── .codex/
    ├── agents/<namespace>-<role-id>.toml
    └── config.toml
```

`harness/harness-spec.json`과 여기서 참조하는 `harness/skills/<skill-id>/SKILL.md`가 의미의 정본입니다. Claude/Codex 파일은 각 런타임이 발견할 수 있게 만든 어댑터이므로, 역할·handoff·skill·evaluator·승인 게이트를 바꿀 때는 공통 정본을 먼저 바꾸고 양쪽을 다시 생성합니다.

## 생성된 하네스 사용

예를 들어 namespace가 `step-control-tower`라면 다음과 같이 호출합니다.

| 작업 | Claude | Codex |
|---|---|---|
| 실행·라우팅 | `/step-control-tower` | `$step-control-tower` |
| 평가·완료 판정 | `/step-control-tower-eval` | `$step-control-tower-eval` |
| 회고·보강 | `/step-control-tower-retro` | `$step-control-tower-retro` |

일반 작업은 실행 스킬만 호출하면 됩니다. 실행 후 evaluator로 자동 인계하고, 반복 실패·평가 공백·콜드스타트 실패가 발생하면 개선 루프가 공통 명세와 어댑터를 보강한 뒤 원 evaluator와 parity를 다시 확인합니다.

## 핵심 보장

- 프로젝트 경계에서 역할·스킬을 도출하며 고정 8역할을 복사하지 않습니다.
- `fast / balanced / deep` 추상 티어를 사용하고 런타임별 실제 모델 선택은 어댑터에 격리합니다.
- 실행자와 증거 수집자·완료 판정자를 계약상 분리합니다.
- evaluator, 원본 증거, journal 기록이 없으면 pass로 처리하지 않습니다.
- state와 append-only ledger로 새 세션에서도 다음 행동을 복원합니다.
- 개선은 공통 명세 선변경 → 전체 어댑터 재생성 → parity·콜드스타트·원 evaluator 재검증 순서로 진행합니다.
- 인간 승인 게이트, 미실행 검증, 인라인 폴백과 잔여 fail을 숨기지 않습니다.

## 문서

- [설치와 업데이트](docs/SETUP.md)
- [운영·평가·개선 루프](docs/OPERATIONS.md)
- [기존 standalone/fixed-team 하네스 마이그레이션](docs/MIGRATION.md)
- [구성자 프로토콜](docs/CONSTRUCTOR-PROTOCOL.md)
- [인도 전 체크리스트](CHECKLIST.md)

## 저장소 검증

```powershell
python scripts\test_runtime_neutral_contract.py
python scripts\skill_smoke_build_harness.py
python scripts\validate_runtime_neutral.py <target-project>
```

첫 두 명령은 플러그인 manifest, 공통 스킬, 동적 역할 생성, Claude/Codex native adapter, TOML/frontmatter, parity, DAG, resolver의 repository/ref 캐시 격리를 검증합니다. 마지막 명령은 실제 생성된 프로젝트를 검사합니다.
