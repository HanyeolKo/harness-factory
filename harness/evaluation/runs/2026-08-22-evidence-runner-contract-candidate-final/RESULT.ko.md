# 생성 하네스 개선 결과

판정은 `improved`다. 초기 하네스에서는 read-only `evidence-runner`가 실행과 증거 저장까지 맡아 Claude와 Gemini에서 완료할 수 없었다. candidate는 request와 validation을 `evidence-runner`, command 실행과 증거 저장을 main orchestrator, verdict를 `contract-evaluator`에 분리했다.

실측에서 provider-neutral 실행 가능 경로는 `0/3`에서 `3/3`, required manifest field는 `0/12`에서 `12/12`로 개선됐다. 정상 종료와 approval-blocked 경로 모두 request hash와 artifact hash가 일치했고 별도 validation result가 `contract-evaluator`로 handoff했다. workspace-write agent 수는 `2`, 전체 agent 수는 `6`, handoff 수는 `4`로 유지돼 permission과 topology regression은 없었다.

Native Claude/Gemini end-to-end 실행과 token·시간·비용 raw telemetry는 측정하지 못했다. 따라서 이 판정은 evidence contract의 실행 가능성과 무결성 개선 범위에 한정한다.
