from fastapi import APIRouter, Query
from app.analyzer.smartmoney import smartmoney_analysis

router = APIRouter()

@router.get("/analyze")
def analyze(symbol: str = Query(...), timeframes: list[str] = Query(["1h", "4h", "1d"])):
    result = {}
    for tf in timeframes:
        result[tf] = smartmoney_analysis(symbol, tf)
    return result
