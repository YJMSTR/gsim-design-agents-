# GSim Design Agents Documentation

This directory is organized in three authority layers, following the
documentation-authority model of [PolyArch/loom](https://github.com/PolyArch/loom):

- `spec-*.md` files own normative **WHAT**: the current workflow contracts.
- `rationales/` owns non-normative **WHY**: the incidents and rejected
  alternatives behind each contract, without duplicating it.
- `scripts/` and `templates/` own **HOW**: the executable realization of the
  contracts.

When a document, a rationale, and a script disagree, the specification is the
only authority; the inconsistency must be fixed rather than interpreted as an
alternate contract.

## Ownership map

| Contract | Owner |
|---|---|
| End-to-end optimization loop, task contract fields, non-interference | `agent-flow.md` |
| Measurement protocol: sessions, instruments, floors, probe hygiene | `spec-measurement-protocol.md` |
| Evidence records: file ownership, ledger schemas, outcome vocabulary, artifact identity | `spec-evidence-records.md` |
| Why the protocol rules exist (each rule's incident) | `rationales/measurement-protocol.md` |
| Why the evidence schemas and vocabulary exist | `rationales/evidence-records.md` |
| Why documentation is split this way | `rationales/documentation-authority.md` |
| Filled contract for the current long-running task | `task-contract.md` (instance document) |
| Existing-worktree orientation checklist | `gsim-worktree-handoff.md` |
| Pattern -> cause -> fix diagnosis handbook | `rtl-diagnosis-playbook.md` |

## Revision rule

When a rule changes, the owning specification is changed to state the one
current contract. The corresponding rationale records what incident or
argument invalidated the old rule. A rationale never preserves an old rule as
an implementable alternative, and a specification never carries the
chronological argument that produced it.
