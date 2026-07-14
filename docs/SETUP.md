# 설치·업데이트 가이드

이 문서는 `harness-factory` 플러그인을 Claude Code와 Codex에 설치하고, namespaced `build-harness` 스킬이 보이는 상태까지 확인하는 절차입니다.

## 준비 사항

- Git
- Claude Code 2.1 이상 또는 최신 Codex/ChatGPT 데스크톱 앱
- 플러그인이 생성물을 쓸 대상 프로젝트에 대한 쓰기 권한

설치된 플러그인은 캐시 사본에서 로드됩니다. 저장소 checkout을 수정했다고 설치본이 즉시 바뀌지는 않습니다.

## Claude Code

### GitHub marketplace 설치

Claude Code 안에서 실행합니다.

```text
/plugin marketplace add HanyeolKo/harness-factory
/plugin install harness-factory@harness-factory-marketplace
/reload-plugins
```

CLI에서 같은 작업을 하려면 다음 명령을 사용할 수 있습니다.

```powershell
claude plugin marketplace add HanyeolKo/harness-factory
claude plugin install harness-factory@harness-factory-marketplace
```

설치 후 새 세션에서 다음 호출을 입력합니다.

```text
/harness-factory:build-harness
```

경로 인자가 없으면 현재 작업 디렉터리가 대상입니다. 플러그인 skill은 항상 `/plugin-name:skill-name` namespace를 사용합니다.

### 로컬 checkout 시험

설치 없이 현재 파일을 직접 로드합니다.

```powershell
claude --plugin-dir D:\workspace\harness-factory
```

세션 안에서 `/harness-factory:build-harness`를 호출합니다. 파일을 수정한 뒤에는 `/reload-plugins`로 다시 읽을 수 있습니다. 같은 이름의 marketplace 설치본이 있어도 이 세션에서는 `--plugin-dir` 사본이 우선합니다.

### ref 고정

GitHub marketplace를 특정 tag/branch에 고정할 때는 shorthand 뒤에 `@ref`를 붙입니다.

```powershell
claude plugin marketplace add HanyeolKo/harness-factory@v0.1.0
```

Git URL을 직접 사용할 때는 `#ref` 형식도 지원됩니다.

## Codex

### marketplace 등록과 설치

```powershell
codex plugin marketplace add HanyeolKo/harness-factory --ref main
codex plugin marketplace list
```

그다음 설치 surface에서 플러그인을 선택합니다.

- Codex CLI: `/plugins`를 열어 `harness-factory-marketplace`의 `harness-factory` 설치
- ChatGPT 데스크톱 앱: Codex → Plugins에서 같은 marketplace와 plugin 선택

설치나 enable 상태를 바꾼 뒤에는 새 작업을 시작합니다. `$` 선택기에 `harness-factory:build-harness`가 보이는지 확인합니다.

### 로컬 checkout 시험

```powershell
codex plugin marketplace add D:\workspace\harness-factory
codex plugin marketplace list
```

Codex는 저장소의 `.claude-plugin/marketplace.json`을 legacy-compatible catalog로 읽을 수 있습니다. `/plugins` 또는 데스크톱 Plugins 화면에서 설치한 뒤 새 작업을 시작합니다.

### ref 고정

```powershell
codex plugin marketplace add HanyeolKo/harness-factory --ref v0.1.0
```

같은 marketplace를 갱신할 때는 다음 명령을 사용합니다.

```powershell
codex plugin marketplace upgrade harness-factory-marketplace
```

갱신 후 Plugins 화면에서 새 버전을 적용하고 새 작업을 시작합니다.

## 실제 호출

Windows 경로는 따옴표로 감싸는 편이 안전합니다.

Claude:

```text
/harness-factory:build-harness "D:\workspace\step_fps"
```

Codex:

```text
$harness-factory:build-harness "D:\workspace\step_fps"
```

