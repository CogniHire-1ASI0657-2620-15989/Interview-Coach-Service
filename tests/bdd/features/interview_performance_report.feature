Feature: Post-Interview Performance Report
    As a candidate
    I want an analysis of my answers
    So that I know what to improve

    # US26 - Recibir reporte de desempeño post-entrevista (Sprint 3)

    Background:
        Given the candidate saved the job 50 "Backend Developer" as favorite
        And the candidate has an active interview session for job 50

    Scenario: Report with scores and recommendations after finishing the interview
        Given the candidate answered 3 questions
        When a POST request is sent to "/api/v1/interview-sessions/{id}/complete"
        Then the response status is 200 OK
        And the report contains technical 78, behavioral 70, communication 82 and overall 76 scores
        And the report lists strengths, improvement areas and recommendations
        And the AI evaluated the full transcript of the session

    Scenario: Report cannot be generated when the AI provider is unavailable
        Given the candidate answered 1 question
        And the AI interview provider is unavailable
        When a POST request is sent to "/api/v1/interview-sessions/{id}/complete"
        Then the response status is 503 Service Unavailable
        And the interview session remains "active"

    @pending
    Scenario: Session too short to generate an accurate report
        When a POST request is sent to "/api/v1/interview-sessions/{id}/complete"
        Then the response status is 400 Bad Request
        And the response body contains the message "La sesión fue muy breve para generar un reporte preciso"
