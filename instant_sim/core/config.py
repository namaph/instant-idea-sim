from typing import List, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, BaseSettings, Field, HttpUrl, root_validator, validator


class _FirestoreRoutiung(BaseModel):
    simulation_result: str = Field(..., min_length=1)
    visualization_result: str = Field(..., min_length=1)

    @root_validator
    def check_uniqueness(cls, values):  # type: ignore
        sres, vres = values.get("simulation_result"), values.get("visualization_result")
        assert sres != vres, "Fields must be unique"


class Settings(BaseSettings):
    API_V1_ROOT: str = "/api/v1"
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    PROJECT_NAME: str
    SENTRY_DSN: Optional[HttpUrl] = None

    CITYIO_ROOT: str = "https://cityio.media.mit.edu/api/table/namaph/"
    GCS_ROOT: str = "https://storage.googleapis.com/instant-sim-viz/"

    FIRESTORE_ROUTING: _FirestoreRoutiung = _FirestoreRoutiung(
        simulation_result="sim_res", visualization_result="viz_img"
    )

    USE_GCP_DEBUGGER: bool
    USE_GCP_PROFILER: bool

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
