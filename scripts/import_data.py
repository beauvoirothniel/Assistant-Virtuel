#!/usr/bin/env python3
"""
Script d'import de données depuis des fichiers CSV/JSON
Usage: python scripts/import_data.py --file data/salon_data.json
"""

import sys
import os
import argparse
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(_file_))))

from app.models.database import SessionLocal
from app.models.salon import SalonDB, ExhibitorDB, EventDB
from app.utils.helpers import load_json_file
from app.utils.logger import setup_logger
from datetime import datetime

logger = setup_logger(_name_)

def import_from_json(file_path: str):
    """Importe les données depuis un fichier JSON"""
    data = load_json_file(file_path)
    db = SessionLocal()
    
    try:
        # Créer le salon
        salon_data = data.get('salon', {})
        salon = SalonDB(
            name=salon_data.get('name', 'Salon Sans Nom'),
            date=datetime.fromisoformat(salon_data.get('date', datetime.now().isoformat())),
            venue=salon_data.get('venue', ''),
            description=salon_data.get('description', '')
        )
        db.add(salon)
        db.commit()
        db.refresh(salon)
        
        # Importer les exposants
        exhibitors_data = data.get('exhibitors', [])
        for exhibitor_data in exhibitors_data:
            exhibitor = ExhibitorDB(
                salon_id=salon.id,
                name=exhibitor_data.get('name', ''),
                category=exhibitor_data.get('category', ''),
                booth_number=exhibitor_data.get('booth_number', ''),
                description=exhibitor_data.get('description', ''),
                contact_person=exhibitor_data.get('contact_person', ''),
                location_x=exhibitor_data.get('location', {}).get('x', 0.0),
                location_y=exhibitor_data.get('location', {}).get('y', 0.0),
                logo_path=exhibitor_data.get('logo_path')
            )
            db.add(exhibitor)
        
        db.commit()
        logger.info(f"✅ Imported {len(exhibitors_data)} exhibitors")
        
        # Importer les événements
        events_data = data.get('events', [])
        for event_data in events_data:
            event = EventDB(
                salon_id=salon.id,
                title=event_data.get('title', ''),
                start_time=datetime.fromisoformat(event_data.get('start_time')),
                end_time=datetime.fromisoformat(event_data.get('end_time')),
                location=event_data.get('location', ''),
                speaker=event_data.get('speaker', ''),
                description=event_data.get('description', ''),
                category=event_data.get('category', '')
            )
            db.add(event)
        
        db.commit()
        logger.info(f"✅ Imported {len(events_data)} events")
        
        print(f"🎉 Data imported successfully for salon: {salon.name}")
        
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def import_from_csv(file_path: str, data_type: str):
    """Importe les données depuis un fichier CSV"""
    try:
        df = pd.read_csv(file_path)
        logger.info(f"📊 Loading CSV with {len(df)} rows")
        
        if data_type == 'exhibitors':
            import_exhibitors_from_df(df)
        elif data_type == 'events':
            import_events_from_df(df)
        else:
            raise ValueError(f"Unknown data type: {data_type}")
            
    except Exception as e:
        logger.error(f"❌ CSV import failed: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Import salon data')
    parser.add_argument('--file', required=True, help='File path to import')
    parser.add_argument('--type', choices=['json', 'csv'], default='json', help='File type')
    parser.add_argument('--data-type', choices=['exhibitors', 'events'], help='Data type for CSV import')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        sys.exit(1)
    
    try:
        if args.type == 'json':
            import_from_json(args.file)
        elif args.type == 'csv':
            if not args.data_type:
                print("❌ --data-type required for CSV import")
                sys.exit(1)
            import_from_csv(args.file, args.data_type)
            
    except Exception as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)

if _name_ == "_main_":
    main()
