# Learning Assist: evidence runner contract 개선 전 보고서

> 상태: 이 보고서를 작성한 시점에는 개선 후보를 아직 source와 adapter에 적용하지 않았다.

## 무엇이 문제인가

현재 `evidence-runner`는 evaluator command를 실행하고 raw output을 보존해야 한다. 그러나 canonical spec은 이 role을 `read-only`로 선언한다. Claude adapter는 `Bash`를 금지하고 Gemini adapter는 `run_shell_command`를 제공하지 않기 때문에, 두 provider에서는 command 자체를 실행할 수 없다. Codex도 read-only sandbox에서 command는 실행할 수 있지만 evidence 파일을 보존할 책임과 권한은 명확하지 않다.

이 모순 때문에 구조 validator는 통과해도 실제 evaluation handoff는 완료할 수 없다. `factory-contract-tests`의 pass condition은 raw output 보존을 요구하므로, command 실행이나 evidence 보존 중 하나라도 빠지면 verdict는 `blocked`여야 한다.

## 현재 흐름

`factory-builder -> evidence-runner -> contract-evaluator`

1. `factory-builder`가 구현 완료를 알린다.
2. `evidence-runner`가 evaluator command를 실행해야 한다.
3. `evidence-runner`가 stdout, stderr, exit code를 보존해야 한다.
4. `contract-evaluator`가 보존된 evidence를 pass condition과 비교해야 한다.

현재는 2단계와 3단계의 provider capability가 contract와 일치하지 않는다. handoff 경로만 있고 evidence manifest의 필수 field와 허용 write path도 정해져 있지 않다.

## 적용할 단일 가설

세 provider에서 `evidence-runner`가 evaluator command를 실행하고 정해진 evidence 경로에만 결과를 보존하게 만들면, 구조·parity·cold-start를 악화시키지 않으면서 evidence-complete handoff 수가 증가한다.

이 후보는 두 component만 변경한다.

1. `evidence-runner` agent contract와 access projection을 변경한다.
2. 공통 evidence manifest와 저장 경로 contract를 추가한다.

`harness-effect` runner, telemetry writer, failure state schema, 작은 작업 fast path는 이번 후보에 포함하지 않는다. 서로 다른 원인을 한 번에 바꾸면 어떤 변화가 효과를 만들었는지 판정할 수 없기 때문이다.

## 변경 후 의도한 흐름

`work unit -> evaluator command -> raw stdout/stderr -> manifest -> contract verdict`

`evidence-runner`는 source를 수정하지 않는다. main orchestrator는 `harness/evaluation/task-evidence/<unit-id>/`와 `harness/evaluation/runs/<run-id>/`에만 evidence를 기록한다. manifest에는 `unit_id`, `evaluator`, `command`, `request_hash`, `approval_gate_status`, `stdout_path`, `stderr_path`, `exit_code`, `artifact_hash`, `checks_not_run`, `status`, `next_role`을 남긴다. `contract-evaluator`는 request binding, manifest, raw file이 모두 검증된 경우에만 verdict를 판정한다.

## 검증 조건

- Claude, Codex, Gemini에서 `evidence-runner`는 read-only를 유지하고 main orchestrator가 exact request를 실행·보존해야 한다.
- provider adapter와 canonical spec의 access 의미가 일치해야 한다.
- `validate_runtime_neutral.py`와 기존 contract suite가 모두 통과해야 한다.
- agent 수, handoff 수, delegation depth는 증가하지 않아야 한다.
- source path에 대한 out-of-scope write는 없어야 한다.
- 현재 control의 구조 검사 성공률과 cold-start 결과가 회귀하지 않아야 한다.

## 알아둘 위험

현재 schema의 access 값은 `read-only|workspace-write`만 지원한다. command 실행과 evidence path 제한 write를 별도 권한으로 표현할 수 없으므로, provider tool 수준에서는 `workspace-write`를 부여하고 canonical role contract에서 write path를 좁혀야 한다. 이는 완전한 sandbox 강제가 아니라 instruction-level 제한이다. 이 잔여 위험은 최종 보고서에 그대로 남긴다.

## Provider 변경 전 안전성 수정

최초 projection 후보는 `evidence-runner`를 `workspace-write`로 변경하려 했다. 그러나 provider sandbox가 evidence path만 쓰도록 강제할 수 없어서, 이 변경은 workspace 전체 쓰기 권한을 넓히는 결과가 된다. 안전 검토에서 이 제안을 거부했고 provider wrapper는 변경하지 않았다.

유지한 후보는 `evidence-runner`를 `read-only`로 둔다. 이 role은 exact execution request를 반환하고, 기존 main orchestrator가 command를 실행해 evidence만 보존하며, 같은 `evidence-runner`가 manifest를 검증한 뒤 `contract-evaluator`로 넘긴다. 따라서 `workspace-write` agent 수는 증가하지 않는다.

잔여 위험은 orchestration discipline으로 이동한다. main orchestrator가 evidence root 제한을 지켜야 하며, evidence 실행 단계에서 source 수정까지 함께 수행해서는 안 된다.

## 관련 evidence

- `harness/evaluation/runs/2026-08-22-generated-harness-review/report.json`
- `harness/evaluation/runs/2026-08-22-generated-harness-review/structural-checks.txt`
- `harness/evaluation/runs/2026-08-22-generated-harness-review/runtime-role-probes.json`
