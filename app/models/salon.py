from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

class ExhibitorCategory(str, Enum):
    """Catégories d'exposants"""
    TECHNOLOGY = "Technologie"
    SERVICES = "Services"
    INNOVATION = "Innovation"
    CONSULTING = "Conseil"
    MANUFACTURING = "Manufacturing"
    STARTUP = "Startup"
    OTHER = "Autre"

class EventCategory(str, Enum):
    """Catégories d'événements"""
    CONFERENCE = "Conférence"
    WORKSHOP = "Atelier"
    DEMONSTRATION = "Démonstration"
    NETWORKING = "Networking"
    KEYNOTE = "Keynote"
    PANEL = "Table ronde"
    OTHER = "Autre"

class Exhibitor(BaseModel):
    """Modèle pour un exposant"""
    id: str = Field(..., description="Identifiant unique de l'exposant")
    name: str = Field(..., description="Nom de l'entreprise")
    booth_number: str = Field(..., description="Numéro de stand")
    category: ExhibitorCategory = Field(..., description="Catégorie d'activité")
    description: str = Field(..., description="Description de l'entreprise")
    contact_person: str = Field(..., description="Personne de contact")
    email: Optional[str] = Field(None, description="Email de contact")
    phone: Optional[str] = Field(None, description="Téléphone")
    website: Optional[str] = Field(None, description="Site web")
    special_offers: List[str] = Field(default_factory=list, description="Offres spéciales")
    tags: List[str] = Field(default_factory=list, description="Mots-clés")
    logo_url: Optional[str] = Field(None, description="URL du logo")
    is_sponsor: bool = Field(default=False, description="Est-ce un sponsor")
    sponsor_level: Optional[str] = Field(None, description="Niveau de sponsoring")
    
    @validator('booth_number')
    def validate_booth_number(cls, v):
        if not v or len(v) < 2:
            raise ValueError('Numéro de stand invalide')
        return v.upper()
    
    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Email invalide')
        return v
    
    class Config:
        use_enum_values = True

class Event(BaseModel):
    """Modèle pour un événement"""
    id: str = Field(..., description="Identifiant unique de l'événement")
    title: str = Field(..., description="Titre de l'événement")
    description: str = Field(..., description="Description détaillée")
    category: EventCategory = Field(..., description="Catégorie d'événement")
    speaker: str = Field(..., description="Intervenant principal")
    additional_speakers: List[str] = Field(default_factory=list, description="Autres intervenants")
    start_time: datetime = Field(..., description="Heure de début")
    end_time: datetime = Field(..., description="Heure de fin")
    location: str = Field(..., description="Lieu/Salle")
    capacity: Optional[int] = Field(None, description="Capacité maximale")
    registration_required: bool = Field(default=False, description="Inscription obligatoire")
    registration_url: Optional[str] = Field(None, description="URL d'inscription")
    tags: List[str] = Field(default_factory=list, description="Mots-clés")
    language: str = Field(default="Français", description="Langue de l'événement")
    level: str = Field(default="Tout public", description="Niveau requis")
    organizer: Optional[str] = Field(None, description="Organisateur")
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('Heure de fin doit être après heure de début')
        return v
    
    @property
    def duration_minutes(self) -> int:
        """Durée en minutes"""
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    @property
    def is_now(self) -> bool:
        """Vérifie si l'événement est en cours"""
        now = datetime.now()
        return self.start_time <= now <= self.end_time
    
    @property
    def is_upcoming(self) -> bool:
        """Vérifie si l'événement est à venir"""
        return self.start_time > datetime.now()
    
    class Config:
        use_enum_values = True

class Venue(BaseModel):
    """Modèle pour le lieu du salon"""
    name: str = Field(..., description="Nom du lieu")
    address: str = Field(..., description="Adresse complète")
    city: str = Field(..., description="Ville")
    postal_code: str = Field(..., description="Code postal")
    country: str = Field(default="France", description="Pays")
    coordinates: Optional[Dict[str, float]] = Field(None, description="Coordonnées GPS")
    capacity: Optional[int] = Field(None, description="Capacité totale")
    facilities: List[str] = Field(default_factory=list, description="Équipements disponibles")
    parking_info: Optional[str] = Field(None, description="Informations parking")
    public_transport: Optional[str] = Field(None, description="Transports en commun")
    
    @property
    def full_address(self) -> str:
        """Adresse complète formatée"""
        return f"{self.address}, {self.postal_code} {self.city}, {self.country}"

class SalonStats(BaseModel):
    """Statistiques du salon"""
    total_exhibitors: int = Field(default=0, description="Nombre total d'exposants")
    total_events: int = Field(default=0, description="Nombre total d'événements")
    expected_visitors: Optional[int] = Field(None, description="Visiteurs attendus")
    total_area_sqm: Optional[int] = Field(None, description="Surface totale en m²")
    opening_hours: Dict[str, str] = Field(default_factory=dict, description="Horaires d'ouverture")
    last_updated: datetime = Field(default_factory=datetime.now, description="Dernière mise à jour")

