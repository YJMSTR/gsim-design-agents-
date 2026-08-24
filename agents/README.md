# Optional agent definitions

`k3.md` is an omp agent definition for consulting the k3 model on hard
research/judgment questions (route ranking, mechanism analysis,
falsification-experiment design). Install into the user's omp agent
registry (`~/.omp/agent/agents/`), then call through the harness agent
pipeline (`agent(prompt, { agent: "k3" })`). Read-only; treat output as
advisory input and cross-check cited numbers against the ledger. See
`prompts/k3-consult.md` for the working pattern.
