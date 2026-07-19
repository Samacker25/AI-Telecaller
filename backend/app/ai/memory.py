"""Conversation memory: a bounded window of recent turns for the prompt.

Only the history needed for the active session is kept in the prompt
window; persistence of full conversations arrives with the Chat API
(Phase 5), which will rebuild this window from stored messages.
"""

import enum
from dataclasses import dataclass


class TurnRole(enum.StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True)
class ConversationTurn:
    """A single utterance in a conversation."""

    role: TurnRole
    content: str


class ConversationMemory:
    """Keeps the most recent conversation turns, oldest dropped first."""

    def __init__(self, *, max_turns: int) -> None:
        if max_turns <= 0:
            raise ValueError("max_turns must be positive")
        self._max_turns = max_turns
        self._turns: list[ConversationTurn] = []

    @property
    def turns(self) -> list[ConversationTurn]:
        """The retained window of turns, oldest first."""
        return list(self._turns)

    def add_user(self, content: str) -> None:
        self._append(ConversationTurn(role=TurnRole.USER, content=content))

    def add_assistant(self, content: str) -> None:
        self._append(ConversationTurn(role=TurnRole.ASSISTANT, content=content))

    def clear(self) -> None:
        """Reset the context, e.g. when a new session starts."""
        self._turns.clear()

    def _append(self, turn: ConversationTurn) -> None:
        self._turns.append(turn)
        if len(self._turns) > self._max_turns:
            del self._turns[: len(self._turns) - self._max_turns]
