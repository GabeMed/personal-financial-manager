from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.api.v1 import auth, users, categories, transactions
from backend.app.core import config
from backend.app.db.base import Base, SessionLocal, engine
from backend.app.services.errors import ConflictError, NotFoundError, ServiceError
import backend.app.models  # noqa: F401  (registers the ORM models)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # No migrations yet: tables are created on startup (see README).
    Base.metadata.create_all(bind=engine)
    if config.SEED_DEMO_DATA:
        from backend.app.seed import seed_demo_data

        with SessionLocal() as db:
            seed_demo_data(db)
    yield


app = FastAPI(title="Finance Manager API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_STATUS_BY_ERROR = {NotFoundError: 404, ConflictError: 409}


@app.exception_handler(ServiceError)
def service_error_handler(_: Request, exc: ServiceError):
    return JSONResponse(
        status_code=_STATUS_BY_ERROR.get(type(exc), 400),
        content={"detail": exc.detail},
    )


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(categories.router)
api_router.include_router(transactions.router)

app.include_router(api_router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
