---
name: verify-harness
description: 생성된 하네스의 schema·참조·DAG·권한·공통 정본·Claude/Codex/Gemini adapter parity·콜드스타트 계약을 검증한다. 사용자가 하네스 검증, 구조 확인, adapter 동기화 확인을 요청하거나 agent·skill·evaluator·runtime 구성이 변경된 직후 사용한다.
---

# verify-harness

구조적 정합성을 검사한다. 하네스가 실제 성과를 높였는지는 `evaluate-harness`가 담당한다.

## 절차

1. `scripts/resolve_factory.py`로 `FACTORY_ROOT`를 확정한다.
2. 대상 경로를 정하고 `python <FACTORY_ROOT>/scripts/validate_runtime_neutral.py <target>`를 실행한다.
3. spec과 공통 agent/skill/evaluator 참조, 정상 handoff DAG, approval gate, state와 journal을 검사한다.
4. 선택 runtime의 managed block, agent 권한, skill byte parity를 검사한다.
5. `harness/HARNESS.md`부터 지정 순서만 읽어 목적·현재 단계·다음 행동·완료 evaluator를 복원한다.
6. 하네스가 변경된 경우 trigger checker와 변경을 촉발한 원 evaluator를 추가 실행한다.
7. pass/fail, 원본 명령, 미실행 검증, 잔여 위험을 보고한다.

검증 요청만 받은 경우 파일을 수정하지 않는다. 수정을 함께 요청받았다면 공통 spec부터 고치고 모든 선택 adapter를 재생성한 뒤 최대 3회 재검증한다.
