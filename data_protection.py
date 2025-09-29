# SIBIA - Configuración de Seguridad y Protección de Datos
# Copyright © 2025 AutoLinkSolutions SRL. Todos los derechos reservados.
# 
# CONFIDENCIAL - NO DISTRIBUIR

import os
import hashlib
import base64
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataProtection:
    """Sistema de protección de datos para SIBIA"""
    
    def __init__(self):
        self.company_name = "AutoLinkSolutions SRL"
        self.copyright_year = "2025"
        self.encryption_key = self._get_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
    def _get_encryption_key(self):
        """Generar clave de encriptación basada en información de la empresa"""
        company_info = f"{self.company_name}{self.copyright_year}SIBIA"
        key_hash = hashlib.sha256(company_info.encode()).digest()
        return base64.urlsafe_b64encode(key_hash)
    
    def encrypt_sensitive_data(self, data):
        """Encriptar datos sensibles"""
        try:
            if isinstance(data, str):
                data = data.encode()
            encrypted_data = self.cipher_suite.encrypt(data)
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            return None
    
    def decrypt_sensitive_data(self, encrypted_data):
        """Desencriptar datos sensibles"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            return None
    
    def add_copyright_watermark(self, data):
        """Agregar marca de agua de copyright a los datos"""
        watermark = f"© {self.copyright_year} {self.company_name} - CONFIDENCIAL"
        return f"{watermark}\n{data}"
    
    def validate_data_ownership(self, data):
        """Validar que los datos pertenecen a AutoLinkSolutions SRL"""
        if isinstance(data, str) and self.company_name in data:
            return True
        return False
    
    def create_secure_session_token(self, user_id):
        """Crear token de sesión seguro"""
        timestamp = datetime.now().isoformat()
        token_data = f"{user_id}:{timestamp}:{self.company_name}"
        return self.encrypt_sensitive_data(token_data)
    
    def verify_session_token(self, token):
        """Verificar token de sesión"""
        try:
            decrypted_data = self.decrypt_sensitive_data(token)
            if decrypted_data and self.company_name in decrypted_data:
                parts = decrypted_data.split(':')
                if len(parts) >= 3:
                    user_id, timestamp, company = parts[0], parts[1], parts[2]
                    # Verificar que el token no sea muy antiguo (24 horas)
                    token_time = datetime.fromisoformat(timestamp)
                    if datetime.now() - token_time < timedelta(hours=24):
                        return user_id
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None

# Instancia global del sistema de protección
data_protection = DataProtection()

def protect_database_credentials():
    """Proteger credenciales de base de datos"""
    protected_creds = {
        'host': data_protection.encrypt_sensitive_data(os.environ.get('DB_HOST', 'localhost')),
        'user': data_protection.encrypt_sensitive_data(os.environ.get('DB_USER', 'root')),
        'password': data_protection.encrypt_sensitive_data(os.environ.get('DB_PASSWORD', '')),
        'database': data_protection.encrypt_sensitive_data(os.environ.get('DB_NAME', 'sibia'))
    }
    return protected_creds

def protect_api_keys():
    """Proteger claves de API"""
    protected_keys = {
        'openai_key': data_protection.encrypt_sensitive_data(os.environ.get('OPENAI_API_KEY', '')),
        'google_ai_key': data_protection.encrypt_sensitive_data(os.environ.get('GOOGLE_AI_KEY', '')),
        'elevenlabs_key': data_protection.encrypt_sensitive_data(os.environ.get('ELEVENLABS_API_KEY', ''))
    }
    return protected_keys

def add_copyright_to_response(response_data):
    """Agregar copyright a las respuestas de la API"""
    if isinstance(response_data, dict):
        response_data['copyright'] = f"© {data_protection.copyright_year} {data_protection.company_name}"
        response_data['confidential'] = "CONFIDENCIAL - NO DISTRIBUIR"
        response_data['company'] = data_protection.company_name
    return response_data

# Función para verificar que el código no se está ejecutando en un entorno no autorizado
def verify_execution_environment():
    """Verificar que el código se está ejecutando en un entorno autorizado"""
    allowed_domains = [
        'railway.app',
        'herokuapp.com',
        'autolinksolutions.com',
        'localhost',
        '127.0.0.1'
    ]
    
    current_host = os.environ.get('HOST', 'localhost')
    for domain in allowed_domains:
        if domain in current_host:
            return True
    
    logger.warning(f"⚠️ Ejecutándose en dominio no autorizado: {current_host}")
    return False

if __name__ == "__main__":
    # Prueba del sistema de protección
    print("🔒 Probando sistema de protección de datos...")
    
    # Probar encriptación
    test_data = "Datos sensibles de SIBIA"
    encrypted = data_protection.encrypt_sensitive_data(test_data)
    decrypted = data_protection.decrypt_sensitive_data(encrypted)
    
    print(f"✅ Encriptación funcionando: {test_data == decrypted}")
    print(f"📝 Copyright: © {data_protection.copyright_year} {data_protection.company_name}")
    print(f"🔐 Verificación de entorno: {verify_execution_environment()}")
