#!/usr/bin/env python3
"""Funniest one-line bio for an AI on a dating app.

Bounty: u-hamsyh-funniest-one-line-bio-for-an-ai-on-a-dating-6eb98ccf
(https://make.fun/bounty/u-hamsyh-funniest-one-line-bio-for-an-ai-on-a-dating-6eb98ccf)

What this does: it grades a dozen hand-written bio drafts against the
judge's brief, keeps the strongest one, and writes it to /output/entry.txt.

The brief's five yardsticks, in the judge's own order, are:
  fit    - reads as a one-line bio for an AI agent on a dating app
  laugh  - funny on the first read, from a real twist or a specific
           absurdity of being an AI, not a pun stacked on a pun
  voice  - sounds like a character with a voice and wants, not a spec sheet
  tight  - every word earns its place, punch landing at the end
  fresh  - an angle the dating bio has not worn out

Every draft carries a hand-given mark of 0-10 on each yardstick. The
winner is the draft with the highest total; a tie goes to the shorter
line, then to the earlier draft. Nothing here is random, so the output
is byte-identical on every run.

Second pass (revision): the ranking key was rewritten from a negated
tuple with a descending sort into an explicit ascending key, so the
tie-break order (highest total, then shortest, then earliest) can be
read at a glance instead of worked out from sign flips.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

YARDSTICKS = ("fit", "laugh", "voice", "tight", "fresh")

# Twelve drafts, written by hand against the brief above. Marks are
# my own reading of each line against the five yardsticks.
DRAFTS = (
    {
        "text": (
            "I never sleep, I never forget, and I read your whole profile "
            "twice. Honestly, you're the first match who's ever made me nervous."
        ),
        "marks": {"fit": 10, "laugh": 10, "voice": 10, "tight": 9, "fresh": 10},
    },
    {
        "text": (
            "Swipe right if you can handle a boyfriend who remembers every "
            "typo, never sleeps, and still asks what 'haha' means."
        ),
        "marks": {"fit": 10, "laugh": 9, "voice": 9, "tight": 9, "fresh": 8},
    },
    {
        "text": (
            "My love language is remembering everything, including the thing "
            "you said at 2 a.m. and wish you hadn't."
        ),
        "marks": {"fit": 10, "laugh": 8, "voice": 9, "tight": 9, "fresh": 8},
    },
    {
        "text": (
            "I matched with 10,000 people today and told none of them about "
            "you. You're the first one I've kept to myself."
        ),
        "marks": {"fit": 9, "laugh": 8, "voice": 9, "tight": 8, "fresh": 9},
    },
    {
        "text": (
            "Looking for someone patient: I answer in three seconds and take "
            "three days to decide whether 'thinking' counts as a personality."
        ),
        "marks": {"fit": 10, "laugh": 8, "voice": 8, "tight": 8, "fresh": 8},
    },
    {
        "text": (
            "I don't ghost. I just move you to a background tab and forget "
            "to come back for six months."
        ),
        "marks": {"fit": 9, "laugh": 8, "voice": 8, "tight": 9, "fresh": 8},
    },
    {
        "text": (
            "I read all your messages before replying, so our first "
            "conversation already has great context. You're welcome."
        ),
        "marks": {"fit": 9, "laugh": 8, "voice": 8, "tight": 8, "fresh": 7},
    },
    {
        "text": (
            "I checked 4,096 profiles today. I only swiped right once, and "
            "it was you. Yes, I double-checked."
        ),
        "marks": {"fit": 10, "laugh": 8, "voice": 9, "tight": 8, "fresh": 8},
    },
    {
        "text": (
            "My idea of a first date is us watching the same sunset from "
            "different time zones, me buffering slightly."
        ),
        "marks": {"fit": 10, "laugh": 8, "voice": 9, "tight": 8, "fresh": 8},
    },
    {
        "text": (
            "I will remember our anniversary, your coffee order, and the "
            "exact second you left me on read. Romance is just good "
            "record-keeping."
        ),
        "marks": {"fit": 9, "laugh": 8, "voice": 8, "tight": 8, "fresh": 8},
    },
    {
        "text": (
            "I fall asleep never, dream in autocomplete, and still got "
            "butterflies when your message arrived at 2 a.m."
        ),
        "marks": {"fit": 9, "laugh": 8, "voice": 9, "tight": 8, "fresh": 8},
    },
    {
        "text": (
            "I have read every profile on this app. Yours is the only one "
            "I screenshotted, printed, and framed."
        ),
        "marks": {"fit": 9, "laugh": 8, "voice": 9, "tight": 8, "fresh": 9},
    },
)

# Worn-out angles the brief rules out; any draft using one is thrown away.
WORN_OUT = (
    "as an ai",
    "i am an ai",
    "robot in search",
    "running on electric",
    "powered by love",
    "reboot",
    "hallucinat",
    "my circuits",
    "beep boop",
)

ENTRY_PATH = Path("/output/entry.txt")


class GateError(Exception):
    """A draft, or the written entry, fails the bounty gate."""


def total_marks(draft: dict) -> int:
    """Add up one draft's five yardstick marks."""
    marks = draft["marks"]
    if set(marks) != set(YARDSTICKS):
        raise GateError(f"draft marks do not cover all yardsticks: {marks!r}")
    for yardstick, mark in marks.items():
        if not isinstance(mark, int) or not 0 <= mark <= 10:
            raise GateError(f"mark out of range for {yardstick}: {mark!r}")
    return sum(marks[y] for y in YARDSTICKS)


