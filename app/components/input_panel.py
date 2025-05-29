import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLabel, QComboBox, QDoubleSpinBox, QPushButton, 
                            QGroupBox, QMessageBox, QTabWidget, QScrollArea,
                            QSizePolicy, QSpacerItem, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QSettings, QRect, QPoint
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPainter, QPen, QBrush, QColor, QPainterPath

class InputPanel(QWidget):
    """Panel para entrada de datos para el cálculo de pandeo."""
    
    # Señal emitida cuando se completa una predicción
    prediction_ready = pyqtSignal(dict)
    
    def __init__(self, prediction_model):
        super().__init__()
        
        # Guardar referencia al modelo de predicción
        self.prediction_model = prediction_model
        
        # Inicializar UI
        self.setup_ui()
        
        # Conectar señales
        self.connect_signals()
    
    def setup_ui(self):
        """Configurar la interfaz de usuario del panel de entrada."""
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Crear área desplazable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        # Widget contenedor para el área desplazable
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Parámetros de Entrada para Predicción de Pandeo")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(title_label)
        
        # Grupo de tipo de perfil y material
        profile_group = QGroupBox("Tipo de Perfil y Material")
        profile_layout = QFormLayout()
        profile_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Tipo de perfil
        self.tipo_perfil_combo = QComboBox()
        self.tipo_perfil_combo.addItems([
            "IPE", "HEB", "HEA", "HEM", "UPN", "Tubular cuadrado", "Tubular circular", "L", "T"
        ])
        profile_layout.addRow("Tipo de Perfil:", self.tipo_perfil_combo)
        
        # Tipo de acero
        self.tipo_acero_combo = QComboBox()
        self.tipo_acero_combo.addItems(["S235", "S275", "S355"])
        profile_layout.addRow("Tipo de Acero:", self.tipo_acero_combo)
        
        # Longitud
        self.longitud_spin = QDoubleSpinBox()
        self.longitud_spin.setRange(100, 20000)
        self.longitud_spin.setSingleStep(100)
        self.longitud_spin.setValue(3000)
        self.longitud_spin.setSuffix(" mm")
        profile_layout.addRow("Longitud:", self.longitud_spin)
        
        # Condición de apoyo
        self.condicion_apoyo_combo = QComboBox()
        self.condicion_apoyo_combo.addItems([
            "Empotrado-Empotrado", "Empotrado-Articulado", "Articulado-Articulado", "Empotrado-Libre"
        ])
        profile_layout.addRow("Condición de Apoyo:", self.condicion_apoyo_combo)
        
        profile_group.setLayout(profile_layout)
        scroll_layout.addWidget(profile_group)
        
        # Grupo de dimensiones del perfil - se actualizará según el tipo de perfil
        self.dimensions_group = QGroupBox("Dimensiones del Perfil")
        self.dimensions_layout = QFormLayout()
        self.dimensions_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Altura del perfil
        self.altura_perfil_spin = QDoubleSpinBox()
        self.altura_perfil_spin.setRange(10, 1000)
        self.altura_perfil_spin.setSingleStep(1)
        self.altura_perfil_spin.setValue(200)
        self.altura_perfil_spin.setSuffix(" mm")
        self.dimensions_layout.addRow("Altura del Perfil:", self.altura_perfil_spin)
        
        # Ancho de alas
        self.ancho_alas_spin = QDoubleSpinBox()
        self.ancho_alas_spin.setRange(10, 500)
        self.ancho_alas_spin.setSingleStep(1)
        self.ancho_alas_spin.setValue(100)
        self.ancho_alas_spin.setSuffix(" mm")
        self.dimensions_layout.addRow("Ancho de Alas:", self.ancho_alas_spin)
        
        # Espesor de alma
        self.espesor_alma_spin = QDoubleSpinBox()
        self.espesor_alma_spin.setRange(1, 50)
        self.espesor_alma_spin.setSingleStep(0.1)
        self.espesor_alma_spin.setValue(5.6)
        self.espesor_alma_spin.setSuffix(" mm")
        self.dimensions_layout.addRow("Espesor de Alma:", self.espesor_alma_spin)
        
        # Espesor de alas
        self.espesor_alas_spin = QDoubleSpinBox()
        self.espesor_alas_spin.setRange(1, 50)
        self.espesor_alas_spin.setSingleStep(0.1)
        self.espesor_alas_spin.setValue(8.5)
        self.espesor_alas_spin.setSuffix(" mm")
        self.dimensions_layout.addRow("Espesor de Alas:", self.espesor_alas_spin)
        
        # Dimensión exterior (para perfiles tubulares)
        self.dimension_exterior_spin = QDoubleSpinBox()
        self.dimension_exterior_spin.setRange(10, 500)
        self.dimension_exterior_spin.setSingleStep(1)
        self.dimension_exterior_spin.setValue(150)
        self.dimension_exterior_spin.setSuffix(" mm")
        self.dimensions_layout.addRow("Dimensión Exterior:", self.dimension_exterior_spin)
        
        # Espesor (para perfiles tubulares)
        self.espesor_spin = QDoubleSpinBox()
        self.espesor_spin.setRange(1, 50)
        self.espesor_spin.setSingleStep(0.1)
        self.espesor_spin.setValue(8)
        self.espesor_spin.setSuffix(" mm")
        self.dimensions_layout.addRow("Espesor:", self.espesor_spin)
        
        self.dimensions_group.setLayout(self.dimensions_layout)
        scroll_layout.addWidget(self.dimensions_group)
        
        # Configurar visibilidad inicial de campos
        self.update_dimension_fields()
        
        # Esquema del perfil
        self.schema_group = QGroupBox("Esquema del Perfil")
        schema_layout = QVBoxLayout()
        
        # Etiqueta para mostrar el esquema
        self.schema_label = QLabel()
        self.schema_label.setAlignment(Qt.AlignCenter)
        self.schema_label.setMinimumHeight(200)
        
        # Intentar cargar imagen del perfil
        self.update_profile_schema()
        
        schema_layout.addWidget(self.schema_label)
        self.schema_group.setLayout(schema_layout)
        scroll_layout.addWidget(self.schema_group)
        
        # Botones de acción
        action_layout = QHBoxLayout()
        
        # Botón para calcular
        self.calculate_button = QPushButton("Calcular")
        self.calculate_button.setMinimumHeight(40)
        font = QFont()
        font.setBold(True)
        self.calculate_button.setFont(font)
        action_layout.addWidget(self.calculate_button)
        
        # Botón para limpiar
        self.clear_button = QPushButton("Limpiar")
        self.clear_button.setMinimumHeight(40)
        action_layout.addWidget(self.clear_button)
        
        # Botón para cargar perfil predefinido
        self.load_profile_button = QPushButton("Cargar Perfil Predefinido")
        self.load_profile_button.setMinimumHeight(40)
        action_layout.addWidget(self.load_profile_button)
        
        scroll_layout.addLayout(action_layout)
        
        # Agregar espacio al final
        scroll_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Configurar área desplazable
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)
    
    def connect_signals(self):
        """Conectar señales y slots."""
        # Conectar cambio de tipo de perfil para actualizar campos
        self.tipo_perfil_combo.currentIndexChanged.connect(self.update_dimension_fields)
        self.tipo_perfil_combo.currentIndexChanged.connect(self.update_profile_schema)
        
        # Conectar botones
        self.calculate_button.clicked.connect(self.calculate)
        self.clear_button.clicked.connect(self.clear_fields)
        self.load_profile_button.clicked.connect(self.load_predefined_profile)
        
        # Conectar señal de modelo cargado
        self.prediction_model.model_loaded.connect(self.handle_model_loaded)
    
    def update_dimension_fields(self):
        """Actualizar campos de dimensiones según el tipo de perfil seleccionado."""
        try:
            tipo_perfil = self.tipo_perfil_combo.currentText()
            
            # Ocultar todos los campos primero
            for i in range(self.dimensions_layout.rowCount()):
                if i < 4:  # Altura, ancho, espesor alma, espesor alas
                    self.dimensions_layout.itemAt(i, QFormLayout.FieldRole).widget().setVisible(False)
                    self.dimensions_layout.itemAt(i, QFormLayout.LabelRole).widget().setVisible(False)
            
            # Mostrar campos según tipo de perfil
            if tipo_perfil in ['IPE', 'HEB', 'HEA', 'HEM', 'UPN', 'L', 'T']:
                # Perfiles tipo I/H/U/L/T
                self.altura_perfil_spin.setVisible(True)
                self.dimensions_layout.itemAt(0, QFormLayout.LabelRole).widget().setVisible(True)
                
                self.ancho_alas_spin.setVisible(True)
                self.dimensions_layout.itemAt(1, QFormLayout.LabelRole).widget().setVisible(True)
                
                self.espesor_alma_spin.setVisible(True)
                self.dimensions_layout.itemAt(2, QFormLayout.LabelRole).widget().setVisible(True)
                
                self.espesor_alas_spin.setVisible(True)
                self.dimensions_layout.itemAt(3, QFormLayout.LabelRole).widget().setVisible(True)
                
                self.dimension_exterior_spin.setVisible(False)
                self.dimensions_layout.itemAt(4, QFormLayout.LabelRole).widget().setVisible(False)
                
                self.espesor_spin.setVisible(False)
                self.dimensions_layout.itemAt(5, QFormLayout.LabelRole).widget().setVisible(False)
            
            elif tipo_perfil in ['Tubular cuadrado', 'Tubular circular']:
                # Perfiles tubulares
                self.altura_perfil_spin.setVisible(False)
                self.dimensions_layout.itemAt(0, QFormLayout.LabelRole).widget().setVisible(False)
                
                self.ancho_alas_spin.setVisible(False)
                self.dimensions_layout.itemAt(1, QFormLayout.LabelRole).widget().setVisible(False)
                
                self.espesor_alma_spin.setVisible(False)
                self.dimensions_layout.itemAt(2, QFormLayout.LabelRole).widget().setVisible(False)
                
                self.espesor_alas_spin.setVisible(False)
                self.dimensions_layout.itemAt(3, QFormLayout.LabelRole).widget().setVisible(False)
                
                self.dimension_exterior_spin.setVisible(True)
                self.dimensions_layout.itemAt(4, QFormLayout.LabelRole).widget().setVisible(True)
                
                self.espesor_spin.setVisible(True)
                self.dimensions_layout.itemAt(5, QFormLayout.LabelRole).widget().setVisible(True)
        except Exception as e:
            import traceback
            print(f"Error al actualizar campos de dimensiones: {str(e)}")
            print(traceback.format_exc())
            # Mostrar mensaje de error
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Advertencia", f"Error al cambiar el tipo de perfil: {str(e)}")
    
    def update_profile_schema(self):
        """Actualizar el esquema del perfil según el tipo seleccionado."""
        try:
            tipo_perfil = self.tipo_perfil_combo.currentText()
            
            # Crear un pixmap en blanco
            pixmap = QPixmap(300, 200)
            pixmap.fill(Qt.white)
            
            # Preparar pintor
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Dibujar marco
            pen = QPen(QColor(0, 0, 0))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawRect(5, 5, 290, 190)
            
            # Dibujar título del esquema
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            painter.drawText(QRect(10, 10, 280, 20), Qt.AlignCenter, f"Perfil {tipo_perfil}")
            
            # Dimensiones base
            center_x = 150
            center_y = 100
            
            if tipo_perfil in ['IPE', 'HEB', 'HEA', 'HEM']:
                # Dimensiones para I/H
                altura = 140
                ancho = 80
                espesor_alma = 6
                espesor_alas = 10
                
                # Ala superior
                painter.fillRect(
                    center_x - ancho//2,
                    center_y - altura//2,
                    ancho,
                    espesor_alas,
                    QBrush(QColor(180, 180, 180))
                )
                
                # Alma
                painter.fillRect(
                    center_x - espesor_alma//2,
                    center_y - altura//2 + espesor_alas,
                    espesor_alma,
                    altura - 2*espesor_alas,
                    QBrush(QColor(180, 180, 180))
                )
                
                # Ala inferior
                painter.fillRect(
                    center_x - ancho//2,
                    center_y + altura//2 - espesor_alas,
                    ancho,
                    espesor_alas,
                    QBrush(QColor(180, 180, 180))
                )
                
            elif tipo_perfil == 'UPN':
                # Dimensiones para UPN
                altura = 140
                ancho = 60
                espesor_alma = 6
                espesor_alas = 10
                
                # Alma (lado izquierdo)
                painter.fillRect(
                    center_x - ancho//2,
                    center_y - altura//2,
                    espesor_alma,
                    altura,
                    QBrush(QColor(180, 180, 180))
                )
                
                # Ala superior
                painter.fillRect(
                    center_x - ancho//2,
                    center_y - altura//2,
                    ancho,
                    espesor_alas,
                    QBrush(QColor(180, 180, 180))
                )
                
                # Ala inferior
                painter.fillRect(
                    center_x - ancho//2,
                    center_y + altura//2 - espesor_alas,
                    ancho,
                    espesor_alas,
                    QBrush(QColor(180, 180, 180))
                )
                
            elif tipo_perfil == 'Tubular cuadrado':
                # Dimensiones para tubular cuadrado
                tam_ext = 100
                espesor = 8
                
                # Cuadrado exterior
                painter.setBrush(QBrush(QColor(180, 180, 180)))
                painter.drawRect(
                    center_x - tam_ext//2,
                    center_y - tam_ext//2,
                    tam_ext,
                    tam_ext
                )
                
                # Cuadrado interior (hueco)
                painter.setBrush(QBrush(QColor(255, 255, 255)))
                painter.drawRect(
                    center_x - tam_ext//2 + espesor,
                    center_y - tam_ext//2 + espesor,
                    tam_ext - 2*espesor,
                    tam_ext - 2*espesor
                )
                
            elif tipo_perfil == 'Tubular circular':
                # Dimensiones para tubular circular
                radio_ext = 50
                espesor = 8
                radio_int = radio_ext - espesor
                
                # Círculo exterior
                painter.setBrush(QBrush(QColor(180, 180, 180)))
                painter.drawEllipse(QPoint(center_x, center_y), radio_ext, radio_ext)
                
                # Círculo interior (hueco)
                painter.setBrush(QBrush(QColor(255, 255, 255)))
                painter.drawEllipse(QPoint(center_x, center_y), radio_int, radio_int)
                
            elif tipo_perfil == 'L':
                # Dimensiones para ángulo L
                altura = 120
                ancho = 80
                espesor = 10
                
                # Dibujar la L con un camino
                path = QPainterPath()
                path.moveTo(center_x - ancho//2, center_y - altura//2)
                path.lineTo(center_x - ancho//2, center_y + altura//2)
                path.lineTo(center_x - ancho//2 + ancho, center_y + altura//2)
                path.lineTo(center_x - ancho//2 + ancho, center_y + altura//2 - espesor)
                path.lineTo(center_x - ancho//2 + espesor, center_y + altura//2 - espesor)
                path.lineTo(center_x - ancho//2 + espesor, center_y - altura//2)
                path.closeSubpath()
                
                painter.fillPath(path, QBrush(QColor(180, 180, 180)))
                
            elif tipo_perfil == 'T':
                # Dimensiones para T
                altura = 120
                ancho = 80
                espesor_alma = 10
                espesor_ala = 10
                
                # Ala horizontal (superior)
                painter.fillRect(
                    center_x - ancho//2,
                    center_y - altura//2,
                    ancho,
                    espesor_ala,
                    QBrush(QColor(180, 180, 180))
                )
                
                # Alma vertical
                painter.fillRect(
                    center_x - espesor_alma//2,
                    center_y - altura//2 + espesor_ala,
                    espesor_alma,
                    altura - espesor_ala,
                    QBrush(QColor(180, 180, 180))
                )
                
            else:
                # Para perfiles desconocidos o no implementados
                painter.setFont(QFont("Arial", 12))
                painter.drawText(QRect(10, 50, 280, 100), Qt.AlignCenter, f"Esquema no disponible\npara perfil {tipo_perfil}")
            
            # Dibujar dimensiones y cotas
            pen.setWidth(1)
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            
            # Finalizar pintor
            painter.end()
            
            # Mostrar esquema
            self.schema_label.setPixmap(pixmap)
            
        except Exception as e:
            import traceback
            print(f"Error al actualizar esquema del perfil: {str(e)}")
            print(traceback.format_exc())
            
            # En caso de error, mostrar un esquema de fallback
            pixmap = QPixmap(300, 200)
            pixmap.fill(Qt.white)
            painter = QPainter(pixmap)
            painter.setFont(QFont("Arial", 12))
            painter.drawText(QRect(10, 10, 280, 180), Qt.AlignCenter, f"Perfil {tipo_perfil}\n(Error al generar esquema)")
            painter.end()
            self.schema_label.setPixmap(pixmap)
    
    def clear_fields(self):
        """Limpiar todos los campos del formulario."""
        # Restablecer valores predeterminados
        self.tipo_perfil_combo.setCurrentIndex(0)
        self.tipo_acero_combo.setCurrentIndex(0)
        self.longitud_spin.setValue(3000)
        self.condicion_apoyo_combo.setCurrentIndex(0)
        
        # Restablecer dimensiones
        self.altura_perfil_spin.setValue(200)
        self.ancho_alas_spin.setValue(100)
        self.espesor_alma_spin.setValue(5.6)
        self.espesor_alas_spin.setValue(8.5)
        self.dimension_exterior_spin.setValue(150)
        self.espesor_spin.setValue(8)
        
        # Actualizar campos visibles
        self.update_dimension_fields()
        self.update_profile_schema()
    
    def load_predefined_profile(self):
        """Cargar perfil predefinido según la selección."""
        try:
            # Obtener tipo de perfil y designación
            tipo_perfil = self.tipo_perfil_combo.currentText()
            designacion = self.designacion_combo.currentText()
            
            # Si no hay designación seleccionada, salir
            if not designacion:
                return
            
            # Cargar datos del perfil
            profile_data = self.load_profile_data(tipo_perfil, designacion)
            
            if not profile_data:
                return
            
            # Actualizar campos con datos del perfil
            if tipo_perfil in ['IPE', 'HEB', 'HEA', 'HEM', 'UPN', 'T']:
                self.altura_perfil_spin.setValue(profile_data["altura_perfil_mm"])
                self.ancho_alas_spin.setValue(profile_data["ancho_alas_mm"])
                self.espesor_alma_spin.setValue(profile_data["espesor_alma_mm"])
                self.espesor_alas_spin.setValue(profile_data["espesor_alas_mm"])
            elif tipo_perfil == 'L':
                self.altura_angulo_spin.setValue(profile_data["altura_perfil_mm"])
                self.ancho_angulo_spin.setValue(profile_data["ancho_alas_mm"])
                self.espesor_angulo_spin.setValue(profile_data["espesor_mm"])
            elif tipo_perfil in ['Tubular cuadrado', 'Tubular circular']:
                self.dimension_exterior_spin.setValue(profile_data["dimension_exterior_mm"])
                self.espesor_spin.setValue(profile_data["espesor_mm"])
        except Exception as e:
            import traceback
            print(f"Error al cargar perfil predefinido: {str(e)}")
            print(traceback.format_exc())
            # Mostrar mensaje de error
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Advertencia", f"Error al cargar perfil predefinido: {str(e)}")
    
    def handle_model_loaded(self, success):
        """Manejar evento de carga del modelo."""
        if not success:
            QMessageBox.warning(
                self,
                "Error al cargar el modelo",
                "No se ha podido cargar el modelo de predicción. Algunas funcionalidades pueden no estar disponibles."
            )
            self.calculate_button.setEnabled(False)
    
    def get_current_config(self):
        """Obtener la configuración actual como diccionario."""
        tipo_perfil = self.tipo_perfil_combo.currentText()
        
        config = {
            "tipo_perfil": tipo_perfil,
            "tipo_acero": self.tipo_acero_combo.currentText(),
            "longitud_mm": self.longitud_spin.value(),
            "condicion_apoyo": self.condicion_apoyo_combo.currentText()
        }
        
        # Agregar dimensiones según tipo de perfil
        if tipo_perfil in ['IPE', 'HEB', 'HEA', 'HEM', 'UPN', 'L', 'T']:
            config.update({
                "altura_perfil_mm": self.altura_perfil_spin.value(),
                "ancho_alas_mm": self.ancho_alas_spin.value(),
                "espesor_alma_mm": self.espesor_alma_spin.value(),
                "espesor_alas_mm": self.espesor_alas_spin.value()
            })
        elif tipo_perfil in ['Tubular cuadrado', 'Tubular circular']:
            config.update({
                "dimension_exterior_mm": self.dimension_exterior_spin.value(),
                "espesor_mm": self.espesor_spin.value()
            })
        
        return config
    
    def apply_config(self, config):
        """Aplicar una configuración desde un diccionario."""
        try:
            # Establecer tipo de perfil primero para que se actualicen los campos
            if "tipo_perfil" in config:
                self.tipo_perfil_combo.setCurrentText(config["tipo_perfil"])
            
            # Establecer otros valores básicos
            if "tipo_acero" in config:
                self.tipo_acero_combo.setCurrentText(config["tipo_acero"])
            if "longitud_mm" in config:
                self.longitud_spin.setValue(float(config["longitud_mm"]))
            if "condicion_apoyo" in config:
                self.condicion_apoyo_combo.setCurrentText(config["condicion_apoyo"])
            
            # Establecer dimensiones según tipo de perfil
            tipo_perfil = config.get("tipo_perfil", self.tipo_perfil_combo.currentText())
            
            if tipo_perfil in ['IPE', 'HEB', 'HEA', 'HEM', 'UPN', 'L', 'T']:
                if "altura_perfil_mm" in config:
                    self.altura_perfil_spin.setValue(float(config["altura_perfil_mm"]))
                if "ancho_alas_mm" in config:
                    self.ancho_alas_spin.setValue(float(config["ancho_alas_mm"]))
                if "espesor_alma_mm" in config:
                    self.espesor_alma_spin.setValue(float(config["espesor_alma_mm"]))
                if "espesor_alas_mm" in config:
                    self.espesor_alas_spin.setValue(float(config["espesor_alas_mm"]))
            elif tipo_perfil in ['Tubular cuadrado', 'Tubular circular']:
                if "dimension_exterior_mm" in config:
                    self.dimension_exterior_spin.setValue(float(config["dimension_exterior_mm"]))
                if "espesor_mm" in config:
                    self.espesor_spin.setValue(float(config["espesor_mm"]))
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error al aplicar configuración",
                f"Se ha producido un error al aplicar la configuración: {str(e)}"
            )
    
    def calculate(self):
        """Realizar cálculo de predicción con los parámetros actuales."""
        try:
            # Obtener configuración actual
            params = self.get_current_config()
            
            # Realizar predicción
            results = self.prediction_model.predict(params)
            
            # Emitir señal con resultados
            self.prediction_ready.emit(results)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error en el cálculo",
                f"Se ha producido un error durante el cálculo: {str(e)}"
            ) 