class AIAssistantError(Exception):
    """Exception de base pour l'application"""
    pass

class VoiceServiceError(AIAssistantError):
    """Erreur du service vocal"""
    pass

class VisionServiceError(AIAssistantError):
    """Erreur du service de vision"""
    pass

class AgentError(AIAssistantError):
    """Erreur de l'agent IA"""
    pass

class DatabaseError(AIAssistantError):
    """Erreur de base de données"""
    pass