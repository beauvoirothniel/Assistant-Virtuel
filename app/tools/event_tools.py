from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from langchain.tools import BaseTool
from app.models.salon import Salon, Event
from app.utils.logger import setup_logger

logger = setup_logger(_name_)

class EventScheduleTool(BaseTool):
    """Outil pour consulter le programme des événements"""
    
    name = "event_schedule"
    description = "Récupère le programme des événements du salon avec filtrage par date/heure"
    
    def _init_(self, salon_data: Salon):
        super()._init_()
        self.salon_data = salon_data
    
    def _run(self, query: str = "today") -> str:
        """Retourne le programme des événements"""
        query_lower = query.lower().strip()
        
        if query_lower in ["today", "aujourd'hui", "maintenant"]:
            return self._get_today_events()
        elif query_lower in ["all", "tous", "complet"]:
            return self._get_all_events()
        elif "demain" in query_lower:
            return self._get_tomorrow_events()
        else:
            return self._search_events(query)
    
    def _get_today_events(self) -> str:
        """Événements d'aujourd'hui"""
        now = datetime.now()
        today_events = []
        
        for event in self.salon_data.events:
            if event.start_time.date() == now.date():
                today_events.append(event)
        
        if not today_events:
            return "📅 Aucun événement prévu aujourd'hui."
        
        # Trier par heure
        today_events.sort(key=lambda x: x.start_time)
        
        result = f"📅 *Programme d'aujourd'hui* ({len(today_events)} événements)\n\n"
        
        for event in today_events:
            status = self._get_event_status(event)
            result += f"{status} *{event.title}*\n"
            result += f"   🕐 {event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}\n"
            result += f"   📍 {event.location}\n"
            result += f"   👤 {event.speaker}\n"
            result += f"   📝 {event.description[:80]}...\n\n"
        
        return result
    
    def _get_all_events(self) -> str:
        """Tous les événements du salon"""
        if not self.salon_data.events:
            return "📅 Aucun événement programmé pour ce salon."
        
        # Grouper par jour
        events_by_day = {}
        for event in self.salon_data.events:
            day_key = event.start_time.strftime('%Y-%m-%d')
            if day_key not in events_by_day:
                events_by_day[day_key] = []
            events_by_day[day_key].append(event)
        
        result = f"📅 *Programme complet* ({len(self.salon_data.events)} événements)\n\n"
        
        for day_key, events in sorted(events_by_day.items()):
            day_date = datetime.strptime(day_key, '%Y-%m-%d')
            result += f"📆 *{day_date.strftime('%A %d/%m/%Y')}*\n"
            
            # Trier par heure
            events.sort(key=lambda x: x.start_time)
            
            for event in events:
                result += f"  🕐 {event.start_time.strftime('%H:%M')} - *{event.title}*\n"
                result += f"     📍 {event.location} • 👤 {event.speaker}\n"
            result += "\n"
        
        return result
    
    def _get_tomorrow_events(self) -> str:
        """Événements de demain"""
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_events = []
        
        for event in self.salon_data.events:
            if event.start_time.date() == tomorrow.date():
                tomorrow_events.append(event)
        
        if not tomorrow_events:
            return "📅 Aucun événement prévu demain."
        
        tomorrow_events.sort(key=lambda x: x.start_time)
        
        result = f"📅 *Programme de demain* ({len(tomorrow_events)} événements)\n\n"
        
        for event in tomorrow_events:
            result += f"🕐 *{event.title}*\n"
            result += f"   ⏰ {event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}\n"
            result += f"   📍 {event.location}\n"
            result += f"   👤 {event.speaker}\n\n"
        
        return result
    
    def _search_events(self, query: str) -> str:
        """Recherche d'événements par mots-clés"""
        matching_events = []
        query_words = query.lower().split()
        
        for event in self.salon_data.events:
            score = 0
            
            # Recherche dans le titre
            for word in query_words:
                if word in event.title.lower():
                    score += 3
                if word in event.description.lower():
                    score += 2
                if word in event.speaker.lower():
                    score += 1
                if word in event.category.lower():
                    score += 1
            
            if score > 0:
                matching_events.append((event, score))
        
        if not matching_events:
            return f"Aucun événement trouvé pour '{query}'"
        
        matching_events.sort(key=lambda x: x[1], reverse=True)
        
        result = f"🔍 *Événements trouvés pour '{query}'* ({len(matching_events)} résultats)\n\n"
        
        for event, score in matching_events:
            status = self._get_event_status(event)
            result += f"{status} *{event.title}*\n"
            result += f"   🕐 {event.start_time.strftime('%d/%m %H:%M')} - {event.end_time.strftime('%H:%M')}\n"
            result += f"   📍 {event.location} • 👤 {event.speaker}\n"
            result += f"   🏷️ {event.category}\n\n"
        
        return result
    
    def _get_event_status(self, event: Event) -> str:
        """Détermine le statut de l'événement"""
        now = datetime.now()
        
        if now < event.start_time:
            delta = event.start_time - now
            if delta.total_seconds() < 3600:  # Moins d'1h
                return "🔜"
            else:
                return "⏳"
        elif event.start_time <= now <= event.end_time:
            return "🔴"  # En cours
        else:
            return "✅"  # Terminé

