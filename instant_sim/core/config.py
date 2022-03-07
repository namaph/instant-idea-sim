from typing import List, Optional, Union

from pydatic import AnyHttpUrl, BaseSettings, HttpUrl, validator


class Settings(BaseSettings):
    API_V1_ROOT: str = "/api/v1"
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    PROJECT_NAME: str
    SENTRY_DSN: Optional[HttpUrl] = None

    CITYIO_ROOT: str = "https://cityio.media.mit.edu/api/table/namaph/"
    GCS_ROOT: str = "https://storage.googleapis.com/instant-sim-viz/"
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
