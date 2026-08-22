# K3 Consultation Prompt (optional external reviewer)

For hard research/judgment questions (route ranking, mechanism analysis,
model discrimination design), consult the k3 model through the harness
agent pipeline (definition lives in the user's omp agent registry as
`k3`; read-only, tools: read/grep/glob/web_search). Pattern that worked:

1. Give it grounding: file paths to campaign reports + the measured facts
   (never let it assume numbers).
2. Ask for: mechanism, failure-mode analysis, falsification experiment,
   and an EV ranking with the ranking criterion named.
3. Treat its output as advisory input to YOUR judgment; cross-check every
   number it cites against the ledger before it enters a record.

Incident: consulting via raw CLI bypasses the harness context/limits
tracking - use the agent pipeline instead.
