# JOURNAL FORMAT — journal.jsonl 라인 스키마

`ledger/journal.jsonl`은 append-only다. 잘못된 기록은 정정 라인을 추가한다.

## 라인 스키마

```json
{"ts":"<ISO8601>", "event":"<유형>", "unit":"<U-00N|null>", "detail":"<한 줄>", "verdict":"<선택>", "evidence":"<원본 근거 경로>", "cost":"<선택>"}
```

`fail`은 `key`와 `grade`를 포함한다. 운영 비용과 harness evaluation 비용은 구분한다.

## 기록 대상 이벤트

| event | 시점 | 필수 필드 |
|---|---|---|
| `session_start` / `session_end` | 세션 경계 | ts, detail |
| `unit_start` / `unit_done` | 작업 단위 경계 | ts, unit |
| `task_eval` | 모든 작업 판정 | ts, unit, verdict, evidence |
| `self_eval_check` | 결정적 checker 실행 | ts, unit, detail(`none|targeted|full`), evidence(targeted/full frozen trigger 경로) |
| `harness_eval` | checker가 요청한 효과 평가 | ts, verdict, evidence, cost |
| `self_eval_ack` | 완료 run recorder 성공 | ts, verdict, evidence(frozen trigger와 갱신 state 경로) |
| `improvement_candidate` | full 회귀·결함에 따른 후보 | ts, detail, evidence |
| `improvement_verdict` | 재평가 후 채택 여부 | ts, verdict, evidence |
| `fail` | 실패 발생 | ts, unit, key, grade, evidence |
| `recovery` / `recovery_exhausted` | 회복 시도·포기 | ts, unit, detail |
| `feedback` | 사용자 피드백 | ts, unit, detail |
| `checkpoint` | 체크포인트 | ts, detail |
| `decision` | DECISIONS.md 포인터 | ts, detail |

## 규칙

- task 평가와 harness effect 평가를 같은 event로 합치지 않는다.
- checker의 `none`도 기록하되 LLM 평가 문서를 로드하지 않는다.
- 기록되지 않은 평가는 수행되지 않은 것이다.
- 집계·추출은 스크립트로 하며 journal 전체를 컨텍스트에 읽지 않는다.
