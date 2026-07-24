# 레거시 0.1 최소 예시 — 문서 밀도 참고용

> 이 예시는 0.1의 주기적 retro 상태 필드를 보존한다. 현재 0.2 생성 계약이나 검증 fixture가 아니며, 이벤트 기반 `none|targeted|full` 자기평가 구조는 `examples/self-improve/`를 참고한다.

가상의 작업 *"legacy-utils 모듈 42개 파일을 TypeScript로 마이그레이션"* 에 대해 당시 하네스의 핵심 2개 파일(`HARNESS.md`, `state/state.json`)만 보여준다.

구성자는 이 예시를 톤과 밀도의 참고 자료로만 삼는다.

- 명령형·판정형 문장
- 수치로 확정된 정책
- 복사해 실행할 수 있는 command

이 예제는 다음 0.2 필수 계약을 의도적으로 포함하지 않는다.

- schema 1.1 `harness-spec.json`과 skill별 evaluator 링크
- `state/self-evaluation.json`
- checker·recorder·targeted suite와 frozen `trigger.json` ACK 수명주기
- Claude, Codex, Gemini adapter와 artifact 단위 `watched_paths`
- loops, recovery, ledger, budget 전체 구조

따라서 이 디렉터리에 0.2 validator를 실행하거나 여기의 `state.json`을 현재 생성 템플릿으로 복사하면 안 된다. 현재 인도물 구조와 필수 파일은 schema·template·validator·CHECKLIST를 따른다.
