# ArogyaSetu - Citywide AI Surge Predictor & Hospital Load Balancer

A real-time healthcare management system that predicts hospital surges and optimizes patient distribution across city hospitals using AI-powered analytics.

## Features

- **AI Surge Prediction**: Analyzes pollution levels, upcoming events, and patient inflow patterns to predict hospital surges (0-100% intensity)
- **Load Balancing**: Identifies overloaded (>85%) and underutilized (<60%) hospitals with automated transfer recommendations
- **Interactive Map Dashboard**: Leaflet.js-powered visualization with color-coded hospital status and surge heatmaps
- **Real-time Monitoring**: Live updates on hospital capacity, ICU beds, and ventilator availability
- **Smart Recommendations**: AI-generated action items for hospital administrators

## Project Structure

```
/backend
    main.py          # FastAPI application entry point
    predictor.py     # Surge Prediction Agent
    load_balancer.py # Load Balancing Agent  
    data_loader.py   # JSON data loading utilities
    agent.py         # Unified agent interface
    db_init.py       # SQLite database initialization

/frontend
    index.html       # Main dashboard page
    styles.css       # Styling
    dashboard.js     # Frontend logic

/data
    hospitals.json   # Hospital information
    events.json      # Upcoming events data
    pollution.json   # Air quality data
    mock_inflow.json # Patient inflow records
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve the dashboard |
| `/hospitals` | GET | Get all hospital data |
| `/surge` | GET | Get surge predictions |
| `/balance` | GET | Get load balancing recommendations |
| `/history` | GET | Get last 200 inflow records |
| `/health` | GET | Health check |

## AI Agents

### Surge Prediction Agent
- Loads pollution, event data, patient inflow, and hospital load
- Computes surge intensity per hospital (0-100%)
- Uses LLM via GROQ API if available, falls back to rule-based predictions

### Load Balancing Agent
- Detects overloaded hospitals (>85% capacity)
- Identifies underutilized hospitals (<60% capacity)
- Recommends optimal patient transfers

## Environment Variables (Optional)

- `GROQ_API_KEY`: For LLM-powered surge predictions
- `OPENAI_API_KEY`: Alternative LLM provider

## Running the Application

The application runs automatically when you click "Run" in Replit.

## Technologies

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite
- **Frontend**: HTML5, CSS3, JavaScript, Leaflet.js
- **AI**: Rule-based analytics with optional LLM integration
