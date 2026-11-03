import httpx

from app.application.ports.learning_path_client import LearningPathClient, LearningPathProgress


class LearningPathwayServiceClient(LearningPathClient):
    def __init__(self, base_url: str, user_id_header: str, internal_api_key: str):
        self._base_url = base_url.rstrip("/")
        self._user_id_header = user_id_header
        self._internal_api_key = internal_api_key

    async def get_progress_by_job(self, user_id: int, job_id: int) -> LearningPathProgress:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                response = await client.get(
                    f"{self._base_url}/api/v1/learning-paths/{job_id}",
                    headers={
                        self._user_id_header: str(user_id),
                        "X-Internal-Api-Key": self._internal_api_key,
                    },
                )
            if response.status_code == 404:
                raise ValueError("Learning path not found.")
            response.raise_for_status()
            body = response.json()
        except httpx.HTTPError as exc:
            raise RuntimeError("Learning Pathway Service is unavailable.") from exc
        return LearningPathProgress(
            learning_path_id=int(body["id"]),
            job_id=int(body["job_id"]),
            progress_percentage=int(body["progress_percentage"]),
            completed_skills=[
                str(item["skill_name"])
                for item in body.get("items") or []
                if item.get("status") == "watched"
            ],
        )
