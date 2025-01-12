import os
from dataclasses import dataclass

@dataclass(frozen=True)
class ServerDetails:
    host: str
    port: str

    @property
    def url(self):
        return f"http://{self.host}:{self.port}"

def get_postgres_uri() -> str:
    user = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASSWORD")
    host = os.environ.get("DB_HOST")
    port = os.environ.get("DB_PORT")
    dbname = os.environ.get("DB_DATABASE")

    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

def get_api_url() -> ServerDetails:
    host = os.environ.get("API_HOST", "localhost")
    port = os.environ.get("API_PORT", "8001")
    return ServerDetails(host=host, port=port)

