from typing import List, Dict, Any, Tuple, Optional
from langchain.tools import BaseTool
from app.models.salon import Salon, Exhibitor, Event
from app.utils.logger import setup_logger

logger = setup_logger(_name_)

class NavigationTool(BaseTool):
    """Outil pour la navigation et orientation dans le salon"""
    
    name = "navigation"
    description = "Aide à la navigation dans le salon : directions, distances, plans des stands"
    
    def _init_(self, salon_data: Salon):
        super()._init_()
        self.salon_data = salon_data
        self._initialize_layout()
    
    def _initialize_layout(self):
        """Initialise la disposition du salon"""
        # Simulation d'un plan de salon avec zones
        self.zones = {
            "A": {"name": "Hall Principal", "booths": [], "facilities": ["Accueil", "Information"]},
            "B": {"name": "Technologie", "booths": [], "facilities": ["Démonstrations"]},
            "C": {"name": "Services", "booths": [], "facilities": ["Espace détente"]},
            "D": {"name": "Innovation", "booths": [], "facilities": ["Laboratoire"]},
            "E": {"name": "Restauration", "booths": [], "facilities": ["Restaurant", "Café"]}
        }
        
        # Répartir les exposants par zones (simulation)
        for i, exhibitor in enumerate(self.salon_data.exhibitors):
            zone_key = list(self.zones.keys())[i % len(self.zones)]
            self.zones[zone_key]["booths"].append(exhibitor.booth_number)
    
    def _run(self, query: str) -> str:
        """Traite une demande de navigation"""
        query_lower = query.lower().strip()
        
        if any(word in query_lower for word in ["plan", "carte", "layout"]):
            return self._get_salon_map()
        elif any(word in query_lower for word in ["toilettes", "wc", "restroom"]):
            return self._get_facilities_info("toilettes")
        elif any(word in query_lower for word in ["restaurant", "café", "manger", "boire"]):
            return self._get_facilities_info("restauration")
        elif any(word in query_lower for word in ["accueil", "information", "aide"]):
            return self._get_facilities_info("accueil")
        elif any(word in query_lower for word in ["sortie", "exit", "parking"]):
            return self._get_facilities_info("sortie")
        elif "stand" in query_lower or any(char.isdigit() for char in query):
            return self._find_booth_location(query)
        else:
            return self._general_navigation_help()
    
    def _get_salon_map(self) -> str:
        """Retourne le plan du salon"""
        result = "🗺️ *Plan du salon*\n\n"
        
        layout = """
        ┌─────────────────────────────────────┐
        │  🚪 ENTRÉE PRINCIPALE               │
        │  ↓                                  │
        │  🏢 ACCUEIL & INFORMATION           │
        ├─────────────────────────────────────┤
        │  ZONE A - HALL PRINCIPAL            │
        │  [A1] [A2] [A3] [A4] [A5]          │
        ├─────────────────────────────────────┤
        │  ZONE B - TECHNOLOGIE               │
        │  [B1] [B2] [B3] [B4] [B5]          │
        │       🖥️ DÉMONSTRATIONS             │
        ├─────────────────────────────────────┤
        │  ZONE C - SERVICES                  │
        │  [C1] [C2] [C3] [C4] [C5]          │
        │       🛋️ ESPACE DÉTENTE             │
        ├─────────────────────────────────────┤
        │  ZONE D - INNOVATION                │
        │  [D1] [D2] [D3] [D4] [D5]          │
        │       🔬 LABORATOIRE                │
        ├─────────────────────────────────────┤
        │  ZONE E - RESTAURATION              │
        │  🍽️ RESTAURANT  ☕ CAFÉ            │
        │  🚻 TOILETTES                       │
        └─────────────────────────────────────┘
        """
        
        result += layout + "\n"
        
        # Ajouter les informations par zone
        for zone_key, zone_info in self.zones.items():
            if zone_info["booths"]:
                result += f"📍 *Zone {zone_key} - {zone_info['name']}*\n"
                result += f"   Stands: {', '.join(zone_info['booths'][:5])}\n"
                if zone_info["facilities"]:
                    result += f"   Services: {', '.join(zone_info['facilities'])}\n"
                result += "\n"
        
        return result
    
    def _find_booth_location(self, query: str) -> str:
        """Trouve l'emplacement d'un stand"""
        # Extraire le numéro de stand
        booth_number = None
        for word in query.split():
            if any(char.isdigit() for char in word):
                booth_number = word.upper()
                break
        
        if not booth_number:
            return "Veuillez préciser le numéro de stand recherché."
        
        # Chercher l'exposant
        exhibitor = None
        for exp in self.salon_data.exhibitors:
            if exp.booth_number.upper() == booth_number:
                exhibitor = exp
                break
        
        if not exhibitor:
            return f"Stand {booth_number} non trouvé."
        
        # Déterminer la zone
        zone_info = self._get_booth_zone(booth_number)
        
        result = f"📍 *Stand {booth_number} - {exhibitor.name}*\n\n"
        result += f"🏢 Exposant: {exhibitor.name}\n"
        result += f"📍 Localisation: {zone_info['zone']} - {zone_info['name']}\n"
        result += f"🚶 Directions: {self._get_directions_to_zone(zone_info['zone'])}\n"
        
        # Services à proximité
        nearby_services = zone_info.get('facilities', [])
        if nearby_services:
            result += f"🎯 Services proches: {', '.join(nearby_services)}\n"
        
        return result
    
    def _get_booth_zone(self, booth_number: str) -> Dict[str, str]:
        """Détermine la zone d'un stand"""
        # Logique simplifiée basée sur le préfixe du stand
        if booth_number.startswith('A'):
            return {"zone": "A", "name": "Hall Principal"}
        elif booth_number.startswith('B'):
            return {"zone": "B", "name": "Technologie"}
        elif booth_number.startswith('C'):
            return {"zone": "C", "name": "Services"}
        elif booth_number.startswith('D'):
            return {"zone": "D", "name": "Innovation"}
        elif booth_number.startswith('E'):
            return {"zone": "E", "name": "Restauration"}
        else:
            return {"zone": "A", "name": "Hall Principal"}
    
    def _get_directions_to_zone(self, zone: str) -> str:
        """Donne les directions vers une zone"""
        directions = {
            "A": "Depuis l'entrée, continuez tout droit",
            "B": "Depuis l'entrée, tournez à droite après l'accueil",
            "C": "Depuis l'entrée, prenez à gauche après la zone B",
            "D": "Au fond du salon, après la zone C",
            "E": "Tout au fond, suivez les panneaux restauration"
        }
        
        return directions.get(zone, "Consultez le plan à l'accueil")
    
    def _get_facilities_info(self, facility_type: str) -> str:
        """Informations sur les services du salon"""
        facilities = {
            "toilettes": {
                "locations": ["Zone E (Restauration)", "Zone A (Accueil)"],
                "description": "🚻 Toilettes disponibles dans 2 zones",
                "access": "Accès libre, suivez la signalétique"
            },
            "restauration": {
                "locations": ["Zone E"],
                "description": "🍽️ Restaurant et café dans la zone E",
                "access": "Ouvert de 8h à 18h, cartes acceptées"
            },
            "accueil": {
                "locations": ["Zone A - Entrée principale"],
                "description": "🏢 Bureau d'accueil et information",
                "access": "Personnel disponible en permanence"
            },
            "sortie": {
                "locations": ["Entrée principale", "Sortie de secours Zone D"],
                "description": "🚪 Sorties et parking",
                "access": "Parking gratuit, 500 places disponibles"
            }
        }
        
        info = facilities.get(facility_type)
        if not info:
            return "Service non reconnu. Services disponibles : toilettes, restauration, accueil, sortie"
        
        result = f"{info['description']}\n"
        result += f"📍 Emplacement(s): {', '.join(info['locations'])}\n"
        result += f"ℹ️ {info['access']}"
        
        return result
    
    def _general_navigation_help(self) -> str:
        """Aide générale à la navigation"""
        return """
🧭 *Aide à la navigation*

*Commandes disponibles:*
* "plan" ou "carte" → Afficher le plan du salon
* "stand X" → Localiser un stand spécifique
* "toilettes" → Trouver les toilettes
* "restaurant" → Espace restauration
* "accueil" → Bureau d'information
* "sortie" → Sorties et parking

*Zones du salon:*
🏢 Zone A - Hall Principal (Accueil)
💻 Zone B - Technologie 
🤝 Zone C - Services
🔬 Zone D - Innovation
🍽️ Zone E - Restauration

*Services:*
* Personnel d'accueil disponible en permanence
* Wifi gratuit dans tout le salon
* Parking gratuit (500 places)
* Restauration ouverte 8h-18h
        """

