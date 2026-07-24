# harness-factory

프로젝트가 소유하는 에이전트 하네스를 만들고, 운영 중 증거를 바탕으로 점진적으로 개선하는 팩토리입니다. 하나의 `harness/` 정본에서 Claude Code, Codex, Gemini CLI용 네이티브 어댑터를 생성합니다.

팩토리는 설치된 하네스의 상태를 중앙으로 가져오거나 패키지 레지스트리처럼 흡수하지 않습니다. 상태·평가 기록·개선 이력은 항상 대상 프로젝트 안에 남고, 팩토리 스킬은 그 프로젝트의 정본을 직접 생성하거나 좁게 수정합니다.

## 일곱 개의 스킬

| 스킬 | 용도 |
|---|---|
| `build-harness` | 프로젝트 분석부터 팀·스킬·오케스트레이션·평가·어댑터까지 처음 구성 |
| `build-agent` | 기존 하네스에 역할 하나를 추가하거나 수정 |
| `build-skill` | 프로젝트 고유 실행 스킬을 추가하거나 수정 |
| `build-evaluator` | task evaluator 또는 harness-effect evaluator를 추가하거나 수정 |
| `verify-harness` | schema·참조·DAG·권한·어댑터 parity를 결정적으로 검증 |
| `evaluate-harness` | baseline/control/treatment로 하네스 변경 효과를 평가 |
| `improve-harness` | 검증된 하네스 결함만 1~2개씩 개선하고 효과를 재평가 |

전체를 다시 만들 필요가 없으면 원자적 스킬을 사용합니다. 각 수정은 `harness/harness-spec.json`과 공통 파일을 먼저 바꾸고, 선택된 런타임 어댑터를 다시 투영한 뒤 검증합니다.

## 바로 호출하기

Claude Code:

```text
/harness-factory:build-harness "D:\workspace\step_fps"
```

Codex:

```text
$harness-factory:build-harness "D:\workspace\step_fps"
```

Gemini CLI에서는 extension 설치 후 자연어로 스킬을 지정합니다.

```text
build-harness 스킬을 사용해 D:\workspace\step_fps에 Claude, Codex, Gemini 공용 하네스를 구성해줘.
```

기존 하네스를 점진적으로 바꾸는 예:

```text
build-evaluator 스킬을 사용해 이 프로젝트에 비용 회귀를 판정하는 harness-effect evaluator를 추가해줘.
```

런타임을 지정하지 않으면 지원되는 Claude·Codex·Gemini 어댑터를 생성합니다. 코드와 문서로 확인할 수 없는 목적, 승인 게이트, 완료 기준만 짧게 확인합니다.

## 평가를 항상 돌리지 않는 구조

작업 완료 판정과 하네스 효과 판정을 분리합니다. schema 1.1의 모든 skill은 evaluator를 링크하며 entry/evaluation/verification/domain은 task evaluator, harness-evaluation/improvement는 `scope: harness`, `type: experiment` evaluator를 사용합니다.

매 작업 경계에서는 결정적 checker만 실행합니다.

```text
task boundary
  → deterministic checker
  → input-invalid:*: verify-harness + 구조 복구, effect evaluation/LLM 금지
  → adapter-change|parity-fail: provider parity pass가 선행
  → none: 종료
  → targeted: evaluation/suites/targeted.json의 reason별 결정적 metric만 실행
  → full: baseline/control/treatment 효과 평가
  → 완료한 targeted/full: deterministic recorder ACK
  → full에서 하네스 결함이 입증된 경우에만 improve-harness
```

`targeted.json`은 `cost-regression`, `retry-pressure`, `deterministic-sample`만 고정 metric으로 연결하므로 모호한 LLM 평가가 매번 열리지 않습니다. `minimum_samples`는 success/cost 회귀 비교에만 적용됩니다. `targeted_sample_rate`는 별도의 결정적 `deterministic-sample` 신호를 만들고, cooldown과 전체 운영비 대비 budget gate는 모든 비필수 신호를 유예합니다. `none` 경로에서는 평가·개선 문서도 로드하지 않습니다. 평가 전 checker JSON을 run의 `trigger.json`에 동결하고, 완료된 평가는 `record_self_evaluation.py`가 frozen decision, managed hash, failure acknowledgement를 확인한 뒤 ACK합니다. full ACK는 처리한 pending event와 frozen failure snapshot만 ACK하고 managed canonical/provider hash를 갱신해 같은 mandatory 신호의 반복 평가를 막습니다. 평가 중 생긴 새 event·failure는 다음 경계에 남습니다.

