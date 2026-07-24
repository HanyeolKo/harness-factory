# EVALUATION CONTRACT — 예제

작업 evaluator는 작업 품질을 판정하고 harness effect evaluator는 그 결과를 baseline/control/treatment 사이에서 비교한다. 실제 정책 정본은 이 예제에서 생략한 schema 1.1 `harness-spec.json.self_evaluation`이다.

## 저장 구조

```text
evaluation/
├── EVALUATION-CONTRACT.md
├── suites/targeted.json
├── baselines/
├── runs/
│   └── EXAMPLE-001/trigger.json
└── reports/
```

`targeted.json`은 `cost-regression`, `retry-pressure`, `deterministic-sample`의 고정 metric 목록만 정의한다. `trigger.json`은 checker의 decision, reasons, hash, incident acknowledgement를 평가 전에 동결한 ACK 입력이다.

## provider hash 입력

실제 spec의 `watched_paths`는 선택 provider마다 다음 artifact의 정확한 집합이다.

- `root_guidance`
- 각 `<skill_root>/<skill-id>/SKILL.md`
- 각 `<agent_root>/<namespace>-<role-id><agent_extension>`
- 선택 `config`

skill/agent root 디렉터리 전체나 canonical harness 내부 경로를 넣지 않는다. checker는 이 목록으로 단일 `current_adapter_hash`를 만들고 full ACK가 `state/self-evaluation.json.hashes.adapters`에 저장한다.

## 라우팅·상태 전이

- `input-invalid:*`는 effect evaluation 입력이 아니다. 구조 검증·복구 후 checker를 다시 실행한다.
- `adapter-change|parity-fail`은 provider parity pass 뒤에만 평가한다.
- targeted/full checker stdout을 run의 `trigger.json`으로 동결하고 report와 recorder가 같은 파일을 참조한다.
- 완료된 targeted/full만 recorder로 ACK한다.
- full ACK는 처리한 pending event와 canonical/provider hash, `acknowledged.coldstart_fail`, `acknowledged.fail_counts`, full interval, cooldown을 갱신한다.
- targeted ACK는 `last_decision`과 cooldown만 갱신하고 mandatory event를 소비하지 않는다.
- `last_decision`은 decision, frozen reasons, `improved|neutral|regressed|inconclusive` verdict를 보존한다.

## 불변조건

- 비교 arm의 commit, fixture, 모델/version, 권한, 도구, 예산을 같게 유지한다.
- 원본 출력과 환경 hash를 verdict보다 먼저 저장한다.
- 운영 비용과 평가 비용을 분리하고 treatment의 하네스 주입 비용을 숨기지 않는다.
- 평가·recorder는 공통 spec이나 adapter 의미를 수정하지 않는다.
- stale frozen hash, 부분 실행, 판정 불가는 ACK하거나 개선으로 처리하지 않는다.
- 결과와 상태는 대상 프로젝트 안에 남으며 팩토리로 자동 전송하지 않는다.
