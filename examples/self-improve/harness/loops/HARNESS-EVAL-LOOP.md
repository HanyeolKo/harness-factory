# HARNESS EVALUATION LOOP — 하네스 효과 평가

작업 evaluator와 분리해 하네스 적용 자체가 baseline보다 나아졌는지 판정한다. 자동 경로는 checker가 `targeted|full`을 반환했을 때만 연다.

## 진입과 불변 입력

1. checker 결과의 `reasons`를 decision보다 먼저 검사한다.
2. `input-invalid:*`가 있으면 effect evaluation과 LLM judge를 금지한다. `verify-harness`로 구조를 복구하고 checker를 다시 실행한다.
3. `adapter-change|parity-fail`은 artifact 단위 provider parity가 pass한 뒤에만 평가한다.
4. 평가할 targeted/full checker stdout을 `evaluation/runs/<run-id>/trigger.json`에 변경 없이 보존한다.
5. 평가·ACK는 같은 frozen `trigger.json`을 입력으로 사용한다. 평가 중 checker를 다시 실행한 결과로 decision/reasons를 바꾸지 않는다.

`examples/self-improve/harness/evaluation/runs/EXAMPLE-001/trigger.json`은 이 불변 입력의 형식만 보여준다. digest는 설명용이다.

## 평가 범위

- `targeted`: `evaluation/suites/targeted.json`에서 frozen reason과 정확히 연결된 결정적 metric만 실행한다. 임의 LLM 평가를 추가하지 않는다.
- `full`: 같은 commit, fixture, 모델/version, 권한, 도구, 예산으로 아래 arm 전체를 실행한다.

| arm | 조건 | 목적 |
|---|---|---|
| baseline | 하네스 없음 | 원래 runtime 성능 |
| control | 일반적인 최소 지시만 사용 | 단순 prompt 효과 분리 |
| treatment | 현재 프로젝트 하네스 적용 | 하네스 고유 효과 측정 |

연결 evaluator는 `scope: harness`, `type: experiment`다.

## 절차

```text
1. FREEZE   suite, fixture, evaluator, 환경 hash와 checker trigger.json을 고정한다.
2. RUN      targeted metric 또는 full arm의 원본 결과와 비용을 run 디렉터리에 보존한다.
3. SCORE    결정적 지표를 우선 계산하고 full의 비결정적 항목만 blind rubric으로 판정한다.
4. COMPARE  full이면 품질·성공률·비용·시간·재시도·인간 개입을 비교한다.
5. VERDICT  improved|neutral|regressed|inconclusive 중 하나를 판정한다.
6. RECORD   report와 journal에 frozen trigger, suite, verdict, evidence 경로를 기록한다.
7. ACK      완료된 targeted/full마다 recorder를 호출한다.
```

완전한 생성물의 ACK command:

```text
python harness/triggers/record_self_evaluation.py harness --decision <targeted|full> --decision-file harness/evaluation/runs/<run-id>/trigger.json --verdict <improved|neutral|regressed|inconclusive>
```

recorder는 frozen decision/reasons/incident acknowledgement와 현재 canonical/provider hash를 확인한 뒤 상태를 원자 갱신한다.

- full ACK: 처리한 pending event와 frozen incident acknowledgement만 ACK하고 `hashes.canonical`, `hashes.adapters`, full interval, cooldown을 갱신한다. 평가 중 추가된 새 event·failure는 보존한다.
- targeted ACK: `last_decision`과 cooldown만 갱신하며 mandatory event나 hash snapshot을 소비하지 않는다.
- 미완료·중단 run과 `none`: recorder를 호출하지 않는다.
- stale hash·decision mismatch: ACK를 실패시키고 새 checker 결과로 새 run을 시작한다.

full report가 `regressed`이거나 하네스 결함을 귀속한 경우에만 improvement owner에게 전달한다. 표본 부족, arm 조건 불일치, evaluator 미실행은 `inconclusive`다.
