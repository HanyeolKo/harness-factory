# Recovery Playbook

Retry transient failures at most three times with 2s, 4s, and 8s backoff. Structural failures require diagnosis and a changed attempt. Stop for unclear scope, retry exhaustion, total budget exhaustion, or an approval gate. Record stable `<class>:<subtype>` keys; three occurrences trigger full evaluation but do not authorize improvement.
