# Required skill body presets

These complete examples define the required entry, evaluation, and improvement semantics. When rendering `SKILL.md.tmpl`, adapt the matching example's procedural content into `{{SKILL_BODY}}`; the generic template owns the final frontmatter and heading. Its `*_JSON` frontmatter placeholders receive one complete JSON-serialized string value, with no extra template quotes, so YAML safely preserves colons, hashes, quotes, and newlines. Every spec skill, including arbitrary `domain` skills, is first rendered as the canonical file named by `skills[].instructions`. Copy that complete canonical file byte-for-byte into Claude `.claude/skills/<skill-id>/SKILL.md` and Codex `.agents/skills/<skill-id>/SKILL.md`; do not render the adapters independently.

## Entry skill

```markdown
---
name: {{SKILL_ID_JSON}}
description: {{SKILL_DESCRIPTION_JSON}}
---

# {{SKILL_NAME}}

1. `{{HARNESS_ROOT}}/HARNESS.md`, `{{HARNESS_ROOT}}/harness-spec.json`, `{{HARNESS_ROOT}}/state/state.json`, spec의 `memory.index`를 읽고 현재 작업에 필요한 지속 메모리만 선택한다.
2. 인자가 있으면 새 요청 또는 큐 필터로, 없으면 `state.next_action`으로 해석한다.
3. spec의 `orchestration.entry_skill`과 같은 skill의 `entry_agent`부터 시작한다.
4. Claude는 `.claude/agents/{{SKILL_NAME}}-<role-id>.md`, Codex는 같은 name을 선언한 `.codex/agents/{{SKILL_NAME}}-<role-id>.toml`의 native agent를 호출한다.
5. `orchestration.handoffs` DAG를 따라 필요한 역할만 위임한다. 역할 수나 이름으로 역량을 추측하지 않고 capabilities, lane, domains, access를 따른다.
6. 각 handoff에는 원문 요청, unit id, 허용 경로, 입력 artifact, evaluator, 승인 게이트만 전달한다.
7. 실행 직후 `{{SKILL_NAME}}-eval`을 수행한다. 반복 실패, evaluator 공백, 콜드스타트 fail이면 `{{SKILL_NAME}}-retro`를 자동 개시한다.
8. state를 갱신하고 journal에 근거·handoff·verdict를 append-only로 기록한다.

evaluator 없는 실행, 증거 없는 pass, 승인 게이트 우회는 금지한다. native agent가 없을 때만 인라인 폴백하고 사유를 기록한다. adapter가 spec과 다르면 parity fail로 중지한다.
```

## Evaluation skill

```markdown
---
name: {{SKILL_ID_JSON}}
description: {{SKILL_DESCRIPTION_JSON}}
---

# {{SKILL_NAME}}-eval

1. `{{HARNESS_ROOT}}/harness-spec.json`, `{{HARNESS_ROOT}}/loops/EVAL-LOOP.md`, 평가 대상 unit을 읽는다.
2. unit에 연결된 evaluator의 runner, owner, command, pass_condition을 확인한다. 없으면 `fail(structural:no-evaluator)`다.
3. runner 역할이 검증을 실행하고 명령·cwd·exit code·원본 출력을 보존한다.
4. owner 역할이 원본 증거를 pass condition과 대조해 verdict를 낸다. 실행 역할의 자기 판정으로 대체하지 않는다.
5. fail이면 `defect-counting` capability 역할이 실패 키를 확정하고 사건당 한 번 카운트한다.
6. journal에 eval·evidence·verdict·count·handoff를 기록한다.
7. 반복 실패, evaluator 공백, 콜드스타트 fail이면 `{{SKILL_NAME}}-retro`를 자동 개시한다.

evaluator 약화는 평가가 아니라 spec 변경이며 개선 절차와 재검증이 필요하다.
```

## Improvement skill

```markdown
---
name: {{SKILL_ID_JSON}}
description: {{SKILL_DESCRIPTION_JSON}}
---

# {{SKILL_NAME}}-retro

1. `{{HARNESS_ROOT}}/harness-spec.json`, `{{HARNESS_ROOT}}/loops/IMPROVE-LOOP.md`, improve 카운터와 관련 journal 범위만 읽는다.
2. `loops.improvement_owner` 역할에 읽기 전용 입력을 주어 근거가 있는 개선안 1~2개를 받는다.
3. 인간 승인 게이트 대상만 적용 전 승인을 기다린다.
4. 기존 하네스는 기준선과 보존 manifest를 확인하고 delta plan의 관리 파일만 갱신한다. 의미 변경을 `harness-spec.json`에 먼저 반영한다.
5. 선택된 모든 런타임의 skills, agents, root guidance, config를 spec에서 다시 생성한다.
6. parity validator, 콜드스타트, 원 evaluator를 다시 실행한다.
7. fail이면 최대 3회 보완하고 잔여 fail을 공개한다. pass하면 겨냥한 실패 키만 리셋한다.
8. 지속 메모리가 생성·이동·대체·보관되면 `memory/INDEX.md`를 같은 변경 단위에서 갱신한다. DECISIONS.md와 journal에 근거, 재생성, 검증 결과를 기록한다.

전면 덮어쓰기, 승인 없는 기존 메모리 삭제, evaluator 완화, 게이트 우회, fail 은폐, 한쪽 adapter만의 의미 변경은 금지한다.
```
