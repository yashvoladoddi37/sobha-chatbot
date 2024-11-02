from typing import Dict, Any
from .base_knowledge import SOBHA_KNOWLEDGE
from .facilities import FACILITIES_KNOWLEDGE
from .nearby_services import NEARBY_SERVICES

class KnowledgeBaseManager:
    def __init__(self):
        self.knowledge_base = {
            **SOBHA_KNOWLEDGE,
            "facilities": FACILITIES_KNOWLEDGE,
            "nearby_services": NEARBY_SERVICES
        }
        
    def get_amenity_info(self, amenity_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific amenity"""
        return self.knowledge_base.get("facilities", {}).get(amenity_name.lower(), {})
    
    def get_emergency_contacts(self) -> Dict[str, str]:
        """Get all emergency contacts"""
        return self.knowledge_base.get("emergency_contacts", {})
    
    def get_floor_info(self, floor_number: int) -> Dict[str, Any]:
        """Get information about a specific floor"""
        if floor_number == 37:
            return self.knowledge_base["floors"]["top_floor"]
        return self.knowledge_base["floors"]["regular_floors"]
    
    def get_nearby_service(self, service_type: str) -> list:
        """Get information about nearby services"""
        return self.knowledge_base["nearby_services"].get(service_type, [])
    
    def get_maintenance_schedule(self) -> Dict[str, Any]:
        """Get maintenance schedules"""
        return self.knowledge_base["maintenance"]
    
    def get_rules(self) -> Dict[str, str]:
        """Get rules and regulations"""
        return self.knowledge_base["rules_and_regulations"] 