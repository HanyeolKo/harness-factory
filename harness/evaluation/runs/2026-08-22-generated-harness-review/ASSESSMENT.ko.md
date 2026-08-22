# 생성 하네스 평가 보고서

## 결론

현재 하네스는 구조적으로는 유효하지만, 운영 contract는 충분하지 않다. deterministic 검사 여섯 개는 모두 통과했지만, 전체 효과 verdict는 비교 가능한 baseline과 실행 가능한 `harness-effect` runner가 없어서 `inconclusive`이다. 그와 별개로 evaluation evidence chain에는 하네스에 직접 귀속할 수 있는 결함이 있다.

11개 차원을 0~4점으로 평가한 결과는 20/44점이며, 평균은 1.8/4점이다. 가장 강한 부분은 Learning Assist와 Learning Gate의 분리, approval gate, cold-start 순서이다. 가장 약한 부분은 evaluator 재현성, evidence 보존 책임, role별 contract 구체성이다.

## 핵심 발견

1. `evidence-runner`는 evaluator command 실행과 raw evidence 보존을 책임지지만 `read-only`이다. Claude와 Gemini adapter에는 shell 실행 도구도 없다.
2. `harness-effect.command`는 실행 명령이 아닌 prose이며, task corpus·fixture·metric 계산·telemetry writer가 없다.
3. main state의 failure 값은 top-level에 있지만 checker는 `main_state.improve`를 읽기 때문에 repeated failure와 cold-start 신호가 누락될 수 있다.
4. 여섯 role의 input/output/rules 본문이 동일하다. 역할 이름은 분리되어 있지만 verdict schema, evidence manifest, stable failure key, route decision이 구체적으로 정해져 있지 않다.
5. 정상 변경은 `router -> builder -> runner -> evaluator`의 세 handoff를 직렬로 거치며, read-only 작업이나 작은 변경을 위한 fast path가 없다.

## 실측 결과

- `validate_runtime_neutral.py`: pass
- `test_runtime_neutral_contract.py`: pass, Windows symlink 권한 관련 skip 1건
- `test_self_evaluation_trigger.py`: pass, Windows symlink 권한 관련 skip 1건
- `test_learning_gate_contract.py`: pass
- `skill_smoke_build_harness.py`: pass
- checker decision: `full`, mandatory
- generated Codex role profile 직접 실행: `runtime-selected`와 현재 ChatGPT account runtime의 비호환으로 시작 전 실패했다. 이 항목은 하네스 결함이 아니라 환경 호환성 제약으로 분리했다.

## 우선 개선 방향

첫 후보는 `evidence-runner`가 세 provider에서 evaluator command를 실행하고, 정해진 evidence 경로에 raw output과 manifest를 보존할 수 있게 만드는 것이다. 이 변경은 runner agent contract와 evidence handoff contract라는 두 component로 제한한다. telemetry runner, failure state schema, 작은 작업 fast path는 후속 hypothesis로 남긴다.

## 판정 한계

초기 하네스 이전의 task corpus와 telemetry가 남아 있지 않으므로 baseline arm을 재구성할 수 없다. 따라서 이 run은 전체 효과를 `improved` 또는 `regressed`라고 주장하지 않는다. 다만 provider tool matrix와 role access를 직접 대조해 확인한 evidence chain 결함은 개선 entry를 열기에 충분한 harness-attributed defect이다.