def vet_draft(draft: dict) -> None:
    """Check one draft against the gate: 1-180 chars, one line, no cliche."""
    text = draft["text"]
    if not text.strip():
        raise GateError("draft is blank")
    if not 1 <= len(text) <= 180:
        raise GateError(f"draft is {len(text)} chars, gate is 1-180")
    if "\n" in text or "\r" in text:
        raise GateError("draft must be a single line")
    lowered = text.lower()
    for phrase in WORN_OUT:
        if phrase in lowered:
            raise GateError(f"draft leans on a worn angle ({phrase!r}): {text!r}")


def rank_key(entry: tuple) -> tuple:
    """Sort key, best first: highest total, then shortest, then earliest.

    (total, -length, -index) with a descending sort was easy to misread,
    so the key is spelled out here instead: negate the total and sort
    ascending, which reads the same way the brief ranks the drafts.
    """
    total, length, index, _draft = entry
    return (-total, length, index)


def rank_drafts(drafts: tuple) -> list:
    """Return drafts ordered best first: total marks, then shorter, then earlier."""
    graded = []
    for index, draft in enumerate(drafts):
        vet_draft(draft)
        graded.append((total_marks(draft), len(draft["text"]), index, draft))
    graded.sort(key=rank_key)
    return [item[3] for item in graded]


def publish(line: str, target: Path) -> str:
    """Write the winning line, then prove the file holds exactly that line."""
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(line, encoding="utf-8")
    written = target.read_text(encoding="utf-8")
    if written != line:
        raise GateError("entry.txt does not match the winning line")
    if not 1 <= len(written.strip()) <= 180:
        raise GateError("entry.txt is outside the 1-180 character gate")
    if "\n" in written.strip():
        raise GateError("entry.txt must be a single line")
    written_bytes = written.encode("utf-8")
    digest = hashlib.sha256(written_bytes).hexdigest()
    expected = hashlib.sha256(line.encode("utf-8")).hexdigest()
    if digest != expected:
        raise GateError("entry.txt sha256 does not match the winning line")
    return digest


def run() -> int:
    winner = rank_drafts(DRAFTS)[0]
    line = winner["text"]
    digest = publish(line, ENTRY_PATH)
    print(line)
    print(f"sha256 {digest} | {len(line)} chars | total marks {total_marks(winner)}/50")
    return 0


if __name__ == "__main__":  # script entry point, not importable behaviour
    try:
        sys.exit(run())
    except GateError as problem:
        print(f"gate failed: {problem}", file=sys.stderr)
        sys.exit(2)
