#!/usr/bin/env python3
"""
Script to reset and reinitialize the database with the current schema
"""
import os
import sys
from app import create_app
from models import db

def reset_database():
    """Remove old database and create new one with current schema"""
    print("🔄 Resetting database...")
    
    # Remove old database file
    db_path = 'instance/todo.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✅ Removed old database: {db_path}")
    
    # Create new database with current schema
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
            print("✅ Created new database with current schema")
            
            # Verify tables were created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Tables created: {tables}")
            
            if 'users' in tables:
                print("✅ Users table exists")
            if 'todos' in tables:
                print("✅ Todos table exists") 
            if 'todolists' in tables:
                print("✅ TodoLists table exists")
                
        except Exception as e:
            print(f"❌ Error creating database: {e}")
            return False
    
    print("🎉 Database reset complete!")
    return True

if __name__ == '__main__':
    success = reset_database()
    sys.exit(0 if success else 1)