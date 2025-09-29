#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración de base de datos para deployment en la nube
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class DatabaseConfig:
    """Configuración de base de datos para diferentes entornos"""
    
    def __init__(self):
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.setup_database_config()
    
    def setup_database_config(self):
        """Configura la base de datos según el entorno"""
        
        if self.environment == 'production':
            # Configuración para producción (Netlify + MongoDB Atlas)
            self.database_url = os.getenv('DATABASE_URL')
            self.database_type = 'mongodb'
            self.mongodb_uri = os.getenv('MONGODB_URI')
            
        elif self.environment == 'staging':
            # Configuración para staging
            self.database_url = os.getenv('STAGING_DATABASE_URL')
            self.database_type = 'mongodb'
            self.mongodb_uri = os.getenv('STAGING_MONGODB_URI')
            
        else:
            # Configuración para desarrollo local
            self.database_url = 'sqlite:///sibia_local.db'
            self.database_type = 'sqlite'
            self.mongodb_uri = None
    
    def get_mongodb_config(self):
        """Obtiene configuración de MongoDB"""
        return {
            'uri': self.mongodb_uri,
            'database': 'sibia_dashboard',
            'collections': {
                'materiales': 'materiales',
                'stock': 'stock',
                'calculos': 'calculos',
                'sensores': 'sensores',
                'configuracion': 'configuracion'
            }
        }
    
    def get_postgresql_config(self):
        """Obtiene configuración de PostgreSQL"""
        return {
            'host': os.getenv('POSTGRES_HOST'),
            'port': os.getenv('POSTGRES_PORT', 5432),
            'database': os.getenv('POSTGRES_DB'),
            'username': os.getenv('POSTGRES_USER'),
            'password': os.getenv('POSTGRES_PASSWORD'),
            'ssl_mode': 'require'
        }

# Configuración global
db_config = DatabaseConfig()

# URLs de conexión para diferentes proveedores
DATABASE_URLS = {
    'mongodb_atlas': 'mongodb+srv://<username>:<password>@cluster.mongodb.net/sibia_dashboard?retryWrites=true&w=majority',
    'postgresql_railway': 'postgresql://<username>:<password>@<host>:<port>/<database>',
    'postgresql_heroku': 'postgresql://<username>:<password>@<host>:<port>/<database>',
    'sqlite_local': 'sqlite:///sibia_local.db'
}

# Configuración de MongoDB Atlas (Recomendado)
MONGODB_ATLAS_CONFIG = {
    'cluster_name': 'sibia-cluster',
    'database_name': 'sibia_dashboard',
    'collections': {
        'materiales': 'materiales_base',
        'stock': 'stock_actual',
        'calculos': 'historial_calculos',
        'sensores': 'datos_sensores',
        'configuracion': 'configuracion_sistema',
        'usuarios': 'usuarios_sistema'
    }
}

# Configuración de PostgreSQL (Alternativa)
POSTGRESQL_CONFIG = {
    'tables': {
        'materiales': 'materiales_base',
        'stock': 'stock_actual',
        'calculos': 'historial_calculos',
        'sensores': 'datos_sensores',
        'configuracion': 'configuracion_sistema',
        'usuarios': 'usuarios_sistema'
    }
}

def get_database_connection():
    """Obtiene la conexión a la base de datos según el entorno"""
    
    if db_config.database_type == 'mongodb':
        try:
            from pymongo import MongoClient
            client = MongoClient(db_config.mongodb_uri)
            db = client[MONGODB_ATLAS_CONFIG['database_name']]
            return db
        except Exception as e:
            print(f"Error conectando a MongoDB: {e}")
            return None
    
    elif db_config.database_type == 'postgresql':
        try:
            import psycopg2
            config = db_config.get_postgresql_config()
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                database=config['database'],
                user=config['username'],
                password=config['password'],
                sslmode=config['ssl_mode']
            )
            return conn
        except Exception as e:
            print(f"Error conectando a PostgreSQL: {e}")
            return None
    
    else:
        # SQLite para desarrollo local
        try:
            import sqlite3
            conn = sqlite3.connect('sibia_local.db')
            return conn
        except Exception as e:
            print(f"Error conectando a SQLite: {e}")
            return None

def migrate_data_to_cloud():
    """Migra datos locales a la base de datos en la nube"""
    
    print("🔄 Iniciando migración de datos a la nube...")
    
    # Cargar datos locales
    local_data = {}
    
    try:
        import json
        
        # Cargar materiales
        with open('materiales_base_config.json', 'r', encoding='utf-8') as f:
            local_data['materiales'] = json.load(f)
        
        # Cargar stock
        with open('stock.json', 'r', encoding='utf-8') as f:
            local_data['stock'] = json.load(f)
        
        # Cargar configuración
        with open('config.json', 'r', encoding='utf-8') as f:
            local_data['configuracion'] = json.load(f)
        
        print(f"✅ Datos locales cargados: {len(local_data)} archivos")
        
        # Conectar a base de datos en la nube
        db = get_database_connection()
        
        if db:
            if db_config.database_type == 'mongodb':
                # Migrar a MongoDB
                for collection_name, data in local_data.items():
                    collection = db[MONGODB_ATLAS_CONFIG['collections'][collection_name]]
                    collection.insert_one({
                        'data': data,
                        'timestamp': datetime.now(),
                        'source': 'local_migration'
                    })
                    print(f"✅ {collection_name} migrado a MongoDB")
            
            elif db_config.database_type == 'postgresql':
                # Migrar a PostgreSQL
                cursor = db.cursor()
                
                for table_name, data in local_data.items():
                    # Crear tabla si no existe
                    cursor.execute(f"""
                        CREATE TABLE IF NOT EXISTS {table_name} (
                            id SERIAL PRIMARY KEY,
                            data JSONB,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            source VARCHAR(50)
                        )
                    """)
                    
                    # Insertar datos
                    cursor.execute(f"""
                        INSERT INTO {table_name} (data, source)
                        VALUES (%s, %s)
                    """, (json.dumps(data), 'local_migration'))
                    
                    print(f"✅ {table_name} migrado a PostgreSQL")
                
                db.commit()
                cursor.close()
            
            print("🎉 Migración completada exitosamente")
            return True
        
        else:
            print("❌ No se pudo conectar a la base de datos en la nube")
            return False
    
    except Exception as e:
        print(f"❌ Error en la migración: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CONFIGURACIÓN DE BASE DE DATOS")
    print("=" * 50)
    
    # Mostrar configuración actual
    print(f"Entorno: {db_config.environment}")
    print(f"Tipo de BD: {db_config.database_type}")
    
    if db_config.database_type == 'mongodb':
        print("MongoDB URI configurado")
    elif db_config.database_type == 'postgresql':
        print("PostgreSQL configurado")
    else:
        print("SQLite local")
    
    print("\n💡 Para configurar la base de datos en la nube:")
    print("1. Crea una cuenta en MongoDB Atlas (gratuito)")
    print("2. Crea un cluster")
    print("3. Obtén la URI de conexión")
    print("4. Configura las variables de entorno")
    print("5. Ejecuta la migración de datos")
