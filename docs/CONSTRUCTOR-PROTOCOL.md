# CONSTRUCTOR-PROTOCOL — 구성자(LLM)용 하네스 생성 규약

이 문서는 `build-harness` 스킬이 실행할 LLM용 지시문이다. 구성자는 대상 프로젝트를 분석해 런타임 중립 정본을 먼저 만들고, 그 정본에서 Claude와 Codex의 네이티브 호출 어댑터를 생성한다.

스킬은 먼저 동봉된 `scripts/resolve_factory.py`로 `FACTORY_ROOT`를 확정한다. 로컬 템플릿이 없을 때만 공식 GitHub 저장소의 지정 ref를 캐시에 가져오며, resolver가 필수 파일 계약을 검증한 경로만 사용한다. 사용한 경로 또는 URL·ref·commit은 D-001에 남긴다.

## 1. 원칙 로드와 자료 수집

- `README.md`, `principles/` 전체, `interview/QUESTION-BANK.md`, `CHECKLIST.md`를 읽는다.
- 대상 프로젝트의 README·docs, 빌드/테스트/CI 설정, 기존 규칙 파일, 디렉토리 구조, 커밋 이력·이슈·로그 등 읽을 수 있는 자료를 수집한다.
- 수집 목적은 (a) 결정적 evaluator 후보 발굴, (b) 인터뷰 질문 소거, (c) 하네스 목적 가설 수립, (d) 도메인 경계와 기존 제어탑·skill·agent·hook 후보 식별이다.
- `harness:harness`의 장점인 제어탑 → 도메인 coordinator → 전문 실행 → 평가/보강 환류를 일반화한다. 역할 이름과 수를 복사하지 않고 대상의 디렉터리·서비스·데이터 계약·검증 책임에서 도출한다.
- 기존 `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.agents/`, `.codex/`는 덮어쓸 대상이 아니라 병합할 사용자 구성이다.
- 목적 가설은 반드시 사용자 입력으로 확정한다. 수집 결과를 남길 때는 원문 덤프가 아니라 인덱스+요약으로 남긴다.

## 2. 인터뷰

- `interview/QUESTION-BANK.md`의 1차 핵심 4문항을 우선 질의한다. 코드베이스에서 이미 답을 확인한 것은 묻지 않는다.
- 필요할 때만 2차 보완 질문을 추가하고, 전체 질문은 최대 2회 배치로 끝낸다.
- 복합 프로젝트·장기 작업·경계면 위험이 보이면 Q11의 도메인·팀·평가·런타임 질문을 사용한다. 사용자가 "알아서"라고 하면 필수 capability backbone과 Claude+Codex 양쪽 어댑터를 적용한다.
- 사용자가 “알아서 해줘”라고 하면 질문 은행의 기본값을 적용하되, 적용한 기본값을 인도 보고에 명시한다.

## 3. 설계 결정 확정

- 인터뷰 답변을 `templates/`의 치환 필드와 `schema/harness-spec.schema.json`에 매핑한다.
- 설계 방향은 기본값(코스트 기반 자동검증·보완)을 우선 적용하되 사용자 요청이 다르면 오버라이드한다.
- 먼저 대상의 domain graph를 확정한다. 각 domain은 경로와 coordinator를 갖고, 교차 경계는 명시적 handoff로 연결한다.
- agent/skill 토폴로지를 확정한다. 역할 수는 고정하지 않지만 routing, execution, verification, verdict, defect-counting, improvement capability 합집합은 반드시 존재한다. 복합 경계에서는 impact-analysis와 coordination을 분리한다.
- 각 역할에는 lane, capabilities, domains, access, `fast|balanced|deep` 모델 티어를 배정한다. Claude/Codex의 구체 모델명은 공통 명세에 넣지 않고 adapter 렌더링에서 매핑한다.
- 모든 인간 승인 조건은 `approval_gates`의 id, trigger, owner, required_action으로 명시한다. 승인 게이트가 없으면 빈 배열로 확정하고 adapter 자유 텍스트에만 별도 게이트를 만들지 않는다.
- Claude agent 권한은 `access`에서 명시적으로 매핑한다. `read-only`는 `tools: Read, Grep, Glob`, `disallowedTools: Write, Edit, NotebookEdit, Bash`, `permissionMode: plan`을 사용한다. `workspace-write`도 필요한 도구만 allowlist하고 기본 permission mode를 유지하며, `bypassPermissions`는 생성하지 않는다.
- 정상 실행 handoff는 DAG로 만든다. 재시도와 개선 환류는 DAG에 역방향 edge를 넣지 않고 loops 계약으로 표현한다.
- 실행자는 작업 산출물을 만들고 evaluator runner가 원본 증거를 생성하며 evaluator owner가 pass/fail을 판정한다.
- 확정한 결정과 근거를 생성될 하네스의 `ledger/DECISIONS.md` D-001에 기록한다.

## 4. 뼈대 인스턴스화

