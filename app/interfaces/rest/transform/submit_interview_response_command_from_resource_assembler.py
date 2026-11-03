from app.domain.model.commands.submit_interview_response_command import SubmitInterviewResponseCommand
from app.interfaces.rest.resources.submit_interview_response_resource import SubmitInterviewResponseResource


class SubmitInterviewResponseCommandFromResourceAssembler:
    @staticmethod
    def to_command(
        user_id: int,
        session_id: int,
        resource: SubmitInterviewResponseResource,
    ) -> SubmitInterviewResponseCommand:
        return SubmitInterviewResponseCommand(user_id=user_id, session_id=session_id, content=resource.content)
