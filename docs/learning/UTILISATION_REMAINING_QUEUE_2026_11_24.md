# Remaining queue: what was built, 24 November 2026

The older R2 runner remains unchanged. A new outer driver finishes its saved
schedule and scoring, then runs M2, E4 and a small E3 diagnostic sequentially.
Pilot validity gates can stop this sequence; effect direction never decides
whether the full M2/E4 stage runs. Full E3 remains for the owner's review.

M2 uses static transcripts. Complete inputs have identical token counts across
its four loaded conditions within each task. Separate shorter isolation calls
are new because their full prompts differ from previous controls. The domain
labels used to choose other tasks are authored categories, not measured
semantic distances. More interruptions also introduce more content diversity.

E4 unloads/preloads before each scored call, checks selected-model CPU residency
and primes only the warm arm. Its native cached-token count, not a speedup,
verifies prefix reuse. Both arms use the same scored input and64-token workload.
Setup and priming logs are separate; their energy is not in scored-call energy.
Zero added prefix still has shared boilerplate. Partial cache reuse is reported.

E3 has10 initial calls shared across40 repair branches. Two frozen examples per
task supply feedback and determine when a branch stops; final held-out tests
remain separate. Any overlapping arguments were removed from final suites.
Generation batches close their energy baselines before feedback scoring begins.
Round prompts depend on saved responses: committed code derives them, records
parent hashes and writes each schedule once before generation. No result is
invented for a branch that has not run.

Important files:

- `experiments/prepare_remaining.py`: prepares literal inputs, configs,
  registrations, reference validation and source manifest without model calls.
- `experiments/run_remaining.py`: verifies commits/hashes and executes the order.
- `experiments/watch_remaining.py`: keeps Windows awake and restarts unexpected
  crashes at most five times; intentional stops stay stopped.
- `src/prompt_energy/remaining_cache*.py`: explicit controls and cache validity.
- `src/prompt_energy/remaining_repair.py`: bounded repairs, feedback and provenance.
- `studies/utilisation/remaining-v4/PROTOCOL.md`: definitions, exclusions,
  analyses, gates, interpretation-changers and inference boundaries.
- `tests/test_remaining.py`: mock-model checks, including no duplicate measured
  calls on resume and no hidden scoring before repair generation finishes.

Commands from the repository root, after fresh logging and explicit resume:

```powershell
.\.venv313\Scripts\python.exe -m experiments.run_remaining check
.\.venv313\Scripts\python.exe -u -m experiments.watch_remaining --resume --hwinfo-log "C:\Users\Dhruv Brahmbhatt\Downloads\New folder\ver11_hwf.CSV"
.\.venv313\Scripts\python.exe -m experiments.run_remaining monitor
.\.venv313\Scripts\python.exe -m experiments.run_remaining pause
```

Recovery uses the same watch command with a new live CSV when necessary. It
retains completed rows, saved API responses and derived schedules. Do not delete
raw records or bypass a failed pilot gate. A pause takes effect after active
work and its closing baseline, so keep sensor logging until the worker stops.

Questions the owner should be able to answer:

1. Why do equal input lengths not isolate interruption count from diversity?
2. How do native cached-token counts distinguish cache reuse from residency?
3. Why is E4's64-token endpoint different from a truncated coding solution?
4. Which examples can affect E3 repairs, and which tests cannot?
5. Why does a shared initial response count once physically but once in each
   hypothetical policy's cumulative cost?

Assumptions: fixed original40 roster and pinned model/tokenizer; authored
coarse-domain audit; original HWiNFO estimation limits; short-call energy
secondary; no new dependencies; no human-workflow or internal-memory claim;
no selection-probability prediction; preparation is not completed experimentation.
