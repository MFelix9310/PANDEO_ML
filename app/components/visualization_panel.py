from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QLabel, QSlider, QPushButton, QComboBox, QCheckBox,
                            QSplitter, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import numpy as np
import sys

# Importar pyvista para visualización 3D
try:
    import pyvista as pv
    from pyvistaqt import QtInteractor
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False

class VisualizationPanel(QWidget):
    """Panel para visualización 3D del perfil y el fenómeno de pandeo."""
    
    def __init__(self):
        super().__init__()
        
        # Resultados actuales
        self.current_results = None
        self.visualization_active = False
        
        # Inicializar UI
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar la interfaz de usuario del panel de visualización."""
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Visualización 3D del Fenómeno de Pandeo")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Mensaje si PyVista no está disponible
        if not PYVISTA_AVAILABLE:
            warning_label = QLabel("PyVista no está instalado. Para habilitar la visualización 3D, instale pyvista y pyvistaqt:\n"
                                 "pip install pyvista pyvistaqt")
            warning_label.setAlignment(Qt.AlignCenter)
            warning_font = QFont()
            warning_font.setItalic(True)
            warning_label.setFont(warning_font)
            main_layout.addWidget(warning_label)
            
            # Botón para instalar dependencias
            install_button = QPushButton("Instalar PyVista")
            install_button.clicked.connect(self.install_pyvista)
            main_layout.addWidget(install_button)
            
            self.setLayout(main_layout)
            return
        
        # Mensaje inicial
        self.empty_label = QLabel("Realice un cálculo para ver la visualización 3D")
        self.empty_label.setAlignment(Qt.AlignCenter)
        empty_font = QFont()
        empty_font.setItalic(True)
        self.empty_label.setFont(empty_font)
        main_layout.addWidget(self.empty_label)
        
        # Crear splitter para dividir controles y visualización
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo: Controles de visualización
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Grupo de opciones de visualización
        viz_options_group = QGroupBox("Opciones de Visualización")
        viz_options_layout = QFormLayout()
        
        # Modo de visualización
        self.viz_mode_combo = QComboBox()
        self.viz_mode_combo.addItems(["Modelo 3D", "Deformación", "Tensiones"])
        viz_options_layout.addRow("Modo:", self.viz_mode_combo)
        
        # Factor de escala para deformación
        self.scale_factor_slider = QSlider(Qt.Horizontal)
        self.scale_factor_slider.setMinimum(1)
        self.scale_factor_slider.setMaximum(100)
        self.scale_factor_slider.setValue(50)
        self.scale_factor_slider.setTickPosition(QSlider.TicksBelow)
        self.scale_factor_slider.setTickInterval(10)
        viz_options_layout.addRow("Factor de Escala:", self.scale_factor_slider)
        
        # Opciones de visualización
        self.show_axes_check = QCheckBox("Mostrar Ejes")
        self.show_axes_check.setChecked(True)
        viz_options_layout.addRow("", self.show_axes_check)
        
        self.show_grid_check = QCheckBox("Mostrar Cuadrícula")
        self.show_grid_check.setChecked(True)
        viz_options_layout.addRow("", self.show_grid_check)
        
        self.show_colorbar_check = QCheckBox("Mostrar Barra de Color")
        self.show_colorbar_check.setChecked(True)
        viz_options_layout.addRow("", self.show_colorbar_check)
        
        viz_options_group.setLayout(viz_options_layout)
        left_layout.addWidget(viz_options_group)
        
        # Grupo de controles de cámara
        camera_group = QGroupBox("Controles de Cámara")
        camera_layout = QVBoxLayout()
        
        # Botones para vistas predefinidas
        view_layout = QHBoxLayout()
        
        self.front_view_button = QPushButton("Frontal")
        self.front_view_button.clicked.connect(lambda: self.set_camera_view("front"))
        view_layout.addWidget(self.front_view_button)
        
        self.side_view_button = QPushButton("Lateral")
        self.side_view_button.clicked.connect(lambda: self.set_camera_view("side"))
        view_layout.addWidget(self.side_view_button)
        
        self.top_view_button = QPushButton("Superior")
        self.top_view_button.clicked.connect(lambda: self.set_camera_view("top"))
        view_layout.addWidget(self.top_view_button)
        
        self.isometric_view_button = QPushButton("Isométrica")
        self.isometric_view_button.clicked.connect(lambda: self.set_camera_view("isometric"))
        view_layout.addWidget(self.isometric_view_button)
        
        camera_layout.addLayout(view_layout)
        
        # Botón para resetear cámara
        self.reset_camera_button = QPushButton("Resetear Cámara")
        self.reset_camera_button.clicked.connect(self.reset_camera)
        camera_layout.addWidget(self.reset_camera_button)
        
        camera_group.setLayout(camera_layout)
        left_layout.addWidget(camera_group)
        
        # Grupo de acciones
        actions_group = QGroupBox("Acciones")
        actions_layout = QVBoxLayout()
        
        # Botón para actualizar visualización
        self.update_button = QPushButton("Actualizar Visualización")
        self.update_button.clicked.connect(self.update_visualization)
        actions_layout.addWidget(self.update_button)
        
        # Botón para exportar vista
        self.export_button = QPushButton("Exportar Vista")
        self.export_button.clicked.connect(self.export_view)
        actions_layout.addWidget(self.export_button)
        
        actions_group.setLayout(actions_layout)
        left_layout.addWidget(actions_group)
        
        # Agregar espacio expandible al final
        left_layout.addStretch()
        
        # Panel derecho: Visualización 3D
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear widget de PyVista
        self.plotter = QtInteractor(right_panel)
        right_layout.addWidget(self.plotter)
        
        # Configurar visualizador
        self.plotter.set_background("white")
        self.plotter.add_axes()
        self.plotter.show_grid()
        
        # Agregar paneles al splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([200, 600])
        
        main_layout.addWidget(splitter)
        
        # Conectar señales
        self.connect_signals()
        
        # Ocultar inicialmente el plotter
        self.plotter.setVisible(False)
        
        self.setLayout(main_layout)
    
    def connect_signals(self):
        """Conectar señales y slots."""
        if PYVISTA_AVAILABLE:
            self.viz_mode_combo.currentIndexChanged.connect(self.update_visualization)
            self.scale_factor_slider.valueChanged.connect(self.update_visualization)
            self.show_axes_check.stateChanged.connect(self.toggle_axes)
            self.show_grid_check.stateChanged.connect(self.toggle_grid)
            self.show_colorbar_check.stateChanged.connect(self.update_visualization)
    
    def update_visualization(self, results=None):
        """Actualizar la visualización 3D."""
        if not PYVISTA_AVAILABLE:
            return
        
        # Actualizar resultados si se proporcionan
        if results is not None:
            self.current_results = results
            
        # Verificar si hay resultados
        if self.current_results is None or not isinstance(self.current_results, dict):
            return
        
        # Ocultar mensaje inicial y mostrar plotter
        self.empty_label.setVisible(False)
        self.plotter.setVisible(True)
        
        # Limpiar visualización actual
        self.plotter.clear()
        
        # Modo de visualización seleccionado
        viz_mode = self.viz_mode_combo.currentText()
        
        # Obtener datos básicos
        tipo_perfil = self.current_results.get('tipo_perfil')
        longitud_mm = self.current_results.get('longitud_mm')
        
        if tipo_perfil is None or longitud_mm is None:
            return
        
        # Crear geometría del perfil
        profile_mesh = self.create_profile_mesh(self.current_results)
        
        # Aplicar deformación si está seleccionado
        if viz_mode == "Deformación" or viz_mode == "Tensiones":
            scale_factor = self.scale_factor_slider.value() / 25.0
            desplazamiento_lateral_mm = self.current_results.get('desplazamiento_lateral_mm', 0) * 5
            
            # Aplicar deformación al perfil
            profile_mesh = self.apply_deformation(profile_mesh, longitud_mm, desplazamiento_lateral_mm, scale_factor)
            
            # Añadir representación del efecto de esbeltez
            excentricidad_inicial = desplazamiento_lateral_mm * 0.2
            
            # Crear línea que representa la posición original
            line_original = pv.Line((0, 0, 0), (0, 0, longitud_mm))
            self.plotter.add_mesh(line_original, color="black", line_width=2, render_lines_as_tubes=True, style="dashed")
            
            # Crear puntos para la línea deformada (eje del elemento)
            points = []
            for i in range(50):
                z = i * longitud_mm / 49
                normalized_z = z / longitud_mm
                excentricidad = (z / longitud_mm) * excentricidad_inicial
                deformation_factor = np.sin(np.pi * normalized_z)
                displacement_x = excentricidad + (desplazamiento_lateral_mm * deformation_factor * scale_factor)
                points.append([displacement_x, 0, z])
            
            # Crear línea deformada (eje del elemento)
            line_deformed = pv.Spline(points, 50)
            self.plotter.add_mesh(line_deformed, color="red", line_width=3, render_lines_as_tubes=True)
            
            # Añadir vectores de fuerza
            self.plotter.add_arrows(
                np.array([[0, 0, 0]]),
                np.array([[0, 0, -longitud_mm * 0.1]]),
                color="red", scale=0.05 * longitud_mm
            )
            
            top_x = points[-1][0]
            self.plotter.add_arrows(
                np.array([[top_x, 0, longitud_mm]]),
                np.array([[0, 0, longitud_mm * 0.1]]),
                color="red", scale=0.05 * longitud_mm
            )
            
            # Añadir línea de excentricidad
            self.plotter.add_line((0, 0, longitud_mm), (excentricidad_inicial, 0, longitud_mm), color="green", width=3)
            
            # Añadir texto para ecuaciones
            self.plotter.add_point_labels(
                [np.array([desplazamiento_lateral_mm * scale_factor * 1.5, 0, longitud_mm * 0.5])],
                ["Ma = P(e+y)\nMa = Pe + Py"],
                font_size=14,
                text_color="red",
                shape_opacity=0.0
            )
        
        # Colorear según modo
        if viz_mode == "Tensiones":
            # Calcular tensiones aproximadas
            tensiones = self.calculate_stresses(profile_mesh, self.current_results)
            
            # Mostrar con mapa de colores
            self.plotter.add_mesh(
                profile_mesh, 
                scalars=tensiones, 
                cmap="jet", 
                show_edges=True,
                show_scalar_bar=self.show_colorbar_check.isChecked()
            )
            
            # Establecer título de la barra de color
            if self.show_colorbar_check.isChecked():
                scalar_bar = self.plotter.scalar_bar
                scalar_bar.SetTitle("Tensión (MPa)")
        else:
            # Mostrar modelo sin colores de tensión
            self.plotter.add_mesh(profile_mesh, color="lightblue", show_edges=True)
        
        # Mostrar ejes y cuadrícula según opciones
        if self.show_axes_check.isChecked():
            self.plotter.add_axes()
        
        if self.show_grid_check.isChecked():
            self.plotter.show_grid()
        
        # Añadir título
        if viz_mode == "Deformación" or viz_mode == "Tensiones":
            self.plotter.add_text("Efecto de Esbeltez en Elementos Comprimidos", font_size=14)
        else:
            self.plotter.add_text("Visualización 3D del Perfil", font_size=14)
        
        # Resetear la cámara
        self.plotter.reset_camera()
        
        # Marcar visualización como activa
        self.visualization_active = True
    
    def create_profile_mesh(self, results):
        """Crear malla 3D para el perfil según los resultados."""
        tipo_perfil = results['tipo_perfil']
        longitud_mm = results['longitud_mm']
        
        # Crear geometría según tipo de perfil
        if tipo_perfil in ['IPE', 'HEB', 'HEA', 'HEM']:
            altura_perfil = results.get('altura_perfil_mm', 200)
            ancho_alas = results.get('ancho_alas_mm', 100)
            espesor_alma = results.get('espesor_alma_mm', 5.6)
            espesor_alas = results.get('espesor_alas_mm', 8.5)
            return self.create_i_section(longitud_mm, altura_perfil, ancho_alas, espesor_alma, espesor_alas)
            
        elif tipo_perfil == 'UPN':
            altura_perfil = results.get('altura_perfil_mm', 200)
            ancho_alas = results.get('ancho_alas_mm', 80)
            espesor_alma = results.get('espesor_alma_mm', 5.6)
            espesor_alas = results.get('espesor_alas_mm', 8.5)
            return self.create_u_section(longitud_mm, altura_perfil, ancho_alas, espesor_alma, espesor_alas)
            
        elif tipo_perfil == 'Tubular cuadrado':
            dimension_exterior = results.get('dimension_exterior_mm', 150)
            espesor = results.get('espesor_mm', 8)
            return self.create_square_tube(longitud_mm, dimension_exterior, espesor)
            
        elif tipo_perfil == 'Tubular circular':
            dimension_exterior = results.get('dimension_exterior_mm', 168.3)
            espesor = results.get('espesor_mm', 10)
            return self.create_circular_tube(longitud_mm, dimension_exterior, espesor)
            
        elif tipo_perfil == 'L':
            altura_perfil = results.get('altura_perfil_mm', 200)
            ancho_alas = results.get('ancho_alas_mm', 100)
            espesor = results.get('espesor_alma_mm', 10)
            return self.create_l_section(longitud_mm, altura_perfil, ancho_alas, espesor)
            
        elif tipo_perfil == 'T':
            altura_perfil = results.get('altura_perfil_mm', 200)
            ancho_alas = results.get('ancho_alas_mm', 100)
            espesor_alma = results.get('espesor_alma_mm', 5.6)
            espesor_alas = results.get('espesor_alas_mm', 8.5)
            return self.create_t_section(longitud_mm, altura_perfil, ancho_alas, espesor_alma, espesor_alas)
            
        else:
            # Perfil genérico (rectangular)
            return pv.Box(bounds=(-50, 50, -100, 100, 0, longitud_mm))
    
    def create_i_section(self, length, height, width, web_thickness, flange_thickness):
        """Crear perfil tipo I/H."""
        # Alma
        web = pv.Box(bounds=(-web_thickness/2, web_thickness/2, 
                            -height/2, height/2, 
                            0, length))
        
        # Ala superior
        top_flange = pv.Box(bounds=(-width/2, width/2, 
                                    height/2 - flange_thickness, height/2, 
                                    0, length))
        
        # Ala inferior
        bottom_flange = pv.Box(bounds=(-width/2, width/2, 
                                      -height/2, -height/2 + flange_thickness, 
                                      0, length))
        
        # Unir partes
        profile = web.merge([top_flange, bottom_flange])
        return profile
    
    def create_u_section(self, length, height, width, web_thickness, flange_thickness):
        """Crear perfil tipo U."""
        # Alma
        web = pv.Box(bounds=(-web_thickness/2, web_thickness/2, 
                            -height/2, height/2, 
                            0, length))
        
        # Desplazar alma al extremo
        web.translate([-width/2 + web_thickness/2, 0, 0])
        
        # Ala superior
        top_flange = pv.Box(bounds=(-width/2, width/2, 
                                    height/2 - flange_thickness, height/2, 
                                    0, length))
        
        # Ala inferior
        bottom_flange = pv.Box(bounds=(-width/2, width/2, 
                                      -height/2, -height/2 + flange_thickness, 
                                      0, length))
        
        # Unir partes
        profile = web.merge([top_flange, bottom_flange])
        return profile
    
    def create_square_tube(self, length, size, thickness):
        """Crear perfil tubular cuadrado."""
        outer_size = size
        inner_size = size - 2 * thickness
        
        # Crear ocho puntos para el cubo exterior
        p0 = [-outer_size/2, -outer_size/2, 0]
        p1 = [ outer_size/2, -outer_size/2, 0]
        p2 = [ outer_size/2,  outer_size/2, 0]
        p3 = [-outer_size/2,  outer_size/2, 0]
        p4 = [-outer_size/2, -outer_size/2, length]
        p5 = [ outer_size/2, -outer_size/2, length]
        p6 = [ outer_size/2,  outer_size/2, length]
        p7 = [-outer_size/2,  outer_size/2, length]
        
        # Crear ocho puntos para el cubo interior
        p8  = [-inner_size/2, -inner_size/2, 0]
        p9  = [ inner_size/2, -inner_size/2, 0]
        p10 = [ inner_size/2,  inner_size/2, 0]
        p11 = [-inner_size/2,  inner_size/2, 0]
        p12 = [-inner_size/2, -inner_size/2, length]
        p13 = [ inner_size/2, -inner_size/2, length]
        p14 = [ inner_size/2,  inner_size/2, length]
        p15 = [-inner_size/2,  inner_size/2, length]
        
        # Definir los puntos
        points = np.array([
            p0, p1, p2, p3, p4, p5, p6, p7,
            p8, p9, p10, p11, p12, p13, p14, p15
        ])
        
        # Definir las caras
        faces_ext = [
            [4, 0, 1, 2, 3],    # Cara inferior
            [4, 4, 5, 6, 7],    # Cara superior
            [4, 0, 1, 5, 4],    # Caras laterales
            [4, 1, 2, 6, 5],
            [4, 2, 3, 7, 6],
            [4, 3, 0, 4, 7]
        ]
        
        faces_int = [
            [4, 8, 9, 10, 11],  # Cara inferior
            [4, 12, 13, 14, 15], # Cara superior
            [4, 8, 9, 13, 12],  # Caras laterales
            [4, 9, 10, 14, 13],
            [4, 10, 11, 15, 14],
            [4, 11, 8, 12, 15]
        ]
        
        faces_conn = [
            [4, 0, 1, 9, 8],    # Cara inferior
            [4, 1, 2, 10, 9],
            [4, 2, 3, 11, 10],
            [4, 3, 0, 8, 11],
            [4, 4, 5, 13, 12],  # Cara superior
            [4, 5, 6, 14, 13],
            [4, 6, 7, 15, 14],
            [4, 7, 4, 12, 15]
        ]
        
        # Aplanar las caras
        faces = []
        for face in faces_ext + faces_int + faces_conn:
            faces.extend(face)
        
        # Crear malla poligonal
        mesh = pv.PolyData(points, faces)
        return mesh
    
    def create_circular_tube(self, length, diameter, thickness):
        """Crear perfil tubular circular."""
        resolution = 30
        
        outer_radius = diameter / 2
        inner_radius = outer_radius - thickness
        
        # Crear anillos de puntos
        points = []
        
        # Anillo exterior base
        for i in range(resolution):
            angle = 2 * np.pi * i / resolution
            x = outer_radius * np.cos(angle)
            y = outer_radius * np.sin(angle)
            points.append([x, y, 0])
        
        # Anillo exterior tope
        for i in range(resolution):
            angle = 2 * np.pi * i / resolution
            x = outer_radius * np.cos(angle)
            y = outer_radius * np.sin(angle)
            points.append([x, y, length])
        
        # Anillo interior base
        for i in range(resolution):
            angle = 2 * np.pi * i / resolution
            x = inner_radius * np.cos(angle)
            y = inner_radius * np.sin(angle)
            points.append([x, y, 0])
        
        # Anillo interior tope
        for i in range(resolution):
            angle = 2 * np.pi * i / resolution
            x = inner_radius * np.cos(angle)
            y = inner_radius * np.sin(angle)
            points.append([x, y, length])
        
        # Convertir a numpy array
        points = np.array(points)
        
        # Crear caras
        faces = []
        
        # Caras del cilindro exterior
        for i in range(resolution):
            v1 = i
            v2 = (i + 1) % resolution
            v3 = v2 + resolution
            v4 = v1 + resolution
            faces.extend([4, v1, v2, v3, v4])
        
        # Caras del cilindro interior
        for i in range(resolution):
            v1 = i + 2*resolution
            v2 = ((i + 1) % resolution) + 2*resolution
            v3 = v2 + resolution
            v4 = v1 + resolution
            faces.extend([4, v1, v2, v3, v4])
        
        # Caras de los anillos superior e inferior
        for i in range(resolution):
            # Anillo inferior
            v1 = i
            v2 = (i + 1) % resolution
            v3 = ((i + 1) % resolution) + 2*resolution
            v4 = i + 2*resolution
            faces.extend([4, v1, v2, v3, v4])
            
            # Anillo superior
            v1 = i + resolution
            v2 = (i + 1) % resolution + resolution
            v3 = ((i + 1) % resolution) + 3*resolution
            v4 = i + 3*resolution
            faces.extend([4, v1, v2, v3, v4])
        
        # Crear malla poligonal
        mesh = pv.PolyData(points, faces)
        return mesh
    
    def create_l_section(self, length, height, width, thickness):
        """Crear perfil tipo L."""
        # Alma vertical
        vertical = pv.Box(bounds=(-thickness, 0, 
                                 -height, 0, 
                                 0, length))
        
        # Ala horizontal
        horizontal = pv.Box(bounds=(-thickness, width, 
                                   -thickness, 0, 
                                   0, length))
        
        # Unir partes
        profile = vertical.merge(horizontal)
        return profile
    
    def create_t_section(self, length, height, width, web_thickness, flange_thickness):
        """Crear perfil tipo T."""
        # Alma
        web = pv.Box(bounds=(-web_thickness/2, web_thickness/2, 
                            -height, 0, 
                            0, length))
        
        # Ala
        flange = pv.Box(bounds=(-width/2, width/2, 
                              0, flange_thickness, 
                              0, length))
        
        # Unir partes
        profile = web.merge(flange)
        return profile
    
    def apply_deformation(self, mesh, length, max_displacement, scale_factor):
        """Aplicar deformación de pandeo a la malla."""
        # Crear copia de la malla
        deformed_mesh = mesh.copy()
        
        # Obtener puntos de la malla
        points = deformed_mesh.points
        
        # Aumentar desplazamiento para visualización
        max_displacement = max_displacement * 5
        
        # Excentricidad inicial en la parte superior
        excentricidad_inicial = max_displacement * 0.2
        
        # Aplicar deformación a cada punto
        for i in range(len(points)):
            # Coordenadas
            z = points[i, 2]
            x_orig = points[i, 0]
            
            # Calcular excentricidad inicial
            excentricidad = (z / length) * excentricidad_inicial
            
            # Forma sinusoidal de la deformación
            normalized_z = z / length
            deformation_factor = np.sin(np.pi * normalized_z)
            
            # Calcular desplazamiento total
            displacement_x = excentricidad + (max_displacement * deformation_factor * scale_factor)
            points[i, 0] = x_orig + displacement_x
            
            # Aplicar rotación
            rotation_factor = np.cos(np.pi * normalized_z)
            rotation_angle = np.radians(15) * rotation_factor * scale_factor
            
            y_orig = points[i, 1]
            points[i, 1] = y_orig * np.cos(rotation_angle)
            points[i, 2] = z + y_orig * np.sin(rotation_angle)
        
        # Actualizar puntos de la malla
        deformed_mesh.points = points
        return deformed_mesh
    
    def calculate_stresses(self, mesh, results):
        """Calcular tensiones aproximadas en la malla."""
        # Obtener puntos de la malla
        points = mesh.points
        
        # Longitud del elemento
        length = results['longitud_mm']
        
        # Tensiones (aproximación simple)
        stresses = np.zeros(len(points))
        
        # Altura del perfil
        if 'altura_perfil_mm' in results:
            height = results['altura_perfil_mm']
        elif 'dimension_exterior_mm' in results:
            height = results['dimension_exterior_mm']
        else:
            height = 200  # Valor por defecto
        
        # Calcular momento de flexión en cada punto
        for i in range(len(points)):
            # Coordenadas
            z = points[i, 2]
            y = points[i, 1]
            
            # Forma sinusoidal del momento de flexión
            normalized_z = z / length
            moment_factor = np.sin(np.pi * normalized_z)
            
            # Calcular tensión aproximada
            stress = abs(y / (height/2)) * moment_factor * results['limite_elastico_MPa']
            stresses[i] = stress
        
        return stresses
    
    def set_camera_view(self, view_type):
        """Establecer vista de cámara predefinida."""
        if not PYVISTA_AVAILABLE or not self.visualization_active:
            return
        
        if view_type == "front":
            self.plotter.view_yz()
        elif view_type == "side":
            self.plotter.view_xz()
        elif view_type == "top":
            self.plotter.view_xy()
        elif view_type == "isometric":
            self.plotter.view_isometric()
    
    def reset_camera(self):
        """Resetear cámara a la vista predeterminada."""
        if not PYVISTA_AVAILABLE or not self.visualization_active:
            return
        
        self.plotter.reset_camera()
    
    def toggle_axes(self, state):
        """Mostrar u ocultar ejes."""
        if not PYVISTA_AVAILABLE or not self.visualization_active:
            return
        
        if state:
            self.plotter.add_axes()
        else:
            self.plotter.remove_bounds_axes()
    
    def toggle_grid(self, state):
        """Mostrar u ocultar cuadrícula."""
        if not PYVISTA_AVAILABLE or not self.visualization_active:
            return
        
        if state:
            self.plotter.show_grid()
        else:
            self.plotter.remove_bounds_grid()
    
    def export_view(self):
        """Exportar vista actual como imagen."""
        if not PYVISTA_AVAILABLE or not self.visualization_active:
            return
        
        from PyQt5.QtWidgets import QFileDialog
        
        # Abrir diálogo para guardar archivo
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Guardar Vista", 
            "", 
            "Archivos PNG (*.png);;Archivos JPEG (*.jpg);;Archivos BMP (*.bmp)"
        )
        
        if file_path:
            try:
                # Exportar vista
                self.plotter.screenshot(file_path)
                QMessageBox.information(self, "Exportar Vista", f"Vista guardada correctamente en {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al guardar la vista: {str(e)}")
    
    def install_pyvista(self):
        """Instalar PyVista y PyVistaQt."""
        from PyQt5.QtWidgets import QMessageBox
        import subprocess
        
        reply = QMessageBox.question(
            self,
            "Instalar PyVista",
            "Se instalará PyVista y PyVistaQt. Este proceso puede tardar unos minutos. ¿Desea continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Ejecutar pip install
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyvista", "pyvistaqt"])
                
                QMessageBox.information(
                    self,
                    "Instalación Completada",
                    "PyVista y PyVistaQt se han instalado correctamente. Por favor, reinicie la aplicación para activar la visualización 3D."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error de Instalación",
                    f"No se ha podido instalar PyVista: {str(e)}\n\n"
                    "Intente instalar manualmente con el comando:\n"
                    "pip install pyvista pyvistaqt"
                ) 