# Terminal supervisor implementation

Build after the execution preregistrations. Run only from explicit terminal
launch, with frozen inputs. Each batch alternates generation and offline
scoring so scoring is absent from power-measurement windows. Bound batches to
100 requests to collect end baselines and check drift. Log each attempted
request before contacting Ollama and preserve envelopes before interpretation.

Five retries means six attempts including the initial call. Count completed
logical API/infrastructure failures, not incorrect generated programs, for the
3% call-failure stop. Energy coverage uses the last 20 completed logical calls;
halt when fewer than 18 have valid post-load coverage. These operational
interpretations are disclosed in the operating guide. Unknown in-flight
attempts after process death consume retry budget. Do not retry input
truncation or completed model answers based on correctness.

Supervisor consumes a frozen pipeline file with E0 and conditional M3 plans.
A missing registration, dataset pin, independent calibration policy or M3
stimulus grid stops preparation with an actionable CHECKPOINT.md. It must
never guess a stimulus or silently bypass the E0 scorer anomaly.
