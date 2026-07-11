# DECISIONS — 설계 결정 기록 (ADR-lite)

하네스 문서·구조·evaluator의 모든 변경은 여기 기록된다.

## 형식

```
## D-00N — <제목> (<날짜>)
- 결정 / 근거 / 영향
```

---

## D-001 — 하네스 초기 구성 (2026-07-11)

- 결정: harness-factory로 하네스 뼈대 생성. 설계 방향 = 코스트 기반 자동검증·보완 (기본형 유지, 오버라이드 없음)
- 근거: 인터뷰 결과 —
  - Q1 (사용자 확정): 대상 = harness-factory 레포 자체, 목적 = 팩토리의 지속 개선 작업 관리, 산출물 = 문서
  - Q2~Q4 및 2차 배치: 사용자 위임("알아서") — 기본값 일괄표 적용
  - 적용된 기본값: EVALUATOR_PRIMARY(결정적 수단 부재 → 검증 스크립트 신설 백로그 1번 + 임시 루브릭), OPERATION_MODE(상주 세션형), BUDGET_POLICY(보통), BUDGET_UNIT(작업 단위 수 — 토큰 측정 불가), PARALLELISM(없음), COMMIT_POLICY(단위 pass마다 1커밋), GATES(산출물 계약 변경·불변 조건 문구 수정), ESCALATION(등급 S 전부), JOURNAL_LEVEL(b), RETRO_INTERVAL(10), FAIL_THRESHOLD(3), RETRY_POLICY(3회 2s/4s/8s)
- 영향: examples/self-improve/harness/ 이하 13개 파일 생성. 주 evaluator = scripts/verify.sh(U-001 신설 예정), 운영 모드 = 상주 세션형.
- 검증·보완 루프 기록 (최대 3회):
  - 1회전: fail 1건 발견 후 보완 — CHECKLIST의 플레이스홀더 검사(`grep '{{'`)가 오탐 4건 산출
    (하네스 문서가 검증 절차 설명에서 리터럴을 정당하게 언급한 사례). 정밀 패턴으로도 예시 리터럴 1건 잔존
    → 해당 예시를 리워딩으로 해소. 구조 13파일·문서 규율·state.json 유효성·콜드스타트·세션 의존 표현은 pass.
    주 evaluator 실행 확인은 U-001 신설 전이므로 임시 루브릭으로 대체 판정.
  - 2회전: 미수행 — 사용자 지시로 1회 한정 실행. 발견된 팩토리 결함(검사 규격 오탐)은 인도 보고에 명시
  - 3회전: 미수행
