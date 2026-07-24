---
name: build-harness
description: 대상 프로젝트를 분석해 런타임 중립 에이전트 팀·스킬·평가·점진 개선 하네스를 새로 만들거나 전체 마이그레이션하고 Claude, Codex, Gemini 어댑터를 생성한다. 최초 하네스 구축이나 전체 토폴로지 재설계에 사용하며 단일 구성요소 변경·검증·성과평가에는 전용 스킬을 사용한다.
---

# build-harness

대상 프로젝트 안에 스스로 상태·평가 증거·개선 이력을 소유하는 하네스를 만든다. 팩토리는 설치된 하네스를 중앙으로 수집하거나 운영 상태를 흡수하지 않는다.

## 범위

- 최초 구축과 기존 하네스의 전체 schema 1.1 마이그레이션에 사용한다.
- 단일 agent·skill·evaluator에는 각각 `build-agent`, `build-skill`, `build-evaluator`를 사용한다.
- 구조 확인은 `verify-harness`, 적용 성과 비교는 `evaluate-harness`, 증거 기반 개선은 `improve-harness`를 사용한다.
- 기존 `state/`, append-only `ledger/`, `evaluation/` 이력을 보존한다.

## 팩토리 확인

1. `scripts/resolve_factory.py`를 실행한다. 이미 경로를 알면 `--factory-root <path>`, 오프라인이면 `--offline`을 사용한다.
2. stdout의 절대 경로를 `FACTORY_ROOT`로 사용한다. 계약 검증 실패를 임의 템플릿으로 우회하지 않는다.
3. `docs/CONSTRUCTOR-PROTOCOL.md`, `references/RUNTIME-CONTRACT.md`, `principles/`, `interview/QUESTION-BANK.md`, `CHECKLIST.md`를 읽는다.
4. source URL·ref·commit은 대상 `ledger/DECISIONS.md`에 기록하되 로컬 경로와 자격증명은 제거한다.

## 입력 해석

- 첫 경로 인자는 대상 프로젝트이며 없으면 현재 디렉터리다.
- 런타임이 없으면 Claude·Codex·Gemini를 모두 생성한다. 기존 하네스에서는 현재 `runtime_targets`를 상속한다.
- 코드로 알 수 없는 목적, 위험한 승인 경계, 완료 기준만 질문한다.

## 생성 절차

1. **DISCOVER** — root 규칙, README/docs, 모듈 경계, 빌드·테스트·CI, 기존 skills/agents/hooks와 보존 대상을 읽는다.
2. **DESIGN** — 프로젝트 경계에서 lower-kebab-case 역할과 skill을 도출하고 lane, capability, domain, access, 추상 model tier, handoff를 부여한다.
3. **SPECIFY** — schema 1.1 spec과 정상 DAG를 만든다. 모든 `skills[].evaluator`를 필수로 연결한다.
   - entry/evaluation/verification/domain → `scope: task`
   - harness-evaluation/improvement → `self_evaluation.evaluator`인 `scope: harness`, `type: experiment`
4. **BUILD COMMON** — HARNESS, team, canonical skills, loops, recovery, budget, append-only ledger, task/self-evaluation state를 렌더링한다.
5. **BUILD EVALUATION** — full baseline/control/treatment 계약과 `evaluation/suites/targeted.json`을 만들고 `self_evaluation.targeted_suite`가 이를 참조하게 한다. targeted suite는 `cost-regression`, `retry-pressure`, `deterministic-sample`을 고정 결정적 metric에만 매핑한다.
6. **INSTALL TRIGGERS** — `check_self_evaluation.py`와 `record_self_evaluation.py`를 설치한다. checker만 task boundary에서 실행하며 `none|targeted|full`을 반환한다. recorder는 완료된 targeted/full을 ACK한다.
7. **WATCH MANAGED ARTIFACTS** — canonical은 checker가 별도 hash한다. `self_evaluation.watched_paths`에는 선택 provider의 정확한 managed artifact만 넣는다: root guidance 파일, spec 각 skill projection, namespaced agent wrapper, 생성 provider config. provider root 디렉터리 전체나 unrelated user skill/agent는 넣지 않는다.
8. **ADAPT PREFLIGHT** — provider adapter를 쓰기 전에 다음 명령을 실행하고 exit 0을 확인한다.

   ```text
   python <FACTORY_ROOT>/scripts/validate_runtime_neutral.py <target> --provider-path-preflight
   ```

   preflight는 provider registry의 `root_guidance`, `skill_root`, `agent_root`, 선택적 `config`를 target 기준으로 resolve한다. 절대 경로, lexical traversal, symlink를 거쳐 target 밖으로 나가는 경로를 모두 거부한다. 실패하면 provider 디렉터리·파일을 생성·쓰기·이동하지 않고 우회 경로도 사용하지 않는다.
