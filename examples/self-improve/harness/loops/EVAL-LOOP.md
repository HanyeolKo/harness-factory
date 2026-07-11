# EVAL LOOP — 평가 루프 (1급 구성요소)

> 완료 판정 기준이 없는 작업 단위는 실행할 수 없다 (원칙 1).

## 주 evaluator

- 유형: 결정적-수동정의 (scripts/verify.sh — **U-001로 신설 예정**. 신설 전까지 아래 임시 루브릭 병행)
- 수단: scripts/verify.sh — 플레이스홀더 잔존·문서 규율·산출물 계약 구조·상호참조 검사를 묶은 스크립트
- 실행: `bash scripts/verify.sh` (커맨드 전문은 ENVIRONMENT.md 검증 표)
- pass 조건: exit 0

## 판정 절차

```
1. RUN      evaluator를 실행한다. 실행 자체가 불가능하면 → 판정 불가 = fail(structural), RECOVERY로.
2. JUDGE    pass 조건 대조. 루브릭형이면 아래 루브릭의 각 기준을 개별 판정한다.
3. RECORD   journal.jsonl에 기록: {"event":"eval", "unit":..., "verdict":"pass|fail", "evidence":...}
            기록되지 않은 평가는 수행되지 않은 것이다.
4. FEED     fail → RECOVERY-PLAYBOOK 입력 (분류·등급 판정, 실패 키 부여, 카운터 계상은 플레이북 책임).
```

## 루브릭 (verify.sh 신설 전 임시 — U-001 완료 시 "미사용" 전환)

| # | 기준 | pass 조건 |
|---|---|---|
| 1 | 잔존 플레이스홀더 | 개정 파일에 `{{` 0건 (templates/ 제외) |
| 2 | 문서 규율 | 개정 파일 100줄 내외, 초과 시 예외 표기 존재 |
| 3 | 상호참조 | 개정이 언급하는 파일·절이 실제 존재 |
| 4 | 톤 | 명령형·판정형, 수치 확정 ("적절히" 류 0건) |

전 기준 pass여야 단위 pass.

## 금지

- "잘 된 것 같음" — 루브릭 없는 LLM 판정은 판정이 아니다.
- LLM의 집계·카운팅을 evaluator로 사용하는 것 (원칙 3). 세는 일은 스크립트가 한다.
- evaluator를 통과시키기 위한 evaluator 약화. evaluator 수정은 DECISIONS.md 기록 필수.
