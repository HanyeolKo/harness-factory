# 생성 하네스 평가와 evidence-runner 개선

## 범위

Harness Factory 자체가 아니라 `D:\workspace\Harness Factory`에 생성된 하네스 결과물만 평가했다. orchestration 강도, agent 규약, capability와 access, handoff, evaluator 재현성, failure recovery, context budget, memory routing, approval gate, Learning Assist, provider parity를 검토했다.

## 초기 평가

초기 full evaluation은 `20/44`(`1.8/4`)였다. 구조 검증은 통과했지만 operational contract는 실패했다. 핵심 원인은 read-only `evidence-runner`가 evaluator command 실행과 raw evidence 저장까지 맡도록 선언돼 Claude와 Gemini adapter에서 완료할 수 없다는 점이었다. 이 밖에 prose-only harness-effect command, failure-state schema mismatch, generic role contract, handoff schema 부재, small-task fast path 부재를 확인했다.

## Learning Assist

변경 전에 `harness/reports/2026-08-22-evidence-runner-contract/LEARNING-ASSIST.md`와 한국어 reader copy를 작성했다. Learning Gate는 `enabled:false`라 quiz나 blocking gate는 생성하지 않았다.

## 반영한 개선

- `evidence-runner`: exact execution request 작성과 read-only validation
- main orchestrator: exact command 실행과 허용된 evidence root 내 raw evidence 저장
- `contract-evaluator`: verdict 소유
- `manifest.json`: 12개 required field와 deterministic request/artifact hash
- `validation-result.json`: manifest를 수정하지 않고 `contract-evaluator`로 handoff
- Claude, Codex, Gemini: description parity만 동기화하고 permission은 유지

workspace-write agent는 `2`, 전체 agent는 `6`, handoff는 `4`로 유지했다.

## 실측 결과

최종 full comparison은 `improved`다. provider-neutral executable evidence path는 `0/3`에서 `3/3`, required manifest field는 `0/12`에서 `12/12`로 개선됐다. 정상 종료와 approval-blocked 경로의 request hash와 artifact hash가 모두 일치했다.

검증 결과:

- runtime-neutral validator: pass
- runtime-neutral contract: 32 tests pass, Windows symlink fixture 1건 skip
- self-evaluation trigger: 29 tests pass, Windows symlink fixture 1건 skip
- Learning Assist/Gate contract: pass
- build-harness smoke: 32 tests pass, Windows symlink fixture 1건 skip
- provider parity와 permission/topology non-regression: pass
- post-ACK boundary checker: `decision:none`

초기 병렬 실행에서 `.test-work` cleanup race가 1건 발생했고, read-only sandbox에서 fixture 생성 거부가 1건 발생했다. 둘 다 changed attempt로 재실행해 통과했으며 candidate 결함으로 계산하지 않았다.

## 잔여 한계

Native Claude/Gemini end-to-end probe와 token·시간·비용 raw telemetry는 실행하지 않았다. 따라서 `improved` 판정은 evidence contract의 실행 가능성과 무결성 범위에 한정한다. evidence root 제한은 dedicated path sandbox가 아니라 main orchestrator 규약으로 강제된다.
