"""
ArogyaSetu - FastAPI Backend
Citywide AI Surge Predictor & Hospital Load Balancer
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path

from .data_loader import load_hospitals, load_events, load_pollution, load_mock_inflow
from .predictor import SurgePredictionAgent
from .load_balancer import LoadBalancingAgent
from .db_init import init_database, get_history

app = FastAPI(
    title="ArogyaSetu",
    description="Citywide AI Surge Predictor & Hospital Load Balancer",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

init_database()

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
async def serve_index():
    """Serve the main dashboard"""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    raise HTTPException(status_code=404, detail="Frontend not found")


@app.get("/hospitals")
async def get_hospitals():
    """Return list of hospitals with their data"""
    try:
        hospitals = load_hospitals()
        return JSONResponse(content=hospitals)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/surge")
async def get_surge():
    """Compute and return surge predictions for all hospitals"""
    try:
        hospitals = load_hospitals()
        events = load_events()
        pollution = load_pollution()
        inflow = load_mock_inflow()
        
        predictor = SurgePredictionAgent(
            hospitals=hospitals,
            events=events,
            pollution=pollution,
            inflow=inflow
        )
        
        surge_data = predictor.predict_surges()
        return JSONResponse(content=surge_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/balance")
async def get_balance():
    """Get load balancing recommendations"""
    try:
        hospitals = load_hospitals()
        events = load_events()
        pollution = load_pollution()
        inflow = load_mock_inflow()
        
        predictor = SurgePredictionAgent(
            hospitals=hospitals,
            events=events,
            pollution=pollution,
            inflow=inflow
        )
        surge_data = predictor.predict_surges()
        
        balancer = LoadBalancingAgent(hospitals=hospitals, surge_data=surge_data)
        recommendations = balancer.get_recommendations()
        
        return JSONResponse(content=recommendations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_inflow_history():
    """Return last 200 inflow records from SQLite database"""
    try:
        history = get_history(limit=200)
        return JSONResponse(content=history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ArogyaSetu"}
