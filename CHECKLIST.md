# CHECKLIST — Phase 4 인도 전 검증

전 항목 pass여야 인도 가능하다.

## 운영: 검증·보완 루프 (최대 3회)

```
1. 전 항목 검증 → fail 목록 작성
2. fail 있으면: 보완 → 재검증 (이 회전을 최대 3회까지)
   - 각 회전의 보완 내용을 생성 하네스의 DECISIONS.md D-001에 누적 기록
3. 3회 후에도 fail 잔존 시: 인도는 하되 잔여 fail 항목과 사유를 인도 보고에 명시하고
   사용자 판단으로 넘긴다. fail을 숨기고 인도하는 것만이 금지된다.
```

## 1. 구조 완결성

- [ ] 공통 산출물이 존재한다: harness-spec.json, HARNESS.md, ENVIRONMENT.md, team/TEAM-ARCHITECTURE.md, spec agent마다 team/agents/<role-id>.md, spec skill마다 skills/<skill-id>/SKILL.md, loops/ 3종, recovery/ 2종, ledger/ 3종(journal.jsonl 포함), memory/INDEX.md, budget/, state/state.json
- [ ] `harness-spec.json`이 schema version, 중첩 required/unsupported key, domain/agent/skill/gate ID 유일성, 상대경로, 참조 무결성, DAG, evaluator, approval_gates, limits 계약을 통과한다
- [ ] 템플릿 출처가 D-001에 기록됐다: 로컬 경로 또는 GitHub URL + ref + 실제 commit. resolver의 필수 템플릿 계약을 통과했다
- [ ] **기존 하네스 융화**: 기존 자산이 있으면 `improve|reconcile` 모드, 기준선 validator/evaluator, 파일별 관리 주체, 보존 manifest, delta plan(`unchanged|add|modify-proposed|conflict|approval-required`)이 기록됐다. 삭제·이름 변경·의미 교체는 승인 없이 적용되지 않았다
- [ ] 미사용 축이 있다면 파일 삭제가 아니라 파일 내 "미사용 — 사유" 표기로 처리됐다
- [ ] `grep -rn '{{' <HARNESS_ROOT>` 결과 0건 — 치환 안 된 플레이스홀더 없음
- [ ] "이 대화에서", "위에서 논의한" 류의 세션 의존 표현이 없다 (미래 세션에게 그 대화는 존재하지 않는다)
- [ ] **문서 규율 (원칙 7)**: 100줄을 크게 초과하는 생성 문서가 없다. 있다면 파일 머리에 `<!-- 문서규율 예외: ... -->` 표기가 있고 인덱스(HARNESS.md 파일 맵 또는 하위 인덱스)에 "전문"으로 등재됐다. 확인: `awk 'END{if(NR>120) print FILENAME" ("NR"줄)"}' <각 .md 파일>`

## 2. 축별 실질 검증

