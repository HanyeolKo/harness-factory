# IMPROVE LOOP — 증거 기반 점진 개선

이 하네스는 대상 프로젝트가 소유한다. 팩토리는 상태를 흡수하지 않으며, 개선도 프로젝트 안에서 작은 변경으로 수행한다.

## 진입 조건

다음 조건을 모두 만족해야 한다.

1. `full` harness effect evaluation이 완료됐다.
2. verdict가 `regressed`이거나 원본 증거가 하네스 결함을 가리킨다.
3. task 실패, 환경 실패, 모델 변동만으로 설명되지 않는다.
4. 변경 전 baseline과 재평가 suite가 고정돼 있다.

정기 주기, targeted 결과, 단일 task fail만으로는 진입하지 않는다.

## 절차

```text
1. ATTRIBUTE  실패가 agent·skill·evaluator·adapter·orchestration 중 어디서 생겼는지 증거로 한정한다.
2. PROPOSE    서로 독립적인 변경 1~2개만 선택하고 예상 효과·회귀 위험을 기록한다.
3. AMEND      프로젝트의 canonical 계약을 먼저 수정하고 runtime adapter를 동기화한다.
4. VERIFY     schema·참조·DAG·권한·adapter parity·coldstart를 결정적으로 검증한다.
5. RE-RUN     같은 full suite와 조건으로 baseline/control/treatment를 다시 비교한다.
6. DECIDE     improved면 채택한다. 정책상 허용된 neutral만 명시적 근거와 함께 채택한다.
              regressed 또는 inconclusive면 변경을 채택하지 않고 증거를 보존한다.
7. RECORD     변경, verdict, 원본 evidence 경로, 다음 관찰 조건을 프로젝트 ledger에 기록한다.
```

## 불변조건

- evaluator와 pass 조건을 변경해 성능 향상처럼 보이게 하지 않는다.
- 여러 원인을 한 번에 바꾸지 않는다.
- improvement 수행 여부를 checker가 직접 결정하지 않는다.
- 프로젝트 밖 팩토리 저장소로 상태·로그·결과를 자동 환류하지 않는다.
