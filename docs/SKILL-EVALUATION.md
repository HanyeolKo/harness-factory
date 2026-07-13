# SKILL-EVALUATION — build-harness 현행 평가

검증일: 2026-07-13
대상: `build-harness`, 호출형 실행·평가·회고 스킬 템플릿, 팀 에이전트 템플릿

## 판정 요약

| 질문 | 판정 | 근거 |
|---|---|---|
| 호출 한 번으로 전체 하네스 구조를 설계하는가 | 통과 | Phase 0~4가 템플릿 해석, 인터뷰, 팀 토폴로지 확정, 생성, 검증·보완을 한 진입점으로 연결한다. |
| 실행 팀이 실제 위임 가능한가 | 통과 | 프로젝트 분석에서 도출한 동적 agent ID를 공통 spec에 기록하고 Claude frontmatter와 self-contained Codex agent TOML로 각각 투영한다. |
| 평가 역할이 독립 팀 레인인가 | 통과 | evaluator runner가 원본 증거를 만들고 owner가 verdict를 소유하며 defect-counting과 improvement capability가 후속 집계·보강을 담당한다. |
| 평가에서 자동 보완까지 연결되는가 | 통과 | 작업 후 평가, 사건당 1회 계상, spec 선변경, 전체 adapter 재생성, parity·콜드스타트·원 evaluator 재검증이 계약에 포함된다. |
| 스킬 폴더만 설치해도 템플릿을 찾는가 | 통과 | 동봉 resolver가 로컬·환경변수·source-isolated cache를 우선하고, 없으면 지정 repository/ref를 가져와 새 필수 계약을 검증한다. |
| Claude와 Codex에서 사용할 수 있는가 | 통과 | dual plugin manifest와 공유 `skills/build-harness`가 namespaced 호출을 제공하고, 생성물은 Claude와 Codex의 공식 native 경로를 각각 사용한다. |

## 확인한 불변 조건

1. evaluator 없는 작업 단위 실행 금지.
2. 원본 평가 증거와 기록 없는 pass 금지.
3. 인간 승인 게이트 무단 통과 금지.
4. `state.json.next_action` 필수, `journal.jsonl` append-only.
5. fail과 인라인 폴백 비은폐.
6. adapter 의미 변경 전 공통 spec 선변경.
7. 선택 runtime 간 agent/skill/evaluator/gate parity.

## 검증 범위

- dual plugin manifest와 공유 `build-harness` frontmatter.
- resolver 로컬·오프라인 해석, repository+raw ref cache key, 세 사본 동일성.
- 고정 8역할과 다른 동적 fixture의 공통 agent 생성.
- Claude agent access별 tools/disallowedTools/permissionMode와 Codex agent TOML/global limits/root block.
- 필수 3종과 임의 domain skill의 공통 canonical SKILL.md 및 Claude/Codex byte-identical 투영.
- spec 중첩 key·참조·DAG·evaluator·approval_gates, 양 adapter parity, 미치환 placeholder, state/journal 콜드스타트 계약.

## 남은 운영 권고

- 기본 GitHub ref는 `main`이므로 재현 가능한 운영은 `HARNESS_FACTORY_REF`에 태그나 commit을 지정한다.
- 네트워크가 금지된 환경은 레포 전체를 설치하거나 `HARNESS_FACTORY_HOME`을 지정하고 resolver를 `--offline`으로 실행한다.
- resolver가 내려받은 템플릿은 실행하지 않고 계약 검증 후 읽기 자료로만 사용한다. 실제 evaluator 실행은 생성된 하네스의 게이트를 따른다.
