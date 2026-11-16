Feature: Contextual Interview Questions
    As a candidate
    I want the AI to ask me about the job I chose and the courses I took
    So that the practice is useful

    # US23 - Recibir preguntas basadas en el contexto (Sprint 3)

    Background:
        Given the candidate saved the job 50 "Backend Developer C#" as favorite

    Scenario: Questions are generated with the job, the skill gaps and the completed courses
        Given the gap report of job 50 lists "C#" as a missing skill
        And the candidate completed the learning pathway course of "C#"
        When a POST request is sent to "/api/v1/interview-sessions" for job 50 with mode "technical"
        Then the response status is 201 Created
        And the AI receives the job title "Backend Developer C#"
        And the AI receives "C#" as a completed skill
        And the AI receives "C#" as a missing hard skill

    Scenario: A standard questionnaire for the role is used when the context services fail
        Given the Gap Analysis and Learning Pathway services are unavailable
        When a POST request is sent to "/api/v1/interview-sessions" for job 50 with mode "technical"
        Then the response status is 201 Created
        And the AI receives the job title "Backend Developer C#"
        And the AI receives no skill gaps nor completed courses
