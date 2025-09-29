import json
import os
import logging
from typing import Dict, Any, List, Union, Tuple
import re

# Configuración de logger básico si no está disponible globalmente
logger = logging.getLogger(__name__)

def cargar_json_seguro(filepath: str) -> Union[Dict[str, Any], List[Any], None]:
    """Carga datos desde un archivo JSON de forma segura."""
    try:
        if not os.path.exists(filepath):
            logger.warning(f"Archivo no encontrado para cargar JSON: {filepath}")
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Error cargando {filepath}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado al cargar {filepath}: {e}")
        return None

def guardar_json_seguro(filepath: str, data: Union[Dict[str, Any], List[Any]]) -> bool:
    """Guarda datos en un archivo JSON de forma segura."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error guardando {filepath}: {e}")
        return False

def cargar_stock(filepath: str) -> Dict[str, Any]:
    """Carga el stock de materiales desde el archivo JSON."""
    logger.info(f"Cargando stock desde: {filepath}")
    data = cargar_json_seguro(filepath)
    if isinstance(data, dict):
        # Aplicar validación y corrección de datos
        if 'materiales' in data:
            materiales_validados, errores = validar_y_convertir_stock(data['materiales'])
            data['materiales'] = materiales_validados
            if errores:
                logger.warning(f"Materiales con errores corregidos: {errores}")
        return data
    else:
        logger.warning(f"El stock cargado desde {filepath} no es un diccionario válido. Devolviendo vacío.")
        return {}

def guardar_stock(filepath: str, stock: Dict[str, Any]) -> bool:
    """Guarda el stock de materiales actual en el archivo JSON."""
    try:
        return guardar_json_seguro(filepath, stock)
    except Exception as e:
        logger.error(f"Error guardando stock en {filepath}: {e}")
        return False

def obtener_stock_actual(filepath: str) -> Dict[str, Dict[str, Any]]:
    """Devuelve el stock actual del archivo. Intenta cargarlo si no está ya en memoria. """
    logger.debug(f"Obteniendo stock actual del archivo: {filepath}")
    return cargar_stock(filepath)

def formatear_numero_es(numero, decimales: int = 2):
    """
    Formatea un número en estilo español: punto para miles, coma para decimales.
    Ejemplo: 1234.56 -> '1.234,56'
    """
    try:
        if not isinstance(numero, (int, float)):
            return str(numero)

        # Redondear el número al número de decimales especificado
        rounded_num = round(float(numero), decimales)

        # Si el número redondeado es un entero, formatearlo sin decimales ni coma
        if rounded_num == int(rounded_num):
            # Formatear el entero con separadores de miles (coma por defecto) y luego cambiar a punto
            return f"{int(rounded_num):,}".replace(',', '.')
        else:
            # Formatear el flotante con separadores de miles (coma por defecto) y decimales (punto por defecto)
            # Luego, intercambiar los separadores para el formato español
            s = f"{rounded_num:,.{decimales}f}" # Example output: "33,123.85" (English locale default)

            # Reemplazar la coma (miles) por un placeholder temporal (X)
            # Reemplazar el punto (decimal) por una coma (decimal en español)
            # Reemplazar el placeholder (X) por un punto (miles en español)
            return s.replace(',', 'X').replace('.', ',').replace('X', '.')

    except (ValueError, TypeError):
        # Si el número no es válido, devolverlo como cadena original
        return str(numero)

def validar_y_convertir_stock(stock_data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Valida y convierte los valores del stock cargado desde JSON,
    asegurando que todas las cantidades sean numéricas y positivas.

    Args:
        stock_data (dict): Diccionario con materiales y sus datos.

    Returns:
        tuple: (diccionario corregido con valores válidos para total_tn y total_solido, lista de materiales con errores)
    """
    stock_validado = {}
    errores = []
    for material, info in stock_data.items():
        try:
            total_tn = float(info.get("total_tn", 0))
            total_solido = info.get("total_solido", 0)

            # Si viene como porcentaje (ej. 35), pasarlo a decimal (0.35)
            if isinstance(total_solido, str):
                total_solido = float(total_solido.replace(",", "."))
            total_solido = float(total_solido)
            if total_solido > 1:  # es un porcentaje mal cargado
                total_solido = total_solido / 100.0
            
            # CORRECCIÓN ESPECÍFICA: Si el valor es muy grande (ej: 99715), es un error de formato
            if total_solido > 100:  # Valores absurdamente grandes
                total_solido = total_solido / 10000.0  # Dividir por 10000 para corregir

            # Validar rangos
            if total_tn < 0:
                total_tn = 0.0
            if not (0.0 <= total_solido <= 1.0):
                total_solido = 0.0

            stock_validado[material] = {
                "total_tn": round(total_tn, 3),
                "total_solido": round(total_solido, 4)
            }

        except Exception as e:
            print(f"Error validando stock de '{material}': {e}. Se omite.")
            errores.append(material)
            continue

    return stock_validado, errores
