"""
Surge Prediction Agent
Analyzes pollution, events, inflow, and hospital load to predict surges
"""

import os
import json
from typing import Dict, List, Any
from datetime import datetime


class SurgePredictionAgent:
    """
    AI Agent for predicting hospital surges.
    Uses LLM if GROQ_API_KEY is available, otherwise falls back to rule-based logic.
    """
    
    def __init__(
        self,
        hospitals: List[Dict],
        events: List[Dict],
        pollution: Dict,
        inflow: List[Dict]
    ):
        self.hospitals = hospitals
        self.events = events
        self.pollution = pollution
        self.inflow = inflow
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
    
    def predict_surges(self) -> Dict[str, Any]:
        """
        Predict surge intensity for each hospital.
        Returns surge data with intensity 0-100%.
        """
        if self.groq_api_key:
            return self._predict_with_groq()
        elif self.openai_api_key:
            return self._predict_with_openai()
        else:
            return self._predict_rule_based()
    
    def _predict_with_groq(self) -> Dict[str, Any]:
        """Use GROQ LLM for surge prediction"""
        try:
            import requests
            
            prompt = self._build_prompt()
            
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a healthcare analytics AI. Analyze hospital data and predict surge intensities. Return ONLY valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return self._parse_llm_response(content)
            else:
                return self._predict_rule_based()
                
        except Exception as e:
            print(f"GROQ API error: {e}")
            return self._predict_rule_based()
    
    def _predict_with_openai(self) -> Dict[str, Any]:
        """Use OpenAI LLM for surge prediction"""
        try:
            import requests
            
            prompt = self._build_prompt()
            
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a healthcare analytics AI. Analyze hospital data and predict surge intensities. Return ONLY valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return self._parse_llm_response(content)
            else:
                return self._predict_rule_based()
                
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._predict_rule_based()
    
    def _build_prompt(self) -> str:
        """Build prompt for LLM analysis"""
        return f"""
Analyze the following healthcare data and predict surge intensity (0-100%) for each hospital.

HOSPITALS:
{json.dumps(self.hospitals, indent=2)}

POLLUTION DATA:
{json.dumps(self.pollution, indent=2)}

UPCOMING EVENTS:
{json.dumps(self.events, indent=2)}

RECENT PATIENT INFLOW:
{json.dumps(self.inflow[:20], indent=2)}

For each hospital, predict the surge intensity based on:
1. Current occupancy and capacity
2. Pollution levels in the area (high pollution = more respiratory cases)
3. Upcoming events (large gatherings = potential injuries/emergencies)
4. Recent inflow trends

Return JSON in this exact format:
{{
    "timestamp": "ISO timestamp",
    "predictions": [
        {{
            "hospital_id": "H001",
            "hospital_name": "name",
            "current_load": 75,
            "predicted_surge": 85,
            "surge_factors": ["pollution", "event"],
            "risk_level": "high"
        }}
    ],
    "city_summary": {{
        "overall_risk": "medium",
        "total_capacity": 1000,
        "total_occupied": 700,
        "recommendations": ["recommendation1"]
    }}
}}
"""
    
    def _parse_llm_response(self, content: str) -> Dict[str, Any]:
        """Parse LLM response to extract JSON"""
        try:
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            return json.loads(content.strip())
        except json.JSONDecodeError:
            return self._predict_rule_based()
    
    def _predict_rule_based(self) -> Dict[str, Any]:
        """Rule-based surge prediction when LLM is not available"""
        predictions = []
        total_capacity = 0
        total_occupied = 0
        
        avg_aqi = self.pollution.get("average_aqi", 100)
        active_events = [e for e in self.events if e.get("status") == "upcoming"]
        event_impact = len(active_events) * 5
        
        for hospital in self.hospitals:
            hospital_id = hospital["id"]
            name = hospital["name"]
            capacity = hospital["capacity"]
            current_patients = hospital["current_patients"]
            
            total_capacity += capacity
            total_occupied += current_patients
            
            base_load = (current_patients / capacity) * 100
            
            location = hospital.get("location", {})
            lat = location.get("lat", 0)
            
            pollution_factor = 0
            if avg_aqi > 150:
                pollution_factor = 15
            elif avg_aqi > 100:
                pollution_factor = 10
            elif avg_aqi > 50:
                pollution_factor = 5
            
            recent_inflow = [
                i for i in self.inflow 
                if i.get("hospital_id") == hospital_id
            ][-24:]
            
            if recent_inflow:
                avg_inflow = sum(i["count"] for i in recent_inflow) / len(recent_inflow)
                inflow_trend = min(avg_inflow * 2, 20)
            else:
                inflow_trend = 5
            
            predicted_surge = min(100, base_load + pollution_factor + event_impact + inflow_trend)
            
            surge_factors = []
            if pollution_factor > 0:
                surge_factors.append("pollution")
            if event_impact > 0:
                surge_factors.append("events")
            if inflow_trend > 10:
                surge_factors.append("high_inflow")
            if base_load > 70:
                surge_factors.append("high_occupancy")
            
            if predicted_surge >= 85:
                risk_level = "critical"
            elif predicted_surge >= 70:
                risk_level = "high"
            elif predicted_surge >= 50:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            predictions.append({
                "hospital_id": hospital_id,
                "hospital_name": name,
                "current_load": round(base_load, 1),
                "predicted_surge": round(predicted_surge, 1),
                "surge_factors": surge_factors,
                "risk_level": risk_level,
                "location": location
            })
        
        overall_occupancy = (total_occupied / total_capacity) * 100 if total_capacity > 0 else 0
        
        if overall_occupancy >= 80:
            overall_risk = "critical"
        elif overall_occupancy >= 65:
            overall_risk = "high"
        elif overall_occupancy >= 50:
            overall_risk = "medium"
        else:
            overall_risk = "low"
        
        recommendations = []
        if avg_aqi > 100:
            recommendations.append("High pollution alert - prepare for respiratory emergencies")
        if active_events:
            recommendations.append(f"{len(active_events)} upcoming events - standby for crowd-related emergencies")
        if overall_occupancy > 70:
            recommendations.append("Consider activating overflow protocols")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "predictions": predictions,
            "city_summary": {
                "overall_risk": overall_risk,
                "total_capacity": total_capacity,
                "total_occupied": total_occupied,
                "overall_occupancy": round(overall_occupancy, 1),
                "average_aqi": avg_aqi,
                "active_events": len(active_events),
                "recommendations": recommendations
            },
            "method": "rule_based"
        }