기본값은 Claude+Codex 양쪽 어댑터 생성입니다. 한쪽만 필요하면 요청에 명시합니다.

```text
$harness-factory:build-harness 이 프로젝트를 분석하되 Codex 어댑터만 생성해줘.
```

기존 하네스가 있으면 별도 지시가 없어도 `improve|reconcile` 모드로 열어 state, append-only ledger, evaluator, gate, 사용자 규칙과 메모리를 보존합니다. 삭제·이름 변경·의미 교체처럼 보존 정책을 바꿀 때만 범위와 승인을 명시합니다.

## 팩토리 source와 오프라인 설정

플러그인 skill은 resolver로 다음 순서의 호환 가능한 팩토리를 찾습니다.

1. 호출에서 지정한 로컬 factory root
2. `HARNESS_FACTORY_HOME`
3. 설치된 plugin/factory 조상 경로
4. 요청한 repository+raw ref와 provenance가 일치하는 cache
5. 네트워크가 허용된 경우 지정 repository/ref

PowerShell:

```powershell
$env:HARNESS_FACTORY_HOME = 'D:\workspace\harness-factory'
$env:HARNESS_FACTORY_REF = 'v0.1.0'
```

Bash:

```bash
export HARNESS_FACTORY_HOME=/workspace/harness-factory
export HARNESS_FACTORY_REF=v0.1.0
```

fork나 사설 저장소를 사용하려면 `HARNESS_FACTORY_REPO`를 설정할 수 있습니다. cache key는 repository URL과 raw ref의 hash를 함께 사용하고 provenance에는 URL 대신 fingerprint를 저장합니다.

완전 오프라인 첫 실행에는 호환되는 전체 checkout을 `HARNESS_FACTORY_HOME`으로 제공해야 합니다. 이미 해당 source/ref cache가 있으면 offline resolver가 재사용할 수 있습니다. source가 다른 동일 ref cache를 대신 사용하지 않습니다.

## 업데이트

Claude:

```text
/plugin marketplace update harness-factory-marketplace
/reload-plugins
```

새 plugin version이 보이면 Installed 탭에서 업데이트하거나 재설치합니다. marketplace plugin은 버전별 cache에 복사되므로 repository 수정만으로 설치본이 바뀌지 않습니다.

Codex:

```powershell
codex plugin marketplace upgrade harness-factory-marketplace
```

Plugins 화면에서 새 버전을 적용한 뒤 데스크톱 앱을 다시 열거나 새 작업을 시작합니다.

## 문제 해결

### namespaced skill이 보이지 않음

- Claude: `/plugin`의 Installed/Errors 탭 확인 → `/reload-plugins`
- Codex: `codex plugin marketplace list` 확인 → `/plugins`에서 설치·enable 확인 → 새 작업 시작
- manifest 이름이 `harness-factory`, skill 이름이 `build-harness`인지 확인

### 템플릿을 찾지 못함

`HARNESS_FACTORY_HOME`이 저장소 루트를 가리키는지 확인합니다. 해당 루트에는 dual plugin manifest, schema, shared skill, adapter templates가 모두 있어야 합니다.

### 기존 root 규칙과 충돌함

생성자는 `CLAUDE.md`와 `AGENTS.md`의 harness-factory 관리 블록만 upsert하고, `.codex/config.toml`의 전역 agent limits를 구조적으로 병합합니다. 같은 namespace나 충돌 필드가 이미 있으면 자동 덮어쓰지 말고 보고하도록 설계되어 있습니다.

## 공식 형식 참고

- [Claude Code plugins](https://code.claude.com/docs/en/plugins)
- [Claude Code marketplaces](https://code.claude.com/docs/en/discover-plugins)
- [Codex plugins](https://developers.openai.com/codex/plugins)
- [Build Codex plugins](https://developers.openai.com/codex/plugins/build)
- [Codex customization](https://developers.openai.com/codex/concepts/customization)
