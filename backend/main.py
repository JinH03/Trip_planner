from fastapi import FastAPI
from backend.database import engine

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Trip Planner API"}