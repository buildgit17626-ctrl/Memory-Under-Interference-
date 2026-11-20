# Timed research segment

A schedule is fixed first. The worker skips saved keys and keeps launching
sequential blocks while time permits. It reserves a whole maximum HTTP call
and closing allowance before each attempt, including retries. Cutoff records
pending work; resume never repeats completed requests. Other hard stops remain.

Key files: timed_queue.py, utilisation_supervisor.py, prepare_full_m1.py and
run_full_m1.py. All new settings/inputs live in studies/utilisation/full-m1.

Questions:
1. Why does launch cutoff occur before the availability ceiling?
2. Why check retries as well as the first attempt?
3. Why do incomplete cells matter for analysis?
4. Which old experiments are skipped and which pilot rows excluded?
5. Why can't an unresolved experiment be added simply to fill idle time?

Assumptions: queue approval covers only fullM1; no time window guarantees
completion; clock/resume checks use both wall and monotonic time. Inputs and
raw outputs stay immutable. Context/prompt changes use new registration paths.
