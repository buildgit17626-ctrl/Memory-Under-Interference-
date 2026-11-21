# Unattended M1 completion

One driver resumes registered M1, then automatically evaluates saved responses
and verifies records. A generation error or incomplete1040-call schedule stops
the chain. This is orchestration, not a new experiment. No R1 starts.

Commands and outputs: experiments.finish_m1_sprint --hwinfo-log PATH;
results/utilisation/m1-full/SPRINT_STATUS.json and sprint-phases.log. Generation
and evaluation run at separate times. The parent stops only its owned child
tree at its overall deadline and preserves all journals for recovery.

Five questions:
1. When does scoring begin?
2. What happens after a generation hard stop?
3. Why is the generation count checked before scoring?
4. What survives an overall deadline?
5. Why doesn't automatic chaining authorise unfinished R1 inputs?

Assumptions: user supplies the active HWiNFO path, AC/Best performance and an
idle machine; there is no duplicate runner. Finishing early is acceptable.
