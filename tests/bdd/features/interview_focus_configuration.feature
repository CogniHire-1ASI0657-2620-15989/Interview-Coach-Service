Feature: Interview Focus Configuration
    As a candidate
    I want to choose whether my mock interview is technical, behavioral or mixed
    So that I can focus on my specific weaknesses

    # US21 - Configurar enfoque de la entrevista (Sprint 3)

    Background:
        Given the candidate saved the job 50 "Backend Developer" as favorite

    Scenario: Start a technical interview
        When a POST request is sent to "/api/v1/interview-sessions" for job 50 with mode "technical"
        Then the response status is 201 Created
        And the session mode is "technical"
        And the coach asks the first question
        And the questions after the second one are "technical" questions

    Scenario: Mixed focus is used by default when no mode is selected
        When a POST request is sent to "/api/v1/interview-sessions" for job 50 without a mode
        Then the response status is 201 Created
        And the session mode is "mixed"

    Scenario: Attempt to start an interview with an unsupported focus
        When a POST request is sent to "/api/v1/interview-sessions" for job 50 with mode "trivia"
        Then the response status is 422 Unprocessable Entity

    Scenario: Attempt to start an interview for a job that is not in favorites
        When a POST request is sent to "/api/v1/interview-sessions" for job 77 without a mode
        Then the response status is 404 Not Found
        And the response body contains the message "The selected job is not in the user's favorites."
