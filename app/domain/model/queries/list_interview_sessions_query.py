from dataclasses import dataclass


@dataclass(frozen=True)
class ListInterviewSessionsQuery:
    user_id: int
