from abc import ABC, abstractmethod

from app.domain.model.aggregates.interview_session import InterviewSession
from app.domain.model.commands.complete_interview_command import CompleteInterviewCommand
from app.domain.model.commands.start_interview_command import StartInterviewCommand
from app.domain.model.commands.submit_interview_response_command import SubmitInterviewResponseCommand


class InterviewCommandService(ABC):
    @abstractmethod
    async def handle_start(self, command: StartInterviewCommand) -> InterviewSession: ...

    @abstractmethod
    async def handle_submit_response(self, command: SubmitInterviewResponseCommand) -> InterviewSession: ...

    @abstractmethod
    async def handle_complete(self, command: CompleteInterviewCommand) -> InterviewSession: ...
