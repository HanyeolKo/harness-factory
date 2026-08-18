# 설치·업데이트 가이드

이 문서는 `harness-factory` 0.2.1을 Claude Code, Codex, Gemini CLI에 설치하고 일곱 스킬이 보이는 상태까지 확인하는 절차입니다.

설치되는 것은 **팩토리 도구**입니다. 이미 생성된 하네스의 state·ledger·평가 결과를 팩토리 저장소로 옮기지 않습니다. 각 하네스는 대상 프로젝트의 `harness/` 안에서 독립적으로 성장합니다.

## 준비 사항

- Git
- 사용할 런타임 중 하나 이상: Claude Code, Codex/ChatGPT 데스크톱, Gemini CLI
- 대상 프로젝트 쓰기 권한
- trigger checker와 validator를 실행할 Python 3.11 이상

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
claude plugin marketplace add HanyeolKo/harness-factory@v0.2.1
```

Codex:

```powershell
codex plugin marketplace add HanyeolKo/harness-factory --ref v0.2.1
```

Gemini:

```powershell
gemini extensions install https://github.com/HanyeolKo/harness-factory --ref v0.2.1
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
같은 대상에서 `build-harness`를 다시 호출하면 현재 상태를 `improve|reconcile`로 판별하고 baseline·소유권·보존 목록을 만든 뒤 필요한 delta만 제안합니다. 단일 agent·skill·evaluator 변경에는 해당 원자적 build 스킬을 사용합니다.

## 변경 보고서와 Learning Assist

새 하네스를 만들 때 사용자에게 변경 보고서를 어디에 정리할지 묻습니다. 기본값은 프로젝트 내부 `file`이고, 필요하면 `notion` 또는 `slack`을 선택할 수 있습니다. Notion/Slack을 선택하면 대상 페이지·데이터베이스·채널·대화 식별자는 사용자가 지정해야 합니다.

선택값은 `harness/policies/reporting.json`에 저장합니다. 외부 위치를 선택해도 `harness/reports/`와 Learning Gate의 Git 파일은 검증 원본으로 유지합니다.

일반 작업은 짧은 Change Report만 남깁니다. 더 자세한 설명을 요청하면 Learning Assist가 실제 diff와 관련 소스만 읽어 쉬운 설명과 선택적 이해도 퀴즈를 제공합니다. Learning Gate가 켜져 있고 적용 대상이면 같은 Learning Assist 설명을 먼저 읽은 뒤 Gate 퀴즈로 이어집니다. 오답에는 정답을 바로 공개하지 않고 방향 힌트 → 구체적 상황 힌트 → 최종 개념 설명 순서로 보정합니다.
