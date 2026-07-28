# 원칙 6 — 증거 기반 점진 개선

## 선언

팩토리는 프로젝트가 소유하는 틀을 만들고 수정합니다. 생성 하네스는 대상 프로젝트 안의 evidence로 성장하며 factory가 여러 프로젝트의 state를 중앙에 흡수하지 않습니다.

자기검증에서 항상 실행해도 되는 것은 결정적 checker뿐입니다. effect evaluator와 개선 에이전트는 유효한 신호와 검증된 입력에서만 로드합니다.

## 규칙

1. **작업과 하네스를 분리한다** — task evaluator는 산출물 완료, harness experiment는 하네스 효과를 판정한다.
2. **모든 skill에 evaluator를 연결한다** — schema 1.1 entry/evaluation/verification/domain은 task, harness-evaluation/improvement는 harness experiment를 참조한다.
3. **checker는 읽기 전용이다** — `none|targeted|full`만 반환하고 LLM 호출·state write·improve 지시를 하지 않는다.
4. **손상 입력은 평가하지 않는다** — `input-invalid:*`는 verify/structural recovery 후 recheck한다. effect evaluation과 LLM을 열지 않는다.
5. **adapter 문제는 verify-first다** — `adapter-change|parity-fail`은 parity pass 전 effect evaluation을 금지한다.
6. **targeted 범위를 고정한다** — `cost-regression|retry-pressure|deterministic-sample`은 `evaluation/suites/targeted.json`의 결정적 metric으로만 평가한다.
7. **managed artifact만 감시한다** — canonical과 선택 provider의 exact root guidance, spec skill projection, namespaced wrapper, 생성 config를 hash한다. unrelated user 파일은 제외한다.
8. **incident 전환을 기록한다** — cold-start false→true와 parity pass→fail은 pending event를 추가한다.
9. **완료 평가는 ACK한다** — targeted/full 뒤 recorder를 호출해 같은 mandatory 신호 반복을 막는다.
10. **평가는 같은 조건의 실험이다** — full은 동일 evaluator로 baseline/control/treatment를 비교한다.
11. **개선은 귀속 evidence 뒤에만 한다** — full regression 또는 하네스 원인 확인 뒤 1~2개를 바꾼다.
12. **수용 기준을 고정한다** — improved 또는 사전 허용 neutral만 수용하고 evaluator 완화·gate 우회·evidence 삭제를 금지한다.

## Trigger 라우팅

```text
checker
├─ input-invalid:* ─────→ verify + structural recovery → recheck
├─ adapter/parity ──────→ parity verify → recheck/pass
├─ none ────────────────→ stop
├─ targeted ────────────→ fixed deterministic suite → recorder ACK
└─ full ────────────────→ harness experiment → recorder ACK
                                      └─ attributed regression → improve
```

mandatory는 canonical/agent/skill/evaluator/adapter change, cold-start/parity incident, 반복 failure입니다. `minimum_samples`는 success/cost 비교에만 적용하고, `targeted_sample_rate`는 독립적인 결정적 sample 신호를 만듭니다. budget·cooldown만 모든 비필수 cost/retry/sample/interval 신호를 유예합니다.

## ACK 상태 전이

완료 run마다 실행합니다.

```text
python harness/triggers/record_self_evaluation.py harness --decision <targeted|full> --decision-file harness/evaluation/runs/<run-id>/trigger.json --verdict <improved|neutral|regressed|inconclusive>
```

평가 전에 checker JSON을 `harness/evaluation/runs/<run-id>/trigger.json`에 동결합니다. recorder는 frozen decision/reasons, current managed hashes, `acknowledgement` failure snapshot을 검증합니다. ACK decision/reasons는 frozen file을 사용하며 변화한 rolling-metric decision으로 대체하지 않습니다.

- full은 처리 시작 pending snapshot과 frozen failure snapshot만 ACK하고 managed hashes, units, cooldown, last verdict를 갱신합니다.
- targeted는 last decision/verdict와 cooldown만 갱신하며 mandatory event를 소비하지 않습니다.
- 평가 중 생긴 새 event·failure는 보존합니다.
- 미완료·stale run은 ACK하지 않습니다.

이 때문에 처리한 mandatory signal은 반복되지 않고 ACK 뒤 새 incident는 transition event로 다시 검출됩니다.

## 표준 개선 절차

1. 완료·ACK된 full report와 하네스 귀속 확인
2. 변경 1~2개와 rollback 조건 선택
3. spec·canonical component 선변경
4. 선택 provider exact managed artifact 전체 재투영
5. structural/task evaluator와 cold-start 실행
6. parity pass 뒤 동일 full experiment 실행
7. recorder ACK
8. 수용 또는 rollback 후 DECISIONS와 journal에 append

사용자 비용 민감도에 따라 sampling, interval, cooldown, budget을 조정하되 mandatory 사건은 숨기지 않습니다. 기존 하네스는 factory로 가져오지 않고 그 프로젝트 안에서 원자적으로 개선합니다.
