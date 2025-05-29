import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt, QTranslator, QLocale
from PyQt5.QtGui import QIcon, QFont, QFontDatabase

# Importar componentes
from app.components.input_panel import InputPanel
from app.components.results_panel import ResultsPanel
from app.components.visualization_panel import VisualizationPanel
from app.components.simulation_panel import SimulationPanel
from app.utils.config_manager import ConfigManager
from app.utils.unit_converter import UnitConverter
from app.utils.result_exporter import ResultExporter
from app.models.prediction_model import PredictionModel

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación para predicción de pandeo en acero."""
    
    def __init__(self):
        super().__init__()
        
        # Configurar la ventana principal
        self.setWindowTitle("PANDEO ML - Predicción Avanzada de Pandeo en Elementos de Acero")
        self.setMinimumSize(1200, 800)
        self.setWindowIcon(QIcon("app/assets/icon.png"))
        
        # Cargar modelo de predicción
        self.prediction_model = PredictionModel()
        
        # Configurar utilidades
        self.config_manager = ConfigManager()
        self.unit_converter = UnitConverter()
        self.result_exporter = ResultExporter()
        
        # Configurar UI
        self.setup_ui()
        
        # Conectar señales
        self.connect_signals()
        
        # Cargar configuración guardada (si existe)
        self.load_saved_config()
        
    def setup_ui(self):
        """Configurar la interfaz de usuario principal."""
        # Crear widget central con pestañas
        self.main_tabs = QTabWidget()
        self.setCentralWidget(self.main_tabs)
        
        # Crear paneles
        self.input_panel = InputPanel(self.prediction_model)
        self.results_panel = ResultsPanel(self.unit_converter)
        self.visualization_panel = VisualizationPanel()
        self.simulation_panel = SimulationPanel()
        
        # Añadir pestañas
        self.main_tabs.addTab(self.input_panel, "Entrada de Datos")
        self.main_tabs.addTab(self.results_panel, "Resultados")
        self.main_tabs.addTab(self.visualization_panel, "Visualización")
        self.main_tabs.addTab(self.simulation_panel, "Simulación")
        
        # Configurar barra de estado
        self.statusBar().showMessage("Listo para predicciones de pandeo")
        
        # Crear menús
        self.create_menus()
    
    def create_menus(self):
        """Crear menús de la aplicación."""
        # Menú Archivo
        file_menu = self.menuBar().addMenu("Archivo")
        
        # Acción para guardar configuración
        save_config_action = file_menu.addAction("Guardar Configuración")
        save_config_action.triggered.connect(self.save_config)
        
        # Acción para cargar configuración
        load_config_action = file_menu.addAction("Cargar Configuración")
        load_config_action.triggered.connect(self.load_config)
        
        # Separador
        file_menu.addSeparator()
        
        # Acción para exportar resultados
        export_action = file_menu.addAction("Exportar Resultados")
        export_action.triggered.connect(self.export_results)
        
        # Separador
        file_menu.addSeparator()
        
        # Acción para salir
        exit_action = file_menu.addAction("Salir")
        exit_action.triggered.connect(self.close)
        
        # Menú Ayuda
        help_menu = self.menuBar().addMenu("Ayuda")
        
        # Acción para mostrar información sobre la aplicación
        about_action = help_menu.addAction("Acerca de")
        about_action.triggered.connect(self.show_about)
        
        # Acción para mostrar ayuda
        help_action = help_menu.addAction("Ayuda")
        help_action.triggered.connect(self.show_help)
    
    def connect_signals(self):
        """Conectar señales entre componentes."""
        # Conectar señal de predicción realizada
        self.input_panel.prediction_ready.connect(self.handle_prediction_results)
        
    def handle_prediction_results(self, results):
        """Manejar los resultados de la predicción."""
        try:
            if results is None:
                return
                
            # Actualizar paneles con los resultados
            self.results_panel.update_results(results)
            
            try:
                self.visualization_panel.update_visualization(results)
            except Exception as e:
                import traceback
                print(f"Error en la visualización: {str(e)}")
                print(traceback.format_exc())
                # No propagamos la excepción para que la aplicación siga funcionando
            
            try:
                self.simulation_panel.update_simulation(results)
            except Exception as e:
                import traceback
                print(f"Error en la simulación: {str(e)}")
                print(traceback.format_exc())
                # No propagamos la excepción para que la aplicación siga funcionando
            
            # Mostrar pestaña de resultados
            self.main_tabs.setCurrentIndex(1)
        except Exception as e:
            import traceback
            print(f"Error al procesar resultados: {str(e)}")
            print(traceback.format_exc())
            # Mostrar mensaje de error
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Error al procesar los resultados: {str(e)}")
    
    def save_config(self):
        """Guardar configuración actual."""
        try:
            # Obtener configuración actual
            config = self.input_panel.get_current_config()
            
            # Abrir diálogo para guardar archivo
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Guardar Configuración", 
                "", 
                "Archivos de Configuración (*.json)"
            )
            
            if file_path:
                # Guardar configuración
                self.config_manager.save_config(file_path, config)
                self.statusBar().showMessage(f"Configuración guardada en {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar la configuración: {str(e)}")
    
    def load_config(self):
        """Cargar configuración desde archivo."""
        try:
            # Abrir diálogo para seleccionar archivo
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Cargar Configuración", 
                "", 
                "Archivos de Configuración (*.json)"
            )
            
            if file_path:
                # Cargar configuración
                config = self.config_manager.load_config(file_path)
                
                # Aplicar configuración
                self.input_panel.apply_config(config)
                self.statusBar().showMessage(f"Configuración cargada desde {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar la configuración: {str(e)}")
    
    def load_saved_config(self):
        """Cargar última configuración guardada (si existe)."""
        default_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "default.json")
        if os.path.exists(default_config_path):
            try:
                config = self.config_manager.load_config(default_config_path)
                self.input_panel.apply_config(config)
                self.statusBar().showMessage("Configuración predeterminada cargada")
            except Exception:
                # Ignorar errores al cargar la configuración predeterminada
                pass
    
    def export_results(self):
        """Exportar resultados actuales."""
        if not hasattr(self.results_panel, "current_results") or self.results_panel.current_results is None:
            QMessageBox.warning(self, "Advertencia", "No hay resultados para exportar")
            return
        
        try:
            # Abrir diálogo para guardar archivo
            file_path, file_type = QFileDialog.getSaveFileName(
                self, 
                "Exportar Resultados", 
                "", 
                "Archivos PDF (*.pdf);;Imágenes PNG (*.png)"
            )
            
            if file_path:
                # Exportar resultados
                results = self.results_panel.current_results
                input_data = self.input_panel.get_current_config()
                
                if file_path.endswith(".pdf"):
                    self.result_exporter.export_to_pdf(file_path, results, input_data)
                elif file_path.endswith(".png"):
                    self.result_exporter.export_to_image(file_path, results, input_data)
                
                self.statusBar().showMessage(f"Resultados exportados a {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar los resultados: {str(e)}")
    
    def show_about(self):
        """Mostrar información sobre la aplicación."""
        QMessageBox.about(
            self,
            "Acerca de PANDEO ML",
            """<h1>PANDEO ML</h1>
            <p>Versión 1.0</p>
            <p>Aplicación para predicción avanzada de pandeo en elementos de acero.</p>
            <p>Desarrollado con modelos de aprendizaje automático entrenados con datos generados a partir de principios físicos y ecuaciones fundamentales de la teoría de pandeo.</p>
            <p>&copy; 2025 Todos los derechos reservados.</p>"""
        )
    
    def show_help(self):
        """Mostrar ayuda de la aplicación."""
        QMessageBox.information(
            self,
            "Ayuda de PANDEO ML",
            """<h1>Ayuda de PANDEO ML</h1>
            <h2>Pasos para realizar una predicción:</h2>
            <ol>
                <li>Seleccione el tipo de perfil y tipo de acero.</li>
                <li>Ingrese las dimensiones geométricas del elemento.</li>
                <li>Seleccione las condiciones de apoyo.</li>
                <li>Haga clic en "Calcular" para obtener la predicción.</li>
                <li>Explore los resultados en las pestañas "Resultados", "Visualización" y "Simulación".</li>
            </ol>
            <p>Para guardar o cargar configuraciones, utilice el menú "Archivo".</p>
            <p>Para exportar resultados, use la opción "Exportar Resultados" en el menú "Archivo".</p>"""
        )

def main():
    """Función principal para iniciar la aplicación."""
    app = QApplication(sys.argv)
    
    # Configurar estilo de la aplicación
    app.setStyle("Fusion")
    
    # Configurar fuente predeterminada
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Cargar hojas de estilo
    with open("app/static/style.qss", "r") as f:
        app.setStyleSheet(f.read())
    
    # Crear y mostrar ventana principal
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 