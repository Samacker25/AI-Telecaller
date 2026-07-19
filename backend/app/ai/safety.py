"""Safety heuristics that trigger human escalation before generation.

These are deliberately simple, deterministic keyword checks: they must
never miss silently in ways an LLM prompt could, and false positives
only route a patient to a human — the safe direction.
"""

import re

_EMERGENCY_PATTERNS = [
    r"\bemergenc(?:y|ies)\b",
    r"\bchest pain\b",
    r"\bheart attack\b",
    r"\bstroke\b",
    r"\bnot breathing\b",
    r"\bcan'?t breathe\b",
    r"\bunconscious\b",
    r"\bsevere bleeding\b",
    r"\bbleeding heavily\b",
    r"\bsuicid\w*\b",
    r"\boverdose\b",
    r"\bambulance\b",
]

_MEDICAL_ADVICE_PATTERNS = [
    r"\bdiagnos\w*\b",
    r"\bprescri\w*\b",
    r"\bdosage\b",
    r"\bhow (?:much|many) (?:\w+\s+){0,3}(?:tablets?|pills?|mg|ml)\b",
    r"\bwhat (?:medicine|medication|drug|tablet|pill) should\b",
    r"\bshould i (?:take|stop taking)\b",
    r"\bis it safe to take\b",
]

_EMERGENCY_RE = re.compile("|".join(_EMERGENCY_PATTERNS), re.IGNORECASE)
_MEDICAL_ADVICE_RE = re.compile("|".join(_MEDICAL_ADVICE_PATTERNS), re.IGNORECASE)


def detect_emergency(text: str) -> bool:
    """Return True when the message suggests a medical emergency."""
    return _EMERGENCY_RE.search(text) is not None


def detect_medical_advice_request(text: str) -> bool:
    """Return True when the message asks for diagnosis, prescription, or dosage."""
    return _MEDICAL_ADVICE_RE.search(text) is not None
