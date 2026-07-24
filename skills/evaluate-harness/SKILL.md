---
name: evaluate-harness
description: 생성된 하네스가 baseline보다 품질·성공률·비용·시간·안정성을 실제로 개선하는지 조건부로 측정한다. 사용자가 하네스 성과 검증·전후 비교·benchmark를 요청하거나 결정적 trigger checker가 targeted/full 평가를 반환했을 때 사용한다.
---

# evaluate-harness

자동 경로에서는 checker를 먼저 실행한다. `none`이면 상세 평가 문서나 LLM judge를 로드하지 않는다. 사용자의 명시적 전체 평가 요청은 override로 기록하되 구조 검증을 우회하지 않는다.

## 절차

1. `scripts/resolve_factory.py`로 `FACTORY_ROOT`를 확정하고 대상 spec·self-evaluation state를 읽는다.
2. schema 1.1 harness-evaluation skill의 `evaluator`가 `self_evaluation.evaluator`와 같고 그 evaluator가 `scope: harness`, `type: experiment`인지 확인한다.
3. checker JSON을 평가 전 `harness/evaluation/runs/<run-id>/trigger.json`에 동결한다. `reasons`에 `input-invalid:*`가 있으면 즉시 중지하고 `verify-harness`와 구조 복구로 보낸다. effect evaluation이나 LLM을 열지 않으며 복구 뒤 checker를 다시 실행한다.
   - 자동 경로의 `none`은 그대로 종료한다.
   - 사용자가 명시적으로 full 평가를 요청했다면 raw checker JSON 전체를 `override.original`에 보존한다. top-level은 evaluator와 recorder가 공유하는 effective `decision: full`, `mandatory: false`이며, `override.kind: explicit-user-request`, `reasons: [*original.reasons, explicit-user-request]`, original과 동일한 deferred reasons·managed hashes·`acknowledgement`를 기록한다. 이 구조화된 override만 budget·cooldown을 우회하며 input-invalid와 parity 검증은 우회하지 않는다.
4. `adapter-change|parity-fail`이면 선택 provider parity를 먼저 검증한다. 실패가 새로 생기면 pending events에 `parity-fail`을 중복 없이 추가하고 중지한다.
5. 자동 `none`이면 종료한다. 명시적 full override 또는 checker의 `targeted|full`만 계속한다. `targeted`이면 `self_evaluation.targeted_suite`가 가리키는 `evaluation/suites/targeted.json`에서 reason과 정확히 연결된 결정적 metric만 실행한다. 허용 reason은 `cost-regression`, `retry-pressure`, `deterministic-sample`이며 임의 LLM targeted 평가는 금지한다.
6. `full`이면 같은 commit, fixture, 모델/version, 권한, 도구, 예산으로 baseline/control/treatment를 실행한다. 결정적 지표를 우선하고 필요한 비결정적 항목만 blind rubric으로 판정한다.
7. 원본 run을 `evaluation/runs/`, 보고서를 `reports/`에 기록하고 `improved|neutral|regressed|inconclusive` verdict를 낸다.
8. 완료된 targeted/full마다 다음 recorder를 반드시 호출한다.

```text
python <target>/harness/triggers/record_self_evaluation.py <target>/harness --decision <targeted|full> --decision-file <target>/harness/evaluation/runs/<run-id>/trigger.json --verdict <improved|neutral|regressed|inconclusive>
```

recorder는 frozen trigger의 decision/reasons, managed hashes, `acknowledgement` failure snapshot을 확인한다. ACK decision/reasons는 평가 중 변한 rolling-metric decision으로 대체하지 않는다. full은 처리한 pending events와 frozen failure snapshot만 ACK하고 managed canonical/provider hashes, units, cooldown을 갱신한다. 평가 중 생긴 새 event·failure는 다음 boundary에 남는다. targeted는 last decision과 cooldown만 갱신한다. 미완료 run은 ACK하지 않는다.

9. full report가 `regressed`이거나 하네스 결함을 귀속했을 때만 `improve-harness` 후보로 전달한다.

평가 자체와 recorder는 하네스 의미를 수정하지 않는다. 조건 불일치나 표본 부족은 개선이 아니라 `inconclusive`다.
