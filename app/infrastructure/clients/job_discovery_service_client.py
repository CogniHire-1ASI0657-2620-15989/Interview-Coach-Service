import httpx

from app.application.ports.favorite_job_client import FavoriteJob, FavoriteJobClient


class JobDiscoveryServiceClient(FavoriteJobClient):
    def __init__(self, base_url: str, user_id_header: str, internal_api_key: str):
        self._base_url = base_url.rstrip("/")
        self._user_id_header = user_id_header
        self._internal_api_key = internal_api_key

    async def get_favorite_job(self, user_id: int, job_id: int) -> FavoriteJob:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                response = await client.get(
                    f"{self._base_url}/api/v1/internal/favorites/{job_id}",
                    headers={
                        self._user_id_header: str(user_id),
                        "X-Internal-Api-Key": self._internal_api_key,
                    },
                )
            if response.status_code == 404:
                raise ValueError("The selected job is not in the user's favorites.")
            response.raise_for_status()
            body = response.json()
        except httpx.HTTPError as exc:
            raise RuntimeError("Job Discovery Service is unavailable.") from exc
        return FavoriteJob(
            id=int(body["id"]),
            title=str(body["title"]),
            description=body.get("description_snippet"),
        )
