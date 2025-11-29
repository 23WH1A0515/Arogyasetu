"""
Load Balancing Agent
Detects overloaded and underutilized hospitals, recommends patient shifting
"""

from typing import Dict, List, Any
from datetime import datetime


class LoadBalancingAgent:
    """
    AI Agent for hospital load balancing.
    Identifies overloaded (>85%) and underutilized (<60%) hospitals.
    Recommends patient transfers to optimize city-wide healthcare capacity.
    """
    
    OVERLOAD_THRESHOLD = 85
    UNDERUTILIZED_THRESHOLD = 60
    
    def __init__(self, hospitals: List[Dict], surge_data: Dict[str, Any]):
        self.hospitals = hospitals
        self.surge_data = surge_data
        self.predictions = surge_data.get("predictions", [])
    
    def get_recommendations(self) -> Dict[str, Any]:
        """
        Analyze hospital loads and generate transfer recommendations.
        """
        overloaded = []
        underutilized = []
        balanced = []
        
        hospital_map = {h["id"]: h for h in self.hospitals}
        
        for pred in self.predictions:
            hospital_id = pred["hospital_id"]
            current_load = pred["current_load"]
            predicted_surge = pred["predicted_surge"]
            
            hospital = hospital_map.get(hospital_id, {})
            capacity = hospital.get("capacity", 100)
            current_patients = hospital.get("current_patients", 0)
            available_beds = capacity - current_patients
            
            hospital_info = {
                "hospital_id": hospital_id,
                "hospital_name": pred["hospital_name"],
                "current_load": current_load,
                "predicted_surge": predicted_surge,
                "capacity": capacity,
                "current_patients": current_patients,
                "available_beds": available_beds,
                "location": pred.get("location", {}),
                "risk_level": pred.get("risk_level", "unknown"),
                "specialties": hospital.get("specialties", [])
            }
            
            effective_load = max(current_load, predicted_surge)
            
            if effective_load >= self.OVERLOAD_THRESHOLD:
                overloaded.append(hospital_info)
            elif effective_load < self.UNDERUTILIZED_THRESHOLD:
                underutilized.append(hospital_info)
            else:
                balanced.append(hospital_info)
        
        overloaded.sort(key=lambda x: x["predicted_surge"], reverse=True)
        underutilized.sort(key=lambda x: x["available_beds"], reverse=True)
        
        transfer_recommendations = self._generate_transfers(overloaded, underutilized)
        
        alerts = self._generate_alerts(overloaded, underutilized)
        
        action_items = self._generate_action_items(overloaded, underutilized, balanced)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_hospitals": len(self.predictions),
                "overloaded_count": len(overloaded),
                "underutilized_count": len(underutilized),
                "balanced_count": len(balanced),
                "transfers_recommended": len(transfer_recommendations)
            },
            "overloaded_hospitals": overloaded,
            "underutilized_hospitals": underutilized,
            "balanced_hospitals": balanced,
            "transfer_recommendations": transfer_recommendations,
            "alerts": alerts,
            "action_items": action_items
        }
    
    def _generate_transfers(
        self, 
        overloaded: List[Dict], 
        underutilized: List[Dict]
    ) -> List[Dict]:
        """Generate patient transfer recommendations"""
        transfers = []
        
        for source in overloaded:
            excess_load = source["predicted_surge"] - 75
            patients_to_transfer = int((excess_load / 100) * source["capacity"])
            patients_to_transfer = max(1, min(patients_to_transfer, 20))
            
            best_destination = None
            best_distance = float('inf')
            
            for dest in underutilized:
                if dest["available_beds"] >= patients_to_transfer:
                    distance = self._calculate_distance(
                        source.get("location", {}),
                        dest.get("location", {})
                    )
                    if distance < best_distance:
                        best_distance = distance
                        best_destination = dest
            
            if best_destination:
                priority = "urgent" if source["predicted_surge"] >= 90 else "recommended"
                
                transfers.append({
                    "from_hospital": {
                        "id": source["hospital_id"],
                        "name": source["hospital_name"],
                        "current_load": source["current_load"],
                        "predicted_surge": source["predicted_surge"]
                    },
                    "to_hospital": {
                        "id": best_destination["hospital_id"],
                        "name": best_destination["hospital_name"],
                        "current_load": best_destination["current_load"],
                        "available_beds": best_destination["available_beds"]
                    },
                    "patients_to_transfer": patients_to_transfer,
                    "distance_km": round(best_distance, 2),
                    "priority": priority,
                    "reason": f"Source hospital at {source['predicted_surge']:.1f}% predicted load"
                })
                
                best_destination["available_beds"] -= patients_to_transfer
        
        return transfers
    
    def _calculate_distance(self, loc1: Dict, loc2: Dict) -> float:
        """Calculate approximate distance between two locations (simplified)"""
        import math
        
        lat1 = loc1.get("lat", 0)
        lng1 = loc1.get("lng", 0)
        lat2 = loc2.get("lat", 0)
        lng2 = loc2.get("lng", 0)
        
        lat_diff = abs(lat1 - lat2)
        lng_diff = abs(lng1 - lng2)
        distance = math.sqrt(lat_diff**2 + lng_diff**2) * 111
        
        return distance
    
    def _generate_alerts(
        self, 
        overloaded: List[Dict], 
        underutilized: List[Dict]
    ) -> List[Dict]:
        """Generate system alerts"""
        alerts = []
        
        critical = [h for h in overloaded if h["predicted_surge"] >= 95]
        if critical:
            alerts.append({
                "level": "critical",
                "title": "Critical Capacity Alert",
                "message": f"{len(critical)} hospital(s) approaching maximum capacity",
                "hospitals": [h["hospital_name"] for h in critical],
                "action_required": True
            })
        
        if len(overloaded) >= 3:
            alerts.append({
                "level": "warning",
                "title": "City-wide High Load",
                "message": f"{len(overloaded)} hospitals are overloaded. Consider city-wide emergency protocols.",
                "action_required": True
            })
        
        if len(underutilized) >= 4:
            alerts.append({
                "level": "info",
                "title": "Capacity Available",
                "message": f"{len(underutilized)} hospitals have significant spare capacity for transfers.",
                "action_required": False
            })
        
        return alerts
    
    def _generate_action_items(
        self,
        overloaded: List[Dict],
        underutilized: List[Dict],
        balanced: List[Dict]
    ) -> List[str]:
        """Generate actionable recommendations"""
        actions = []
        
        if overloaded:
            actions.append(f"Initiate patient transfers from {len(overloaded)} overloaded hospitals")
        
        critical = [h for h in overloaded if h["predicted_surge"] >= 90]
        if critical:
            actions.append("Activate emergency overflow protocols at critical facilities")
        
        if underutilized:
            actions.append(f"Notify {len(underutilized)} underutilized hospitals to prepare for incoming transfers")
        
        if len(overloaded) > len(underutilized):
            actions.append("Consider activating reserve medical facilities")
        
        if not overloaded and not underutilized:
            actions.append("System operating normally - continue monitoring")
        
        return actions
