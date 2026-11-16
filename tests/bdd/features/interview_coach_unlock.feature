Feature: Interview Coach Unlock
    As a candidate
    I want the simulator to be enabled automatically when I reach 100% of my learning pathway
    So that I can start practicing

    # US20 - Desbloqueo del Coach de Entrevistas (Sprint 3)
    # Pendiente: handle_start solo exige que la vacante sea favorita; no consulta el progreso de la ruta.

    @pending
    Scenario: Simulator is enabled when the learning pathway reaches 100%
        Given the candidate saved the job 50 "Backend Developer" as favorite
        And the learning pathway of job 50 is 100% completed
        When a POST request is sent to "/api/v1/interview-sessions" for job 50 without a mode
        Then the response status is 201 Created

    @pending
    Scenario: Simulator stays locked while the learning pathway is below 100%
        Given the candidate saved the job 50 "Backend Developer" as favorite
        And the learning pathway of job 50 is 50% completed
        When a POST request is sent to "/api/v1/interview-sessions" for job 50 without a mode
        Then the response status is 403 Forbidden
        And the response body contains the message "Completa tu ruta de aprendizaje para desbloquear el simulador"
