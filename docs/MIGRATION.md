# 마이그레이션 가이드

이 문서는 plugin 0.1.x 또는 schema 1.0 하네스를 plugin 0.2.0 / schema 1.1의 프로젝트 소유·이벤트 기반 구조로 옮기는 절차입니다. standalone `build-harness`, 고정 팀, Claude 전용 control tower도 같은 원칙으로 전환합니다.

## 핵심 경계

마이그레이션은 기존 하네스를 factory package 안으로 가져오는 작업이 아닙니다. 기존 프로젝트의 `harness/`를 그 자리에서 보존·확장하고, factory의 원자적 스킬로 정본과 어댑터를 점진적으로 갱신합니다.

다음 데이터는 factory나 별도 registry로 이동하지 않습니다.

- `harness/state/`
- `harness/ledger/journal.jsonl`
- `harness/ledger/DECISIONS.md`
- task evaluation evidence와 harness-effect report
- 진행 중 queue, `next_action`, failure counter
- 사용자 작성 `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`

journal은 append-only입니다. schema 변경을 이유로 이전 event를 재작성하지 않습니다.

## 1. 변경 전 inventory

- 현재 schema와 factory ref
- 기존 실행·평가·회고 skill ID
- 실제 task evaluator 명령과 pass condition
- agent, domain, handoff, access 정책
- 선택된 provider와 native 경로
- 승인 gate와 waiting 상태
- state/ledger backup 또는 rollback ref
- 최근 성공률, 비용, 재시도 baseline

baseline이 없으면 “개선됨” 판정을 내릴 수 없습니다. 최소한 최근 안정 구간의 task 수, pass 수, 비용 단위, retry 수를 기록합니다.

## 2. 0.2.0 스킬 확인

각 런타임에서 다음 일곱 스킬을 확인합니다.

```text
build-harness
build-agent
build-skill
build-evaluator
verify-harness
evaluate-harness
improve-harness
```

기존 정본이 유효하면 `build-harness`로 전면 재생성하지 않습니다. 빠진 evaluator는 `build-evaluator`, provider 추가는 관련 build 스킬, 구조 확인은 `verify-harness`처럼 가장 작은 작업 단위를 선택합니다.

## 3. schema 1.1 계약 추가

기존 ID를 가능한 한 유지하며 다음을 추가합니다.

- 모든 `skills[].evaluator` 링크
  - entry/evaluation/verification/domain → `scope: task`
  - harness-evaluation/improvement → `scope: harness`, `type: experiment`
- `self_evaluation` checker, recorder, state, harness evaluator, sampling/cooldown/budget/threshold
- `self_evaluation.targeted_suite: harness/evaluation/suites/targeted.json`
- canonical 별도 hash와 `self_evaluation.watched_paths`: 선택 provider의 exact managed artifact만
- mandatory event와 full harness evaluation loop

```text
harness/loops/HARNESS-EVAL-LOOP.md
harness/evaluation/EVALUATION-CONTRACT.md
harness/evaluation/suites/targeted.json
harness/triggers/check_self_evaluation.py
harness/triggers/record_self_evaluation.py
harness/state/self-evaluation.json
```

`targeted.json`은 `cost-regression|retry-pressure|deterministic-sample`을 고정 결정적 metric에 매핑합니다. 초기 state에는 `canonical-contract-change` pending event와 빈 managed hash를 둡니다. 첫 full baseline을 완료하면 recorder로 ACK합니다.
## 4. 평가 의미 분리

기존 `<namespace>-eval`이 작업 완료를 판정했다면 **task evaluator**로 유지합니다. 기존 `<namespace>-retro`가 주기적으로 LLM 회고를 실행했다면 다음처럼 바꿉니다.

- 단순 주기 회고 → 결정적 trigger checker의 `full_interval_units`
- 작업 실패 집계 → task evaluation과 defect 기록
- 하네스 효과 비교 → harness-effect evaluator
- 하네스 문서 수정 → `improve-harness`

호환 alias를 잠시 둘 수 있지만 `retro`가 trigger만으로 자동 수정하지 않도록 합니다. 새 이름의 의미는 `evaluate-harness`가 효과 판정, `improve-harness`가 증거 기반 수정입니다.

## 5. provider adapter 재투영

Claude:

