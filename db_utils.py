import os
import logging
import pymysql
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración centralizada del modo local
MODO_LOCAL = False  # Forzar conexión remota

# Configuración de logging
logger = logging.getLogger(__name__)

# Disponibilidad de MySQL
try:
    import pymysql
    MYSQL_DISPONIBLE = True
except ImportError:
    MYSQL_DISPONIBLE = False

# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'www.acaiot.com.ar'),
    'database': os.getenv('DB_NAME', 'u357888498_gvbio'),
    'user': os.getenv('DB_USER', 'gvbio'),
    'password': os.getenv('DB_PASSWORD', 'GvBio2024#'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'autocommit': True,
    'connect_timeout': 3
}

# --- Mock de Conexión para Modo Local ---
class MockCursor:
    """Un cursor de base de datos falso que devuelve datos de prueba."""
    def execute(self, query):
        logger.info(f"MockCursor ejecutando query: {query[:70]}...")

    def fetchone(self):
        # Devuelve un solo valor de prueba en una tupla
        return (150.7,)

    def fetchall(self):
        # Devuelve una lista de diccionarios, imitando DictCursor
        return [{'kwGen': 150.5, 'fecha_hora': '2025-06-28 10:00:00'}]

    def close(self):
        pass

class MockConnection:
    """Una conexión de base de datos falsa que usa MockCursor."""
    def cursor(self, cursor_type=None):
        return MockCursor()

    def close(self):
        pass

def obtener_conexion_db():
    """
    Obtiene una conexión a la base de datos.
    En MODO_LOCAL, devuelve un objeto de conexión simulado.
    """
    if MODO_LOCAL:
        logger.info("🏠 MODO LOCAL ACTIVADO - Devolviendo conexión simulada (Mock). [DESACTIVADO POR CONFIG]")
        # Forzado a no usar mock
        return None
    
    if not MYSQL_DISPONIBLE:
        logger.warning("PyMySQL no disponible. No se puede crear una conexión real.")
        return None
    
    try:
        connection = pymysql.connect(**DB_CONFIG)
        logger.info("✅ Conexión a base de datos MySQL real establecida.")
        return connection
    except pymysql.Error as e:
        logger.error(f"❌ No se pudo conectar a MySQL real: {e}")
        return None 