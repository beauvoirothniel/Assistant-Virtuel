from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Modèles SQLAlchemy pour la base de données
class SalonDB(Base):
    __tablename__ = "salons"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    date = Column(DateTime, nullable=False)
    venue = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    exhibitors = relationship("ExhibitorDB", back_populates="salon")
    events = relationship("EventDB", back_populates="salon")

class ExhibitorDB(Base):
    __tablename__ = "exhibitors"
    
    id = Column(Integer, primary_key=True)
    salon_id = Column(Integer, ForeignKey("salons.id"))
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    booth_number = Column(String(20))
    description = Column(Text)
    contact_person = Column(String(255))
    location_x = Column(Float)
    location_y = Column(Float)
    logo_path = Column(String(500))
    
    salon = relationship("SalonDB", back_populates="exhibitors")

# Modèles Pydantic pour l'API
class ExhibitorCreate(BaseModel):
    name: str
    category: str
    booth_number: str
    description: str
    contact_person: str
    special_offers: List[str] = []
    location: Dict[str, float] = {}
    logo_path: Optional[str] = None

class ExhibitorResponse(ExhibitorCreate):
    id: int
    
    class Config:
        from_attributes = True


### 3. Services principaux