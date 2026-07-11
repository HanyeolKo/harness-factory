# JOURNAL FORMAT — journal.jsonl 라인 스키마

`ledger/journal.jsonl`은 append-only다. 수정·삭제 금지. 잘못된 기록은 정정 라인을 추가한다.

## 라인 스키마

```json
{"ts":"<ISO8601>", "event":"<유형>", "unit":"<U-00N|null>", "detail":"<한 줄>", "verdict":"<pass|fail|null>", "evidence":"<판정 근거>", "cost":"<선택>"}
```

`fail` 이벤트 추가 필드: `"key":"<분류:하위유형>"`, `"grade":"<R|S>"`. 승격 라인은 `"escalated":true`를 붙이고 **카운터에 재계상하지 않는다** (계상은 사건당 최초 1회).

## 기록 대상 이벤트 (수준: 단위 시작/종료 + 판정 + 실패 + 결정)

| event | 시점 | 필수 필드 |
|---|---|---|
| `session_start` / `session_end` | 세션 경계 | ts, detail |
| `unit_start` / `unit_done` | 작업 단위 경계 | ts, unit |
| `eval` | 모든 평가 판정 | ts, unit, verdict, evidence |
| `fail` | 실패 발생 (등급 승격 포함) | ts, unit, key, grade, evidence |
| `recovery` / `recovery_exhausted` | 회복 시도·포기 | ts, unit, detail |
| `feedback` | 등급 S 중지에 대한 사용자 피드백 수신 | ts, unit, detail(요지·재개 방향) |
| `checkpoint` | 체크포인트 | ts, detail |
| `decision` | DECISIONS.md 추가 시 포인터 | ts, detail(D-번호) |
| `retro` | 보완 루프 회고 수행 | ts, detail(안건 요약) |

## 규칙

- 기록되지 않은 평가는 수행되지 않은 것이다 (원칙 1).
- 집계·추출은 스크립트로 한다 (원칙 3). 예: `grep '"event":"fail"' ledger/journal.jsonl | tail -20`
- journal.jsonl을 통째로 컨텍스트에 읽어들이지 않는다. 필요한 구간만 추출한다 (원칙 2).
