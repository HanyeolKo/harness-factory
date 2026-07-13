---
name: build-harness
description: harness-factory 프로토콜로 대상 프로젝트/작업의 호출형 하네스를 설계·생성한다. 사용자가 "하네스 구성해줘", "이 레포 참고해서 하네스 만들어줘", "builder-harness로 팀 구조 잡아줘"라고 요청할 때 사용. 실행 팀과 평가·자동보완 레인을 구성하며, 로컬 템플릿이 없으면 공식 GitHub 저장소에서 호환 템플릿을 해석한다.
---

# build-harness

harness-factory의 구성자 수행 프로토콜(`docs/CONSTRUCTOR-PROTOCOL.md`)을 실행한다. 목표는 문서 묶음만 만드는 것이 아니라, 대상 프로젝트에서 호출 가능한 하네스 스킬이 라우팅·영향분석·위임·평가·보강을 유기적으로 수행하게 하는 것이다.

## 템플릿 루트 확인

1. 이 `SKILL.md`와 같은 스킬 폴더의 `scripts/resolve_factory.py`를 실행한다. 이미 알고 있는 팩토리 루트가 있으면 `--factory-root <경로>`를 함께 준다.
2. resolver는 로컬 팩토리, `HARNESS_FACTORY_HOME`, 검증된 캐시 순으로 찾는다. 없으면 사용자에게 네트워크 접근을 알린 뒤 공식 저장소 `https://github.com/HanyeolKo/harness-factory.git`의 `HARNESS_FACTORY_REF`(기본 `main`)를 캐시에 가져온다.
3. stdout의 절대 경로를 `FACTORY_ROOT`로 사용한다. resolver가 필수 템플릿 계약을 통과시키지 못하면 임의 템플릿을 만들지 말고 중지한다.
4. 사용한 로컬 경로 또는 GitHub URL·ref·commit을 생성 하네스의 D-001에 기록한다. 오프라인 요청이면 `--offline`을 사용하고 네트워크 폴백을 시도하지 않는다.

## 절차

1. **Phase 0 — 원칙 로드·자료 수집**: `FACTORY_ROOT`의 `README.md`, `docs/CONSTRUCTOR-PROTOCOL.md`, `principles/` 전체(01~07), `interview/QUESTION-BANK.md`, `CHECKLIST.md`를 읽는다. 대상 자료를 수집해 (a) 결정적 evaluator 후보, (b) 질문 소거 재료, (c) 하네스 목적 가설, (d) 실행 팀 경계와 평가 레인 후보를 만든다.
2. **Phase 1 — 인터뷰**: `interview/QUESTION-BANK.md`의 1차 배치 4문항을 질의한다. Q1에서는 Phase 0의 목적 가설을 제시하고 사용자 입력으로 확정받는다. 복합 프로젝트·장기 작업·경계면 위험이 있으면 Q11로 팀 구조와 평가 책임을 확인한다. 사용자가 "알아서"라고 하면 기본값 일괄표와 기본 팀 구조를 적용한다.
3. **Phase 2 — 결정 확정**: 답변을 템플릿 치환 필드에 매핑하고 D-001 초안을 정리한다. `harness:harness`의 장점인 라우팅 → 영향분석 → 코디네이터 위임 구조를 일반화하되, 대상이 단순하면 축약 실행으로 기록한다. 기존 builder-harness의 평가 역할은 `evaluation-lead`·`verification-runner`·`defect-counter`·`improvement-coordinator` 평가 레인으로 승격한다.
4. **Phase 3 — 인스턴스화**: `FACTORY_ROOT/templates/` 이하를 대상 위치(기본 `<대상>/harness/`)로 복사하며 `{{...}}`를 전부 치환한다. 실행·평가·회고 스킬 3종을 런타임 스킬 경로에 설치한다. Claude에서는 렌더링된 팀 정의 8종을 `<대상>/.claude/agents/{{SKILL_NAME}}-<role>.md`에도 설치해 실제 위임 가능하게 한다. 다른 런타임은 지원되는 서브에이전트 도구에 같은 역할 정의를 전달하고, 미지원일 때만 인라인 폴백과 사유를 기록한다.
5. **Phase 4 — 검증·보완 루프(최대 3회)·인도**: `FACTORY_ROOT/CHECKLIST.md` 전 항목을 수행한다. 미치환 플레이스홀더 0건, 콜드스타트, 팀 위임 구조, 평가 책임, fail 카운터와 자동 보강 환류를 확인한다. Claude 대상이면 `.claude/agents/` 8종의 frontmatter와 실행 스킬의 실제 위임 지시도 검증한다. fail이 있으면 보완 후 재검증하고 D-001에 누적한다.

## 인자 해석

- 경로가 주어지면: 해당 경로를 대상 프로젝트로 삼는다.
- 작업 설명이 주어지면: Q1(대상·산출물)의 답으로 선반영하고 인터뷰에서 재확인만 한다.
- 인자가 없으면: 현재 작업 디렉토리를 대상으로 Q1부터 질의한다.
