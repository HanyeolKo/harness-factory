---
name: build-skill
description: 생성된 하네스에 호출 가능한 런타임 중립 skill을 추가하거나 수정하고 canonical SKILL.md와 Claude/Codex/Gemini 투영본을 동기화한다. 사용자가 실행·도메인·평가·개선 workflow를 스킬로 만들거나 기존 스킬의 책임과 진입 역할을 바꿀 때 사용한다.
---

# build-skill

skill 의미는 `harness/skills/<skill-id>/SKILL.md`에 한 번만 정의하고 runtime 파일은 발견용 투영으로 만든다.

## 팩토리 확인

1. `scripts/resolve_factory.py`로 `FACTORY_ROOT`를 확정한다.
2. runtime contract와 대상 `harness/harness-spec.json`을 읽는다. 공통 spec이 없으면 `build-harness`를 사용한다.

## 절차

1. skill 목적, kind, domain, entry agent, 입력·출력, 실행 조건을 정한다.
2. 책임이 겹치면 새 skill보다 기존 canonical 본문 확장을 우선 검토한다.
3. schema 1.1의 `skills[].evaluator`를 반드시 연결한다.
   - entry/evaluation/verification/domain → `scope: task`; verification은 구조 validator evaluator
   - harness-evaluation/improvement → `self_evaluation.evaluator`인 `scope: harness`, `type: experiment`
4. spec의 skill과 orchestration 참조를 먼저 변경한다.
5. canonical `harness/skills/<skill-id>/SKILL.md`를 만든다.
6. provider adapter를 쓰기 전에 `python <FACTORY_ROOT>/scripts/validate_runtime_neutral.py <target> --provider-path-preflight`를 실행하고 exit 0을 확인한다. provider 경로가 절대 경로·lexical traversal·symlink escape로 target 밖을 가리키면 실패하며, 그때는 provider 디렉터리·파일을 생성·쓰기·이동하거나 우회 경로를 사용하지 않는다.
7. canonical skill을 선택된 Claude, Codex, Gemini 위치에 byte-identical하게 투영한다.
8. canonical은 checker의 별도 hash에 포함된다. `self_evaluation.watched_paths`에는 선택 provider별 정확한 skill projection 경로만 추가한다. provider skill root 전체나 unrelated user skill은 감시하지 않는다.
9. root managed block과 팀 문서를 갱신하고 `pending_events`에 `skill-change`와 필요한 `adapter-change`를 중복 없이 추가한다.
10. `verify-harness`와 연결 evaluator를 실행한다. 새 parity fail은 pending event로 추가한다.

## 원자성

spec, canonical skill, 모든 선택 runtime 투영, watched path, 호출 문서, 결정 기록을 한 단위로 변경한다. runtime별 의미 분기, adapter 단독 수정, 증거 없는 pass를 허용하지 않는다.
