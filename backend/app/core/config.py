import os
from datetime import timedelta

# All settings can be overridden through environment variables (see README).
# The defaults are meant for local development only.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-insecure-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = timedelta(
    minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
)
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
SEED_DEMO_DATA = os.getenv("SEED_DEMO_DATA", "false").lower() in {"1", "true", "yes"}