class EventReminderTool(BaseTool):
    """Outil pour les rappels d'événements"""
    
    name = "event_reminder"
    description = "Gère les rappels et notifications pour les événements à venir"
    
    def _init_(self, salon_data: Salon):
        super()._init_()
        self.salon_data = salon_data
    
    def _run(self, timeframe: str = "30min") -> str:
        """Retourne les événements à venir dans la période spécifiée"""
        now = datetime.now()
        
        # Analyser la période
        minutes = self._parse_timeframe(timeframe)
        target_time = now + timedelta(minutes=minutes)
        
        upcoming_events = []
        
        for event in self.salon_data.events:
            if now <= event.start_time <= target_time:
                upcoming_events.append(event)
        
        if not upcoming_events:
            return f"Aucun événement dans les {minutes} prochaines minutes."
        
        upcoming_events.sort(key=lambda x: x.start_time)
        
        result = f"⏰ *Événements à venir* (dans les {minutes} prochaines minutes)\n\n"
        
        for event in upcoming_events:
            time_until = event.start_time - now
            minutes_until = int(time_until.total_seconds() / 60)
            
            result += f"🔔 *{event.title}*\n"
            result += f"   ⏰ Dans {minutes_until} minutes ({event.start_time.strftime('%H:%M')})\n"
            result += f"   📍 {event.location}\n"
            result += f"   👤 {event.speaker}\n\n"
        
        return result
    
    def _parse_timeframe(self, timeframe: str) -> int:
        """Parse la période en minutes"""
        timeframe = timeframe.lower().strip()
        
        if "30min" in timeframe or "30 min" in timeframe:
            return 30
        elif "1h" in timeframe or "1 heure" in timeframe:
            return 60
        elif "2h" in timeframe or "2 heures" in timeframe:
            return 120
        elif timeframe.endswith("min"):
            try:
                return int(timeframe.replace("min", ""))
            except:
                return 30
        else:
            return 30

class EventCategoryTool(BaseTool):
    """Outil pour filtrer les événements par catégorie"""
    
    name = "event_category"
    description = "Filtre et liste les événements par catégorie (conférence, atelier, démonstration, etc.)"
    
    def _init_(self, salon_data: Salon):
        super()._init_()
        self.salon_data = salon_data
    
    def _run(self, category: str = "all") -> str:
        """Filtre les événements par catégorie"""
        if category.lower() in ["all", "tous"]:
            return self._list_all_categories()
        else:
            return self._filter_by_category(category)
    
    def _list_all_categories(self) -> str:
        """Liste toutes les catégories d'événements"""
        categories = {}
        
        for event in self.salon_data.events:
            if event.category not in categories:
                categories[event.category] = []
            categories[event.category].append(event)
        
        if not categories:
            return "Aucune catégorie d'événement disponible."
        
        result = f"🏷️ *Catégories d'événements* ({len(categories)} catégories)\n\n"
        
        for category, events in categories.items():
            result += f"📂 *{category}* ({len(events)} événements)\n"
            
            # Afficher les 3 prochains événements de cette catégorie
            upcoming = [e for e in events if e.start_time > datetime.now()]
            upcoming.sort(key=lambda x: x.start_time)
            
            for event in upcoming[:3]:
                result += f"   • {event.title} - {event.start_time.strftime('%d/%m %H:%M')}\n"
            
            if len(upcoming) > 3:
                result += f"   ... et {len(upcoming) - 3} autres\n"
            
            result += "\n"
        
        return result
    
    def _filter_by_category(self, category: str) -> str:
        """Filtre les événements par catégorie spécifique"""
        category_lower = category.lower()
        matching_events = []
        
        for event in self.salon_data.events:
            if category_lower in event.category.lower():
                matching_events.append(event)
        
        if not matching_events:
            return f"Aucun événement trouvé dans la catégorie '{category}'"
        
        # Séparer passés et à venir
        now = datetime.now()
        upcoming = [e for e in matching_events if e.start_time > now]
        past = [e for e in matching_events if e.start_time <= now]
        
        upcoming.sort(key=lambda x: x.start_time)
        past.sort(key=lambda x: x.start_time, reverse=True)
        
        result = f"🏷️ *Événements - {category}* ({len(matching_events)} total)\n\n"
        
        if upcoming:
            result += f"🔮 *À venir* ({len(upcoming)})\n"
            for event in upcoming:
                result += f"  🕐 {event.start_time.strftime('%d/%m %H:%M')} - *{event.title}*\n"
                result += f"     📍 {event.location} • 👤 {event.speaker}\n"
            result += "\n"
        
        if past:
            result += f"✅ *Passés* ({len(past)})\n"
            for event in past[:5]:  # Afficher les 5 derniers
                result += f"  🕐 {event.start_time.strftime('%d/%m %H:%M')} - *{event.title}*\n"
            
            if len(past) > 5:
                result += f"  ... et {len(past) - 5} autres événements passés\n"
        
        return result