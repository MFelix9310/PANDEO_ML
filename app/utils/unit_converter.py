class UnitConverter:
    """Clase para conversión entre diferentes unidades de fuerza y longitud."""
    
    # Factores de conversión para fuerzas
    FORCE_CONVERSION = {
        'kN_to_kg': 101.9716,
        'kN_to_ton': 0.1019716,
        'kg_to_kN': 0.00980665,
        'kg_to_ton': 0.001,
        'ton_to_kN': 9.80665,
        'ton_to_kg': 1000
    }
    
    # Factores de conversión para longitudes
    LENGTH_CONVERSION = {
        'mm_to_cm': 0.1,
        'mm_to_m': 0.001,
        'cm_to_mm': 10,
        'cm_to_m': 0.01,
        'm_to_mm': 1000,
        'm_to_cm': 100
    }
    
    # Factores de conversión para presiones
    PRESSURE_CONVERSION = {
        'MPa_to_kPa': 1000,
        'MPa_to_psi': 145.038,
        'kPa_to_MPa': 0.001,
        'kPa_to_psi': 0.145038,
        'psi_to_MPa': 0.00689476,
        'psi_to_kPa': 6.89476
    }
    
    def __init__(self):
        """Inicializar el convertidor de unidades."""
        pass
    
    def convert_force(self, value, from_unit, to_unit):
        """
        Convertir un valor de fuerza entre diferentes unidades.
        
        Args:
            value (float): Valor a convertir.
            from_unit (str): Unidad de origen ('kN', 'kg', 'ton').
            to_unit (str): Unidad de destino ('kN', 'kg', 'ton').
            
        Returns:
            float: Valor convertido.
        """
        if from_unit == to_unit:
            return value
        
        conversion_key = f"{from_unit}_to_{to_unit}"
        if conversion_key in self.FORCE_CONVERSION:
            return value * self.FORCE_CONVERSION[conversion_key]
        
        # Si no hay conversión directa, convertir a través de kN
        if from_unit != 'kN' and to_unit != 'kN':
            # Primero convertir a kN
            to_kn = value * self.FORCE_CONVERSION[f"{from_unit}_to_kN"]
            # Luego convertir de kN a la unidad destino
            return to_kn * self.FORCE_CONVERSION[f"kN_to_{to_unit}"]
        
        raise ValueError(f"No se puede convertir de {from_unit} a {to_unit}")
    
    def convert_length(self, value, from_unit, to_unit):
        """
        Convertir un valor de longitud entre diferentes unidades.
        
        Args:
            value (float): Valor a convertir.
            from_unit (str): Unidad de origen ('mm', 'cm', 'm').
            to_unit (str): Unidad de destino ('mm', 'cm', 'm').
            
        Returns:
            float: Valor convertido.
        """
        if from_unit == to_unit:
            return value
        
        conversion_key = f"{from_unit}_to_{to_unit}"
        if conversion_key in self.LENGTH_CONVERSION:
            return value * self.LENGTH_CONVERSION[conversion_key]
        
        # Si no hay conversión directa, convertir a través de mm
        if from_unit != 'mm' and to_unit != 'mm':
            # Primero convertir a mm
            to_mm = value * self.LENGTH_CONVERSION[f"{from_unit}_to_mm"]
            # Luego convertir de mm a la unidad destino
            return to_mm * self.LENGTH_CONVERSION[f"mm_to_{to_unit}"]
        
        raise ValueError(f"No se puede convertir de {from_unit} a {to_unit}")
    
    def convert_pressure(self, value, from_unit, to_unit):
        """
        Convertir un valor de presión entre diferentes unidades.
        
        Args:
            value (float): Valor a convertir.
            from_unit (str): Unidad de origen ('MPa', 'kPa', 'psi').
            to_unit (str): Unidad de destino ('MPa', 'kPa', 'psi').
            
        Returns:
            float: Valor convertido.
        """
        if from_unit == to_unit:
            return value
        
        conversion_key = f"{from_unit}_to_{to_unit}"
        if conversion_key in self.PRESSURE_CONVERSION:
            return value * self.PRESSURE_CONVERSION[conversion_key]
        
        # Si no hay conversión directa, convertir a través de MPa
        if from_unit != 'MPa' and to_unit != 'MPa':
            # Primero convertir a MPa
            to_mpa = value * self.PRESSURE_CONVERSION[f"{from_unit}_to_MPa"]
            # Luego convertir de MPa a la unidad destino
            return to_mpa * self.PRESSURE_CONVERSION[f"MPa_to_{to_unit}"]
        
        raise ValueError(f"No se puede convertir de {from_unit} a {to_unit}")
    
    def format_force(self, value, unit='kN', decimals=2):
        """
        Formatear un valor de fuerza con su unidad.
        
        Args:
            value (float): Valor a formatear.
            unit (str): Unidad ('kN', 'kg', 'ton').
            decimals (int): Número de decimales.
            
        Returns:
            str: Valor formateado con unidad.
        """
        return f"{value:.{decimals}f} {unit}"
    
    def format_length(self, value, unit='mm', decimals=2):
        """
        Formatear un valor de longitud con su unidad.
        
        Args:
            value (float): Valor a formatear.
            unit (str): Unidad ('mm', 'cm', 'm').
            decimals (int): Número de decimales.
            
        Returns:
            str: Valor formateado con unidad.
        """
        return f"{value:.{decimals}f} {unit}"
    
    def format_pressure(self, value, unit='MPa', decimals=2):
        """
        Formatear un valor de presión con su unidad.
        
        Args:
            value (float): Valor a formatear.
            unit (str): Unidad ('MPa', 'kPa', 'psi').
            decimals (int): Número de decimales.
            
        Returns:
            str: Valor formateado con unidad.
        """
        return f"{value:.{decimals}f} {unit}" 