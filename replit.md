# ArogyaSetu - Citywide AI Surge Predictor & Hospital Load Balancer

## Overview
A real-time healthcare management system that predicts hospital surges and optimizes patient distribution across city hospitals using AI-powered analytics.

## Current State
- **Status**: MVP Complete and Running
- **Last Updated**: November 29, 2025
- **Python Version**: 3.11
- **Framework**: FastAPI with Uvicorn

## Project Architecture

### Backend (`/backend`)
- `main.py` - FastAPI application with routes for hospitals, surge, balance, history
- `predictor.py` - Surge Prediction Agent (rule-based with LLM fallback)
- `load_balancer.py` - Load Balancing Agent for patient transfers
- `data_loader.py` - JSON data loading utilities
- `agent.py` - Unified agent interface
- `db_init.py` - SQLite database initialization with mock data

### Frontend (`/frontend`)
- `index.html` - Main dashboard with Leaflet.js map
- `styles.css` - Custom styling
- `dashboard.js` - Frontend logic for API calls and UI updates

### Data (`/data`)
- `hospitals.json` - 8 hospitals in Delhi NCR
- `events.json` - Upcoming events affecting hospital load
- `pollution.json` - Air quality data by zone
- `mock_inflow.json` - Sample patient inflow records

### Database
- SQLite (`arogya_setu.db`) with 7 days of hourly patient inflow data (1352 records)

## API Endpoints
- `GET /` - Serve dashboard
- `GET /hospitals` - Hospital data
- `GET /surge` - Surge predictions (0-100%)
- `GET /balance` - Load balancing recommendations
- `GET /history` - Last 200 inflow records
- `GET /health` - Health check

## Key Features
1. Color-coded hospital markers on interactive map
2. Surge heatmap circles showing predicted load
3. AI recommendations for patient transfers
4. City-wide summary with risk level and occupancy stats

## Environment Variables (Optional)
- `GROQ_API_KEY` - For LLM-powered predictions
- `OPENAI_API_KEY` - Alternative LLM provider

## Running
The application runs on port 5000 via uvicorn.
