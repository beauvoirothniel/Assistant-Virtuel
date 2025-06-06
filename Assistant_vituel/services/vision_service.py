import cv2
import numpy as np
import asyncio
import logging
from typing import Optional, List, Tuple, Dict
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

from app.config import settings
from app.utils.exceptions import VisionServiceError
from app.utils.logger import setup_logger

logger = setup_logger(_name_)

class VisionService:
    def _init_(self):
        self.camera = None
        self.face_cascade = None
        self.is_running = False
        self._load_classifiers()
    
    def _load_classifiers(self):
        """Charge les classificateurs OpenCV"""
        try:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            logger.info("✅ Vision classifiers loaded")
        except Exception as e:
            logger.error(f"❌ Failed to load classifiers: {e}")
            raise VisionServiceError(f"Classifier loading failed: {e}")
    
    def start_camera(self, camera_index: int = None) -> bool:
        """Démarre la caméra"""
        try:
            index = camera_index or settings.CAMERA_INDEX
            self.camera = cv2.VideoCapture(index)
            
            if not self.camera.isOpened():
                raise VisionServiceError(f"Cannot open camera {index}")
            
            # Configuration de la caméra
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_running = True
            logger.info(f"✅ Camera {index} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Camera start failed: {e}")
            return False
    
    def stop_camera(self):
        """Arrête la caméra"""
        if self.camera:
            self.camera.release()
            self.is_running = False
            cv2.destroyAllWindows()
            logger.info("📷 Camera stopped")
    
    def is_camera_available(self) -> bool:
        """Vérifie si la caméra est disponible"""
        return self.camera is not None and self.camera.isOpened()
    
    async def detect_visitors_async(self) -> Dict[str, any]:
        """Détection asynchrone des visiteurs"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.detect_visitors)
    
    def detect_visitors(self) -> Dict[str, any]:
        """Détecte les visiteurs dans le champ de vision"""
        if not self.is_camera_available():
            return {"count": 0, "faces": [], "error": "Camera not available"}
        
        try:
            ret, frame = self.camera.read()
            if not ret:
                return {"count": 0, "faces": [], "error": "Failed to capture frame"}
            
            # Conversion en niveaux de gris
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Détection des visages
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Analyse des visages détectés
            face_data = []
            for (x, y, w, h) in faces:
                face_info = {
                    "position": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                    "confidence": self._calculate_face_confidence(gray[y:y+h, x:x+w]),
                    "timestamp": datetime.now().isoformat()
                }
                face_data.append(face_info)
            
            return {
                "count": len(faces),
                "faces": face_data,
                "frame_size": {"width": frame.shape[1], "height": frame.shape[0]},
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Visitor detection failed: {e}")
            return {"count": 0, "faces": [], "error": str(e)}
    
    def _calculate_face_confidence(self, face_roi) -> float:
        """Calcule un score de confiance pour la détection de visage"""
        try:
            # Analyse de la variance (plus élevée = plus de détails)
            variance = np.var(face_roi)
            # Score normalisé entre 0 et 1
            confidence = min(variance / 1000.0, 1.0)
            return round(confidence, 2)
        except:
            return 0.5
    
    async def capture_scene_async(self) -> Optional[str]:
        """Capture asynchrone de la scène"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.capture_scene)
    
    def capture_scene(self) -> Optional[str]:
        """Capture la scène actuelle en base64"""
        if not self.is_camera_available():
            return None
        
        try:
            ret, frame = self.camera.read()
            if not ret:
                return None
            
            # Encoder en JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            # Convertir en base64
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return img_base64
            
        except Exception as e:
            logger.error(f"❌ Scene capture failed: {e}")
            return None
    
    def analyze_crowd_density(self, frame=None) -> Dict[str, any]:
        """Analyse la densité de la foule"""
        if frame is None:
            if not self.is_camera_available():
                return {"density": "unknown", "level": 0}
            
            ret, frame = self.camera.read()
            if not ret:
                return {"density": "unknown", "level": 0}
        
        try:
            # Détection des personnes (approximation avec les visages)
            visitor_data = self.detect_visitors()
            face_count = visitor_data["count"]
            
            # Classification de la densité
            if face_count == 0:
                density = "empty"
                level = 0
            elif face_count <= 2:
                density = "low"
                level = 1
            elif face_count <= 5:
                density = "medium"
                level = 2
            elif face_count <= 10:
                density = "high"
                level = 3
            else:
                density = "very_high"
                level = 4
            
            return {
                "density": density,
                "level": level,
                "face_count": face_count,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Crowd analysis failed: {e}")
            return {"density": "unknown", "level": 0, "error": str(e)}
