# 0.2 예시 — 프로젝트 소유의 이벤트 기반 자기개선

harness-factory가 생성한 하네스를 대상 프로젝트가 직접 소유하고 점진적으로 개선하는 흐름의 핵심 문서 예시다. 팩토리는 설치된 하네스의 상태·로그·평가 결과를 회수하거나 중앙에서 운영하지 않는다.

## 이 예제의 범위

이 디렉터리는 완전한 생성 fixture나 validator 입력이 아니다. 다음 핵심 연결만 보여준다.

- 모든 작업은 연결된 task evaluator로 완료 여부를 판정한다.
- 하네스 효과 평가는 값싼 checker가 `targeted|full`을 반환한 경우에만 수행한다.
- `input-invalid:*`는 `full` decision보다 먼저 해석해 effect evaluation과 LLM judge를 금지하고 구조 검증만 수행한다.
- 완료된 targeted/full run은 동결한 `trigger.json`을 `record_self_evaluation.py --decision-file`로 ACK한다.
- improvement는 full 평가가 회귀 또는 하네스 결함을 확인한 경우에만 수행한다.

포함된 `harness/evaluation/runs/EXAMPLE-001/trigger.json`은 checker 출력을 변경하지 않고 보존하는 형식 예시다. `1…`·`2…` digest는 설명용이며 실제 recorder의 stale-hash 검사를 통과하는 실행 데이터가 아니다.

## 의도적으로 생략한 파일

중복 구현을 피하려고 다음 생성 산출물을 넣지 않았다.

- `harness/harness-spec.json`
- `harness/triggers/check_self_evaluation.py`
- `harness/triggers/record_self_evaluation.py`
- Claude, Codex, Gemini root guidance·skill·agent adapter와 Codex config

따라서 이 디렉터리만으로 checker·recorder·validator를 실행할 수 없다. 실제 생성물은 schema 1.1 spec, 두 trigger script, `evaluation/suites/targeted.json`, 선택 provider adapter를 모두 포함한다.

## provider 감시 범위

실제 spec의 `self_evaluation.watched_paths`는 선택 provider마다 다음 **개별 artifact**의 정확한 집합이다.

- provider `root_guidance`
- 각 spec skill의 `<skill_root>/<skill-id>/SKILL.md`
- 각 spec agent의 `<agent_root>/<namespace>-<role-id><agent_extension>`
- provider가 정의한 `config`

`<skill_root>`나 `<agent_root>` 디렉터리 전체를 넣지 않는다. 그래야 다른 하네스의 unrelated skill·agent 변경이 `adapter-change` full 평가를 유발하지 않는다.

## 생성물의 ACK 수명주기

```text
1. CHECK   read-only checker를 실행한다.
2. GUARD   reasons에 input-invalid:*가 있으면 verify-harness와 구조 복구만 수행한 뒤 다시 CHECK한다.
3. FREEZE  targeted|full stdout을 evaluation/runs/<run-id>/trigger.json에 그대로 저장한다.
4. RUN     targeted는 고정 metric만, full은 고정 baseline/control/treatment를 실행한다.
5. ACK     완료 run만 frozen trigger.json과 verdict를 recorder에 전달한다.
```

```text
python harness/triggers/record_self_evaluation.py harness --decision <targeted|full> --decision-file harness/evaluation/runs/<run-id>/trigger.json --verdict <improved|neutral|regressed|inconclusive>
```

recorder는 frozen decision·reasons·incident acknowledgement와 현재 canonical/provider hash를 대조한다. full ACK는 처리한 pending event와 hash snapshot을 갱신하고, targeted ACK는 mandatory event를 소비하지 않는다. 미완료 run과 `none`에는 recorder를 호출하지 않는다.

`examples/minimal/`은 0.1 문서 밀도를 보존한 레거시 예시이며 현재 0.2 생성 계약의 정본으로 사용하지 않는다.
