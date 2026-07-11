# HARNESS — legacy-utils TypeScript 마이그레이션

> 이 파일은 이 하네스의 **단일 진입점**이다. 새 세션은 반드시 이 파일부터 읽는다.
> 생성: 2026-07-11 / 팩토리: harness-factory / 마지막 개정: 2026-07-11

## 목적

`src/legacy-utils/` 이하 42개 `.js` 파일을 TypeScript로 마이그레이션한다. 산출물은 코드.
완료 판정: 파일별로 `npm run typecheck` + 해당 모듈 테스트(`npm test -- <모듈>`) 통과, 전체 완료 시 `npm test` 전체 통과.

## 설계 방향

코스트 기반 자동검증·보완 (기본형 유지) — 예산을 축으로 결정적 evaluator 자동 검증과 자기 보완 루프가 회전한다. 변경 시 DECISIONS.md 기록 + 이 절 갱신.

## 문서 규율 (원칙 7)

추가 문서는 인덱스 기반 100줄 내외 기본값. 초과는 분할 또는 `<!-- 문서규율 예외: ... -->` 표기 후 파일 맵에 "전문" 등재.

## 세션 시작 프로토콜 (읽기 예산: 아래 목록 외 선행 읽기 금지)

1. 이 파일 (HARNESS.md)
2. `state/state.json` — 현재 상태·작업 큐·다음 행동
3. `budget/CONTEXT-BUDGET.md`의 소진 장부 마지막 3행
4. state.json `current.refs`에 명시된 파일만

읽기 완료 후 즉시 `loops/EXECUTION-LOOP.md`의 루프를 개시한다.

## 세션 종료 프로토콜

1. `state/state.json` 갱신 (체크포인트)
2. `ledger/journal.jsonl`에 `session_end` 기록
3. `budget/CONTEXT-BUDGET.md` 소진 장부 1행 추가
4. 커밋: 단위 pass마다 1커밋, 메시지 `migrate(<모듈명>): js→ts`

## 축 구성

| 축 | 상태 | 문서 |
|---|---|---|
| 실행 | 사용 | `loops/EXECUTION-LOOP.md` — 작업 단위: 파일 1개 (의존 묶음은 2~3개까지 허용) |
| 평가 (1급) | 사용 | `loops/EVAL-LOOP.md` — 주 evaluator: typecheck + 모듈 테스트 (결정적-자동) |
| 회복 | 사용 | `recovery/RECOVERY-PLAYBOOK.md`, `recovery/CHECKPOINT.md` |
| 보완 | 사용 | `loops/IMPROVE-LOOP.md` — 회고 주기: 단위 10개 완료마다 |
| 기록 | 사용 | `ledger/` — 수준: 단위 시작/종료 + 판정 + 실패 + 결정 |
| 코스트 | 사용 | `budget/CONTEXT-BUDGET.md` — 정책: 보통 (80% 경고 / 100% 체크포인트+교체) |

## 운영 방식

- 모드: 상주 세션형 (사용자와 세션 단위 진행)
- 에스컬레이션: 스코프 실패 즉시 / 재시도 3회 상한 도달 / 예산 소진 — 모두 보고 후 대기
- 인간 승인 게이트: `package.json` 의존성 변경, 공개 API 시그니처 변경

## 파일 맵

```
harness/
├── HARNESS.md            # (이 파일) 진입점
├── ENVIRONMENT.md        # npm run typecheck / npm test 등 커맨드 표
├── loops/                # EXECUTION·EVAL·IMPROVE
├── recovery/             # RECOVERY-PLAYBOOK, CHECKPOINT
├── ledger/               # journal.jsonl, DECISIONS.md, JOURNAL-FORMAT.md
├── budget/               # CONTEXT-BUDGET.md
└── state/state.json      # 현재 상태 (단일 source of truth)
```
