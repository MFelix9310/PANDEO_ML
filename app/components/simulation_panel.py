from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QLabel, QSlider, QPushButton, QSpinBox, QCheckBox,
                            QSplitter, QFormLayout, QMessageBox, QComboBox,
                            QFileDialog, QApplication)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import sys
import os

# Añadir ruta al directorio padre
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.result_exporter import ResultExporter

class SimulationPanel(QWidget):
    """Panel para simulación animada del fenómeno de pandeo."""
    
    # Señal emitida cuando cambia la animación
    animation_step_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        
        # Resultados actuales
        self.current_results = None
        
        # Estado de la simulación
        self.is_playing = False
        self.current_step = 0
        self.total_steps = 100
        
        # Temporizador para animación
        self.timer = QTimer()
        self.timer.timeout.connect(self.advance_animation)
        
        # Objetos de animación
        self.animation = None
        self.profile_patches = []
        
        # Inicializar UI
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar la interfaz de usuario del panel de simulación."""
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Simulación del Fenómeno de Pandeo")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Mensaje inicial
        self.empty_label = QLabel("Realice un cálculo para ver la simulación")
        self.empty_label.setAlignment(Qt.AlignCenter)
        empty_font = QFont()
        empty_font.setItalic(True)
        self.empty_label.setFont(empty_font)
        main_layout.addWidget(self.empty_label)
        
        # Crear splitter para dividir controles y simulación
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo: Controles de simulación
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Grupo de opciones de simulación
        sim_options_group = QGroupBox("Opciones de Simulación")
        sim_options_layout = QFormLayout()
        
        # Velocidad de la simulación
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(10, 500)
        self.speed_spin.setValue(100)
        self.speed_spin.setSuffix(" ms")
        sim_options_layout.addRow("Velocidad:", self.speed_spin)
        
        # Duración total de la simulación
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(10, 300)
        self.duration_spin.setValue(60)
        self.duration_spin.setSuffix(" s")
        sim_options_layout.addRow("Duración:", self.duration_spin)
        
        # Factor de escala para deformación
        self.scale_factor_slider = QSlider(Qt.Horizontal)
        self.scale_factor_slider.setMinimum(1)
        self.scale_factor_slider.setMaximum(100)
        self.scale_factor_slider.setValue(50)
        self.scale_factor_slider.setTickPosition(QSlider.TicksBelow)
        self.scale_factor_slider.setTickInterval(10)
        sim_options_layout.addRow("Factor de Escala:", self.scale_factor_slider)
        
        # Tipo de visualización
        self.view_type_combo = QComboBox()
        self.view_type_combo.addItems(["Frontal", "Lateral", "Superior", "Isométrica"])
        sim_options_layout.addRow("Vista:", self.view_type_combo)
        
        # Mostrar tensiones
        self.show_stress_check = QCheckBox("Mostrar Tensiones")
        self.show_stress_check.setChecked(True)
        sim_options_layout.addRow("", self.show_stress_check)
        
        # Mostrar deformada
        self.show_deformed_check = QCheckBox("Mostrar Deformada")
        self.show_deformed_check.setChecked(True)
        sim_options_layout.addRow("", self.show_deformed_check)
        
        sim_options_group.setLayout(sim_options_layout)
        left_layout.addWidget(sim_options_group)
        
        # Grupo de controles de simulación
        controls_group = QGroupBox("Controles de Simulación")
        controls_layout = QVBoxLayout()
        
        # Botones de control
        control_buttons_layout = QHBoxLayout()
        
        self.play_button = QPushButton("Reproducir")
        self.play_button.clicked.connect(self.toggle_play)
        control_buttons_layout.addWidget(self.play_button)
        
        self.reset_button = QPushButton("Reiniciar")
        self.reset_button.clicked.connect(self.reset_animation)
        control_buttons_layout.addWidget(self.reset_button)
        
        controls_layout.addLayout(control_buttons_layout)
        
        # Slider para progreso de la animación
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(self.total_steps - 1)
        self.progress_slider.setValue(0)
        self.progress_slider.setTickPosition(QSlider.TicksBelow)
        self.progress_slider.setTickInterval(10)
        self.progress_slider.valueChanged.connect(self.set_animation_step)
        controls_layout.addWidget(self.progress_slider)
        
        # Etiqueta para mostrar progreso
        self.progress_label = QLabel("0%")
        self.progress_label.setAlignment(Qt.AlignCenter)
        controls_layout.addWidget(self.progress_label)
        
        controls_group.setLayout(controls_layout)
        left_layout.addWidget(controls_group)
        
        # Grupo de acciones
        actions_group = QGroupBox("Acciones")
        actions_layout = QVBoxLayout()
        
        # Botón para exportar simulación
        self.export_button = QPushButton("Exportar Simulación")
        self.export_button.clicked.connect(self.export_simulation)
        actions_layout.addWidget(self.export_button)
        
        # Botón para exportar datos a Excel
        self.export_excel_button = QPushButton("Exportar a Excel")
        self.export_excel_button.clicked.connect(self.export_to_excel)
        actions_layout.addWidget(self.export_excel_button)
        
        actions_group.setLayout(actions_layout)
        left_layout.addWidget(actions_group)
        
        # Agregar espacio expandible al final
        left_layout.addStretch()
        
        # Panel derecho: Área de simulación
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear figura para simulación
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(right_panel)
        right_layout.addWidget(self.canvas)
        
        # Agregar paneles al splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter)
        
        # Conectar señales
        self.connect_signals()
        
        # Inicializar figura vacía
        self.init_figure()
        
        # Ocultar inicialmente los controles de simulación
        self.reset_button.setEnabled(False)
        self.play_button.setEnabled(False)
        self.progress_slider.setEnabled(False)
        self.export_button.setEnabled(False)
        self.export_excel_button.setEnabled(False)
        
        self.setLayout(main_layout)
    
    def connect_signals(self):
        """Conectar señales y slots."""
        self.speed_spin.valueChanged.connect(self.update_animation_speed)
        self.scale_factor_slider.valueChanged.connect(self.update_simulation)
        self.view_type_combo.currentIndexChanged.connect(self.change_view)
        self.show_stress_check.stateChanged.connect(self.update_simulation)
        self.show_deformed_check.stateChanged.connect(self.update_simulation)
        self.animation_step_changed.connect(self.update_animation_display)
    
    def init_figure(self):
        """Inicializar figura vacía."""
        self.figure.clear()
        self.ax = self.figure.add_subplot(111, projection='3d')
        
        # Configurar ejes sin etiquetas por ahora (se añadirán después)
        self.ax.set_xlabel('', labelpad=0)
        self.ax.set_ylabel('', labelpad=0)
        self.ax.set_zlabel('', labelpad=0)
        
        # Quitar las etiquetas existentes
        self.ax.xaxis.set_ticklabels([])
        self.ax.yaxis.set_ticklabels([])
        self.ax.zaxis.set_ticklabels([])
        
        # Ajustar el título
        self.ax.set_title('Simulación de Pandeo', fontsize=12, pad=10)
        
        # Añadir textos para ejes con posiciones fijas
        self.ax.text2D(0.5, 0.01, "X (mm)", transform=self.ax.transAxes, fontsize=10, ha='center')
        self.ax.text2D(0.01, 0.5, "Y (mm)", transform=self.ax.transAxes, fontsize=10, va='center')
        self.ax.text2D(0.85, 0.85, "Z (mm)", transform=self.ax.transAxes, fontsize=10)
        
        self.canvas.draw()
    
    def update_simulation(self, results=None):
        """
        Actualizar la simulación.
        
        Args:
            results (dict, optional): Diccionario con los resultados de la predicción.
                Si es None, se utilizan los resultados actuales.
        """
        # Actualizar resultados si se proporcionan
        if results is not None:
            self.current_results = results
            
        # Verificar si hay resultados y si son un diccionario
        if self.current_results is None or not isinstance(self.current_results, dict):
            return
        
        # Ocultar mensaje inicial
        self.empty_label.setVisible(False)
        
        # Habilitar controles de simulación
        self.reset_button.setEnabled(True)
        self.play_button.setEnabled(True)
        self.progress_slider.setEnabled(True)
        self.export_button.setEnabled(True)
        self.export_excel_button.setEnabled(True)
        
        # Detener animación actual si está reproduciéndose
        if self.is_playing:
            self.toggle_play()
        
        # Reiniciar animación
        self.current_step = 0
        self.progress_slider.setValue(0)
        
        # Actualizar figura
        self.figure.clear()
        self.ax = self.figure.add_subplot(111, projection='3d')
        
        # Configurar ejes sin etiquetas por ahora (se añadirán después)
        self.ax.set_xlabel('', labelpad=0)
        self.ax.set_ylabel('', labelpad=0)
        self.ax.set_zlabel('', labelpad=0)
        
        # Quitar las etiquetas existentes
        self.ax.xaxis.set_ticklabels([])
        self.ax.yaxis.set_ticklabels([])
        self.ax.zaxis.set_ticklabels([])
        
        # Configurar vista según selección
        view_type = self.view_type_combo.currentText()
        if view_type == "Frontal":
            self.ax.view_init(elev=0, azim=0)
        elif view_type == "Lateral":
            self.ax.view_init(elev=0, azim=90)
        elif view_type == "Superior":
            self.ax.view_init(elev=90, azim=0)
        else:  # Isométrica
            self.ax.view_init(elev=30, azim=30)
        
        # Obtener datos del perfil
        tipo_perfil = self.current_results.get('tipo_perfil')
        longitud_mm = self.current_results.get('longitud_mm')
        
        if tipo_perfil is None or longitud_mm is None:
            # Si no tenemos los datos mínimos necesarios, no continuamos
            return
        
        # Crear geometría según tipo de perfil
        self.create_profile_geometry()
        
        # Configurar ejes
        max_dim = max(longitud_mm, 500)  # Asegurar espacio suficiente
        
        self.ax.set_xlim(-max_dim/4, max_dim/4)
        self.ax.set_ylim(-max_dim/4, max_dim/4)
        self.ax.set_zlim(0, longitud_mm)
        
        # Añadir textos para ejes con posiciones fijas
        self.ax.text2D(0.5, 0.01, "X (mm)", transform=self.ax.transAxes, fontsize=10, ha='center')
        self.ax.text2D(0.01, 0.5, "Y (mm)", transform=self.ax.transAxes, fontsize=10, va='center')
        self.ax.text2D(0.85, 0.85, "Z (mm)", transform=self.ax.transAxes, fontsize=10)
        
        # Ajustar el título
        self.ax.set_title('Simulación de Pandeo', fontsize=12, pad=10)
        
        # Mostrar figura
        self.canvas.draw()
    
    def create_profile_geometry(self):
        """Crear geometría del perfil para la simulación."""
        # Limpiar lista de parches
        self.profile_patches = []
        
        # Verificar si hay resultados válidos
        if not isinstance(self.current_results, dict):
            return
            
        # Obtener datos del perfil
        tipo_perfil = self.current_results.get('tipo_perfil')
        longitud_mm = self.current_results.get('longitud_mm')
        
        if tipo_perfil is None or longitud_mm is None:
            return
        
        # Número de secciones a lo largo de la longitud
        # Aumentar el número para mayor detalle y mejor visualización de la deformada
        num_sections = 40
        
        # Crear secciones del perfil a lo largo de la longitud
        for i in range(num_sections + 1):
            z = i * longitud_mm / num_sections
            
            # Crear sección según tipo de perfil
            if tipo_perfil in ['IPE', 'HEB', 'HEA', 'HEM']:
                # Perfiles tipo I/H
                altura_perfil = self.current_results.get('altura_perfil_mm', 200)
                ancho_alas = self.current_results.get('ancho_alas_mm', 100)
                
                self.create_i_section_patch(altura_perfil, ancho_alas, z)
                
            elif tipo_perfil == 'UPN':
                # Perfiles tipo U
                altura_perfil = self.current_results.get('altura_perfil_mm', 200)
                ancho_alas = self.current_results.get('ancho_alas_mm', 80)
                
                self.create_u_section_patch(altura_perfil, ancho_alas, z)
                
            elif tipo_perfil == 'Tubular cuadrado':
                # Perfiles tubulares cuadrados
                dimension_exterior = self.current_results.get('dimension_exterior_mm', 150)
                
                self.create_square_tube_patch(dimension_exterior, z)
                
            elif tipo_perfil == 'Tubular circular':
                # Perfiles tubulares circulares
                dimension_exterior = self.current_results.get('dimension_exterior_mm', 168.3)
                
                self.create_circular_tube_patch(dimension_exterior, z)
                
            elif tipo_perfil == 'L':
                # Perfiles tipo L
                altura_perfil = self.current_results.get('altura_perfil_mm', 200)
                ancho_alas = self.current_results.get('ancho_alas_mm', 100)
                
                self.create_l_section_patch(altura_perfil, ancho_alas, z)
                
            elif tipo_perfil == 'T':
                # Perfiles tipo T
                altura_perfil = self.current_results.get('altura_perfil_mm', 200)
                ancho_alas = self.current_results.get('ancho_alas_mm', 100)
                
                self.create_t_section_patch(altura_perfil, ancho_alas, z)
                
            else:
                # Perfil genérico (rectangular)
                self.create_rectangular_patch(100, 200, z)
    
    def create_i_section_patch(self, height, width, z):
        """Crear parche para sección tipo I/H en posición z."""
        # Coordenadas de la sección
        x = np.array([-width/2, width/2, width/2, -width/2, -width/2])
        y = np.array([height/2, height/2, -height/2, -height/2, height/2])
        
        # Crear parche y añadir al eje - aumentar linewidth para mejor visualización
        patch = self.ax.plot(x, y, z, 'b-', linewidth=3)[0]
        self.profile_patches.append((patch, x, y, z))
    
    def create_u_section_patch(self, height, width, z):
        """Crear parche para sección tipo U en posición z."""
        # Coordenadas de la sección
        x = np.array([-width/2, width/2, width/2, -width/2, -width/2])
        y = np.array([height/2, height/2, -height/2, -height/2, height/2])
        
        # Crear parche y añadir al eje - aumentar linewidth para mejor visualización
        patch = self.ax.plot(x, y, z, 'b-', linewidth=3)[0]
        self.profile_patches.append((patch, x, y, z))
    
    def create_square_tube_patch(self, size, z):
        """Crear parche para sección tubular cuadrada en posición z."""
        # Coordenadas de la sección
        x = np.array([-size/2, size/2, size/2, -size/2, -size/2])
        y = np.array([size/2, size/2, -size/2, -size/2, size/2])
        
        # Crear parche y añadir al eje - aumentar linewidth para mejor visualización
        patch = self.ax.plot(x, y, z, 'b-', linewidth=3)[0]
        self.profile_patches.append((patch, x, y, z))
    
    def create_circular_tube_patch(self, diameter, z):
        """Crear parche para sección tubular circular en posición z."""
        # Coordenadas de la sección (aproximación con polígono)
        # Usar más puntos para una mejor aproximación
        theta = np.linspace(0, 2*np.pi, 30)
        x = diameter/2 * np.cos(theta)
        y = diameter/2 * np.sin(theta)
        
        # Crear parche y añadir al eje - aumentar linewidth para mejor visualización
        patch = self.ax.plot(x, y, z, 'b-', linewidth=3)[0]
        self.profile_patches.append((patch, x, y, z))
    
    def create_l_section_patch(self, height, width, z):
        """Crear parche para sección tipo L en posición z."""
        # Coordenadas de la sección
        x = np.array([0, width, width, 0, 0, 0])
        y = np.array([0, 0, -height/10, -height/10, -height, 0])
        
        # Crear parche y añadir al eje - aumentar linewidth para mejor visualización
        patch = self.ax.plot(x, y, z, 'b-', linewidth=3)[0]
        self.profile_patches.append((patch, x, y, z))
    
    def create_t_section_patch(self, height, width, z):
        """Crear parche para sección tipo T en posición z."""
        # Coordenadas de la sección
        x = np.array([-width/2, width/2, width/2, width/10, width/10, -width/10, -width/10, -width/2, -width/2])
        y = np.array([0, 0, -height/10, -height/10, -height, -height, -height/10, -height/10, 0])
        
        # Crear parche y añadir al eje - aumentar linewidth para mejor visualización
        patch = self.ax.plot(x, y, z, 'b-', linewidth=3)[0]
        self.profile_patches.append((patch, x, y, z))
    
    def create_rectangular_patch(self, width, height, z):
        """Crear parche para sección rectangular en posición z."""
        # Coordenadas de la sección
        x = np.array([-width/2, width/2, width/2, -width/2, -width/2])
        y = np.array([height/2, height/2, -height/2, -height/2, height/2])
        
        # Crear parche y añadir al eje - aumentar linewidth para mejor visualización
        patch = self.ax.plot(x, y, z, 'b-', linewidth=3)[0]
        self.profile_patches.append((patch, x, y, z))
    
    def toggle_play(self):
        """Iniciar o pausar la animación."""
        if self.is_playing:
            # Pausar
            self.timer.stop()
            self.play_button.setText("Reproducir")
            self.is_playing = False
        else:
            # Reproducir
            interval = self.speed_spin.value()
            self.timer.start(interval)
            self.play_button.setText("Pausar")
            self.is_playing = True
    
    def advance_animation(self):
        """Avanzar un paso en la animación."""
        if self.current_step < self.total_steps - 1:
            self.current_step += 1
        else:
            self.current_step = 0
        
        self.progress_slider.setValue(self.current_step)
        self.animation_step_changed.emit(self.current_step)
    
    def set_animation_step(self, step):
        """Establecer paso específico de la animación."""
        self.current_step = step
        self.progress_label.setText(f"{int(step / (self.total_steps - 1) * 100)}%")
        self.animation_step_changed.emit(step)
        self.update_animation_display(step)
    
    def update_animation_display(self, step):
        """Actualizar visualización de la animación según el paso actual."""
        if not self.profile_patches or not isinstance(self.current_results, dict):
            return
        
        # Calcular factor de carga para este paso
        load_factor = step / (self.total_steps - 1)
        
        # Obtener el desplazamiento lateral máximo
        max_displacement = self.current_results.get('desplazamiento_lateral_mm', 0)
        
        # Aumentar significativamente el desplazamiento para hacerlo más visible
        # Usar un factor más grande para hacer la deformación muy visible
        max_displacement = max_displacement * 20
        
        # Obtener factor de escala (1-100)
        scale_factor = self.scale_factor_slider.value() / 50.0
        
        # Longitud del elemento
        longitud_mm = self.current_results.get('longitud_mm', 1000)
        
        # Obtener condición de apoyo
        condicion_apoyo = self.current_results.get('condicion_apoyo', 'Biarticulado')
        
        # Mostrar deformada según opción
        show_deformed = self.show_deformed_check.isChecked()
        
        # Mostrar tensiones según opción
        show_stress = self.show_stress_check.isChecked()
        
        # Limpiar ejes de anotaciones anteriores
        for artist in self.ax.texts + self.ax.lines:
            if artist not in [patch[0] for patch in self.profile_patches]:
                artist.remove()
        
        # Actualizar cada parche
        for patch, x_orig, y_orig, z in self.profile_patches:
            if show_deformed:
                # Aplicar deformación según la carga
                # Para valores escalares de z
                if isinstance(z, (int, float)):
                    normalized_z = z / longitud_mm
                    
                    # Seleccionar la forma de deformación según el tipo de apoyo
                    if condicion_apoyo == 'Biarticulado' or condicion_apoyo == 'Articulado-Articulado':
                        # Forma sinusoidal para biarticulado
                        deformation_factor = np.sin(np.pi * normalized_z)
                    elif condicion_apoyo == 'Empotrado-Empotrado' or condicion_apoyo == 'Biempotrado':
                        # Forma sinusoidal para biempotrado
                        deformation_factor = np.sin(2 * np.pi * normalized_z)
                    elif condicion_apoyo == 'Empotrado-Articulado':
                        # Forma sinusoidal asimétrica para empotrado-articulado
                        deformation_factor = np.sin(0.7 * np.pi * normalized_z)
                    elif condicion_apoyo == 'Empotrado-Libre':
                        # Forma cuadrática para empotrado-libre (voladizo)
                        deformation_factor = (1 - np.cos(np.pi * normalized_z / 2))
                    else:
                        # Valor por defecto si no se reconoce el tipo de apoyo
                        deformation_factor = np.sin(np.pi * normalized_z)
                    
                    # Excentricidad inicial
                    excentricidad_inicial = max_displacement * 0.2
                    excentricidad = (normalized_z) * excentricidad_inicial
                    
                    # Calcular desplazamiento total
                    displacement_x = excentricidad + (max_displacement * deformation_factor * scale_factor * load_factor)
                    
                    # Aplicar desplazamiento a cada punto del perfil
                    x_deformed = x_orig + displacement_x
                    z_values = np.full_like(x_orig, z)
                # Para arrays de z (en caso de que z ya sea un array)
                else:
                    x_deformed = np.zeros_like(x_orig)
                    z_values = np.zeros_like(z)
                    
                    # Aplicar deformación a cada punto individualmente
                    for i in range(len(z)):
                        normalized_z = z[i] / longitud_mm
                        
                        # Seleccionar la forma de deformación según el tipo de apoyo
                        if condicion_apoyo == 'Biarticulado' or condicion_apoyo == 'Articulado-Articulado':
                            # Forma sinusoidal para biarticulado
                            deformation_factor = np.sin(np.pi * normalized_z)
                        elif condicion_apoyo == 'Empotrado-Empotrado' or condicion_apoyo == 'Biempotrado':
                            # Forma sinusoidal para biempotrado
                            deformation_factor = np.sin(2 * np.pi * normalized_z)
                        elif condicion_apoyo == 'Empotrado-Articulado':
                            # Forma sinusoidal asimétrica para empotrado-articulado
                            deformation_factor = np.sin(0.7 * np.pi * normalized_z)
                        elif condicion_apoyo == 'Empotrado-Libre':
                            # Forma cuadrática para empotrado-libre (voladizo)
                            deformation_factor = (1 - np.cos(np.pi * normalized_z / 2))
                        else:
                            # Valor por defecto si no se reconoce el tipo de apoyo
                            deformation_factor = np.sin(np.pi * normalized_z)
                        
                        # Excentricidad inicial
                        excentricidad_inicial = max_displacement * 0.2
                        excentricidad = (normalized_z) * excentricidad_inicial
                        
                        # Deformación sinusoidal con efecto de segundo orden
                        displacement_x = excentricidad + (max_displacement * deformation_factor * scale_factor * load_factor)
                        
                        # Aplicar desplazamiento
                        x_deformed[i] = x_orig[i] + displacement_x
                        z_values[i] = z[i]
                
                # Actualizar coordenadas
                patch.set_data_3d(x_deformed, y_orig, z_values)
                
                if show_stress:
                    # Calcular tensión aproximada (normalizada de 0 a 1)
                    if isinstance(z, (int, float)):
                        # Seleccionar la forma de tensión según el tipo de apoyo
                        if condicion_apoyo == 'Biarticulado' or condicion_apoyo == 'Articulado-Articulado':
                            stress_level = load_factor * np.sin(np.pi * (z / longitud_mm))
                        elif condicion_apoyo == 'Empotrado-Empotrado' or condicion_apoyo == 'Biempotrado':
                            stress_level = load_factor * np.sin(2 * np.pi * (z / longitud_mm))
                        elif condicion_apoyo == 'Empotrado-Articulado':
                            stress_level = load_factor * np.sin(0.7 * np.pi * (z / longitud_mm))
                        elif condicion_apoyo == 'Empotrado-Libre':
                            stress_level = load_factor * (1 - np.cos(np.pi * (z / longitud_mm) / 2))
                        else:
                            stress_level = load_factor * np.sin(np.pi * (z / longitud_mm))
                    else:
                        # Promedio para arrays
                        normalized_z_mean = np.mean(z) / longitud_mm
                        if condicion_apoyo == 'Biarticulado' or condicion_apoyo == 'Articulado-Articulado':
                            stress_level = load_factor * np.sin(np.pi * normalized_z_mean)
                        elif condicion_apoyo == 'Empotrado-Empotrado' or condicion_apoyo == 'Biempotrado':
                            stress_level = load_factor * np.sin(2 * np.pi * normalized_z_mean)
                        elif condicion_apoyo == 'Empotrado-Articulado':
                            stress_level = load_factor * np.sin(0.7 * np.pi * normalized_z_mean)
                        elif condicion_apoyo == 'Empotrado-Libre':
                            stress_level = load_factor * (1 - np.cos(np.pi * normalized_z_mean / 2))
                        else:
                            stress_level = load_factor * np.sin(np.pi * normalized_z_mean)
                    
                    # Colores desde azul (0) hasta rojo (1)
                    color = plt.cm.jet(stress_level)
                    patch.set_color(color)
                else:
                    # Color azul si no se muestran tensiones
                    patch.set_color('blue')
            else:
                # Mostrar geometría sin deformar
                z_values = np.full_like(x_orig, z) if isinstance(z, (int, float)) else z
                patch.set_data_3d(x_orig, y_orig, z_values)
                patch.set_color('blue')
        
        # Añadir visualización del efecto de esbeltez
        if show_deformed:
            # Excentricidad inicial (e)
            excentricidad_inicial = max_displacement * 0.2
            
            # Dibujar eje de la columna sin deformar (línea central)
            self.ax.plot([0, 0], [0, 0], [0, longitud_mm], 'k--', linewidth=1)
            
            # Calcular puntos de la deformada para una línea central
            z_points = np.linspace(0, longitud_mm, 50)
            x_deformed_points = []
            for z_point in z_points:
                normalized_z = z_point / longitud_mm
                
                # Seleccionar la forma de deformación según el tipo de apoyo
                if condicion_apoyo == 'Biarticulado' or condicion_apoyo == 'Articulado-Articulado':
                    deformation_factor = np.sin(np.pi * normalized_z)
                elif condicion_apoyo == 'Empotrado-Empotrado' or condicion_apoyo == 'Biempotrado':
                    deformation_factor = np.sin(2 * np.pi * normalized_z)
                elif condicion_apoyo == 'Empotrado-Articulado':
                    deformation_factor = np.sin(0.7 * np.pi * normalized_z)
                elif condicion_apoyo == 'Empotrado-Libre':
                    deformation_factor = (1 - np.cos(np.pi * normalized_z / 2))
                else:
                    deformation_factor = np.sin(np.pi * normalized_z)
                
                # Excentricidad inicial
                excentricidad = (normalized_z) * excentricidad_inicial
                x_deformed_point = excentricidad + (max_displacement * deformation_factor * scale_factor * load_factor)
                x_deformed_points.append(x_deformed_point)
            
            # Dibujar la deformada (línea central)
            self.ax.plot(x_deformed_points, np.zeros_like(z_points), z_points, 'r-', linewidth=2)
            
            # Excentricidad inicial en la parte superior
            self.ax.plot([0, excentricidad_inicial], [0, 0], [longitud_mm, longitud_mm], 'g-', linewidth=2)
            
            # Texto para la excentricidad inicial
            self.ax.text(excentricidad_inicial/2, 0, longitud_mm, 'e', color='green', fontsize=12)
            
            # Obtener el desplazamiento en el punto medio
            mid_index = len(z_points) // 2
            mid_z = z_points[mid_index]
            mid_x = x_deformed_points[mid_index]
            
            # Dibujar línea de desplazamiento y
            self.ax.plot([0, mid_x], [0, 0], [mid_z, mid_z], 'm-', linewidth=2)
            
            # Texto para el desplazamiento y
            self.ax.text(mid_x/2, 0, mid_z, 'y', color='magenta', fontsize=12)
            
            # Dibujar vectores de fuerza en extremos
            # Vector en la base
            self.ax.quiver(0, 0, 0, 0, 0, -longitud_mm*0.1, color='red', arrow_length_ratio=0.3, linewidth=3)
            
            # Vector en la parte superior (con excentricidad)
            top_x = x_deformed_points[-1]
            self.ax.quiver(top_x, 0, longitud_mm, 0, 0, longitud_mm*0.1, color='red', arrow_length_ratio=0.3, linewidth=3)
            
            # Añadir ecuaciones como texto
            # Posición para las ecuaciones (ajustar según sea necesario)
            eq_x = max_displacement * scale_factor * 0.4  # Ajustado para que no quede tan lejos
            eq_y = 0
            eq_z = longitud_mm * 0.5
            
            # Ecuaciones
            self.ax.text(eq_x, eq_y, eq_z, 'Ma = P(e+y)', color='red', fontsize=10)
            self.ax.text(eq_x, eq_y, eq_z - longitud_mm*0.05, 'Ma = Pe + Py', color='red', fontsize=10)
            self.ax.text(eq_x, eq_y, eq_z - longitud_mm*0.1, f'Carga: {load_factor*100:.0f}%', color='black', fontsize=10)
            
            # Información adicional sobre condición de apoyo
            self.ax.text(eq_x, eq_y, eq_z - longitud_mm*0.15, f'Apoyo: {condicion_apoyo}', color='black', fontsize=10)
            
            # Actualizar título con información de carga
            carga_actual = self.current_results.get('carga_maxima_kN', 0) * load_factor
            self.ax.set_title(f'Efecto de Esbeltez - Carga: {carga_actual:.2f} kN')
        else:
            # Actualizar título para estado sin deformar
            self.ax.set_title('Simulación de Pandeo - Estado inicial')
        
        # Actualizar canvas
        self.canvas.draw()
    
    def reset_animation(self):
        """Reiniciar la animación."""
        # Detener animación si está reproduciéndose
        if self.is_playing:
            self.toggle_play()
        
        # Reiniciar a paso 0
        self.current_step = 0
        self.progress_slider.setValue(0)
        
        # Restablecer la geometría original (sin deformación)
        for patch, x_orig, y_orig, z in self.profile_patches:
            # Asegurar que z sea una secuencia
            z_values = np.full_like(x_orig, z) if isinstance(z, (int, float)) else z
            # Restaurar las coordenadas originales
            patch.set_data_3d(x_orig, y_orig, z_values)
            # Restaurar color original
            patch.set_color('blue')
        
        # Limpiar ejes de anotaciones anteriores
        for artist in self.ax.texts + self.ax.lines:
            if artist not in [patch[0] for patch in self.profile_patches]:
                artist.remove()
        
        # Actualizar título
        self.ax.set_title('Simulación de Pandeo - Estado inicial')
        
        # Actualizar el progreso en la etiqueta
        self.progress_label.setText("0%")
        
        # Actualizar canvas
        self.canvas.draw()
    
    def update_animation_speed(self, value):
        """Actualizar velocidad de la animación."""
        if self.is_playing:
            self.timer.stop()
            self.timer.start(value)
    
    def export_simulation(self):
        """Exportar simulación como archivo de video."""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        
        try:
            import matplotlib.animation as animation
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_agg import FigureCanvasAgg
        except ImportError:
            QMessageBox.critical(
                self, 
                "Error", 
                "No se han podido importar las bibliotecas necesarias para exportar la simulación.\n"
                "Asegúrese de tener instalado FFmpeg y matplotlib."
            )
            return
        
        # Abrir diálogo para guardar archivo
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Exportar Simulación", 
            "", 
            "Archivos MP4 (*.mp4);;Archivos GIF (*.gif)"
        )
        
        if not file_path:
            return
        
        try:
            # Crear nueva figura para la exportación
            fig = plt.figure(figsize=(10, 8), dpi=100)
            ax = fig.add_subplot(111, projection='3d')
            
            # Configurar vista según selección
            view_type = self.view_type_combo.currentText()
            if view_type == "Frontal":
                ax.view_init(elev=0, azim=0)
            elif view_type == "Lateral":
                ax.view_init(elev=0, azim=90)
            elif view_type == "Superior":
                ax.view_init(elev=90, azim=0)
            else:  # Isométrica
                ax.view_init(elev=30, azim=30)
            
            # Configurar ejes
            longitud_mm = self.current_results['longitud_mm']
            max_dim = max(longitud_mm, 500)
            
            ax.set_xlim(-max_dim/4, max_dim/4)
            ax.set_ylim(-max_dim/4, max_dim/4)
            ax.set_zlim(0, longitud_mm)
            
            ax.set_xlabel('X (mm)')
            ax.set_ylabel('Y (mm)')
            ax.set_zlabel('Z (mm)')
            
            # Crear geometría y parches iniciales
            patches = []
            x_orig_list = []
            y_orig_list = []
            z_list = []
            
            # Recrear geometría para la animación
            for patch, x_orig, y_orig, z in self.profile_patches:
                line, = ax.plot(x_orig, y_orig, z, 'b-', linewidth=2)
                patches.append(line)
                x_orig_list.append(x_orig)
                y_orig_list.append(y_orig)
                z_list.append(z)
            
            # Función de actualización para la animación
            def update_frame(frame):
                # Calcular factor de carga para este paso
                load_factor = frame / self.total_steps
                
                # Obtener el desplazamiento lateral máximo
                max_displacement = self.current_results['desplazamiento_lateral_mm']
                
                # Obtener factor de escala
                scale_factor = self.scale_factor_slider.value() / 50.0
                
                # Opciones de visualización
                show_deformed = self.show_deformed_check.isChecked()
                show_stress = self.show_stress_check.isChecked()
                
                # Actualizar cada parche
                for i, (patch, x_orig, y_orig, z) in enumerate(zip(patches, x_orig_list, y_orig_list, z_list)):
                    if show_deformed:
                        # Aplicar deformación según la carga
                        normalized_z = z / longitud_mm
                        deformation_factor = np.sin(np.pi * normalized_z)
                        displacement_x = max_displacement * deformation_factor * scale_factor * load_factor
                        
                        # Aplicar desplazamiento
                        x_deformed = x_orig + displacement_x
                        
                        # Actualizar coordenadas
                        patch.set_data_3d(x_deformed, y_orig, z)
                        
                        if show_stress:
                            # Calcular tensión aproximada (normalizada de 0 a 1)
                            stress_level = load_factor * deformation_factor
                            
                            # Colores desde azul (0) hasta rojo (1)
                            color = plt.cm.jet(stress_level)
                            patch.set_color(color)
                        else:
                            # Color azul si no se muestran tensiones
                            patch.set_color('blue')
                    else:
                        # Mostrar geometría sin deformar
                        patch.set_data_3d(x_orig, y_orig, z)
                        patch.set_color('blue')
                
                # Actualizar título con información de carga
                carga_actual = self.current_results['carga_maxima_kN'] * load_factor
                ax.set_title(f'Simulación de Pandeo - Carga: {carga_actual:.2f} kN')
                
                return patches
            
            # Crear animación
            frames = self.total_steps
            interval = self.speed_spin.value()
            anim = FuncAnimation(fig, update_frame, frames=frames, interval=interval, blit=False)
            
            # Mostrar mensaje de progreso
            progress_msg = QMessageBox()
            progress_msg.setWindowTitle("Exportando Simulación")
            progress_msg.setText("Exportando simulación. Este proceso puede tardar varios minutos.\n"
                                "Por favor, espere...")
            progress_msg.setStandardButtons(QMessageBox.NoButton)
            progress_msg.show()
            
            # Exportar animación
            if file_path.endswith('.mp4'):
                Writer = animation.writers['ffmpeg']
                writer = Writer(fps=1000/interval, metadata=dict(artist='PANDEO ML'), bitrate=1800)
                anim.save(file_path, writer=writer)
            elif file_path.endswith('.gif'):
                anim.save(file_path, writer='pillow', fps=1000/interval)
            
            # Cerrar mensaje de progreso
            progress_msg.close()
            
            # Mostrar mensaje de éxito
            QMessageBox.information(
                self, 
                "Exportación Completada", 
                f"Simulación exportada correctamente a {file_path}"
            )
            
            # Cerrar figura de matplotlib
            plt.close(fig)
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error en la Exportación", 
                f"Se ha producido un error al exportar la simulación:\n{str(e)}"
            )
    
    def change_view(self):
        """Cambiar la vista según la selección."""
        view_type = self.view_type_combo.currentText()
        
        if view_type == "Frontal":
            self.ax.view_init(elev=0, azim=0)
        elif view_type == "Lateral":
            self.ax.view_init(elev=0, azim=90)
        elif view_type == "Superior":
            self.ax.view_init(elev=90, azim=0)
        else:  # Isométrica
            self.ax.view_init(elev=30, azim=30)
        
        # Actualizar canvas
        self.canvas.draw()
    
    def export_to_excel(self):
        """Exportar resultados a un archivo Excel."""
        if not isinstance(self.current_results, dict):
            QMessageBox.warning(
                self, 
                "Error", 
                "No hay resultados disponibles para exportar."
            )
            return
        
        # Abrir diálogo para guardar archivo
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Exportar Resultados a Excel", 
            "", 
            "Archivos Excel (*.xlsx)"
        )
        
        if not file_path:
            return
        
        if not file_path.endswith('.xlsx'):
            file_path += '.xlsx'
        
        try:
            # Mostrar mensaje de espera
            wait_msg = QMessageBox()
            wait_msg.setWindowTitle("Exportando a Excel")
            wait_msg.setText("Generando archivo Excel con los resultados.\nEsto puede tardar unos segundos...")
            wait_msg.setStandardButtons(QMessageBox.NoButton)
            wait_msg.show()
            
            # Procesar eventos para mostrar el diálogo
            QApplication.processEvents()
            
            # Crear objeto exportador
            exporter = ResultExporter()
            
            # Crear un diccionario con los datos de entrada
            input_data = {
                'tipo_perfil': self.current_results.get('tipo_perfil', ''),
                'tipo_acero': self.current_results.get('tipo_acero', ''),
                'longitud_mm': self.current_results.get('longitud_mm', 0),
                'condicion_apoyo': self.current_results.get('condicion_apoyo', ''),
                'altura_perfil_mm': self.current_results.get('altura_perfil_mm', 0),
                'ancho_alas_mm': self.current_results.get('ancho_alas_mm', 0),
                'espesor_alma_mm': self.current_results.get('espesor_alma_mm', 0),
                'espesor_alas_mm': self.current_results.get('espesor_alas_mm', 0),
                'dimension_exterior_mm': self.current_results.get('dimension_exterior_mm', 0),
                'espesor_mm': self.current_results.get('espesor_mm', 0)
            }
            
            # Exportar a Excel
            exporter.export_to_excel(file_path, self.current_results, input_data)
            
            # Cerrar mensaje de espera
            wait_msg.close()
            
            # Mostrar mensaje de éxito
            QMessageBox.information(
                self, 
                "Exportación Completada", 
                f"Los resultados han sido exportados correctamente a:\n{file_path}"
            )
            
        except Exception as e:
            # Mostrar mensaje de error
            QMessageBox.critical(
                self, 
                "Error en la Exportación", 
                f"Se ha producido un error al exportar a Excel:\n{str(e)}\n\nIntentando exportar en formato simplificado..."
            )
            
            try:
                # Intentar exportar en formato simplificado sin gráficos
                import pandas as pd
                
                # Crear DataFrames básicos
                input_df = pd.DataFrame([
                    {"Parámetro": "Tipo de Perfil", "Valor": input_data.get("tipo_perfil", "")},
                    {"Parámetro": "Tipo de Acero", "Valor": input_data.get("tipo_acero", "")},
                    {"Parámetro": "Longitud", "Valor": f"{input_data.get('longitud_mm', 0):.2f} mm"},
                    {"Parámetro": "Condición de Apoyo", "Valor": input_data.get("condicion_apoyo", "")}
                ])
                
                results_df = pd.DataFrame([
                    {"Parámetro": "Carga Máxima (kN)", "Valor": f"{self.current_results.get('carga_maxima_kN', 0):.2f}"},
                    {"Parámetro": "Carga Máxima (kg)", "Valor": f"{self.current_results.get('carga_maxima_kg', 0):.2f}"},
                    {"Parámetro": "Desplazamiento Lateral (mm)", "Valor": f"{self.current_results.get('desplazamiento_lateral_mm', 0):.2f}"}
                ])
                
                # Guardar en Excel simplificado
                with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                    input_df.to_excel(writer, sheet_name='Datos de Entrada', index=False)
                    results_df.to_excel(writer, sheet_name='Resultados', index=False)
                
                QMessageBox.information(
                    self, 
                    "Exportación Simplificada Completada", 
                    f"Se ha exportado una versión simplificada de los resultados a:\n{file_path}\n\n"
                    f"Esta versión no incluye gráficos para evitar errores."
                )
                
            except Exception as e2:
                QMessageBox.critical(
                    self, 
                    "Error en la Exportación", 
                    f"No se ha podido exportar los resultados en ningún formato:\n{str(e2)}"
                ) 