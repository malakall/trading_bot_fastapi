from fastapi import FastAPI
from app.api import router

app = FastAPI(title="Smart Money Analyzer")
app.include_router(router)
