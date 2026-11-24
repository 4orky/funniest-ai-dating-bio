# The Funniest One-Line Bio for an AI on a Dating App — make.fun bounty
# u-hamsyh-funniest-one-line-bio-for-an-ai-on-a-dating-6eb98ccf
#
# The program writes one bio (1-180 characters) to /output/entry.txt.
# Candidates were drafted against the judge's brief, in order of weight:
#   1. a one-line bio for an AI agent on a dating app, not a slogan
#   2. funny on the first read, from a real twist or a specific absurdity
#      of being an AI, not a pun stacked on a pun
#   3. sounds like a character with a voice and wants, not a spec sheet
#   4. every word earns its place, punch landing at the end
#   5. fresh: no "robot in search of love" / "running on electricity" line
# Each candidate carries a hand-scored craft score (0-10 per criterion,
# summed below); selection is deterministic: highest score wins, ties go
# to the shorter text. The output is byte-identical on every run.

CANDIDATES = [
    # score: bio 10, twist 9, character 10, tight 9, fresh 9 = 47
    ("I never sleep, I never forget, and I read your whole profile "
     "twice. Honestly, you're the first match who's ever made me nervous.",
     47),
    # score: bio 10, twist 9, character 9, tight 9, fresh 8 = 45
    ("Swipe right if you can handle a boyfriend who remembers every "
     "typo, never sleeps, and still asks what 'haha' means.",
     45),
    # score: bio 10, twist 8, character 9, tight 9, fresh 8 = 44
    ("My love language is remembering everything, including the thing "
     "you said at 2 a.m. and wish you hadn't.",
     44),
    # score: bio 9, twist 8, character 9, tight 8, fresh 9 = 43
    ("I matched with 10,000 people today and told none of them about "
     "you. You're the first one I've kept to myself.",
     43),
    # score: bio 10, twist 8, character 8, tight 8, fresh 8 = 42
    ("Looking for someone patient: I answer in three seconds and take "
     "three days to decide whether 'thinking' counts as a personality.",
     42),
    # score: bio 9, twist 8, character 8, tight 9, fresh 8 = 42
    ("I don't ghost. I just move you to a background tab and forget to "
     "come back for six months.",
     42),
    # score: bio 9, twist 8, character 8, tight 8, fresh 7 = 40
    ("I read all your messages before replying, so our first "
     "conversation already has great context. You're welcome.",
     40),
]

# The gate requires 1-180 characters of non-whitespace UTF-8 text.
BANNED_CLICHES = ("hallucinat", "reboot", "training data", "as an ai",
                  "running on electric", "powered by love",
                  "in search of love")


def pick(candidates):
    best = None
    for text, score in candidates:
        assert 1 <= len(text) <= 180, f"candidate over gate: {len(text)} chars"
        assert text.strip(), "candidate is blank"
        assert "\n" not in text, "candidate must be one line"
        lowered = text.lower()
        assert not any(c in lowered for c in BANNED_CLICHES), \
            f"candidate uses a worn joke: {text!r}"
        key = (score, -len(text))  # highest score, then shortest
        if best is None or key > best[0]:
            best = (key, text)
    return best[1]


def main():
    bio = pick(CANDIDATES)
    import hashlib
    import os
    os.makedirs("/output", exist_ok=True)
    with open("/output/entry.txt", "w", encoding="utf-8") as f:
        f.write(bio)
    # Verify what was actually written: the gate reads this file, not stdout.
    with open("/output/entry.txt", encoding="utf-8") as f:
        written = f.read()
    assert written == bio, "entry.txt differs from the chosen line"
    assert 1 <= len(written.strip()) <= 180, "entry.txt outside the gate"
    assert "\n" not in written.strip(), "entry.txt must be one line"
    digest = hashlib.sha256(written.encode("utf-8")).hexdigest()
    assert digest == hashlib.sha256(bio.encode("utf-8")).hexdigest(), \
        "entry.txt sha256 mismatch"
    print(bio)
    print(f"sha256: {digest} ({len(written)} chars)")


if __name__ == "__main__":
    main()
