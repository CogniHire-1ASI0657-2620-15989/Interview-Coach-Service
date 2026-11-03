# Interview Coach Service

Microservicio FastAPI responsable de las sesiones de simulación de entrevistas de PathBridge.

Cada sesión se contextualizará con la vacante favorita del usuario, su perfil, el reporte de brechas y el progreso de su ruta de aprendizaje. El servicio usa una clave Groq propia (`INTERVIEW_GROQ_API_KEY`), separada de la empleada por Gap Analysis.

## Configuración local

1. Copia `.env.example` a `.env` y completa sus valores.
2. Instala dependencias y ejecuta las migraciones:

```powershell
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8004
```

3. Comprueba `GET /health`.

## Endpoints

Todas las rutas, salvo `/health`, requieren que el API Gateway reenvíe `X-User-Id` y `X-Internal-Api-Key`.

- `GET /health`
- `POST /api/v1/interview-sessions`
- `POST /api/v1/interview-sessions/{session_id}/messages`
- `POST /api/v1/interview-sessions/{session_id}/complete`
- `GET /api/v1/interview-sessions`
- `GET /api/v1/interview-sessions/{session_id}`

Para iniciar una entrevista:

```json
{
  "job_id": 123,
  "mode": "mixed"
}
```

Cada entrevista tiene como máximo seis preguntas y requiere que la vacante pertenezca a los favoritos del usuario.
