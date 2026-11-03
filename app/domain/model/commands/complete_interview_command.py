from dataclasses import dataclass


@dataclass(frozen=True)
class CompleteInterviewCommand:
    user_id: int
    session_id: int
