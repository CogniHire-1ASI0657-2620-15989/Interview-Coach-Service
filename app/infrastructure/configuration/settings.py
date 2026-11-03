import os
import re
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str
    database_schema: str
    identity_service_url: str
    job_discovery_service_url: str
    gap_analysis_service_url: str
    learning_pathway_service_url: str
    interview_groq_api_key: str | None
    interview_groq_model: str
    gateway_user_id_header: str
    internal_api_key: str


@lru_cache
def get_settings() -> Settings:
    values = {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "IDENTITY_SERVICE_URL": os.getenv("IDENTITY_SERVICE_URL"),
        "JOB_DISCOVERY_SERVICE_URL": os.getenv("JOB_DISCOVERY_SERVICE_URL"),
        "GAP_ANALYSIS_SERVICE_URL": os.getenv("GAP_ANALYSIS_SERVICE_URL"),
        "LEARNING_PATHWAY_SERVICE_URL": os.getenv("LEARNING_PATHWAY_SERVICE_URL"),
        "GATEWAY_USER_ID_HEADER": os.getenv("GATEWAY_USER_ID_HEADER"),
        "INTERNAL_API_KEY": os.getenv("INTERNAL_API_KEY"),
    }
    missing = [name for name, value in values.items() if not value or not value.strip()]
    if missing:
        raise RuntimeError(f"Missing required configuration: {', '.join(missing)}")

    database_schema = os.getenv("DATABASE_SCHEMA", "interview_coach").strip()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", database_schema):
        raise RuntimeError("DATABASE_SCHEMA must be a valid PostgreSQL identifier.")

    return Settings(
        database_url=values["DATABASE_URL"].strip(),
        database_schema=database_schema,
        identity_service_url=values["IDENTITY_SERVICE_URL"].rstrip("/"),
        job_discovery_service_url=values["JOB_DISCOVERY_SERVICE_URL"].rstrip("/"),
        gap_analysis_service_url=values["GAP_ANALYSIS_SERVICE_URL"].rstrip("/"),
        learning_pathway_service_url=values["LEARNING_PATHWAY_SERVICE_URL"].rstrip("/"),
        interview_groq_api_key=os.getenv("INTERVIEW_GROQ_API_KEY") or None,
        interview_groq_model=os.getenv("INTERVIEW_GROQ_MODEL", "qwen/qwen3.8-27b").strip(),
        gateway_user_id_header=values["GATEWAY_USER_ID_HEADER"].strip(),
        internal_api_key=values["INTERNAL_API_KEY"].strip(),
    )
