# EXECUTION LOOP — 실행 루프

작업 단위는 개정 안건 1건이다. task evaluation은 항상 수행하고 harness effect evaluation은 checker가 요청할 때만 수행한다.

## 루프

```text
1. PICK       state/state.json에서 다음 단위를 선택한다.
2. GUARD      예산과 인간 승인 게이트를 확인한다.
3. DEFINE     이 단위의 scope=task evaluator와 pass 조건을 확정한다.
4. EXECUTE    작업을 수행한다.
5. TASK-EVAL  loops/EVAL-LOOP.md로 작업 결과를 판정한다.
6. RECORD     완료 unit마다 current_unit 갱신, units_since_full += 1,
              cooldown_remaining_units = max(0, n-1)을 정확히 한 번 적용하고
              pass/fail, 재시도, 비용, 시간을 상태와 journal에 기록한다.
7. INCIDENT   coldstart_fail false→true 또는 parity pass→fail을 pending event에 중복 없이 추가한다.
8. CHECK      read-only checker를 실행한다. LLM을 호출하지 않는다.
9. ROUTE      reasons에 input-invalid:*가 있으면 effect evaluation·LLM·improvement를 금지한다.
              verify-harness로 구조만 복구하고 checker를 다시 실행한다.
              adapter-change|parity-fail은 provider parity pass 전 평가를 금지한다.
              none은 추가 로드 없이 종료한다.
              targeted/full은 checker stdout을 run의 trigger.json에 그대로 동결한 뒤 평가한다.
10. ACK       완료된 targeted/full run만 recorder에 frozen decision file과 verdict를 전달한다.
11. COMMIT    task pass와 필요한 구조 검증을 확인한 뒤 프로젝트 저장소에 커밋한다.
```

## 결정적 경계

- checker는 파일을 수정하지 않고 compact JSON만 반환한다.
- `targeted.json`은 `cost-regression|retry-pressure|deterministic-sample`을 고정 metric에 연결한다.
- budget·cooldown은 비필수 신호만 유예하며 mandatory full을 묵살하지 않는다.
- recorder는 완료 run 뒤에만 호출한다. full ACK가 처리한 pending event와 frozen failure snapshot만 ACK하고 managed hash를 갱신한다.
- task evaluator는 self-evaluation decision과 관계없이 작업마다 실행한다.

## 불변조건

- evaluator 없는 작업 실행, 증거 없는 pass, gate 우회는 금지한다.
- checker의 `none`이나 `input-invalid:*`를 개선 필요로 해석하지 않는다.
- targeted 결과만으로 하네스를 수정하지 않는다.
- 한 번에 쓰기 주체는 하나다. 결과는 대상 프로젝트에 남는다.
