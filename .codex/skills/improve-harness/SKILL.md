---
name: improve-harness
description: 설치된 프로젝트 하네스의 자체 evaluation 결과를 바탕으로 agent·skill·evaluator를 점진 개선하고 회귀 검증 후 효과가 입증된 변경만 채택한다. 사용자가 근거 있는 하네스 개선을 요청하거나 full 평가가 regression·하네스 결함을 확인했을 때 사용한다.
---

# improve-harness

개선 이력은 대상 프로젝트 안에 유지한다. 팩토리가 설치된 하네스를 중앙으로 흡수하지 않는다.

## 진입 조건

- 완료·ACK된 full report가 `regressed` 또는 하네스 결함을 판정했거나,
- 사용자가 full 근거와 함께 개선을 명시해야 한다.

`input-invalid:*`, 미해결 parity, 단일 약한 신호, 정기 간격은 LLM 개선 진입 조건이 아니다. 구조 문제는 먼저 `verify-harness`와 결정적 recovery로 복구하고 checker를 다시 실행한다.

## 절차

1. full decision/report, 관련 journal 최소 구간, 직전 개선 효과를 읽는다. improvement skill의 `evaluator`가 `scope: harness`, `type: experiment`인지 확인한다.
2. 제품 코드와 하네스 원인을 분리한다. 하네스 원인이 없으면 작업 recovery로 돌려보낸다.
3. 한 가설과 1~2개 변경만 제안하고 예상 metric, 영향 파일, 원복 조건을 기록한다.
4. agent·skill·evaluator는 해당 build 스킬의 원자 변경 계약을 따른다. common spec을 먼저 바꾸고 선택 provider의 정확한 managed artifact 전체를 재투영한다.
5. provider parity가 pass하지 않으면 effect evaluation을 열지 않는다. 새 parity fail은 pending events에 추가하고 구조 복구한다.
6. `verify-harness`, cold-start, 연결 task structural evaluator, 변경을 촉발한 원 task evaluator를 실행한다.
7. checker JSON을 `harness/evaluation/runs/<run-id>/trigger.json`에 동결한 뒤 동일 full suite의 scope=harness,type=experiment evaluator를 재실행하고 불변 report를 저장한다.
8. 완료된 full run을 recorder로 ACK한다.

```text
python <target>/harness/triggers/record_self_evaluation.py <target>/harness --decision full --decision-file <target>/harness/evaluation/runs/<run-id>/trigger.json --verdict <improved|neutral|regressed|inconclusive>
```

9. improved 또는 사전 허용된 neutral만 채택한다. regressed/inconclusive는 원복하고 rejected proposal로 보존한다.
10. DECISIONS, append-only journal, evaluation state에 근거와 결과를 기록한다.

평가기준 완화, gate 우회, 실패 은폐, 한 provider만의 의미 변경은 개선이 아니다.
