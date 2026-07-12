# ENVIRONMENT — harness-factory 레포

> 모든 커맨드는 복사해서 그대로 실행 가능해야 한다. 설명문으로 적지 않는다.

## 실행 커맨드

| 목적 | 커맨드 | 비고 |
|---|---|---|
| 빌드 | 없음 | 문서 레포 — 빌드 없음 |
| 실행 | 없음 | 문서 레포 — 실행 없음 |

## 검증 커맨드 (evaluator — EVAL-LOOP에서 참조)

| 목적 | 커맨드 | pass 조건 |
|---|---|---|
| 주 검증 | `bash scripts/verify.sh` | exit 0 (U-001 신설 전에는 아래 개별 커맨드) |
| 플레이스홀더 잔존 | `! grep -rn '{{' --include='*.md' --include='*.tmpl' . --exclude-dir=templates --exclude-dir=.git` | 출력 0건 |
| 문서 규율 | `find . -name '*.md' -not -path './.git/*' -exec awk 'END{if(NR>120) print FILENAME" ("NR"줄)"}' {} \;` | 예외 표기 없는 초과 0건 |

## 디렉토리 맵 (대상 프로젝트)

```
harness-factory/
├── README.md          # 구성자 가이드북 (진입점, 불변 조건 포함)
├── CHECKLIST.md       # Phase 4 검증
├── principles/        # 원칙 7편
├── interview/         # QUESTION-BANK.md
├── templates/         # 뼈대 .tmpl
└── examples/          # minimal(밀도 기준), self-improve(이 하네스)
```

## 기존 오프로딩 자산 (재발명 금지 — 원칙 3)

| 자산 | 위치 | 용도 |
|---|---|---|
| 없음 (스크립트 부재) | — | CHECKLIST.md의 인라인 커맨드가 유일 — U-001에서 scripts/verify.sh로 묶는다 |

## 금지사항

- main 브랜치 직접 push 금지 (작업 브랜치 사용)
- README §불변 조건 5개를 침범하는 개정 금지
- 게이트 대상 단계(산출물 계약 변경, 불변 조건 문구 수정)는 인간 승인 없이 수행 금지
