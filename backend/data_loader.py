"""
Data Loader Module
Loads JSON data files for hospitals, events, pollution, and inflow
"""

import json
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_json_file(filename: str) -> Any:
    """Load a JSON file from the data directory"""
    file_path = DATA_DIR / filename
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {filename} not found at {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing {filename}: {e}")
        return None


def load_hospitals() -> List[Dict]:
    """Load hospital data"""
    data = load_json_file("hospitals.json")
    return data if data else []


def load_events() -> List[Dict]:
    """Load events data"""
    data = load_json_file("events.json")
    return data if data else []


def load_pollution() -> Dict:
    """Load pollution data"""
    data = load_json_file("pollution.json")
    return data if data else {"average_aqi": 100, "zones": []}


def load_mock_inflow() -> List[Dict]:
    """Load mock patient inflow data"""
    data = load_json_file("mock_inflow.json")
    return data if data else []