class ProximityTool(BaseTool):
    """Outil pour trouver les stands ou services à proximité"""
    
    name = "proximity"
    description = "Trouve les exposants ou services proches d'un point donné"
    
    def _init_(self, salon_data: Salon):
        super()._init_()
        self.salon_data = salon_data
    
    def _run(self, location: str) -> str:
        """Trouve ce qui est proche d'un emplacement"""
        location_lower = location.lower().strip()
        
        # Déterminer la zone de référence
        reference_zone = self._parse_location(location_lower)
        
        if not reference_zone:
            return f"Emplacement '{location}' non reconnu. Utilisez un numéro de stand ou une zone (A, B, C, D, E)."
        
        return self._get_nearby_info(reference_zone)
    
    def _parse_location(self, location: str) -> Optional[str]:
        """Parse l'emplacement pour déterminer la zone"""
        # Si c'est directement une zone
        if location.upper() in ['A', 'B', 'C', 'D', 'E']:
            return location.upper()
        
        # Si c'est un stand
        for exhibitor in self.salon_data.exhibitors:
            if exhibitor.booth_number.lower() in location:
                return exhibitor.booth_number[0].upper()
        
        # Recherche par mots-clés
        zone_keywords = {
            'A': ['accueil', 'entrée', 'principal'],
            'B': ['technologie', 'tech', 'démonstration'],
            'C': ['service', 'détente'],
            'D': ['innovation', 'laboratoire', 'labo'],
            'E': ['restaurant', 'café', 'manger', 'toilettes']
        }
        
        for zone, keywords in zone_keywords.items():
            if any(keyword in location for keyword in keywords):
                return zone
        
        return None
    
    def _get_nearby_info(self, zone: str) -> str:
        """Retourne les informations de proximité pour une zone"""
        zone_names = {
            'A': 'Hall Principal',
            'B': 'Technologie', 
            'C': 'Services',
            'D': 'Innovation',
            'E': 'Restauration'
        }
        
        result = f"📍 *À proximité de la Zone {zone} - {zone_names[zone]}*\n\n"
        
        # Exposants de cette zone
        zone_exhibitors = [e for e in self.salon_data.exhibitors if e.booth_number.startswith(zone)]
        
        if zone_exhibitors:
            result += f"🏢 *Exposants dans cette zone* ({len(zone_exhibitors)})\n"
            for exhibitor in zone_exhibitors[:5]:
                result += f"• {exhibitor.name} - Stand {exhibitor.booth_number}\n"
            
            if len(zone_exhibitors) > 5:
                result += f"... et {len(zone_exhibitors) - 5} autres\n"
            result += "\n"
        
        # Services à proximité
        services = self._get_zone_services(zone)
        if services:
            result += f"🎯 *Services disponibles*\n"
            for service in services:
                result += f"• {service}\n"
            result += "\n"
        
        # Zones adjacentes
        adjacent_zones = self._get_adjacent_zones(zone)
        if adjacent_zones:
            result += f"🚶 *Zones proches*\n"
            for adj_zone, distance in adjacent_zones:
                result += f"• Zone {adj_zone} - {zone_names[adj_zone]} ({distance})\n"
        
        return result
    
    def _get_zone_services(self, zone: str) -> List[str]:
        """Retourne les services disponibles dans une zone"""
        services_map = {
            'A': ['🏢 Accueil et information', '🚻 Toilettes', '📱 Point wifi'],
            'B': ['🖥️ Démonstrations technologiques', '⚡ Prises électriques'],
            'C': ['🛋️ Espace détente', '📞 Cabines téléphoniques'],
            'D': ['🔬 Laboratoire de test', '🔋 Station de recharge'],
            'E': ['🍽️ Restaurant', '☕ Café', '🚻 Toilettes', '🧴 Distributeurs']
        }
        
        return services_map.get(zone, [])
    
    def _get_adjacent_zones(self, zone: str) -> List[Tuple[str, str]]:
        """Retourne les zones adjacentes avec distance estimée"""
        adjacency_map = {
            'A': [('B', '50m'), ('C', '80m')],
            'B': [('A', '50m'), ('C', '30m'), ('D', '60m')],
            'C': [('A', '80m'), ('B', '30m'), ('D', '40m'), ('E', '70m')],
            'D': [('B', '60m'), ('C', '40m'), ('E', '50m')],
            'E': [('C', '70m'), ('D', '50m')]
        }
        
        return adjacency_map.get(zone, [])

