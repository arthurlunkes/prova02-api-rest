from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config.database import create_db_and_tables
from src.routes.reservas_routes import reservas_router
from src.routes.voos_routes import voos_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(voos_router)
app.include_router(reservas_router)

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}
