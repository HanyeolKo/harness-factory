# MEMORY INDEX — harness-factory 레포 지속 개선

이 표에서 현재 작업에 필요한 지속 메모리만 선택한다. 진행 상태와 실행 사건은 각각 `state/state.json`, `ledger/journal.jsonl`에서 읽는다.

| ID | 경로 | 한 줄 요약 | 언제 읽나 | 출처 | 마지막 검증 | 상태 |
|---|---|---|---|---|---|---|
| - | - | 등록된 지속 메모리 없음 | - | - | 2026-07-24 | empty |

허용 상태는 `active`, `superseded`, `archived`, `empty`다. 일반 본문·index 행 변경은 결정적 구조 검증만 수행하고, schema·보존 정책·읽기 라우팅 변경만 full 하네스 평가 사유로 취급한다.