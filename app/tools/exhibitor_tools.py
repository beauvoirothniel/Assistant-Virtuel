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
            return "Aucun exposant enregistré pour ce salon."
        
        # Grouper par catégorie
        categories = {}
        for exhibitor in self.salon_data.exhibitors:
            if exhibitor.category not in categories:
                categories[exhibitor.category] = []
            categories[exhibitor.category].append(exhibitor)
        
        result = f"📋 *Liste des {len(self.salon_data.exhibitors)} exposants:*\n\n"
        
        for category, exhibitors in categories.items():
            result += f"🏷️ *{category}* ({len(exhibitors)} exposants)\n"
            for exhibitor in exhibitors:
                result += f"  • {exhibitor.name} - Stand {exhibitor.booth_number}\n"
            result += "\n"
        
        return result
    
    def _list_by_category(self, category: str) -> str:
        """Liste les exposants d'une catégorie"""
        category_lower = category.lower()
        matching_exhibitors = []
        
        for exhibitor in self.salon_data.exhibitors:
            if category_lower in exhibitor.category.lower():
                matching_exhibitors.append(exhibitor)
        
        if not matching_exhibitors:
            return f"Aucun exposant trouvé dans la catégorie '{category}'."
        
        result = f"🏷️ *Exposants - {category}* ({len(matching_exhibitors)} résultats)\n\n"
        
        for exhibitor in matching_exhibitors:
            result += f"🏢 *{exhibitor.name}* - Stand {exhibitor.booth_number}\n"
            result += f"   📝 {exhibitor.description[:100]}...\n"
            if exhibitor.special_offers:
                result += f"   🎁 Offres: {', '.join(exhibitor.special_offers)}\n"
            result += "\n"
        
        return result

class ExhibitorSearchTool(BaseTool):
    """Outil de recherche avancée d'exposants"""
    
    name = "exhibitor_search"
    description = "Recherche avancée d'exposants par mots-clés, produits ou services"
    
    def _init_(self, salon_data: Salon):
        super()._init_()
        self.salon_data = salon_data
    
    def _run(self, keywords: str) -> str:
        """Recherche d'exposants par mots-clés"""
        keywords_list = [kw.strip().lower() for kw in keywords.split(",")]
        matching_exhibitors = []
        
        for exhibitor in self.salon_data.exhibitors:
            score = 0
            
            # Recherche dans le nom
            for kw in keywords_list:
                if kw in exhibitor.name.lower():
                    score += 3
                
                # Recherche dans la description
                if kw in exhibitor.description.lower():
                    score += 2
                
                # Recherche dans la catégorie
                if kw in exhibitor.category.lower():
                    score += 1
            
            if score > 0:
                matching_exhibitors.append((exhibitor, score))
        
        if not matching_exhibitors:
            return f"Aucun exposant trouvé pour les mots-clés: {keywords}"
        
        # Trier par score de pertinence
        matching_exhibitors.sort(key=lambda x: x[1], reverse=True)
        
        result = f"🔍 *Résultats de recherche pour '{keywords}'* ({len(matching_exhibitors)} résultats)\n\n"
        
        for exhibitor, score in matching_exhibitors[:10]:  # Top 10
            result += f"🏢 *{exhibitor.name}* - Stand {exhibitor.booth_number}\n"
            result += f"   🏷️ {exhibitor.category}\n"
            result += f"   📝 {exhibitor.description[:100]}...\n"
            result += f"   ⭐ Pertinence: {score}/5\n\n"
        
        if len(matching_exhibitors) > 10:
            result += f"... et {len(matching_exhibitors) - 10} autres résultats\n"
        
        return result