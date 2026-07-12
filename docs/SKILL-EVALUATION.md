# SKILL-EVALUATION — build-harness 현행 평가

검증일: 2026-07-12
대상: `build-harness` 스킬과 `templates/skills/SKILL-TEMPLATE.md`

## 판정 요약

| 질문 | 판정 | 근거 |
|---|---|---|
| 프로젝트 하네스 구성의 뼈대 역할을 벗어나지 않았는가 | Pass | 스킬은 README §3의 Phase 0~4를 실행하고, 산출물 계약 파일을 생성·검증하는 데 한정된다. 실행 산출물 자체를 대신 구현하지 않는다. |
| 기본 설계 구조와 실행·검증·개선 회고 루프가 확실히 돌아가는가 | Pass | `EXECUTION-LOOP`의 RETRO-CHECK, `EVAL-LOOP`의 기록 의무, `IMPROVE-LOOP`의 트리거·개정·검증·리셋 절차가 연결되어 있다. 스모크 검증은 disposable 하네스에서 산출물 계약, 콜드스타트 핵심값, 스킬 렌더링을 확인한다. |
| Claude와 GPT(Codex)에서 내려받아 스킬로 사용할 수 있는가 | Pass after improvement | 동일한 `build-harness` 스킬을 `.claude/skills/`와 `.codex/skills/`에 제공하고, 런타임별 질의 도구 표현을 중립화했다. 런타임 스킬 템플릿도 Codex/Claude 양쪽 설치 경로를 명시한다. |

## 확인한 불변 조건

1. evaluator 없는 작업 단위 실행 금지.
2. 평가 기록 없는 pass 금지.
3. 인간 승인 게이트 무단 통과 금지.
4. `state.json.next_action` 필수, `journal.jsonl` append-only.
5. fail 비은폐.

## 반영한 개선점

- Codex용 실제 스킬 배포 경로 `.codex/skills/build-harness/SKILL.md`를 추가했다.
- Claude용 스킬의 사용자 질의 문구를 Claude 전용 `AskUserQuestion` 강제에서 런타임 중립 표현으로 바꿨다.
- 스모크 검증에 레포 내 Claude/Codex 스킬 존재, frontmatter, Phase 0~4, 런타임 중립 질의 문구 검사를 추가했다.
- README 디렉토리 맵에 `.codex/skills/build-harness/`를 명시했다.

## 남은 운영 권고

- 실제 설치 배포 시에는 레포 전체 또는 `.codex/skills/build-harness/`, `.claude/skills/build-harness/` 하위만 내려받아도 동작하지만, 스킬 본문은 harness-factory 루트의 `README.md`, `principles/`, `interview/`, `templates/`, `CHECKLIST.md`를 참조하므로 해당 파일들이 함께 있어야 한다.
- 대상 런타임이 frontmatter `description` 검색을 약하게 지원하면 사용자가 “하네스 구성”, “build-harness”처럼 명시적으로 호출하도록 README 또는 프로젝트 규칙 파일에 안내한다.