- `CLAUDE.md` 관리 블록 upsert
- `.claude/skills/<skill-id>/SKILL.md`
- `.claude/agents/<namespace>-<role-id>.md`

Codex:

- `AGENTS.md` 관리 블록 upsert
- `.agents/skills/<skill-id>/SKILL.md`
- `.codex/agents/<namespace>-<role-id>.toml`
- `.codex/config.toml`의 관련 limits만 구조적 병합

Gemini:

- `GEMINI.md` 관리 블록 upsert
- `.gemini/skills/<skill-id>/SKILL.md`
- `.gemini/agents/<namespace>-<role-id>.md`

공통 skill과 provider 투영본은 byte-identical이어야 합니다. root 문서의 관리 블록 밖 사용자 내용은 보존합니다.
`watched_paths`에는 각 root guidance 파일, spec skill projection, namespaced agent wrapper, 생성 config의 exact path만 넣습니다. provider root 전체와 unrelated user skill/agent는 넣지 않습니다.

## 6. trigger 정책 이관

기존 periodic retro는 checker의 interval/cooldown/budget으로 바꾸되 LLM을 직접 호출하지 않습니다. canonical·agent·skill·evaluator·adapter 변경과 cold-start/parity 실패는 mandatory pending event입니다. cold-start false→true, parity pass→fail 전환 때 새 event를 중복 없이 추가합니다.

라우팅 순서는 고정합니다.

1. `input-invalid:*` → effect evaluation/LLM 금지, `verify-harness`와 구조 복구 후 recheck
2. `adapter-change|parity-fail` → parity pass 전 effect evaluation 금지
3. `none` → 종료
4. `targeted` → `targeted.json` reason별 결정적 metric만
5. `full` → harness experiment evaluator

평가 전에 checker JSON을 `<target>\harness\evaluation\runs\<run-id>\trigger.json`에 동결합니다. 완료된 targeted/full마다 recorder를 호출합니다.

```powershell
python <target>\harness\triggers\record_self_evaluation.py <target>\harness --decision <targeted|full> --decision-file <target>\harness\evaluation\runs\<run-id>\trigger.json --verdict <improved|neutral|regressed|inconclusive>
```

full ACK는 처리 시작 pending event와 frozen failure snapshot만 ACK하고 exact managed artifact hashes, units, cooldown을 갱신합니다. 평가 중 생긴 새 event·failure는 보존합니다. targeted는 last decision과 cooldown만 갱신합니다. 따라서 같은 mandatory 신호가 반복 평가되지 않습니다.
## 7. 검증 순서

1. schema 1.1 parse, 모든 skill evaluator 링크, evaluator scope/type
2. checker와 recorder fixture; malformed decision file, decision mismatch, stale managed hash ACK 거부
3. `input-invalid:*`가 effect evaluation/LLM을 열지 않는지 확인
4. adapter/parity reason이 verify를 선행하는지 확인
5. targeted reason이 고정 deterministic suite와 정확히 매핑되는지 확인
6. full ACK가 frozen pending/failure만 ACK하고 평가 중 생긴 새 incident를 보존하는지 확인
7. watched exact managed artifact의 drift·삭제 검출과 unrelated file 제외
8. Claude·Codex·Gemini byte parity, native path, root managed block
9. cold-start false→true와 parity pass→fail incident 재검출
10. 기존 task evaluator, baseline full experiment, state/ledger 보존 확인

검증과 초기 full/recorder ACK가 끝날 때까지 오래된 standalone 스킬과 alias를 삭제하지 않습니다.
## 8. 정리

제거 후보는 새 호출과 rollback 경로가 검증된 뒤에만 정리합니다.

- 프로젝트에 복사했던 standalone factory skill
- 과거 비표준 provider skill 경로
- spec에 없는 stale agent
- 자동 LLM retro를 직접 호출하는 구형 hook

state, ledger, evaluation evidence는 제거 후보가 아닙니다.

## 롤백

1. 변경 전 spec과 managed adapter block 복원
2. 보존한 state, ledger, evidence 유지
3. 기존 task evaluator 재실행
4. 기존 factory ref 또는 commit으로 고정
5. cold-start 재실행
6. 실패 원인을 새 journal event와 DECISIONS에 append

롤백에서도 실패 기록을 삭제하거나 counter를 임의로 낮추지 않습니다.
