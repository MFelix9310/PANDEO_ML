import json
import os

class ConfigManager:
    """Clase para gestionar la configuración de la aplicación."""
    
    def __init__(self):
        """Inicializar el gestor de configuración."""
        # Asegurar que el directorio de configuración existe
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def save_config(self, file_path, config):
        """
        Guardar configuración en un archivo JSON.
        
        Args:
            file_path (str): Ruta del archivo donde guardar la configuración.
            config (dict): Diccionario de configuración.
        """
        # Crear el directorio si no existe
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Guardar configuración
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    
    def load_config(self, file_path):
        """
        Cargar configuración desde un archivo JSON.
        
        Args:
            file_path (str): Ruta del archivo de configuración.
            
        Returns:
            dict: Diccionario de configuración.
        """
        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo de configuración no existe: {file_path}")
        
        # Cargar configuración
        with open(file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return config
    
    def get_default_config_path(self):
        """
        Obtener la ruta del archivo de configuración predeterminado.
        
        Returns:
            str: Ruta del archivo de configuración predeterminado.
        """
        return os.path.join(self.config_dir, "default.json")
    
    def save_default_config(self, config):
        """
        Guardar configuración predeterminada.
        
        Args:
            config (dict): Diccionario de configuración.
        """
        self.save_config(self.get_default_config_path(), config)
    
    def load_default_config(self):
        """
        Cargar configuración predeterminada.
        
        Returns:
            dict: Diccionario de configuración predeterminada.
        """
        try:
            return self.load_config(self.get_default_config_path())
        except FileNotFoundError:
            # Devolver configuración por defecto vacía
            return {} 