- [ ] **실행 팀**: `team/TEAM-ARCHITECTURE.md`가 대상 domain graph, spec handoff DAG, 역할 병합·분리 근거를 설명하며 routing/execution/verification/verdict/defect-counting/improvement capability 합집합이 존재한다
- [ ] **Claude 위임**: 선택 시 spec agent 각각에 `.claude/agents/<namespace>-<role-id>.md`가 있고 파일명과 frontmatter 이름이 일치한다. `read-only` agent는 읽기 도구만 allowlist하고 Write/Edit/NotebookEdit/Bash를 금지하며 plan mode를 사용한다. spec skill 각각에 `.claude/skills/<skill-id>/SKILL.md`가 있다
- [ ] **Codex 위임**: 선택 시 spec agent 각각에 파일명과 같은 name, description, developer_instructions를 가진 파싱 가능한 `.codex/agents/<namespace>-<role-id>.toml`이 있다. `.codex/config.toml`의 max_threads/max_depth가 spec limits 이상이고, spec skill 각각에 `.agents/skills/<skill-id>/SKILL.md`가 있다
- [ ] **root 규칙 병합**: 선택 runtime의 CLAUDE.md/AGENTS.md 관리 블록이 정확히 1개이며 기존 사용자 내용이 보존됐다
- [ ] **adapter parity**: spec agent/skill/evaluator/gate 의미와 선택된 모든 runtime adapter의 ID 집합·handoff가 같다. 각 `skills[].instructions` 공통 SKILL.md와 Claude/Codex 투영본이 byte-identical이며 domain skill도 예외가 아니다
- [ ] **평가**: 주 evaluator가 실제로 실행된다 (`ENVIRONMENT.md`의 검증 커맨드를 직접 1회 실행해 확인). 루브릭형이면 루브릭 표가 채워져 있다
- [ ] **평가 팀 레인**: `team/TEAM-ARCHITECTURE.md`와 `EVAL-LOOP.md`가 evaluator runner의 증거 생성, owner의 판정, defect-counting, improvement owner 책임을 분리한다
- [ ] **호출형 스킬**: 실행·평가·회고 스킬이 spec에서 entry agent/evaluator/improvement owner를 찾아 native agent로 위임하고 고정 역할명을 전제하지 않는다
- [ ] **실행**: 작업 단위 정의가 구체적이고, state.json의 queue에 최소 1개 단위가 evaluator와 함께 들어 있다
- [ ] **회복**: 실패 5분류 각각에 대응 등급(R/S)과 수치(재시도 횟수·백오프·승격 상한)가 적혀 있다. 등급 S = 중지·사용자 피드백 대기가 명시됐다. 게이트 목록이 확정됐다 (없으면 "없음" 명시)
- [ ] **보완**: 트리거 3종의 수치가 확정됐고 state.json의 improve 카운터(`fail_counts` 키 규격 `분류:하위유형`, `units_since_retro`, `coldstart_fail`, `last_retro_targets`)가 초기화돼 있다. EXECUTION-LOOP에 RETRO-CHECK(매 회전 트리거 검사)가 존재한다
- [ ] **자동 보완 연결**: 작업 직후 평가 자동 인계 → fail 사건당 1회 계상 → 반복 실패/평가 공백/콜드스타트 fail의 회고 자동 개시 → spec 선변경 → 전체 adapter 재생성 → parity+콜드스타트+원 evaluator 재검증이 연결된다
- [ ] **불변 조건**: 인터뷰에서 오버라이드가 있었다면 README §불변 조건 5개를 침범하지 않았다
- [ ] **기록**: journal.jsonl에 최초 라인(`session_start` 또는 생성 기록)이 있다. DECISIONS.md에 D-001(초기 구성 결정 + 인터뷰 요약 + 적용 기본값)이 기록됐다
- [ ] **코스트**: 예산 단위·단위당 예산·80%/100% 행동이 확정됐다
- [ ] **메모리 인덱스**: spec `1.1`의 `memory.index`가 `memory/INDEX.md`를 가리키고 `preserve-and-reconcile` 정책과 줄 예산이 있다. 인덱스에 경로·요약·읽기 시점·출처·마지막 검증·상태 열이 있으며 active 경로, 중복 ID/경로, 고아 문서를 검사했다
- [ ] **보존 재검증**: 기존 하네스면 전후 보존 manifest가 일치하고 원 evaluator를 다시 실행했다. 기준선 실패와 새 회귀를 구분해 기록했다

## 3. 콜드스타트 테스트 (원칙 5 — 핵심 관문)

컨텍스트가 없다고 가정하고 HARNESS.md부터 지시된 순서로만 읽은 뒤, 파일 근거로 답하라:

- [ ] 이 하네스의 목적과 현재 진행 단계는? → 근거: HARNESS.md 목적 절 + state.json `phase`
- [ ] 지금 즉시 수행할 다음 행동 하나는? → 근거: state.json `next_action` (비어 있으면 fail)
- [ ] 그 행동의 완료는 무엇으로 판정하나? → 근거: 해당 단위의 evaluator 필드
- [ ] 복합 요청일 때 domain별 실행 팀은 어떤 순서로 동작하나? → 근거: harness-spec.json orchestration + team/TEAM-ARCHITECTURE.md
- [ ] 실패가 반복되면 어디로 환류되나? → 근거: EVAL-LOOP.md 평가 팀 레인 + IMPROVE-LOOP.md 보강 신호
- [ ] 현재 작업에 필요한 지속 메모리를 어디서 선택하나? → 근거: harness-spec.json `memory.index` + memory/INDEX.md

## 4. 인도 보고

사용자에게 다음을 요약해 전달한다:

- [ ] 생성 파일 목록 (트리 형태)
- [ ] 적용된 결정: 인터뷰 답변 + 적용 기본값 + 설계 방향 + domain/agent/skill 토폴로지 + 추상 모델 티어와 runtime별 매핑
- [ ] 기존 하네스면 적용 모드 + delta plan + 보존·흡수·충돌 항목 + memory index 상태
- [ ] 검증·보완 루프 결과: 수행 회전 수, 각 회전의 보완 내용, 잔여 fail (없으면 "없음")
- [ ] 첫 실행 방법: HARNESS.md 시작 프로토콜 + Claude `/<skill-id>` / Codex `$<skill-id>` 실행·평가·회고 호출명
- [ ] 첫 백로그 항목 (예: 검증 스크립트 신설이 필요했다면 그 안내)
