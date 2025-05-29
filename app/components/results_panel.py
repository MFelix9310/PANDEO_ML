from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QGroupBox, QSplitter, QTabWidget, 
                            QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class ResultsPanel(QWidget):
    """Panel para mostrar los resultados de la predicción de pandeo."""
    
    def __init__(self, unit_converter):
        super().__init__()
        
        # Guardar referencia al convertidor de unidades
        self.unit_converter = unit_converter
        
        # Resultados actuales
        self.current_results = None
        
        # Inicializar UI
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar la interfaz de usuario del panel de resultados."""
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        title_label = QLabel("Resultados de Predicción de Pandeo")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Mensaje inicial
        self.empty_label = QLabel("Realice un cálculo para ver los resultados")
        self.empty_label.setAlignment(Qt.AlignCenter)
        empty_font = QFont()
        empty_font.setItalic(True)
        self.empty_label.setFont(empty_font)
        main_layout.addWidget(self.empty_label)
        
        # Splitter para dividir la pantalla en resultados y gráficos
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo: Resultados numéricos
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Grupo para mostrar los resultados principales
        self.main_results_group = QGroupBox("Carga Máxima")
        main_results_layout = QGridLayout()
        
        # Etiquetas para resultados principales
        self.carga_kn_label = QLabel("0.00 kN")
        self.carga_kg_label = QLabel("0.00 kg")
        self.carga_ton_label = QLabel("0.00 ton")
        
        # Configurar fuente grande para los resultados principales
        result_font = QFont()
        result_font.setPointSize(16)
        result_font.setBold(True)
        self.carga_kn_label.setFont(result_font)
        self.carga_kg_label.setFont(result_font)
        self.carga_ton_label.setFont(result_font)
        
        # Agregar etiquetas al layout
        main_results_layout.addWidget(QLabel("Kilonewtons (kN):"), 0, 0)
        main_results_layout.addWidget(self.carga_kn_label, 0, 1)
        main_results_layout.addWidget(QLabel("Kilogramos (kg):"), 1, 0)
        main_results_layout.addWidget(self.carga_kg_label, 1, 1)
        main_results_layout.addWidget(QLabel("Toneladas (ton):"), 2, 0)
        main_results_layout.addWidget(self.carga_ton_label, 2, 1)
        
        self.main_results_group.setLayout(main_results_layout)
        left_layout.addWidget(self.main_results_group)
        
        # Tabla de resultados detallados
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Parámetro", "Valor"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        
        left_layout.addWidget(self.results_table)
        
        # Panel derecho: Gráficos
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Pestañas para diferentes gráficos
        self.graph_tabs = QTabWidget()
        
        # Gráfico 1: Relación carga-esbeltez
        self.chart1_widget = QWidget()
        chart1_layout = QVBoxLayout(self.chart1_widget)
        self.figure1 = Figure(figsize=(5, 4), dpi=100)
        self.canvas1 = FigureCanvas(self.figure1)
        chart1_layout.addWidget(self.canvas1)
        self.graph_tabs.addTab(self.chart1_widget, "Relación Carga-Esbeltez")
        
        # Gráfico 2: Comparación con carga crítica de Euler
        self.chart2_widget = QWidget()
        chart2_layout = QVBoxLayout(self.chart2_widget)
        self.figure2 = Figure(figsize=(5, 4), dpi=100)
        self.canvas2 = FigureCanvas(self.figure2)
        chart2_layout.addWidget(self.canvas2)
        self.graph_tabs.addTab(self.chart2_widget, "Comparación con Euler")
        
        # Gráfico 3: Factor de reducción
        self.chart3_widget = QWidget()
        chart3_layout = QVBoxLayout(self.chart3_widget)
        self.figure3 = Figure(figsize=(5, 4), dpi=100)
        self.canvas3 = FigureCanvas(self.figure3)
        chart3_layout.addWidget(self.canvas3)
        self.graph_tabs.addTab(self.chart3_widget, "Factor de Reducción")
        
        right_layout.addWidget(self.graph_tabs)
        
        # Agregar paneles al splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
        
        # Ocultar inicialmente los resultados
        self.main_results_group.setVisible(False)
        self.results_table.setVisible(False)
        self.graph_tabs.setVisible(False)
        
        self.setLayout(main_layout)
    
    def update_results(self, results):
        """
        Actualizar los resultados mostrados.
        
        Args:
            results (dict): Diccionario con los resultados de la predicción.
        """
        # Guardar resultados actuales
        self.current_results = results
        
        # Ocultar mensaje inicial
        self.empty_label.setVisible(False)
        
        # Mostrar controles de resultados
        self.main_results_group.setVisible(True)
        self.results_table.setVisible(True)
        self.graph_tabs.setVisible(True)
        
        # Actualizar etiquetas de resultados principales
        self.carga_kn_label.setText(f"{results['carga_maxima_kN']:.2f} kN")
        self.carga_kg_label.setText(f"{results['carga_maxima_kg']:.2f} kg")
        self.carga_ton_label.setText(f"{results['carga_maxima_ton']:.2f} ton")
        
        # Actualizar tabla de resultados
        self.update_results_table(results)
        
        # Actualizar gráficos
        self.update_graphs(results)
    
    def update_results_table(self, results):
        """
        Actualizar la tabla de resultados detallados.
        
        Args:
            results (dict): Diccionario con los resultados de la predicción.
        """
        # Definir los parámetros a mostrar en la tabla
        table_data = [
            # Datos generales
            ("Tipo de Perfil", results["tipo_perfil"]),
            ("Tipo de Acero", results["tipo_acero"]),
            ("Longitud", f"{results['longitud_mm']:.2f} mm"),
            ("Condición de Apoyo", results["condicion_apoyo"]),
            
            # Datos del pandeo
            ("Longitud de Pandeo", f"{results['longitud_pandeo_mm']:.2f} mm"),
            ("Esbeltez Mecánica", f"{results['esbeltez_mecanica']:.2f}"),
            ("Esbeltez Relativa", f"{results['esbeltez_relativa']:.2f}"),
            ("Curva de Pandeo", results["curva_pandeo"]),
            ("Coeficiente de Imperfección", f"{results['coef_imperfeccion']:.3f}"),
            
            # Propiedades geométricas
            ("Área", f"{results['area_mm2']:.2f} mm²"),
            ("Inercia", f"{results['inercia_mm4']:.2f} mm⁴"),
            ("Radio de Giro", f"{results['radio_giro_mm']:.2f} mm"),
            
            # Resultados adicionales
            ("Carga Crítica de Euler", f"{results['carga_critica_euler_kN']:.2f} kN"),
            ("Factor de Reducción", f"{results['factor_reduccion']:.3f}"),
            ("Resistencia Plástica", f"{results['resistencia_plastica_kN']:.2f} kN"),
            ("Desplazamiento Lateral", f"{results['desplazamiento_lateral_mm']:.2f} mm")
        ]
        
        # Actualizar tabla
        self.results_table.setRowCount(len(table_data))
        
        for i, (param, value) in enumerate(table_data):
            # Crear items
            param_item = QTableWidgetItem(param)
            value_item = QTableWidgetItem(str(value))
            
            # Configurar alineación
            param_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Establecer fondo para filas alternas
            if i % 2 == 0:
                param_item.setBackground(QBrush(QColor(240, 240, 240)))
                value_item.setBackground(QBrush(QColor(240, 240, 240)))
            
            # Hacer items no editables
            param_item.setFlags(param_item.flags() & ~Qt.ItemIsEditable)
            value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)
            
            # Agregar a la tabla
            self.results_table.setItem(i, 0, param_item)
            self.results_table.setItem(i, 1, value_item)
    
    def update_graphs(self, results):
        """
        Actualizar los gráficos con los resultados.
        
        Args:
            results (dict): Diccionario con los resultados de la predicción.
        """
        # Gráfico 1: Relación carga-esbeltez
        self.figure1.clear()
        ax1 = self.figure1.add_subplot(111)
        
        # Generar datos para la curva de pandeo
        esbeltez_rel_range = np.linspace(0, 2.5, 100)
        factor_red_range = []
        coef_imp = results['coef_imperfeccion']
        
        for esbeltez_rel in esbeltez_rel_range:
            if esbeltez_rel <= 0.2:
                factor_red_range.append(1.0)
            else:
                phi = 0.5 * (1 + coef_imp * (esbeltez_rel - 0.2) + esbeltez_rel**2)
                factor_red = 1 / (phi + np.sqrt(phi**2 - esbeltez_rel**2))
                factor_red_range.append(factor_red)
        
        carga_plastica = results['resistencia_plastica_kN']
        curva_pandeo = [f * carga_plastica for f in factor_red_range]
        
        # Graficar curva de pandeo
        ax1.plot(esbeltez_rel_range, curva_pandeo, 'b-', linewidth=2, label='Curva de pandeo')
        
        # Marcar punto de predicción
        ax1.plot([results['esbeltez_relativa']], [results['carga_maxima_kN']], 'ro', markersize=8, label='Predicción')
        
        # Personalizar gráfico
        ax1.set_xlabel('Esbeltez Relativa')
        ax1.set_ylabel('Carga (kN)')
        ax1.set_title('Relación Carga-Esbeltez')
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.legend()
        
        # Gráfico 2: Comparación con carga crítica de Euler
        self.figure2.clear()
        ax2 = self.figure2.add_subplot(111)
        
        # Datos para el gráfico de barras
        categorias = ['Carga Máxima', 'Carga de Euler', 'Resistencia Plástica']
        valores = [
            results['carga_maxima_kN'],
            results['carga_critica_euler_kN'],
            results['resistencia_plastica_kN']
        ]
        
        # Crear gráfico de barras
        bars = ax2.bar(categorias, valores, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        
        # Añadir etiquetas con valores
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 5,
                    f'{height:.2f} kN', ha='center', va='bottom')
        
        # Personalizar gráfico
        ax2.set_ylabel('Carga (kN)')
        ax2.set_title('Comparación de Cargas')
        ax2.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Gráfico 3: Factor de reducción
        self.figure3.clear()
        ax3 = self.figure3.add_subplot(111)
        
        # Graficar factor de reducción vs esbeltez relativa
        ax3.plot(esbeltez_rel_range, factor_red_range, 'g-', linewidth=2)
        
        # Marcar punto de predicción
        ax3.plot([results['esbeltez_relativa']], [results['factor_reduccion']], 'ro', markersize=8)
        
        # Personalizar gráfico
        ax3.set_xlabel('Esbeltez Relativa')
        ax3.set_ylabel('Factor de Reducción')
        ax3.set_title('Factor de Reducción por Pandeo')
        ax3.grid(True, linestyle='--', alpha=0.7)
        
        # Actualizar gráficos
        self.canvas1.draw()
        self.canvas2.draw()
        self.canvas3.draw()
        
    def reset(self):
        """Reiniciar el panel de resultados."""
        # Mostrar mensaje inicial
        self.empty_label.setVisible(True)
        
        # Ocultar controles de resultados
        self.main_results_group.setVisible(False)
        self.results_table.setVisible(False)
        self.graph_tabs.setVisible(False)
        
        # Limpiar resultados actuales
        self.current_results = None 