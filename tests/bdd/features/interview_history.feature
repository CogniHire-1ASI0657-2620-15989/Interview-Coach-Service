Feature: Interview History
    As a candidate
    I want to see the history of all my practice interviews
    So that I can compare my evolution over time

    # US27 - Consultar historial de simulacros (Sprint 3)

    Scenario: List previous mock interviews with date, role and score
        Given the candidate saved the job 50 "Backend Developer" as favorite
        And the candidate has an active interview session for job 50
        And the candidate answered 1 question
        And the candidate finished the interview session
        When a GET request is sent to "/api/v1/interview-sessions"
        Then the response status is 200 OK
        And the history contains 1 interview for "Backend Developer" with overall score 76 and a date

    Scenario: Empty history when no mock interview was performed
        When a GET request is sent to "/api/v1/interview-sessions"
        Then the response status is 200 OK
        And the history is empty

    Scenario: A candidate cannot open another candidate's interview
        Given the candidate saved the job 50 "Backend Developer" as favorite
        And the candidate has an active interview session for job 50
        When another candidate requests the session at "/api/v1/interview-sessions/{id}"
        Then the response status is 404 Not Found
        And the response body contains the message "Interview session not found."
