# Issue 001 — 스킬 템플릿의 플랫폼 결합과 실행 규율 부족

## 배경

`templates/skills/SKILL-TEMPLATE.md`는 하네스 루프를 스킬로 노출하기 위한 선택 템플릿이다. 현재 내용은 Claude Code의 `.claude/skills/<skill-name>/SKILL.md` 설치 경로와 간단한 3단계 실행만 안내한다.

## 문제

1. **플랫폼 결합**: Codex 계열 스킬은 `$CODEX_HOME/skills/<skill-name>/SKILL.md`처럼 다른 설치 경로와 트리거 문법을 쓴다. 현재 템플릿은 Claude Code 전용처럼 보인다.
2. **트리거 불명확**: 세션 시작, 하네스 실행, 회고 요청, 인자 제공 시 어떤 스킬을 언제 호출해야 하는지 description에 충분히 드러나지 않는다.
3. **콜드스타트·불변 조건 누락**: README의 핵심 규율(콜드스타트, evaluator 선정, state/journal 갱신, fail 비은폐)이 스킬 템플릿에 직접 반영되어 있지 않아 스킬 경유 실행 시 누락될 수 있다.
4. **회고 전용 스킬 미완성**: `{{SKILL_NAME}}-retro`를 만들 수 있다고만 말하고, 실제 복사 가능한 템플릿은 없다.

## 기대 효과

- 하네스 스킬을 Claude Code와 Codex 모두에 이식하기 쉬워진다.
- 스킬을 통해 실행해도 README §3/§불변 조건과 생성 하네스의 루프 규율이 유지된다.
- 회고 스킬을 복사 가능한 형태로 제공해 보완 루프 진입 비용을 낮춘다.

## 제안 작업

- 스킬 템플릿을 플랫폼 중립 설치 가이드 + Codex/Claude 경로 예시로 개편한다.
- 실행 스킬 본문에 콜드스타트, evaluator 확인, 기록/체크포인트 의무, 인자 해석을 명시한다.
- 회고 전용 스킬 템플릿을 함께 제공한다.
- README의 디렉토리 맵 설명을 현재 템플릿 성격과 맞춘다.


## 검증 방식

- `scripts/skill_smoke_build_harness.py`로 disposable 대상 프로젝트를 생성한다.
- `.claude/skills/build-harness/SKILL.md`의 Phase 0~4 흐름을 따라 하네스 템플릿을 치환한다.
- 렌더링된 실행 스킬과 회고 스킬을 Codex/Claude 양쪽 위치에 설치한다.
- 산출물 계약 파일 존재, `state.next_action`, 큐 evaluator, 초기 journal, 미치환 플레이스홀더, 스킬 frontmatter를 검증한다.
