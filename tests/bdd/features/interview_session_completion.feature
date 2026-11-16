Feature: Interview Session Completion
    As a candidate
    I want to finish the interview at any moment or after all the questions
    So that I can move on to the results

    # US25 - Terminar sesión de entrevista (Sprint 3)

    Background:
        Given the candidate saved the job 50 "Backend Developer" as favorite
        And the candidate has an active interview session for job 50

    Scenario: Finish the interview before answering every question
        Given the candidate answered 2 questions
        When a POST request is sent to "/api/v1/interview-sessions/{id}/complete"
        Then the response status is 200 OK
        And the session status is "completed"
        And the session has a completion date

    Scenario: The coach stops asking questions after the sixth one
        Given the candidate answered 6 questions
        Then the session has 6 questions and the last message is from the candidate

    Scenario: Attempt to keep answering after the session was finished
        Given the candidate finished the interview session
        When the candidate sends the answer "Una respuesta más" to "/api/v1/interview-sessions/{id}/messages"
        Then the response status is 400 Bad Request
        And the response body contains the message "Interview session is no longer active."

    @pending
    Scenario: Session closed without pressing finish is saved as incomplete
        Given the candidate answered 2 questions
        And the candidate closed the browser tab without finishing
        When the candidate opens the interview history
        Then the session status is "abandoned"