class Salon(BaseModel):
    """Modèle principal pour un salon professionnel"""
    id: str = Field(..., description="Identifiant unique du salon")
    name: str = Field(..., description="Nom du salon")
    description: str = Field(..., description="Description du salon")
    theme: Optional[str] = Field(None, description="Thème principal")
    date: datetime = Field(..., description="Date de début du salon")
    end_date: Optional[datetime] = Field(None, description="Date de fin")
    venue: Venue = Field(..., description="Lieu du salon")
    exhibitors: List[Exhibitor] = Field(default_factory=list, description="Liste des exposants")
    events: List[Event] = Field(default_factory=list, description="Programme des événements")
    organizer: str = Field(..., description="Organisateur principal")
    contact_email: str = Field(..., description="Email de contact")
    website: Optional[str] = Field(None, description="Site web officiel")
    social_media: Dict[str, str] = Field(default_factory=dict, description="Réseaux sociaux")
    registration_info: Optional[str] = Field(None, description="Informations d'inscription")
    entry_fee: Optional[str] = Field(None, description="Tarif d'entrée")
    stats: SalonStats = Field(default_factory=SalonStats, description="Statistiques")
    is_active: bool = Field(default=True, description="Salon actif")
    created_at: datetime = Field(default_factory=datetime.now, description="Date de création")
    updated_at: datetime = Field(default_factory=datetime.now, description="Dernière modification")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'date' in values and v <= values['date']:
            raise ValueError('Date de fin doit être après la date de début')
        return v
    
    @property
    def duration_days(self) -> int:
        """Durée du salon en jours"""
        if self.end_date:
            return (self.end_date - self.date).days + 1
        return 1
    
    @property
    def is_ongoing(self) -> bool:
        """Vérifie si le salon est en cours"""
        now = datetime.now()
        end = self.end_date or self.date
        return self.date <= now <= end
    
    @property
    def is_upcoming(self) -> bool:
        """Vérifie si le salon est à venir"""
        return self.date > datetime.now()
    
    def get_exhibitor_by_booth(self, booth_number: str) -> Optional[Exhibitor]:
        """Trouve un exposant par numéro de stand"""
        for exhibitor in self.exhibitors:
            if exhibitor.booth_number.upper() == booth_number.upper():
                return exhibitor
        return None
    
    def get_exhibitors_by_category(self, category: ExhibitorCategory) -> List[Exhibitor]:
        """Filtre les exposants par catégorie"""
        return [e for e in self.exhibitors if e.category == category]
    
    def get_events_by_date(self, date: datetime) -> List[Event]:
        """Filtre les événements par date"""
        return [e for e in self.events if e.start_time.date() == date.date()]
    
    def get_current_events(self) -> List[Event]:
        """Retourne les événements en cours"""
        return [e for e in self.events if e.is_now]
    
    def get_upcoming_events(self, hours: int = 24) -> List[Event]:
        """Retourne les événements à venir dans les X heures"""
        now = datetime.now()
        cutoff = now + timedelta(hours=hours)
        return [e for e in self.events if now < e.start_time <= cutoff]
    
    def update_stats(self):
        """Met à jour les statistiques du salon"""
        self.stats.total_exhibitors = len(self.exhibitors)
        self.stats.total_events = len(self.events)
        self.stats.last_updated = datetime.now()
        self.updated_at = datetime.now()
    
    def search_exhibitors(self, query: str) -> List[Exhibitor]:
        """Recherche d'exposants par mots-clés"""
        query_lower = query.lower()
        results = []
        
        for exhibitor in self.exhibitors:
            score = 0
            
            # Recherche dans le nom (priorité haute)
            if query_lower in exhibitor.name.lower():
                score += 5
            
            # Recherche dans la description
            if query_lower in exhibitor.description.lower():
                score += 3
            
            # Recherche dans les tags
            for tag in exhibitor.tags:
                if query_lower in tag.lower():
                    score += 2
            
            # Recherche dans la catégorie
            if query_lower in exhibitor.category.lower():
                score += 1
            
            if score > 0:
                results.append((exhibitor, score))
        
        # Trier par score de pertinence
        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results]
    
    def search_events(self, query: str) -> List[Event]:
        """Recherche d'événements par mots-clés"""
        query_lower = query.lower()
        results = []
        
        for event in self.events:
            score = 0
            
            # Recherche dans le titre
            if query_lower in event.title.lower():
                score += 5
            
            # Recherche dans la description
            if query_lower in event.description.lower():
                score += 3
            
            # Recherche dans l'intervenant
            if query_lower in event.speaker.lower():
                score += 2
            
            # Recherche dans les tags
            for tag in event.tags:
                if query_lower in tag.lower():
                    score += 2
            
            # Recherche dans la catégorie
            if query_lower in event.category.lower():
                score += 1
            
            if score > 0:
                results.append((event, score))
        
        # Trier par score puis par date
        results.sort(key=lambda x: (x[1], x[0].start_time), reverse=True)
        return [r[0] for r in results]
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }