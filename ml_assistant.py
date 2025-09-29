import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import json
import os

try:
    import nltk
    nltk.download('stopwords', quiet=True)
    stop_words_spanish = set(nltk.corpus.stopwords.words('spanish'))
except ImportError:
    # Definir manualmente stopwords si nltk no está disponible
    stop_words_spanish = {'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 'un', 'para', 'con', 'no', 'una', 'su', 'al', 'lo', 'como', 'más', 'pero', 'sus', 'le', 'ya', 'o', 'este', 'sí', 'porque', 'esta', 'entre', 'cuando', 'muy', 'sin'}

class AdaptiveAssistantModel:
    def __init__(self, model_path='adaptive_assistant_model.joblib'):
        self.model_path = model_path
        
        # Usar lista de stopwords en español
        self.vectorizer = TfidfVectorizer(stop_words=list(stop_words_spanish))
        
        self.classifier = RandomForestClassifier(n_estimators=100)
        self.knowledge_base_path = 'knowledge_base.json'
        
        # Cargar o inicializar base de conocimientos
        self.knowledge_base = self.cargar_base_conocimientos()
        
        # Intentar cargar modelo existente
        if os.path.exists(model_path):
            self.cargar_modelo()
        else:
            self.inicializar_modelo()

    def cargar_base_conocimientos(self):
        """Cargar o inicializar base de conocimientos"""
        if os.path.exists(self.knowledge_base_path):
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'preguntas': [],
            'respuestas': [],
            'retroalimentacion': [],
            'formulas': {}
        }

    def guardar_base_conocimientos(self):
        """Guardar base de conocimientos"""
        with open(self.knowledge_base_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=4)

    def inicializar_modelo(self):
        """Inicializar modelo con datos semilla"""
        datos_semilla = [
            {
                'pregunta': 'Calcular mezcla diaria',
                'respuesta': 'Función para calcular distribución óptima de materiales',
                'categoria': 'calculo_mezcla'
            },
            {
                'pregunta': 'Obtener stock de materiales',
                'respuesta': 'Consulta el inventario actual de materiales',
                'categoria': 'stock'
            }
        ]

        preguntas = [d['pregunta'] for d in datos_semilla]
        respuestas = [d['respuesta'] for d in datos_semilla]
        categorias = [d['categoria'] for d in datos_semilla]

        X = self.vectorizer.fit_transform(preguntas)
        y = categorias

        self.classifier.fit(X, y)
        self.guardar_modelo()

    def guardar_modelo(self):
        """Guardar modelo entrenado"""
        joblib.dump({
            'vectorizer': self.vectorizer,
            'classifier': self.classifier
        }, self.model_path)

    def cargar_modelo(self):
        """Cargar modelo previamente entrenado"""
        datos_modelo = joblib.load(self.model_path)
        self.vectorizer = datos_modelo['vectorizer']
        self.classifier = datos_modelo['classifier']

    def entrenar_con_retroalimentacion(self, pregunta, respuesta, retroalimentacion):
        """
        Entrenar modelo con retroalimentación del usuario
        """
        # Agregar a base de conocimientos
        self.knowledge_base['preguntas'].append(pregunta)
        self.knowledge_base['respuestas'].append(respuesta)
        self.knowledge_base['retroalimentacion'].append(retroalimentacion)

        # Reentrenar modelo si hay suficientes datos
        if len(self.knowledge_base['preguntas']) > 10:
            X = self.vectorizer.transform(self.knowledge_base['preguntas'])
            y = [1 if retro == 'positiva' else 0 for retro in self.knowledge_base['retroalimentacion']]
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            
            # Reentrenar clasificador
            self.classifier = RandomForestClassifier(n_estimators=100)
            self.classifier.fit(X_train, y_train)
            
            # Guardar modelo actualizado
            self.guardar_modelo()
        
        # Guardar base de conocimientos
        self.guardar_base_conocimientos()

    def registrar_formula(self, nombre_formula, descripcion, implementacion):
        """
        Registrar una fórmula en la base de conocimientos
        """
        self.knowledge_base['formulas'][nombre_formula] = {
            'descripcion': descripcion,
            'implementacion': implementacion,
            'fecha_registro': pd.Timestamp.now().isoformat()
        }
        self.guardar_base_conocimientos()

    def buscar_formula(self, consulta):
        """
        Buscar fórmula similar a la consulta
        """
        if not self.knowledge_base['formulas']:
            return None

        # Vectorizar consulta
        consulta_vec = self.vectorizer.transform([consulta])
        
        # Encontrar fórmula más similar
        formulas = list(self.knowledge_base['formulas'].keys())
        formulas_vec = self.vectorizer.transform(formulas)
        
        # Calcular similitud
        similitudes = (consulta_vec @ formulas_vec.T).toarray()[0]
        indice_mas_similar = np.argmax(similitudes)
        
        return {
            'nombre': formulas[indice_mas_similar],
            'datos': self.knowledge_base['formulas'][formulas[indice_mas_similar]]
        }

# Instancia global
adaptive_assistant = AdaptiveAssistantModel() 