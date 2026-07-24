---
name: build-evaluator
description: 생성된 하네스에 원본 증거·runner·verdict owner·명시적 pass 조건을 갖춘 evaluator를 추가하거나 수정한다. 사용자가 테스트·빌드·린트·검증 스크립트·루브릭을 완료 기준으로 연결하거나 하네스 적용 전후 성과 평가 suite를 정의할 때 사용한다.
---

# build-evaluator

작업 완료 evaluator와 하네스 효과 evaluator를 분리한다. 인간 승인은 evaluator가 아니라 approval gate다.

## 유형

- **task** — unit 또는 entry/evaluation/verification/domain skill의 산출물을 판정한다. verification에는 구조 validator를 연결한다.
- **harness** — baseline/control/treatment를 비교한다. 반드시 `type: experiment`이며 harness-evaluation/improvement skill과 `self_evaluation.evaluator`가 이 ID를 참조한다.

## 절차

1. `scripts/resolve_factory.py`로 `FACTORY_ROOT`를 확정하고 평가 원칙, 대상 spec, 기존 명령을 읽는다.
2. 대상, 원본 evidence, runner, verdict owner, command, pass condition을 확정한다. 결정적 수단이 없을 때만 rubric을 사용한다.
3. task evaluator를 관련 queue unit과 모든 해당 `skills[].evaluator`에 연결한다.
4. harness evaluator는 `scope: harness`, `type: experiment`로 만들고 self-evaluation 및 harness-evaluation/improvement skill에 같은 ID를 연결한다.
5. targeted 경로를 변경하면 `self_evaluation.targeted_suite`가 가리키는 `evaluation/suites/targeted.json`의 `cost-regression|retry-pressure|deterministic-sample` reason별 결정적 metric만 갱신한다. 임의 LLM targeted suite는 만들지 않는다.
6. 실제 명령을 실행해 evidence 형식과 pass/fail 동작을 확인한다. 실행 불가는 `fail(structural:evaluator-unavailable)`이다.
7. spec/canonical 문서를 먼저 바꾼다.
8. provider adapter를 쓰기 전에 `python <FACTORY_ROOT>/scripts/validate_runtime_neutral.py <target> --provider-path-preflight`를 실행하고 exit 0을 확인한다. provider 경로가 절대 경로·lexical traversal·symlink escape로 target 밖을 가리키면 실패하며, 그때는 provider 디렉터리·파일을 생성·쓰기·이동하거나 우회 경로를 사용하지 않는다.
9. 선택 adapter를 투영하고 정확한 managed artifact만 `watched_paths`에 유지한다.
10. `pending_events`에 `evaluator-change`와 필요한 `adapter-change`를 추가하고 `verify-harness`를 실행한다. parity pass 전 effect evaluation은 금지한다.

결과를 통과시키기 위한 기준 완화, 실행자 자기 판정, arm 간 모델·권한·fixture 차이, 평가 비용 은폐를 금지한다.
