import httpx

from app.application.ports.identity_profile_client import CandidateProfile, IdentityProfileClient


class IdentityServiceClient(IdentityProfileClient):
    def __init__(self, base_url: str, internal_api_key: str):
        self._base_url = base_url.rstrip("/")
        self._internal_api_key = internal_api_key

    async def get_profile(self, user_id: int) -> CandidateProfile:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                response = await client.get(
                    f"{self._base_url}/api/v1/internal/users/{user_id}/job-profile",
                    headers={"X-Internal-Api-Key": self._internal_api_key},
                )
            if response.status_code == 404:
                raise ValueError("User profile not found.")
            response.raise_for_status()
            body = response.json()
        except httpx.HTTPError as exc:
            raise RuntimeError("Identity Service is unavailable.") from exc
        return CandidateProfile(
            user_id=int(body["id"]),
            name=str(body["name"]),
            segment=str(body["segment"]),
            target_position=body.get("target_position"),
            hard_skills=[str(skill["name"]) for skill in body.get("hard_skills") or []],
            soft_skills=[str(skill["name"]) for skill in body.get("soft_skills") or []],
            professional_summary=body.get("professional_summary"),
        )