9. **ADAPT** — provider registry를 따라 thin adapter를 만든다.
   - Claude: `CLAUDE.md`, `.claude/skills`, `.claude/agents`
   - Codex: `AGENTS.md`, `.agents/skills`, `.codex/agents`, `.codex/config.toml`
   - Gemini: `GEMINI.md`, `.gemini/skills`, `.gemini/agents`
10. **EXPOSE** — `<id>` 실행, 내부 task evaluation, `<id>-verify`, `<id>-evaluate`, `<id>-improve`를 만든다. 기존 `-eval`, `-retro`는 호환 alias로만 유지한다.
11. **VALIDATE** — validator와 연결 evaluator를 실행한다. cold-start가 false→true이면 `coldstart-fail`, parity가 pass→fail이면 `parity-fail`을 pending events에 중복 없이 추가한다.
12. **ROUTE** — checker reason이 `input-invalid:*`이면 effect evaluation/LLM을 열지 않고 `verify-harness`와 구조 복구 후 재실행한다. `adapter-change|parity-fail`은 parity pass 전 effect evaluation을 금지한다.
13. **REPAIR** — 최대 3회 보완한다. 공통 정본을 먼저 바꾸고 모든 선택 adapter를 재생성한다. 잔여 fail은 숨기지 않는다.

## 평가·ACK 계약

- task evaluator는 작업마다 수행한다. harness effect 평가는 유효한 targeted/full 또는 명시 요청에서만 수행한다.
- targeted는 `targeted.json`의 reason 매핑만 실행하며 임의 LLM judge를 열지 않는다.
- 완료된 targeted/full마다 다음 recorder를 호출한다.

```text
python <target>/harness/triggers/record_self_evaluation.py <target>/harness --decision <targeted|full> --decision-file <target>/harness/evaluation/runs/<run-id>/trigger.json --verdict <improved|neutral|regressed|inconclusive>
```

- 평가 전에 checker JSON을 `<target>/harness/evaluation/runs/<run-id>/trigger.json`에 동결한다. 명시적 full 요청은 raw checker JSON 전체를 `override.original`에 보존하고, top-level effective `decision: full`, `mandatory: false`, `override.kind: explicit-user-request`, original reasons 뒤의 marker, 동일한 deferred reasons·hashes·`acknowledgement`를 기록한다. 단순 decision 변조나 구조화되지 않은 budget·cooldown 우회는 recorder가 거부한다. recorder는 frozen decision/reasons, managed hashes, failure snapshot을 검증한다. full은 처리한 pending-event/failure snapshot만 ACK하고 managed hashes·units·cooldown을 갱신한다. 평가 중 생긴 새 event·failure는 보존한다. targeted는 last decision·cooldown만 갱신한다.
- full regression 또는 하네스 원인 확인 뒤에만 `improve-harness`를 연다. 한 가설·1~2개 변경과 동일 suite 재평가를 기본으로 한다.

## 인도

생성 트리, 공통 역할·skill·evaluator, runtime별 호출명, 보존 상태, trigger/ACK 정책, 검증 결과와 잔여 위험을 보고한다. 자동 commit하거나 대상 프로젝트 밖에 운영 상태를 기록하지 않는다.

## 불변 조건

- 공통 spec·canonical skill이 정본이며 adapter는 파생물이다.
- evaluator 원본 증거와 journal 기록 없는 pass는 없다.
- 승인 gate 우회, evaluator 완화, provider 한쪽만의 의미 변경을 허용하지 않는다.
- 팩토리는 설치된 하네스의 state·journal·평가 결과를 흡수하지 않는다.
