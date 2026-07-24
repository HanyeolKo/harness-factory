# TASK EVAL LOOP — 작업 완료 평가

> 이 루프는 개별 작업의 완료 여부를 판정한다. 하네스 적용 효과는 `HARNESS-EVAL-LOOP.md`가 별도로 판정한다.

## 주 evaluator

- 유형: 결정적-수동정의 (`scripts/verify.sh` — U-001로 신설 예정)
- 실행: `bash scripts/verify.sh`
- pass 조건: exit 0
- 스크립트 신설 전: 아래 임시 루브릭 전 기준 pass

## 판정 절차

```text
1. RUN      작업 evaluator를 실행한다. 실행 불가는 fail(structural)이다.
2. JUDGE    명시된 pass 조건과 원본 결과를 대조한다.
3. RECORD   journal.jsonl에 task_eval, verdict, evidence, retry, cost를 기록한다.
4. FEED     fail은 RECOVERY-PLAYBOOK으로 전달한다. 하네스 개선을 직접 실행하지 않는다.
5. SIGNAL   집계 가능한 값만 self-evaluation 상태에 반영한다.
```

## 임시 루브릭

| # | 기준 | pass 조건 |
|---|---|---|
| 1 | 잔존 플레이스홀더 | 개정 파일에 `{{` 0건 |
| 2 | 문서 규율 | 100줄 내외, 초과 시 예외 표기 |
| 3 | 상호참조 | 언급한 파일·절이 존재 |
| 4 | 톤 | 명령형·판정형이며 모호한 기준 0건 |

## 금지

- task fail을 곧바로 하네스 결함으로 간주하지 않는다.
- evaluator를 통과시키기 위해 evaluator를 약화하지 않는다.
- LLM에 집계·카운팅을 맡기지 않는다.
