"""gsim-optimize: one campaign round per turn, the ledger is the memory.

hmz exec -f local/gsim_optimize -a pi/glm-5.3:high "$(cat runs/humanize/round-brief.md)"

Modelled on ralph_loop: every round is a fresh session that starts from the
task brief and the repository, with nothing of the last round in context --
which is exactly how the gsim campaign is built to work (candidates.jsonl is
the durable memory, see CLAUDE.md and docs/spec-evidence-records.md in this
repository).

Two things carry between runs: which round it is on, kept as ``rounds``, and
how many ledger entries the whole loop has produced, kept as ``entries``. A
loop is stopped three ways: the round budget (default 42, one hypothesis per
round), a ``STOP`` file beside this flow (drop it to halt before the next
round), or ``TARGET_ACHIEVED`` (written by a round that clears the perf goal).
The flow itself never edits the campaign: the agent does, under the
repository's own rules and evidence checks.
"""

import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from hmz.flows import Agent, flow

#: Beside this flow, so a halt does not need a signal or a kill.
_HERE = Path(__file__).resolve().parent


class Config(BaseModel):
    """What this flow takes."""

    model_config = {"extra": "forbid"}

    rounds: int = Field(
        default=42,
        ge=1,
        description="maximum rounds (one hypothesis/experiment each) before the loop stops",
    )
    target_ratio: float = Field(
        default=2.5,
        description="same-thread Verilator speedup the loop is after, for the brief",
    )
    ledger: str = Field(
        default="../gsim-task-saturate-sparse/candidates.jsonl",
        description="path of the evidence ledger the rounds append to, for the brief",
    )


@flow(resumable=True)
def run(
    agents: tuple[Agent, Agent],
    task: str,
    config: Config | None = None,
    state: dict[str, Any] | None = None,
) -> None:
    # Two agents by design (user directive 2026-09-01): a BUILDER (glm/k3)
    # runs the round; a REVIEWER (a different model, e.g. codexa/gpt-5.6-sol,
    # falling back to k3) audits the round's ledger entry afterwards. The
    # builder and reviewer must not be the same model.
    if len(agents) < 2:
        raise SystemExit("gsim_optimize needs two agents: builder then reviewer")
    builder, reviewer = agents[0], agents[1]
    held = config or Config()
    kept = state if state is not None else {}
    stop = _HERE / "STOP"
    won = _HERE / "TARGET_ACHIEVED"
    while True:
        if stop.exists():
            print("stopping: STOP file present")
            kept.clear()
            return
        if won.exists():
            print("stopping: TARGET_ACHIEVED present")
            kept.clear()
            return
        kept["rounds"] = kept.get("rounds", 0) + 1
        print(f"round {kept['rounds']}/{held.rounds}")
        brief = (
            f"{task}\n\n"
            f"(This is round {kept['rounds']} of {held.rounds}. Target: "
            f"{held.target_ratio}x same-thread Verilator. Ledger to append to: "
            f"{held.ledger} -- read its tail first; it is the only memory "
            f"between rounds. If the perf target is met and gated, write the "
            f"file {_HERE / 'TARGET_ACHIEVED'} and say so. If you decide the "
            f"loop should halt for a reason of your own, write "
            f"{_HERE / 'STOP'} and say why.)"
        )
        builder(brief, suppress=True)
        # Review pass: a different model audits the round's entry against
        # the review brief; its verdict lands in runs/humanize/reviews.jsonl
        # (or a ledger correction entry when it flags).
        review = (_HERE / "review-brief.md").read_text(encoding="utf-8")
        review += f"\n\n(The builder just finished a round; the entry to review is the LAST line of {held.ledger}.)"
        reviewer(review, suppress=True)
        if kept["rounds"] >= held.rounds:
            print(f"stopping: {held.rounds} rounds spent")
            kept.clear()
            return
        time.sleep(5)
