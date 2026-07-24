# 설치·업데이트 가이드

이 문서는 `harness-factory` 0.2.0을 Claude Code, Codex, Gemini CLI에 설치하고 일곱 스킬이 보이는 상태까지 확인하는 절차입니다.

설치되는 것은 **팩토리 도구**입니다. 이미 생성된 하네스의 state·ledger·평가 결과를 팩토리 저장소로 옮기지 않습니다. 각 하네스는 대상 프로젝트의 `harness/` 안에서 독립적으로 성장합니다.

## 준비 사항

- Git
- 사용할 런타임 중 하나 이상: Claude Code, Codex/ChatGPT 데스크톱, Gemini CLI
- 대상 프로젝트 쓰기 권한
- trigger checker와 validator를 실행할 Python 3

marketplace나 extension으로 설치한 사본은 캐시에서 로드될 수 있습니다. checkout 수정 사항을 바로 시험할 때는 아래 로컬 개발 방법을 사용합니다.

## Claude Code

### GitHub marketplace 설치

Claude Code 안에서 실행합니다.

```text
/plugin marketplace add HanyeolKo/harness-factory
/plugin install harness-factory@harness-factory-marketplace
/reload-plugins
```

CLI에서 같은 작업을 수행할 수도 있습니다.

```powershell
claude plugin marketplace add HanyeolKo/harness-factory
claude plugin install harness-factory@harness-factory-marketplace
```

설치 후 새 세션에서 `/harness-factory:build-harness`를 입력합니다. 원자적 작업에는 같은 namespace의 `build-agent`, `build-skill`, `build-evaluator`, `verify-harness`, `evaluate-harness`, `improve-harness`를 사용합니다.

### 로컬 checkout 시험

```powershell
claude --plugin-dir D:\workspace\harness-factory
```

수정 후 `/reload-plugins`로 다시 읽습니다.

## Codex

### marketplace 등록과 설치

```powershell
codex plugin marketplace add HanyeolKo/harness-factory --ref main
codex plugin marketplace list
```

Codex CLI의 `/plugins` 또는 ChatGPT 데스크톱의 Plugins 화면에서 `harness-factory`를 설치한 뒤 새 작업을 시작합니다. `$` 선택기에 `harness-factory:build-harness`와 나머지 여섯 스킬이 보이는지 확인합니다.

### 로컬 checkout 시험

```powershell
codex plugin marketplace add D:\workspace\harness-factory
codex plugin marketplace list
```

설치 또는 enable 상태를 바꾼 뒤에는 새 작업을 시작합니다.

## Gemini CLI

저장소 루트의 `gemini-extension.json`과 `GEMINI.md`를 사용하는 extension입니다.

### GitHub 설치

```powershell
gemini extensions install https://github.com/HanyeolKo/harness-factory --ref main
```

설치 후 Gemini CLI를 다시 시작하고 확인합니다.

```text
/extensions list
```

Gemini의 agent skill은 필요할 때 로드되므로 자연어로 이름을 지정합니다.

```text
verify-harness 스킬을 사용해 현재 프로젝트의 하네스를 검사해줘.
```

### 로컬 checkout 시험

```powershell
gemini extensions link D:\workspace\harness-factory
```

설치본은 source 사본이므로 일반 설치를 갱신할 때는 다음 명령을 사용합니다.

```powershell
gemini extensions update harness-factory
```

Gemini extension 명령은 interactive session 밖의 터미널에서 실행합니다. 공식 형식은 [Gemini CLI extension reference](https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/reference.md)를 참고합니다.

## 버전 고정

재현 가능한 운영에서는 branch보다 tag 또는 commit을 권장합니다.

Claude:

```powershell
claude plugin marketplace add HanyeolKo/harness-factory@v0.2.0
```

Codex:

```powershell
codex plugin marketplace add HanyeolKo/harness-factory --ref v0.2.0
```

Gemini:

```powershell
gemini extensions install https://github.com/HanyeolKo/harness-factory --ref v0.2.0
```

## 실제 호출

Windows 경로는 따옴표로 감쌉니다.

```text
/harness-factory:build-harness "D:\workspace\step_fps"
$harness-factory:build-harness "D:\workspace\step_fps"
```

Gemini에서는 다음처럼 요청합니다.

```text
build-harness 스킬을 사용해 D:\workspace\step_fps에 하네스를 구성해줘.
```

기본값은 Claude·Codex·Gemini 어댑터입니다. 필요한 런타임만 명시해 축소할 수 있습니다. 기존 state와 ledger가 있으면 새 package로 가져오는 대신 **대상 프로젝트에서 보존하며 schema 1.1로 점진 마이그레이션**합니다.

## 팩토리 source와 오프라인 설정

각 factory skill의 resolver는 다음 순서로 호환 가능한 source를 찾습니다.

1. 호출에서 지정한 로컬 factory root
2. `HARNESS_FACTORY_HOME`
3. 설치된 plugin 또는 extension의 조상 경로
4. repository와 raw ref provenance가 일치하는 cache
5. 네트워크가 허용된 경우 지정 repository/ref

PowerShell:

```powershell
$env:HARNESS_FACTORY_HOME = 'D:\workspace\harness-factory'
$env:HARNESS_FACTORY_REF = 'v0.2.0'
```

Bash:

```bash
export HARNESS_FACTORY_HOME=/workspace/harness-factory
export HARNESS_FACTORY_REF=v0.2.0
```

fork나 사설 저장소는 `HARNESS_FACTORY_REPO`를 지정합니다. 완전 오프라인 첫 실행에는 schema, providers, templates, scripts, skills를 포함한 전체 checkout을 `HARNESS_FACTORY_HOME`으로 제공해야 합니다.

## 업데이트

Claude:

```text
/plugin marketplace update harness-factory-marketplace
/reload-plugins
```

Codex:

```powershell
codex plugin marketplace upgrade harness-factory-marketplace
```

Gemini:

```powershell
gemini extensions update harness-factory
```

업데이트 후에는 새 세션을 시작하고 manifest가 0.2.0인지, 일곱 스킬이 모두 보이는지 확인합니다.

## 문제 해결

### 스킬이 일부만 보임

- Claude: `/plugin`의 Installed/Errors 확인 후 `/reload-plugins`
- Codex: marketplace와 enable 상태를 확인하고 새 작업 시작
- Gemini: `/extensions list` 확인 후 CLI 재시작
- 설치 source가 0.2.0이고 `skills/` 아래 일곱 폴더가 있는지 확인

### 템플릿 또는 provider 계약을 찾지 못함

`HARNESS_FACTORY_HOME`이 저장소 루트를 가리키는지 확인합니다. 루트에는 plugin/extension manifest, `schema/`, `providers/`, `templates/`, `scripts/`, `skills/`가 있어야 합니다.

### 기존 root 규칙과 충돌함

생성자는 `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`의 harness-factory 관리 블록만 upsert합니다. `.codex/config.toml`은 관련 agent limits만 구조적으로 병합합니다. 관리 블록 밖 사용자 문장과 unrelated 설정은 보존해야 하며, 충돌은 자동 덮어쓰지 않고 보고합니다.

### 평가가 매번 LLM을 호출함

정상 0.2.0 하네스는 작업 경계에서 결정적 trigger checker만 실행합니다. `harness/harness-spec.json`의 `self_evaluation` 정책과 `harness/state/self-evaluation.json`을 확인하고, 실행 루프가 checker의 `none|targeted|full` 결과를 건너뛰지 않는지 검사합니다.
