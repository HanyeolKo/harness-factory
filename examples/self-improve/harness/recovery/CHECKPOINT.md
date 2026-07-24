# CHECKPOINT — 체크포인트 규격과 재개 절차

재개는 기억이 아니라 파일에서 시작한다.

## 체크포인트 시점

- 작업 단위 pass 직후
- 게이트 단계 직전
- 예산 80% 도달 시
- 세션 종료 또는 에스컬레이션 직전

## 절차

```text
1. state/state.json의 작업 상태를 갱신한다.
2. state/self-evaluation.json의 rolling metric과 pending event를 갱신한다.
3. journal.jsonl에 checkpoint를 기록한다.
4. task evaluator와 필요한 구조 검증이 pass한 단위만 커밋한다.
```

## 상태 분리

`state.json`은 작업 큐·다음 행동·실패 신호를 보존한다.

```json
{
  "schema_version": "1.1",
  "updated": "<ISO8601>",
  "phase": "<현재 단계>",
  "queue": [{"id":"U-001", "evaluator":"<task evaluator>", "status":"todo|in-progress|done|blocked"}],
  "current": {"id":"U-001", "step":"<EXECUTION-LOOP 단계>", "refs":[]},
  "next_action": "<즉시 수행할 행동>",
  "improve": {"fail_counts":{}, "coldstart_fail":false, "last_candidate":null, "last_effect_verdict":null},
  "budget": {"units_done":0, "note":"<운영·평가 비용 요약>"}
}
```

`self-evaluation.json`은 baseline·recent·rolling metric, canonical/provider hash, pending event, acknowledged incident snapshot, cooldown, 마지막 decision·reasons·verdict를 보존한다. LLM의 회고 메모를 checker 입력으로 쓰지 않는다.

## 재개 절차

```text
1. HARNESS.md 세션 시작 프로토콜을 수행한다.
2. state.json.next_action을 확인한다.
3. EXECUTE 이후 중단됐다면 산출물 존재를 확인하고 TASK-EVAL부터 재개한다.
4. self-evaluation pending event는 삭제하지 말고 다음 태스크 경계 checker가 처리하게 한다.
5. 재개 사실을 journal.jsonl에 기록한다.
```
