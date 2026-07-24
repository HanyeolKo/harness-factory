# Generated skill surface

신규 생성은 `templates/adapters/shared/SKILL-TEMPLATE.md`와 schema 1.1 spec을 사용한다. 이 파일은 호출명 참고용이다.

| skill | 역할 | 자동 로드 |
|---|---|---|
| `<id>` | 작업 실행과 task evaluator 인계 | 사용자 작업 요청 시 |
| `<id>-eval` | 개별 작업 pass/fail (호환/내부) | 작업 직후 |
| `<id>-verify` | schema·adapter parity·cold-start | 구성 변경 후 |
| `<id>-evaluate` | baseline/control/treatment 효과 비교 | 명시 요청 또는 targeted/full trigger |
| `<id>-improve` | 증거 기반 점진 개선 | full regression/하네스 결함 확인 후 |

Canonical skill은 `harness/skills/<skill-id>/SKILL.md`이며 Claude `.claude/skills`, Codex `.agents/skills`, Gemini `.gemini/skills` 투영본은 byte-identical해야 한다. 기존 `<id>-retro`는 `<id>-improve` 호환 alias로만 유지한다.
