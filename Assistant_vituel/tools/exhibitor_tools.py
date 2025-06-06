from typing import List, Dict, Any
from langchain.tools import BaseTool
from app.models.salon import Salon, Exhibitor
from app.utils.logger import setup_logger

logger = setup_logger(_name_)

class ExhibitorInfoTool(BaseTool):
    """Outil pour récupérer les informations sur les exposants"""
    
    name = "exhibitor_info"
    description = "Récupère les informations détaillées sur un exposant spécifique par nom ou numéro de stand"
    
    def _init_(self, salon_data: Salon):
        super()._init_()
        self.salon_data = salon_data
    
    def _run(self, query: str) -> str:
        """Recherche un exposant par nom ou numéro de stand"""
        query_lower = query.lower().strip()
        
        # Recherche par nom
        for exhibitor in self.salon_data.exhibitors:
            if (query_lower in exhibitor.name.lower() or 
                query_lower == exhibitor.booth_number.lower()):
                
                info = f"""
                🏢 *{exhibitor.name}*
                📍 Stand N°: {exhibitor.booth_number}
                🏷️ Catégorie: {exhibitor.category}
                📝 Description: {exhibitor.description}
                👤 Contact: {exhibitor.contact_person}
                """
                
                if exhibitor.special_offers:
                    info += f"\n🎁 Offres spéciales: {', '.join(exhibitor.special_offers)}"
                
                return info.strip()
        
        # Si aucun exposant trouvé, proposer des suggestions
        suggestions = self._get_suggestions(query_lower)
        if suggestions:
            return f"Exposant '{query}' non trouvé. Voulez-vous dire: {', '.join(suggestions[:3])} ?"
        
        return f"Aucun exposant trouvé pour '{query}'. Consultez la liste complète avec 'liste exposants'."
    
    def _get_suggestions(self, query: str) -> List[str]:
        """Propose des suggestions d'exposants similaires"""
        suggestions = []
        
        for exhibitor in self.salon_data.exhibitors:
            # Recherche par similarité dans le nom
            if any(word in exhibitor.name.lower() for word in query.split()):
                suggestions.append(exhibitor.name)
            # Recherche par catégorie
            elif query in exhibitor.category.lower():
                suggestions.append(exhibitor.name)
        
        return suggestions

class ExhibitorListTool(BaseTool):
    """Outil pour lister les exposants par catégorie"""
    
    name = "exhibitor_list"
    description = "Liste tous les exposants ou les exposants d'une catégorie spécifique"
    
    def _init_(self, salon_data: Salon):
        super()._init_()
        self.salon_data = salon_data
    
    def _run(self, category: str = "all") -> str:
        """Liste les exposants"""
        if category.lower() in ["all", "tous", "tout"]:
            return self._list_all_exhibitors()
        else:
            return self._list_by_category(category)
    
    def _list_all_exhibitors(self) -> str:
        """Liste tous les exposants"""
        if not self.salon_data.exhibitors:
            return