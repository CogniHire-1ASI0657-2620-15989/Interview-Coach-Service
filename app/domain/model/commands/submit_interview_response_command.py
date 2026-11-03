from dataclasses import dataclass


@dataclass(frozen=True)
class SubmitInterviewResponseCommand:
    user_id: int
    session_id: int
    content: str
