import os
import joblib
import numpy as np
import pandas as pd
from PyQt5.QtCore import QObject, pyqtSignal

class PredictionModel(QObject):
    """Modelo para realizar predicciones de pandeo en elementos de acero."""
    
    # Señal emitida cuando el modelo está listo
    model_loaded = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        
        # Ruta al modelo
        self.model_path = None
        
        # Buscar primero en el directorio raíz del proyecto
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        for filename in os.listdir(root_dir):
            if filename.startswith("modelo_pandeo_acero_") and filename.endswith(".joblib"):
                self.model_path = os.path.join(root_dir, filename)
                break
        
        # Modelo de predicción
        self.model = None
        
        # Cargar modelo
        self.load_model()
    
    def load_model(self):
        """Cargar el modelo de predicción desde el archivo joblib."""
        try:
            if self.model_path is not None:
                self.model = joblib.load(self.model_path)
                self.model_loaded.emit(True)
            else:
                # Buscar en la carpeta models
                model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
                if not os.path.exists(model_dir):
                    os.makedirs(model_dir)
                
                for filename in os.listdir(model_dir):
                    if filename.startswith("modelo_pandeo_acero_") and filename.endswith(".joblib"):
                        self.model_path = os.path.join(model_dir, filename)
                        self.model = joblib.load(self.model_path)
                        self.model_loaded.emit(True)
                        break
                
                # Si no encuentra el modelo, buscar en el directorio raíz de nuevo (por compatibilidad)
                if self.model is None:
                    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    for filename in os.listdir(root_dir):
                        if filename.startswith("modelo_pandeo_acero_") and filename.endswith(".joblib"):
                            self.model_path = os.path.join(root_dir, filename)
                            self.model = joblib.load(self.model_path)
                            self.model_loaded.emit(True)
                            break
        except Exception as e:
            print(f"Error al cargar el modelo: {str(e)}")
            self.model_loaded.emit(False)
    
    def predict(self, params):
        """
        Realizar predicción de carga máxima.
        
        Args:
            params (dict): Diccionario con los parámetros de entrada.
                - tipo_perfil: Tipo de perfil
                - tipo_acero: Tipo de acero
                - longitud_mm: Longitud del elemento en mm
                - condicion_apoyo: Condición de apoyo
                - altura_perfil_mm: Altura del perfil en mm (opcional)
                - ancho_alas_mm: Ancho de las alas en mm (opcional)
                - espesor_alma_mm: Espesor del alma en mm (opcional)
                - espesor_alas_mm: Espesor de las alas en mm (opcional)
                - dimension_exterior_mm: Dimensión exterior en mm (opcional)
                - espesor_mm: Espesor en mm (opcional)
        
        Returns:
            dict: Diccionario con los resultados de la predicción.
        """
        if self.model is None:
            raise ValueError("El modelo no está cargado")
        
        # Extraer parámetros
        tipo_perfil = params.get("tipo_perfil")
        tipo_acero = params.get("tipo_acero")
        longitud_mm = params.get("longitud_mm")
        condicion_apoyo = params.get("condicion_apoyo")
        altura_perfil_mm = params.get("altura_perfil_mm")
        ancho_alas_mm = params.get("ancho_alas_mm")
        espesor_alma_mm = params.get("espesor_alma_mm")
        espesor_alas_mm = params.get("espesor_alas_mm")
        dimension_exterior_mm = params.get("dimension_exterior_mm")
        espesor_mm = params.get("espesor_mm")
        
        # Definir factores de longitud efectiva según condiciones de apoyo
        factores_k = {
            'Empotrado-Empotrado': 0.5,
            'Empotrado-Articulado': 0.7,
            'Articulado-Articulado': 1.0,
            'Empotrado-Libre': 2.0
        }
        
        # Obtener factor de longitud efectiva
        factor_longitud_efectiva = factores_k.get(condicion_apoyo, 1.0)
        
        # Calcular longitud de pandeo
        longitud_pandeo_mm = longitud_mm * factor_longitud_efectiva
        
        # Definir propiedades del material según tipo de acero
        propiedades_acero = {
            'S235': {'modulo_elasticidad_MPa': 210000, 'limite_elastico_MPa': 235, 'tension_rotura_MPa': 360},
            'S275': {'modulo_elasticidad_MPa': 210000, 'limite_elastico_MPa': 275, 'tension_rotura_MPa': 430},
            'S355': {'modulo_elasticidad_MPa': 210000, 'limite_elastico_MPa': 355, 'tension_rotura_MPa': 510}
        }
        
        # Obtener propiedades del material
        props = propiedades_acero.get(tipo_acero, propiedades_acero['S275'])
        modulo_elasticidad_MPa = props['modulo_elasticidad_MPa']
        limite_elastico_MPa = props['limite_elastico_MPa']
        tension_rotura_MPa = props['tension_rotura_MPa']
        
        # Calcular área e inercia según tipo de perfil
        if tipo_perfil in ['IPE', 'HEB', 'HEA', 'HEM', 'UPN']:
            # Verificar que se proporcionaron los parámetros necesarios
            if not all([altura_perfil_mm, ancho_alas_mm, espesor_alma_mm, espesor_alas_mm]):
                raise ValueError("Para perfiles tipo I/H se requieren altura_perfil_mm, ancho_alas_mm, espesor_alma_mm y espesor_alas_mm")
            
            # Calcular área e inercia para perfiles I/H
            area_mm2 = 2 * ancho_alas_mm * espesor_alas_mm + (altura_perfil_mm - 2 * espesor_alas_mm) * espesor_alma_mm
            inercia_mm4 = (ancho_alas_mm * altura_perfil_mm**3) / 12 - ((ancho_alas_mm - espesor_alma_mm) * (altura_perfil_mm - 2 * espesor_alas_mm)**3) / 12
            
            # Asignar valores para dimensiones tubulares para evitar valores 0
            dimension_exterior_mm = altura_perfil_mm * 0.8 if dimension_exterior_mm is None or dimension_exterior_mm == 0 else dimension_exterior_mm
            espesor_mm = espesor_alma_mm * 1.2 if espesor_mm is None or espesor_mm == 0 else espesor_mm
                
        elif tipo_perfil in ['Tubular cuadrado', 'Tubular circular']:
            # Verificar y asignar valores por defecto si es necesario
            if dimension_exterior_mm is None or dimension_exterior_mm == 0:
                dimension_exterior_mm = 150.0  # Valor por defecto si no se proporciona
            
            if espesor_mm is None or espesor_mm == 0:
                espesor_mm = 8.0  # Valor por defecto si no se proporciona
            
            # Calcular área e inercia para perfiles tubulares
            if tipo_perfil == 'Tubular cuadrado':
                area_mm2 = dimension_exterior_mm**2 - (dimension_exterior_mm - 2*espesor_mm)**2
                inercia_mm4 = (dimension_exterior_mm**4 - (dimension_exterior_mm - 2*espesor_mm)**4) / 12
            else:  # Tubular circular
                radio_ext = dimension_exterior_mm / 2
                radio_int = radio_ext - espesor_mm
                area_mm2 = 3.14159 * (radio_ext**2 - radio_int**2)
                inercia_mm4 = 3.14159 * (radio_ext**4 - radio_int**4) / 4
            
            # Asignar valores para dimensiones de perfiles I/H
            altura_perfil_mm = dimension_exterior_mm if altura_perfil_mm is None or altura_perfil_mm == 0 else altura_perfil_mm
            ancho_alas_mm = dimension_exterior_mm if ancho_alas_mm is None or ancho_alas_mm == 0 else ancho_alas_mm
            espesor_alma_mm = espesor_mm if espesor_alma_mm is None or espesor_alma_mm == 0 else espesor_alma_mm
            espesor_alas_mm = espesor_mm if espesor_alas_mm is None or espesor_alas_mm == 0 else espesor_alas_mm
        else:
            # Para otros tipos de perfiles, usar valores proporcionados
            if not all([altura_perfil_mm, ancho_alas_mm, espesor_alma_mm, espesor_alas_mm]):
                raise ValueError("Para perfiles no estándar se requieren todos los parámetros")
            
            # Calcular área e inercia aproximada
            area_mm2 = 2 * ancho_alas_mm * espesor_alas_mm + (altura_perfil_mm - 2 * espesor_alas_mm) * espesor_alma_mm
            inercia_mm4 = (ancho_alas_mm * altura_perfil_mm**3) / 12
            
            # Asignar valores para dimensiones tubulares para evitar valores 0
            dimension_exterior_mm = altura_perfil_mm * 0.8 if dimension_exterior_mm is None or dimension_exterior_mm == 0 else dimension_exterior_mm
            espesor_mm = espesor_alma_mm * 1.2 if espesor_mm is None or espesor_mm == 0 else espesor_mm
        
        # Calcular radio de giro
        radio_giro_mm = (inercia_mm4 / area_mm2)**0.5
        
        # Calcular esbeltez mecánica
        esbeltez_mecanica = longitud_pandeo_mm / radio_giro_mm
        
        # Definir curva de pandeo y coeficiente de imperfección según tipo de perfil
        curvas_pandeo = {
            'IPE': 'b',
            'HEB': 'b',
            'HEA': 'b',
            'HEM': 'a',
            'Tubular cuadrado': 'a',
            'Tubular circular': 'a',
            'UPN': 'c',
            'L': 'd',
            'T': 'c'
        }
        
        coef_imperfeccion = {
            'a0': 0.13,
            'a': 0.21,
            'b': 0.34,
            'c': 0.49,
            'd': 0.76
        }
        
        # Obtener curva de pandeo y coeficiente de imperfección
        curva_pandeo = curvas_pandeo.get(tipo_perfil, 'c')
        coef_imperfeccion_val = coef_imperfeccion.get(curva_pandeo, 0.34)
        
        # Calcular esbeltez relativa
        esbeltez_base = 3.14159 * (modulo_elasticidad_MPa / limite_elastico_MPa)**0.5
        esbeltez_relativa = esbeltez_mecanica / esbeltez_base
        
        # Calcular excentricidad inicial (entre L/1000 y L/200)
        excentricidad_inicial_mm = longitud_mm / 500  # Valor medio
        
        # Crear DataFrame con los datos de entrada
        input_data = pd.DataFrame({
            'tipo_perfil': [tipo_perfil],
            'tipo_acero': [tipo_acero],
            'longitud_mm': [longitud_mm],
            'condicion_apoyo': [condicion_apoyo],
            'factor_longitud_efectiva': [factor_longitud_efectiva],
            'longitud_pandeo_mm': [longitud_pandeo_mm],
            'area_mm2': [area_mm2],
            'inercia_mm4': [inercia_mm4],
            'radio_giro_mm': [radio_giro_mm],
            'esbeltez_mecanica': [esbeltez_mecanica],
            'modulo_elasticidad_MPa': [modulo_elasticidad_MPa],
            'limite_elastico_MPa': [limite_elastico_MPa],
            'tension_rotura_MPa': [tension_rotura_MPa],
            'excentricidad_inicial_mm': [excentricidad_inicial_mm],
            'curva_pandeo': [curva_pandeo],
            'coef_imperfeccion': [coef_imperfeccion_val],
            'esbeltez_relativa': [esbeltez_relativa],
            'altura_perfil_mm': [altura_perfil_mm],
            'ancho_alas_mm': [ancho_alas_mm],
            'espesor_alma_mm': [espesor_alma_mm],
            'espesor_alas_mm': [espesor_alas_mm],
            'dimension_exterior_mm': [dimension_exterior_mm],
            'espesor_mm': [espesor_mm]
        })
        
        # Realizar predicción
        carga_maxima_kN = float(self.model.predict(input_data)[0])
        
        # Calcular carga crítica de Euler
        carga_critica_euler_N = (np.pi**2 * modulo_elasticidad_MPa * inercia_mm4) / (longitud_pandeo_mm**2)
        carga_critica_euler_kN = carga_critica_euler_N / 1000
        
        # Calcular factor de reducción por pandeo
        if esbeltez_relativa <= 0.2:
            factor_reduccion = 1.0
        else:
            phi = 0.5 * (1 + coef_imperfeccion_val * (esbeltez_relativa - 0.2) + esbeltez_relativa**2)
            factor_reduccion = 1 / (phi + np.sqrt(phi**2 - esbeltez_relativa**2))
        
        # Calcular desplazamiento lateral aproximado
        if esbeltez_relativa < 0.2:
            desplazamiento_lateral_mm = excentricidad_inicial_mm * 1.1
        else:
            desplazamiento_lateral_mm = excentricidad_inicial_mm * (1 / (1 - carga_maxima_kN / carga_critica_euler_kN))
        
        # Resultados adicionales
        resistencia_plastica_kN = (area_mm2 * limite_elastico_MPa) / 1000
        carga_maxima_kg = carga_maxima_kN * 101.9716
        carga_maxima_ton = carga_maxima_kN * 0.1019716
        
        # Crear diccionario de resultados
        results = {
            # Datos de entrada procesados
            'tipo_perfil': tipo_perfil,
            'tipo_acero': tipo_acero,
            'longitud_mm': longitud_mm,
            'condicion_apoyo': condicion_apoyo,
            'factor_longitud_efectiva': factor_longitud_efectiva,
            'longitud_pandeo_mm': longitud_pandeo_mm,
            'area_mm2': area_mm2,
            'inercia_mm4': inercia_mm4,
            'radio_giro_mm': radio_giro_mm,
            'esbeltez_mecanica': esbeltez_mecanica,
            'esbeltez_relativa': esbeltez_relativa,
            'curva_pandeo': curva_pandeo,
            'coef_imperfeccion': coef_imperfeccion_val,
            
            # Resultados principales
            'carga_maxima_kN': carga_maxima_kN,
            'carga_maxima_kg': carga_maxima_kg,
            'carga_maxima_ton': carga_maxima_ton,
            
            # Resultados adicionales
            'carga_critica_euler_kN': carga_critica_euler_kN,
            'factor_reduccion': factor_reduccion,
            'resistencia_plastica_kN': resistencia_plastica_kN,
            'desplazamiento_lateral_mm': desplazamiento_lateral_mm
        }
        
        return results 