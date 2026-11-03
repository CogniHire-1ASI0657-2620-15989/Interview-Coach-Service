from dataclasses import dataclass


@dataclass(frozen=True)
class GetInterviewSessionQuery:
    user_id: int
    session_id: int
