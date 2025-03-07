import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
import dotenv

from app.database.session import init_db
from app.routes import users, rides, auth, cars


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database - this will create all tables defined in models
    await init_db()
    yield


# Load environment variables
dotenv.load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="NeedARide API",
    description="API for ride-sharing service",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {"message": "Welcome to NeedARide API"}


# Include routers
app.include_router(users.router, prefix="/v1/users", tags=["users"])
app.include_router(rides.router, prefix="/v1/rides", tags=["rides"])
app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(cars.router, prefix="/v1/cars", tags=["cars"])
# app.include_router(payments.router, prefix="/v1/payments", tags=["payments"])
