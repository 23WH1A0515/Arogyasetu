"""
Agent Module
Unified interface for AI agents in the system
"""

from typing import Dict, List, Any, Optional
from .predictor import SurgePredictionAgent
from .load_balancer import LoadBalancingAgent
from .data_loader import load_hospitals, load_events, load_pollution, load_mock_inflow


class ArogyaSetuAgent:
    """
    Main orchestrating agent for ArogyaSetu system.
    Coordinates between prediction and load balancing agents.
    """
    
    def __init__(self):
        self.hospitals = load_hospitals()
        self.events = load_events()
        self.pollution = load_pollution()
        self.inflow = load_mock_inflow()
        self._surge_data: Optional[Dict] = None
        self._balance_data: Optional[Dict] = None
    
    def refresh_data(self):
        """Reload all data from sources"""
        self.hospitals = load_hospitals()
        self.events = load_events()
        self.pollution = load_pollution()
        self.inflow = load_mock_inflow()
        self._surge_data = None
        self._balance_data = None
    
    def get_surge_predictions(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get surge predictions from the prediction agent"""
        if self._surge_data is None or force_refresh:
            predictor = SurgePredictionAgent(
                hospitals=self.hospitals,
                events=self.events,
                pollution=self.pollution,
                inflow=self.inflow
            )
            self._surge_data = predictor.predict_surges()
        return self._surge_data
    
    def get_load_balance_recommendations(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get load balancing recommendations"""
        surge_data = self.get_surge_predictions(force_refresh)
        
        if self._balance_data is None or force_refresh:
            balancer = LoadBalancingAgent(
                hospitals=self.hospitals,
                surge_data=surge_data
            )
            self._balance_data = balancer.get_recommendations()
        return self._balance_data
    
    def get_full_analysis(self) -> Dict[str, Any]:
        """Get complete system analysis"""
        surge = self.get_surge_predictions(force_refresh=True)
        balance = self.get_load_balance_recommendations()
        
        return {
            "surge_predictions": surge,
            "load_balance": balance,
            "hospitals": self.hospitals,
            "pollution": self.pollution,
            "events": self.events
        }
    
    def get_hospital_status(self, hospital_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status for a specific hospital"""
        hospital = next((h for h in self.hospitals if h["id"] == hospital_id), None)
        if not hospital:
            return None
        
        surge = self.get_surge_predictions()
        prediction = next(
            (p for p in surge.get("predictions", []) if p["hospital_id"] == hospital_id),
            None
        )
        
        balance = self.get_load_balance_recommendations()
        
        incoming_transfers = [
            t for t in balance.get("transfer_recommendations", [])
            if t["to_hospital"]["id"] == hospital_id
        ]
        outgoing_transfers = [
            t for t in balance.get("transfer_recommendations", [])
            if t["from_hospital"]["id"] == hospital_id
        ]
        
        return {
            "hospital": hospital,
            "prediction": prediction,
            "incoming_transfers": incoming_transfers,
            "outgoing_transfers": outgoing_transfers
        }
