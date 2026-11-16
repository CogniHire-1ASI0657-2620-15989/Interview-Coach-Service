Feature: Interview Text Conversation and Live Transcript
    As a candidate
    I want to talk with the AI and see the transcript of the conversation
    So that I can simulate the pressure of a real interview without losing the thread

    # US22 - Realizar entrevista por voz o texto (canal de texto; el micrófono y sus permisos son del frontend)
    # US24 - Ver transcripción en vivo (Sprint 3)

    Background:
        Given the candidate saved the job 50 "Backend Developer" as favorite
        And the candidate has an active interview session for job 50

    Scenario: The coach replies with the next question after the candidate answers
        When the candidate sends the answer "Usé FastAPI y PostgreSQL en mi proyecto" to "/api/v1/interview-sessions/{id}/messages"
        Then the response status is 200 OK
        And the transcript shows "coach, candidate, coach" in that order
        And the question count is 2

    Scenario: The transcript can be consulted during the active session
        Given the candidate answered 2 questions
        When the candidate opens the session at "/api/v1/interview-sessions/{id}"
        Then the response status is 200 OK
        And the transcript shows "coach, candidate, coach, candidate, coach" in that order
        And the transcript messages are numbered consecutively

    Scenario: Attempt to send an empty answer
        When the candidate sends the answer "" to "/api/v1/interview-sessions/{id}/messages"
        Then the response status is 422 Unprocessable Entity

    Scenario: The AI provider is unavailable while answering
        Given the AI interview provider is unavailable
        When the candidate sends the answer "Mi respuesta" to "/api/v1/interview-sessions/{id}/messages"
        Then the response status is 503 Service Unavailable
        And the candidate answer is kept in the transcript