canonical은 checker가 별도 hash합니다. `self_evaluation.watched_paths`에는 선택 provider의 정확한 managed artifact—root guidance, spec skill projection, namespaced agent wrapper, 생성 config—만 둡니다. provider 디렉터리 전체나 unrelated user 파일은 감시하지 않습니다.

## 설치 요약

### Claude Code

```text
/plugin marketplace add HanyeolKo/harness-factory
/plugin install harness-factory@harness-factory-marketplace
/reload-plugins
```

### Codex

```powershell
codex plugin marketplace add HanyeolKo/harness-factory --ref main
codex plugin marketplace list
```

Codex CLI의 `/plugins` 또는 데스크톱 Plugins 화면에서 `harness-factory`를 설치한 뒤 새 작업을 시작합니다.

### Gemini CLI

```powershell
gemini extensions install https://github.com/HanyeolKo/harness-factory --ref main
```

로컬 개발 사본은 다음처럼 연결할 수 있습니다.

```powershell
gemini extensions link D:\workspace\harness-factory
```

설치와 업데이트, 버전 고정, 오프라인 resolver는 [설치 가이드](docs/SETUP.md)를 참고하세요.

## 생성 결과

```text
<target>/
├── harness/                              # 프로젝트가 소유하는 런타임 중립 정본
│   ├── harness-spec.json                 # schema 1.1
│   ├── HARNESS.md
│   ├── team/agents/<role-id>.md
│   ├── skills/<skill-id>/SKILL.md
│   ├── loops/
│   │   └── HARNESS-EVAL-LOOP.md
│   ├── evaluation/EVALUATION-CONTRACT.md
│   ├── evaluation/suites/targeted.json
│   ├── triggers/check_self_evaluation.py
│   ├── triggers/record_self_evaluation.py
│   ├── state/
│   │   ├── state.json
│   │   └── self-evaluation.json
│   └── ledger/
├── CLAUDE.md
├── .claude/{skills,agents}/
├── AGENTS.md
├── .agents/skills/
├── .codex/{agents,config.toml}
├── GEMINI.md
└── .gemini/{skills,agents}/
```

`harness/harness-spec.json`과 그 참조 파일이 의미의 정본입니다. 런타임 어댑터만 직접 고치면 다음 투영에서 사라질 수 있으므로, 공통 정본을 먼저 변경합니다.

## 핵심 보장

- 대상 프로젝트 경계에서 역할과 스킬을 도출하며 고정 팀을 복사하지 않습니다.
- `fast / balanced / deep` 추상 티어를 사용하고 실제 모델 선택은 어댑터에 격리합니다.
- 실행자, 증거 수집자, task verdict owner, harness-effect evaluator의 책임을 구분합니다.
- 원본 증거와 기록이 없으면 pass로 처리하지 않습니다.
- 저비용 checker는 항상 실행할 수 있지만 LLM 평가와 개선은 조건부이며, 완료 평가는 recorder ACK로 중복 실행을 막습니다.
- 선택 provider의 정확한 managed artifact만 hash해 adapter drift·삭제를 찾고 무관한 사용자 파일은 제외합니다.
- 개선은 한 번에 1~2건이며 효과 평가가 나빠지면 수용하지 않습니다.
- state와 append-only ledger는 대상 프로젝트에 남아 새 세션에서도 복원됩니다.
- 인간 승인 게이트, 미실행 검증, 잔여 fail을 숨기지 않습니다.

## 문서

- [설치와 업데이트](docs/SETUP.md)
- [운영·평가·개선](docs/OPERATIONS.md)
- [0.1/schema 1.0 마이그레이션](docs/MIGRATION.md)
- [구성자 프로토콜](docs/CONSTRUCTOR-PROTOCOL.md)
- [평가 계약](docs/SKILL-EVALUATION.md)
- [인도 전 체크리스트](CHECKLIST.md)

## 저장소 검증

```powershell
python scripts\test_runtime_neutral_contract.py
python scripts\test_self_evaluation_trigger.py
python scripts\skill_smoke_build_harness.py
python scripts\validate_runtime_neutral.py <target-project>
```

저장소 검증은 plugin 0.2.0 manifest, 일곱 스킬, Claude·Codex·Gemini 어댑터, schema 1.1, parity, 결정적 trigger 정책을 확인합니다. 마지막 명령은 실제 대상 프로젝트의 생성물을 검사합니다.
