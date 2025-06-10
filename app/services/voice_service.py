import asyncio
import logging
from typing import Optional
import speech_recognition as sr
import pyttsx3
from app.config import settings
from app.utils.exceptions import VoiceServiceError

logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self._setup_voice()
        self._is_listening = False
    
    def _setup_voice(self):
        """Configure la voix de synthèse"""
        try:
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            self.tts_engine.setProperty('rate', settings.VOICE_RATE)
            self.tts_engine.setProperty('volume', settings.VOICE_VOLUME)
            logger.info("Voice service configured successfully")
        except Exception as e:
            logger.error(f"Error configuring voice service: {e}")
            raise VoiceServiceError(f"Voice configuration failed: {e}")
    
    async def listen_async(self, timeout: int = 5) -> Optional[str]:
        """Écoute asynchrone"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._listen_sync, timeout)
    
    def _listen_sync(self, timeout: int) -> Optional[str]:
        """Écoute synchrone (pour l'executor)"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info("🎤 Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            text = self.recognizer.recognize_google(
                audio, 
                language=settings.VOICE_LANGUAGE
            )
            logger.info(f"👤 Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            raise VoiceServiceError(f"Recognition failed: {e}")
    
    async def speak_async(self, text: str):
        """Synthèse vocale asynchrone"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._speak_sync, text)
    
    def _speak_sync(self, text: str):
        """Synthèse vocale synchrone"""
        try:
            logger.info(f"🤖 Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS error: {e}")
            raise VoiceServiceError(f"Speech synthesis failed: {e}")