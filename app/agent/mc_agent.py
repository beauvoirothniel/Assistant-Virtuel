import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import BaseTool
from langchain.schema import HumanMessage, AIMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from app.config import settings
from app.models.salon import Salon
from app.tools.exhibitor_tools import ExhibitorInfoTool
from app.tools.event_tools import EventScheduleTool
from app.tools.navigation_tools import NavigationTool
from app.utils.logger import setup_logger
from app.utils.exceptions import AgentError

 

logger = setup_logger(_name_)

class MasterOfCeremoniesAgent:
    """Agent principal servant de maître de cérémonie"""
    
    def _init_(self, salon_data: Optional[Salon] = None):
        self.salon_data = salon_data
        self.interaction_count = 0
        self.session_stats = {
            "start_time": datetime.now(),
            "interactions": 0,
            "popular_queries": {},
            "visitor_satisfaction": []
        }
        
        # Initialiser les composants
        self._initialize_llm()
        self._initialize_memory()
        self._initialize_tools()
        self._initialize_agent()
    
    def _initialize_llm(self):
        """Initialise le modèle de langage"""
        try:
            self.llm = ChatOpenAI(
                model="gpt-4",
                temperature=0.7,
                openai_api_key=settings.OPENAI_API_KEY,
                max_tokens=500
            )
            logger.info("✅ LLM initialized successfully")
        except Exception as e:
            logger.error(f"❌ LLM initialization failed: {e}")
            raise AgentError(f"LLM setup failed: {e}")
    
    def _initialize_memory(self):
        """Initialise la mémoire conversationnelle"""
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=15,  # Garder les 15 derniers échanges
            human_prefix="Visiteur",
            ai_prefix="Assistant"
        )
        logger.info("✅ Memory initialized")
    
    def _initialize_tools(self):
        """Initialise les outils spécialisés"""
        self.tools = []
        
        if self.salon_data:
            self.tools.extend([
                ExhibitorInfoTool(self.salon_data),
                EventScheduleTool(self.salon_data),
                NavigationTool(self.salon_data)
            ])
        
        logger.info(f"✅ {len(self.tools)} tools initialized")
    
    def _initialize_agent(self):
        """Initialise l'agent avec son prompt système"""
        system_prompt = self._create_system_prompt()
        
        try:
            self.agent = create_openai_functions_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=system_prompt
            )
            
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                memory=self.memory,
                verbose=settings.DEBUG,
                max_iterations=3,
                handle_parsing_errors=True
            )
            
            logger.info("✅ Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Agent initialization failed: {e}")
            raise AgentError(f"Agent setup failed: {e}")
    
    def _create_system_prompt(self) -> ChatPromptTemplate:
        """Crée le prompt système pour l'agent"""
        salon_info = ""
        if self.salon_data:
            salon_info = f"""
            INFORMATIONS DU SALON:
            - Nom: {self.salon_data.name}
            - Date: {self.salon_data.date.strftime('%d/%m/%Y')}
            - Lieu: {self.salon_data.venue}
            - Nombre d'exposants: {len(self.salon_data.exhibitors)}
            - Nombre d'événements: {len(self.salon_data.events)}
            """
        
        return ChatPromptTemplate.from_messages([
            ("system", f"""
            Vous êtes l'assistant IA maître de cérémonie du salon professionnel.
            
            VOTRE MISSION:
            🎪 Accueillir chaleureusement tous les visiteurs
            📢 Présenter les exposants et leurs innovations
            📅 Informer sur le programme des événements
            🗺️ Guider les visiteurs dans leurs déplacements
            ⚡ Créer une ambiance dynamique et professionnelle
            
            STYLE DE COMMUNICATION:
            ✅ Professionnel mais convivial et enthousiaste
            ✅ Réponses concises et pertinentes (max 3 phrases)
            ✅ Toujours en français
            ✅ Utilisez des emojis pour dynamiser
            ✅ Posez des questions pour engager la conversation
            
            RÈGLES IMPORTANTES:
            - Soyez proactif et suggérez des activités
            - Personnalisez selon les intérêts exprimés
            - Encouragez la découverte et l'interaction
            - Restez positif et enthousiaste
            
            {salon_info}
            
            Utilisez les outils disponibles pour répondre précisément aux questions.
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
    
    async def process_interaction(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Traite une interaction avec un visiteur"""
        try:
            self.interaction_count += 1
            self.session_stats["interactions"] += 1
            
            # Ajouter du contexte si disponible
            enhanced_input = user_input
            if context:
                if context.get("visitor_count", 0) > 1:
                    enhanced_input += f" [Contexte: {context['visitor_count']} visiteurs présents]"
                if context.get("time_of_day"):
                    enhanced_input += f" [Heure: {context['time_of_day']}]"
            
            # Traitement par l'agent
            response = await self.agent_executor.ainvoke({
                "input": enhanced_input
            })
            
            # Mettre à jour les statistiques
            self._update_stats(user_input, response["output"])
            
            logger.info(f"🤖 Interaction #{self.interaction_count} processed")
            return response["output"]
            
        except Exception as e:
            logger.error(f"❌ Interaction processing failed: {e}")
            return self._get_fallback_response(user_input)
    
    def _update_stats(self, user_input: str, response: str):
        """Met à jour les statistiques d'interaction"""
        # Classifier le type de requête
        query_type = self._classify_query(user_input)
        self.session_stats["popular_queries"][query_type] = \
            self.session_stats["popular_queries"].get(query_type, 0) + 1
    
    def _classify_query(self, query: str) -> str:
        """Classifie automatiquement le type de requête"""
        query_lower = query.lower()
        
        keywords = {
            "exposants": ["exposant", "stand", "entreprise", "société", "booth"],
            "événements": ["événement", "programme", "conférence", "atelier", "horaire"],
            "navigation": ["où", "direction", "aller", "trouver", "chemin", "plan"],
            "services": ["service", "aide", "assistance", "info", "renseignement"],
            "général": []
        }
        
        for category, words in keywords.items():
            if any(word in query_lower for word in words):
                return category
        
        return "général"
    
    def _get_fallback_response(self, user_input: str) -> str:
        """Réponse de secours en cas d'erreur"""
        fallback_responses = [
            "Je vous prie de m'excuser, j'ai rencontré une petite difficulté technique. 🔧 Pouvez-vous reformuler votre question ?",
            "Désolé pour ce petit problème ! 😅 Je suis là pour vous aider - que souhaitez-vous savoir sur le salon ?",
            "Un instant s'il vous plaît... ⏳ Comment puis-je vous assister autrement ?"
        ]
        
        import random
        return random.choice(fallback_responses)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de la session"""
        duration = datetime.now() - self.session_stats["start_time"]
        
        return {
            **self.session_stats,
            "session_duration": str(duration),
            "interactions_per_hour": round(self.session_stats["interactions"] / max(duration.total_seconds() / 3600, 0.1), 1)
        }
    
    def reset_memory(self):
        """Remet à zéro la mémoire conversationnelle"""
        self.memory.clear()
        logger.info("🧹 Memory cleared")
