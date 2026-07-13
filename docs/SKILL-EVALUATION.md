# SKILL-EVALUATION — build-harness 현행 평가

검증일: 2026-07-13
대상: `build-harness`, 호출형 실행·평가·회고 스킬 템플릿, 팀 에이전트 템플릿

## 판정 요약

| 질문 | 판정 | 근거 |
|---|---|---|
| 호출 한 번으로 전체 하네스 구조를 설계하는가 | 통과 | Phase 0~4가 템플릿 해석, 인터뷰, 팀 토폴로지 확정, 생성, 검증·보완을 한 진입점으로 연결한다. |
| 실행 팀이 실제 위임 가능한가 | 통과 | 8개 역할이 이름이 격리된 agent frontmatter를 가지며 Claude에서는 `.claude/agents/`에 설치된다. 실행 스킬은 라우터→영향분석가→코디네이터→작업자를 이름으로 위임한다. |
| 평가 역할이 독립 팀 레인인가 | 통과 | verification-runner가 원본 증거를 만들고 evaluation-lead가 verdict를 소유한다. defect-counter와 improvement-coordinator는 집계와 보강 제안만 담당한다. |
| 평가에서 자동 보완까지 연결되는가 | 통과 | 작업 후 평가 자동 인계, fail 사건당 1회 카운트, 트리거 시 회고 자동 개시, 제안 자동 적용, 콜드스타트·원 evaluator 재검증이 계약에 포함된다. |
| 스킬 폴더만 설치해도 템플릿을 찾는가 | 통과 | 동봉 resolver가 로컬·환경변수·캐시를 우선하고, 없으면 공식 GitHub ref를 가져와 필수 템플릿 계약을 검증한다. |
| Claude와 Codex에서 사용할 수 있는가 | 통과 | 동일한 `build-harness` 스킬과 실행·평가·회고 스킬을 양쪽 경로에 제공한다. 실제 서브에이전트 API가 없는 런타임만 기록 가능한 인라인 폴백을 사용한다. |

## 확인한 불변 조건

1. evaluator 없는 작업 단위 실행 금지.
2. 원본 평가 증거와 기록 없는 pass 금지.
3. 인간 승인 게이트 무단 통과 금지.
4. `state.json.next_action` 필수, `journal.jsonl` append-only.
5. fail과 인라인 폴백 비은폐.

## 검증 범위

- `skill-creator` frontmatter 검증: Claude/Codex `build-harness` 양쪽.
- resolver 로컬·오프라인 해석과 양쪽 사본 동일성.
- disposable 대상의 템플릿 렌더링과 미치환 플레이스홀더 0건.
- 실행·평가·회고 스킬 3종 설치.
- Claude 에이전트 8종 설치와 namespaced frontmatter.
- 팀 흐름, 평가 레인, 자동 보완 규칙, state/journal 콜드스타트 계약.

## 남은 운영 권고

- 기본 GitHub ref는 `main`이므로 재현 가능한 운영은 `HARNESS_FACTORY_REF`에 태그나 commit을 지정한다.
- 네트워크가 금지된 환경은 레포 전체를 설치하거나 `HARNESS_FACTORY_HOME`을 지정하고 resolver를 `--offline`으로 실행한다.
- resolver가 내려받은 템플릿은 실행하지 않고 계약 검증 후 읽기 자료로만 사용한다. 실제 evaluator 실행은 생성된 하네스의 게이트를 따른다.
