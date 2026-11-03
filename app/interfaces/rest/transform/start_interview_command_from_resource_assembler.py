from app.domain.model.commands.start_interview_command import StartInterviewCommand
from app.interfaces.rest.resources.start_interview_resource import StartInterviewResource


class StartInterviewCommandFromResourceAssembler:
    @staticmethod
    def to_command(user_id: int, resource: StartInterviewResource) -> StartInterviewCommand:
        return StartInterviewCommand(user_id=user_id, job_id=resource.job_id, mode=resource.mode)