- `templates/harness-spec.json.tmpl`을 먼저 렌더링해 `harness/harness-spec.json`을 만든다. JSON parse, 중첩 required/unsupported key, ID 중복, 상대경로, 참조, DAG, approval gate를 확인한 뒤 다음 단계로 간다.
- YAML/TOML의 동적 scalar는 값 조각을 escape하지 않는다. 전체 값을 JSON string으로 한 번 직렬화해 `*_JSON` placeholder에 넣고, template에서 placeholder 주위에 따옴표를 다시 붙이지 않는다. 이 JSON string subset은 YAML과 TOML 양쪽에서 안전하며 colon, hash, quote, newline을 보존한다.
- 공통 `templates/`를 렌더링한다. `templates/team/agents/AGENT.md.tmpl`은 spec agent마다 한 번씩 `team/agents/<role-id>.md`로 생성한다.
- spec의 모든 skill은 `skills[].instructions`가 가리키는 `harness/skills/<skill-id>/SKILL.md`를 공통 정본으로 만든다. `templates/adapters/shared/SKILL.md.tmpl`을 skill마다 렌더링하고, 필수 실행·평가·회고 본문은 `SKILL-TEMPLATE.md`의 preset을 사용할 수 있으며 임의 domain skill도 같은 generic template으로 만든다.
- `state/state.json`에는 최소 1개 queue item, evaluator, 비어 있지 않은 `next_action`, 초기화된 `improve` 카운터를 둔다.
- `ledger/journal.jsonl`에는 최초 생성 또는 `session_start` 라인을 둔다.
- Claude adapter: 기존 `CLAUDE.md`의 관리 블록 밖을 보존하고, 각 공통 skill 정본을 `.claude/skills/<skill-id>/SKILL.md`로 byte-identical copy하며 agent별 `.claude/agents/<namespace>-<role-id>.md`를 만든다.
- Codex adapter: 기존 `AGENTS.md`와 `.codex/config.toml`을 구조적으로 병합하고, 같은 공통 skill 정본을 `.agents/skills/<skill-id>/SKILL.md`로 byte-identical copy하며 agent별 `name`·`description`·`developer_instructions`를 가진 `.codex/agents/<namespace>-<role-id>.toml`, 전역 agent limits를 만든다.
- 두 agent adapter는 실행 의미를 복제하지 않는 thin wrapper로 렌더링한다. Claude 본문과 Codex `developer_instructions`에는 공통 spec·역할 파일 경로와 그 정본을 따르라는 고정 문장만 두며 `ROLE_INSTRUCTIONS`를 다시 삽입하지 않는다.
- 기존 관리 블록은 같은 namespace 블록을 교체해 idempotent하게 갱신한다. 사용자 문장이나 unrelated TOML table을 삭제하지 않는다. 충돌하는 agent ID나 TOML 필드가 있으면 자동 덮어쓰지 않고 보고한다.

## 5. 검증·보완 루프

- `python <FACTORY_ROOT>/scripts/validate_runtime_neutral.py <target>`와 `CHECKLIST.md` 전 항목을 검증한다.
- 핵심 관문은 콜드스타트 테스트다: `HARNESS.md`부터 지시된 순서로만 읽고 목적/현재 단계, 즉시 다음 행동, 완료 evaluator를 파일 근거로 답한다.
- 팀 구조 관문도 수행한다: spec과 `TEAM-ARCHITECTURE.md`만 읽고 domain graph, 실행 흐름, evaluator runner/owner, 실패가 improvement owner로 환류되는 경로를 답할 수 있어야 한다.
- 자동 연결 관문도 수행한다: 실행 직후 평가 스킬 자동 인계, fail 사건당 1회 카운트, 임계값·평가 공백·콜드스타트 fail의 회고 자동 개시, 제안서 자동 적용, 콜드스타트+원 evaluator 재검증이 이어져야 한다.
- Claude/Codex adapter의 agent ID·skill ID 집합이 spec과 같아야 한다. Claude frontmatter 이름과 access별 tools/disallowedTools/permissionMode, Codex agent TOML의 name/description/instructions, global limits, root 관리 블록, native skill 경로를 검증한다. 모든 runtime skill은 `skills[].instructions` 공통 파일과 byte-identical이어야 한다.
- 한쪽 adapter만 보완하지 않는다. 공통 의미가 바뀌면 spec → 공통 문서 → 모든 선택 adapter 순으로 재생성하고 parity를 다시 확인한다.
- fail이 있으면 보완 후 재검증한다. 이 검증→보완 회전은 최대 3회까지 허용한다.
- 각 회전에서 고친 내용은 생성될 하네스의 `ledger/DECISIONS.md` D-001에 누적한다.
- 3회 후에도 fail이 남으면 인도를 중단하지 말고 잔여 fail과 사유를 사용자에게 명시한다. fail 은폐만 금지된다.

## 6. 인도 보고

사용자에게 다음을 요약한다.

- 생성 파일 목록.
- 적용 결정: 인터뷰 답변, 적용 기본값, domain graph, 동적 agent/skill 토폴로지, 추상 모델 티어와 런타임 매핑, 위임/폴백 모드, 템플릿 출처·ref·commit.
- 검증·보완 루프 결과: 회전 수, 보완 내용, 잔여 fail.
- 첫 실행 방법: 새 세션에서 `<HARNESS_ROOT>/HARNESS.md`를 읽고 시작 프로토콜을 따르거나, 설치된 실행 스킬을 호출하도록 안내한다.
- 스킬을 설치했다면 Claude `/<skill-id>`와 Codex `$<skill-id>` 형식으로 실행·평가·회고 호출명을 각각 안내한다.

## 7. 불변 조건

1. evaluator 없는 작업 단위는 실행하지 않는다.
2. 평가 기록 없는 pass 처리는 없다.
3. 인간 승인 게이트는 승인 없이 통과하지 않는다.
4. `state.json.next_action`은 비워두지 않고, `journal.jsonl`은 append-only로만 다룬다.
5. fail은 검증·인도·보고에서 숨기지 않는다.
6. adapter는 정본이 아니다. 의미 변경은 `harness-spec.json`에 먼저 반영한다.
7. 선택된 런타임 사이에서 역할·skill·evaluator·gate 의미가 달라지지 않는다.
