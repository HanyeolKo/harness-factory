# HARNESS — harness-factory 레포 지속 개선

> 이 파일은 이 하네스의 **단일 진입점**이다. 새 세션은 반드시 이 파일부터 읽는다.
> 생성: 2026-07-11 / 팩토리: harness-factory / 마지막 개정: 2026-07-11

## 목적

harness-factory 레포(원칙·템플릿·질문은행·체크리스트)의 지속 개선 작업을 관리한다. 산출물은 문서(마크다운 규칙·템플릿).
완료 판정: `scripts/verify.sh` 통과 (U-001로 신설 예정 — 신설 전까지 EVAL-LOOP의 임시 루브릭) + 개정 건별 콜드스타트 재검증.

## 설계 방향

코스트 기반 자동검증·보완 (기본형 유지). 변경 시 DECISIONS.md 기록 + 이 절 갱신.

## 문서 규율 (원칙 7)

추가 문서는 인덱스 기반 100줄 내외 기본값. 초과는 분할 또는 `<!-- 문서규율 예외: ... -->` 표기 후 파일 맵에 "전문" 등재.

## 세션 시작 프로토콜 (읽기 예산: 아래 목록 외 선행 읽기 금지)

1. 이 파일 (HARNESS.md)
2. `state/state.json` — 현재 상태·작업 큐·다음 행동
3. `budget/CONTEXT-BUDGET.md`의 소진 장부 마지막 3행
4. state.json `current.refs`에 명시된 파일만

읽기 완료 후 다음 3문항에 파일 근거로 답할 수 있는지 확인한다 — 목적과 현재 단계 / 즉시 수행할 다음 행동 / 그 행동의 완료 판정.
**하나라도 답할 수 없으면 콜드스타트 fail이다**: state.json `improve.coldstart_fail = true` 기록 → IMPROVE-LOOP 트리거.
답할 수 있으면 즉시 `loops/EXECUTION-LOOP.md`의 루프를 개시한다.

## 세션 종료 프로토콜

1. `state/state.json` 갱신 (체크포인트 — `recovery/CHECKPOINT.md` 규격)
2. `ledger/journal.jsonl`에 `session_end` 기록
3. `budget/CONTEXT-BUDGET.md` 소진 장부 1행 추가
4. 커밋: 작업 단위 pass마다 1커밋, 메시지 `improve(<대상 파일>): <개정 요지>`

## 축 구성

| 축 | 상태 | 문서 |
|---|---|---|
| 실행 | 사용 | `loops/EXECUTION-LOOP.md` — 작업 단위: 개정 안건 1건 (파일 1~2개 범위) |
| 평가 (1급) | 사용 | `loops/EVAL-LOOP.md` — 주 evaluator: scripts/verify.sh (결정적-수동정의, 신설 전 임시 루브릭) |
| 회복 | 사용 | `recovery/RECOVERY-PLAYBOOK.md`, `recovery/CHECKPOINT.md` |
| 보완 | 사용 | `loops/IMPROVE-LOOP.md` — 회고 주기: 작업 단위 10개마다 |
| 기록 | 사용 | `ledger/` — 수준: 단위 시작/종료 + 판정 + 실패 + 결정 |
| 코스트 | 사용 | `budget/CONTEXT-BUDGET.md` — 정책: 보통 (80% 경고 / 100% 체크포인트+교체) |

## 운영 방식

- 모드: 상주 세션형
- 에스컬레이션: 등급 S 전부 (`recovery/RECOVERY-PLAYBOOK.md` §중지 프로토콜)
- 인간 승인 게이트: 산출물 계약(파일명·위치) 변경, README §불변 조건 문구 수정

## 파일 맵

```
examples/self-improve/harness/
├── HARNESS.md            # (이 파일) 진입점
├── ENVIRONMENT.md        # 검증 커맨드, 디렉토리 맵, 금지사항
├── loops/                # EXECUTION·EVAL·IMPROVE
├── recovery/             # RECOVERY-PLAYBOOK, CHECKPOINT
├── ledger/               # journal.jsonl, DECISIONS.md, JOURNAL-FORMAT.md, retro-<N>.md(운영 중)
├── budget/               # CONTEXT-BUDGET.md
└── state/state.json      # 현재 상태 (단일 source of truth)
```

파일명·위치 변경 시: `ledger/DECISIONS.md` 기록 + 이 파일 맵 갱신을 한 커밋으로.
