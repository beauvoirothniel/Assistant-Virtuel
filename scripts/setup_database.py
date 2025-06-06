#!/usr/bin/env python3
"""
Script d'initialisation de la base de données
Usage: python scripts/setup_database.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(_file_))))

from app.models.database import engine, Base
from app.models.salon import SalonDB, ExhibitorDB, EventDB
from app.utils.logger import setup_logger
from datetime import datetime

logger = setup_logger(_name_)

def create_sample_data():
    """Crée des données d'exemple"""
    from app.models.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        # Créer un salon d'exemple
        salon = SalonDB(
            name="Salon de l'Innovation 2025",
            date=datetime.now(),
            venue="Centre des Congrès de Brazzaville",
            description="Le plus grand salon technologique du Congo"
        )
        db.add(salon)
        db.commit()
        
        # Créer des exposants d'exemple
        exhibitors = [
            ExhibitorDB(
                salon_id=salon.id,
                name="TechInnovation SARL",
                category="Technologie",
                booth_number="A12",
                description="Solutions innovantes en IA et IoT",
                contact_person="Marie Dubois",
                location_x=12.0,
                location_y=5.0
            ),
            ExhibitorDB(
                salon_id=salon.id,
                name="EcoFuture",
                category="Environnement",
                booth_number="B08",
                description="Solutions durables pour l'avenir",
                contact_person="Jean Martin",
                location_x=8.0,
                location_y=3.0
            )
        ]
        
        for exhibitor in exhibitors:
            db.add(exhibitor)
        
        db.commit()
        
        logger.info("✅ Sample data created successfully")
        print("Base de données initialisée avec des données d'exemple")
        
    except Exception as e:
        logger.error(f"❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Fonction principale"""
    try:
        logger.info("🗄️ Initializing database...")
        
        # Créer toutes les tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables created successfully")
        
        # Créer des données d'exemple
        create_sample_data()
        
        print("🎉 Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        sys.exit(1)

if _name_ == "_main_":
    main()