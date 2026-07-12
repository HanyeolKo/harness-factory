# CHECKPOINT — 체크포인트 규격과 재개 절차

재개는 기억이 아니라 파일에서 시작한다 (원칙 4·5).

## 체크포인트를 찍는 시점

- 작업 단위 pass 직후 (매 회전) / 게이트 단계 직전 / 예산 80% 도달 시 / 세션 종료 / 에스컬레이션 직전

## 체크포인트 절차

```
1. state/state.json 갱신 (아래 스키마 전 필드)
2. journal.jsonl에 {"event":"checkpoint", ...} 기록
3. 커밋: 작업 단위 pass마다 1커밋, 메시지 `improve(<대상 파일>): <개정 요지>`
```

## state.json 스키마

```json
{
  "updated": "<ISO8601>",
  "phase": "<현재 단계 요약 한 줄>",
  "queue": [ {"id": "U-001", "desc": "...", "evaluator": "...", "status": "todo|in-progress|done|blocked"} ],
  "current": { "id": "U-00N", "step": "<EXECUTION-LOOP의 단계 번호>", "refs": ["<참조 중인 파일 경로>"] },
  "next_action": "<새 세션이 즉시 수행할 다음 행동 한 줄>",
  "improve": { "fail_counts": {"<분류:하위유형>": 0}, "units_since_retro": 0, "coldstart_fail": false, "last_retro_targets": [] },
  "budget": { "units_done": 0, "note": "<소진 요약>" }
}
```

`next_action`은 비워둘 수 없다 (불변 조건). `fail_counts` 키는 `분류:하위유형` 규격, 새 키 생성 전 기존 키 재사용 우선.

## 재개 절차 (새 세션 / 회복된 세션)

```
1. HARNESS.md 세션 시작 프로토콜 수행 (읽기 예산 준수)
2. state.json의 next_action을 확인한다
3. current.step이 EXECUTE(5) 이후였다면 — 산출물이 실제로 존재하는지 파일로 검증한 뒤 EVALUATE(6)부터 재개.
   기억이 아니라 evaluator가 진위를 정한다.
4. current.step이 그 이전이면 해당 단계부터 재개
5. 재개 사실을 journal.jsonl에 기록
```
