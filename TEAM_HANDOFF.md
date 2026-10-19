# Four-person role handoff and explanation guide

**Do not claim teammates independently wrote work they did not write.** Assign responsibility for review, understanding, testing, and presenting each role; update authorship/contribution notes honestly if required by the instructor.

## Person A — Knowledge & Memory Archivist
Owns and validates `01_Alignment_Brief.md`. Explain why *Euthyphro* seeks definitions, why Galilean dialogue involves contrasting perspectives, and why role prompting can still be biased. Run and record at least one genuine LLM test; fill the uncompleted model comparison rubric.

**Likely question:** How is Socratic discovery different from persuasion?  
**Suggested explanation:** Discovery tests and revises a claim until it withstands scrutiny or reaches aporia. Persuasion brings competing arguments into dialogue and tests their comparative force.

## Person B — Protocol & Interface Specialist
Owns and validates `02_Socratic_Protocol_Map.md`. Explain the states CLAIM, PROBE, RESPONSE, AUDIT, REFINE, and END. Walk through an example and explain why no contradiction means continuing rather than fabricating a revision.

**Likely question:** What stops the loop?  
**Suggested explanation:** Explicit aporia, or a configured round limit; only a human-reviewed result can be described confidently as a well-refined definition.

## Person C — Security & Ethical Navigator
Owns and validates `03_Galilean_Sandbox.md`. Explain why the three personas have different goals, the AI-weight-release thought experiment, and how safety and fairness are audited.

**Likely question:** Does multi-agent debate eliminate bias?  
**Suggested explanation:** No. It surfaces disagreements but all personas can still share the same model biases; outputs require human evaluation.

## Person D — Core Architect
Owns and validates `04_dialogic_engine.py`, `README.md`, and the authentic `05_Execution_Transcript.txt`. Explain API authentication, system prompts, program entry point, finite loops, output capture, and error handling. Must personally run the program and confirm the GitHub repository layout.

**Likely question:** Are there actually three different models?  
**Suggested explanation:** No; three distinct persona instructions generate separate sequential calls using the same model API, which satisfies three role-based agents while being simple to reproduce.

## All four sign-offs

- [ ] Architect — code executed, repository organized, transcript checked
- [ ] Protocol Specialist — transitions and termination reviewed
- [ ] Archivist — philosophical analysis and prompts reviewed
- [ ] Navigator — scenario and safety audit reviewed

Record each person's comments and the date they verified their part. Sign off only on work genuinely reviewed.