class PathFindingTool(BaseTool):
    """Outil pour calculer les itinéraires optimaux"""
    
    name = "pathfinding"
    description = "Calcule l'itinéraire optimal entre deux points du salon"
    
    def _init_(self, salon_data: Salon):
        super()._init_()
        self.salon_data = salon_data
    
    def _run(self, route_query: str) -> str:
        """Calcule un itinéraire entre deux points"""
        # Parse "de X à Y" ou "X vers Y"
        route_query = route_query.lower().strip()
        
        if " à " in route_query:
            parts = route_query.split(" à ")
            start = parts[0].replace("de ", "").strip()
            end = parts[1].strip()
        elif " vers " in route_query:
            parts = route_query.split(" vers ")
            start = parts[0].strip()
            end = parts[1].strip()
        else:
            return "Format: 'de [point A] à [point B]' ou '[point A] vers [point B]'"
        
        # Déterminer les zones
        start_zone = self._location_to_zone(start)
        end_zone = self._location_to_zone(end)
        
        if not start_zone or not end_zone:
            return "Un des points n'a pas pu être localisé. Vérifiez les noms."
        
        return self._calculate_route(start, start_zone, end, end_zone)
    
    def _location_to_zone(self, location: str) -> Optional[str]:
        """Convertit un emplacement en zone"""
        # Direct zone reference
        if location.upper() in ['A', 'B', 'C', 'D', 'E']:
            return location.upper()
        
        # Booth number
        for exhibitor in self.salon_data.exhibitors:
            if (location in exhibitor.name.lower() or 
                location in exhibitor.booth_number.lower()):
                return exhibitor.booth_number[0].upper()
        
        # Keywords
        zone_keywords = {
            'A': ['accueil', 'entrée', 'principal'],
            'B': ['technologie', 'tech'],
            'C': ['service'],
            'D': ['innovation', 'labo'],
            'E': ['restaurant', 'café', 'toilettes']
        }
        
        for zone, keywords in zone_keywords.items():
            if any(keyword in location for keyword in keywords):
                return zone
        
        return None
    
    def _calculate_route(self, start: str, start_zone: str, end: str, end_zone: str) -> str:
        """Calcule l'itinéraire optimal"""
        if start_zone == end_zone:
            return f"📍 *Itinéraire court* : {start} → {end}\n\nVous êtes dans la même zone ! Distance estimée : 20-30m"
        
        # Routes prédéfinies entre zones
        routes = {
            ('A', 'B'): ['Zone A', 'Zone B'],
            ('A', 'C'): ['Zone A', 'Zone B', 'Zone C'],
            ('A', 'D'): ['Zone A', 'Zone B', 'Zone C', 'Zone D'],
            ('A', 'E'): ['Zone A', 'Zone B', 'Zone C', 'Zone E'],
            ('B', 'C'): ['Zone B', 'Zone C'],
            ('B', 'D'): ['Zone B', 'Zone C', 'Zone D'],
            ('B', 'E'): ['Zone B', 'Zone C', 'Zone E'],
            ('C', 'D'): ['Zone C', 'Zone D'],
            ('C', 'E'): ['Zone C', 'Zone E'],
            ('D', 'E'): ['Zone D', 'Zone E']
        }
        
        # Chemin direct ou inverse
        path = routes.get((start_zone, end_zone)) or list(reversed(routes.get((end_zone, start_zone), [])))
        
        if not path:
            return "Itinéraire non calculable"
        
        result = f"🗺️ *Itinéraire : {start} → {end}*\n\n"
        result += f"📍 Départ : {start} (Zone {start_zone})\n"
        result += f"🎯 Arrivée : {end} (Zone {end_zone})\n\n"
        
        result += "👣 *Étapes :*\n"
        for i, step in enumerate(path):
            if i == len(path) - 1:
                result += f"{i+1}. Arrivée à {step}\n"
            else:
                result += f"{i+1}. Traverser {step}\n"
        
        distance = len(path) * 50  # 50m par zone
        time = len(path) * 2  # 2 min par zone
        
        result += f"\n⏱️ Temps estimé : {time} minutes\n"
        result += f"📏 Distance : ~{distance}m"
        
        return result