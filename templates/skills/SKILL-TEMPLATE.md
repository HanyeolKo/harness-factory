# SKILL 템플릿 — 하네스 루프의 스킬 노출

하네스를 Claude Code 등에서 슬래시 커맨드로 부르고 싶을 때, 대상 프로젝트의
`.claude/skills/<skill-name>/SKILL.md`로 아래를 치환해 설치한다. 선택 사항이다.

---

```markdown
---
name: {{SKILL_NAME}}
description: {{TARGET}} 하네스의 실행 루프를 개시한다. 세션 시작 시 또는 "하네스 돌려줘" 요청 시 사용.
---

# {{SKILL_NAME}}

1. `{{HARNESS_ROOT}}/HARNESS.md`를 읽고 세션 시작 프로토콜을 그대로 수행한다.
   (읽기 예산 준수 — 프로토콜에 명시된 파일 외 선행 읽기 금지)
2. `loops/EXECUTION-LOOP.md`의 루프를 개시한다.
3. 종료 시 세션 종료 프로토콜(체크포인트·기록·장부)을 빠짐없이 수행한다.

인자가 주어지면: 인자를 작업 큐 필터로 해석한다 (예: 특정 단위 id).
```

---

같은 방식으로 회고 전용 스킬(`{{SKILL_NAME}}-retro` → IMPROVE-LOOP 개시)을 추가할 수 있다.
