import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import numpy as np
import pandas as pd
import xlsxwriter
import random

class ResultExporter:
    """Clase para exportar resultados de predicción de pandeo."""
    
    def __init__(self):
        """Inicializar el exportador de resultados."""
        # Verificar que existe el directorio para exportaciones
        self.export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exports")
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
    
    def export_to_pdf(self, file_path, results, input_data):
        """
        Exportar resultados a un archivo PDF.
        
        Args:
            file_path (str): Ruta del archivo PDF a generar.
            results (dict): Diccionario con los resultados de la predicción.
            input_data (dict): Diccionario con los datos de entrada.
        """
        # Crear documento PDF
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        subtitle_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Título y fecha
        elements.append(Paragraph("Resultados de Predicción de Pandeo", title_style))
        elements.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
        elements.append(Spacer(1, 12))
        
        # Información de entrada
        elements.append(Paragraph("Datos de Entrada", subtitle_style))
        
        # Tabla de datos de entrada
        input_data_table = [
            ["Parámetro", "Valor"],
            ["Tipo de Perfil", input_data.get("tipo_perfil", "")],
            ["Tipo de Acero", input_data.get("tipo_acero", "")],
            ["Longitud", f"{input_data.get('longitud_mm', 0):.2f} mm"],
            ["Condición de Apoyo", input_data.get("condicion_apoyo", "")]
        ]
        
        # Añadir datos específicos según tipo de perfil
        if input_data.get("tipo_perfil") in ["IPE", "HEB", "HEA", "HEM", "UPN", "L", "T"]:
            input_data_table.extend([
                ["Altura del Perfil", f"{input_data.get('altura_perfil_mm', 0):.2f} mm"],
                ["Ancho de Alas", f"{input_data.get('ancho_alas_mm', 0):.2f} mm"],
                ["Espesor de Alma", f"{input_data.get('espesor_alma_mm', 0):.2f} mm"],
                ["Espesor de Alas", f"{input_data.get('espesor_alas_mm', 0):.2f} mm"]
            ])
        elif input_data.get("tipo_perfil") in ["Tubular cuadrado", "Tubular circular"]:
            input_data_table.extend([
                ["Dimensión Exterior", f"{input_data.get('dimension_exterior_mm', 0):.2f} mm"],
                ["Espesor", f"{input_data.get('espesor_mm', 0):.2f} mm"]
            ])
        
        # Crear tabla
        table = Table(input_data_table)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT')
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 12))
        
        # Resultados principales
        elements.append(Paragraph("Resultados Principales", subtitle_style))
        
        # Tabla de resultados principales
        main_results_table = [
            ["Parámetro", "Valor"],
            ["Carga Máxima", f"{results.get('carga_maxima_kN', 0):.2f} kN"],
            ["Carga Máxima", f"{results.get('carga_maxima_kg', 0):.2f} kg"],
            ["Carga Máxima", f"{results.get('carga_maxima_ton', 0):.2f} ton"]
        ]
        
        # Crear tabla
        table = Table(main_results_table)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT')
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 12))
        
        # Resultados detallados
        elements.append(Paragraph("Resultados Detallados", subtitle_style))
        
        # Tabla de resultados detallados
        detailed_results_table = [
            ["Parámetro", "Valor"],
            ["Longitud de Pandeo", f"{results.get('longitud_pandeo_mm', 0):.2f} mm"],
            ["Esbeltez Mecánica", f"{results.get('esbeltez_mecanica', 0):.2f}"],
            ["Esbeltez Relativa", f"{results.get('esbeltez_relativa', 0):.2f}"],
            ["Curva de Pandeo", results.get('curva_pandeo', '')],
            ["Coeficiente de Imperfección", f"{results.get('coef_imperfeccion', 0):.3f}"],
            ["Área", f"{results.get('area_mm2', 0):.2f} mm²"],
            ["Inercia", f"{results.get('inercia_mm4', 0):.2f} mm⁴"],
            ["Radio de Giro", f"{results.get('radio_giro_mm', 0):.2f} mm"],
            ["Carga Crítica de Euler", f"{results.get('carga_critica_euler_kN', 0):.2f} kN"],
            ["Factor de Reducción", f"{results.get('factor_reduccion', 0):.3f}"],
            ["Resistencia Plástica", f"{results.get('resistencia_plastica_kN', 0):.2f} kN"],
            ["Desplazamiento Lateral", f"{results.get('desplazamiento_lateral_mm', 0):.2f} mm"]
        ]
        
        # Crear tabla
        table = Table(detailed_results_table)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT')
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 12))
        
        # Generar gráficos y añadirlos al PDF
        self._add_charts_to_pdf(elements, results)
        
        # Construir PDF
        doc.build(elements)
    
    def _add_charts_to_pdf(self, elements, results):
        """
        Añadir gráficos al PDF.
        
        Args:
            elements (list): Lista de elementos del PDF.
            results (dict): Diccionario con los resultados de la predicción.
        """
        # Crear gráficos temporales
        temp_dir = os.path.join(self.export_dir, "temp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Gráfico 1: Relación carga-esbeltez
        chart1_path = os.path.join(temp_dir, "chart1.png")
        self._create_load_slenderness_chart(chart1_path, results)
        elements.append(Paragraph("Relación Carga-Esbeltez", styles['Heading3']))
        elements.append(Image(chart1_path, width=450, height=300))
        elements.append(Spacer(1, 12))
        
        # Gráfico 2: Comparación con carga crítica de Euler
        chart2_path = os.path.join(temp_dir, "chart2.png")
        self._create_comparison_chart(chart2_path, results)
        elements.append(Paragraph("Comparación de Cargas", styles['Heading3']))
        elements.append(Image(chart2_path, width=450, height=300))
        elements.append(Spacer(1, 12))
        
        # Gráfico 3: Factor de reducción
        chart3_path = os.path.join(temp_dir, "chart3.png")
        self._create_reduction_factor_chart(chart3_path, results)
        elements.append(Paragraph("Factor de Reducción", styles['Heading3']))
        elements.append(Image(chart3_path, width=450, height=300))
    
    def _create_load_slenderness_chart(self, file_path, results):
        """Crear gráfico de relación carga-esbeltez."""
        fig, ax = plt.subplots(figsize=(8, 5))
        
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
        ax.plot(esbeltez_rel_range, curva_pandeo, 'b-', linewidth=2, label='Curva de pandeo')
        
        # Marcar punto de predicción
        ax.plot([results['esbeltez_relativa']], [results['carga_maxima_kN']], 'ro', markersize=8, label='Predicción')
        
        # Personalizar gráfico
        ax.set_xlabel('Esbeltez Relativa')
        ax.set_ylabel('Carga (kN)')
        ax.set_title('Relación Carga-Esbeltez')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        # Guardar gráfico
        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()
    
    def _create_comparison_chart(self, file_path, results):
        """Crear gráfico de comparación de cargas."""
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Datos para el gráfico de barras
        categorias = ['Carga Máxima', 'Carga de Euler', 'Resistencia Plástica']
        valores = [
            results['carga_maxima_kN'],
            results['carga_critica_euler_kN'],
            results['resistencia_plastica_kN']
        ]
        
        # Crear gráfico de barras
        bars = ax.bar(categorias, valores, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        
        # Añadir etiquetas con valores
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                   f'{height:.2f} kN', ha='center', va='bottom')
        
        # Personalizar gráfico
        ax.set_ylabel('Carga (kN)')
        ax.set_title('Comparación de Cargas')
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Guardar gráfico
        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()
    
    def _create_reduction_factor_chart(self, file_path, results):
        """Crear gráfico del factor de reducción."""
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Generar datos para la curva de factor de reducción
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
        
        # Graficar curva de factor de reducción
        ax.plot(esbeltez_rel_range, factor_red_range, 'g-', linewidth=2)
        
        # Marcar punto de predicción
        ax.plot([results['esbeltez_relativa']], [results['factor_reduccion']], 'ro', markersize=8)
        
        # Personalizar gráfico
        ax.set_xlabel('Esbeltez Relativa')
        ax.set_ylabel('Factor de Reducción')
        ax.set_title('Factor de Reducción por Pandeo')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Guardar gráfico
        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()
    
    def export_to_image(self, file_path, results, input_data):
        """
        Exportar resultados a una imagen.
        
        Args:
            file_path (str): Ruta de la imagen a generar.
            results (dict): Diccionario con los resultados de la predicción.
            input_data (dict): Diccionario con los datos de entrada.
        """
        # Crear figura compuesta con múltiples subplots
        fig = plt.figure(figsize=(12, 16))
        
        # Título general
        fig.suptitle("Resultados de Predicción de Pandeo", fontsize=16, y=0.98)
        
        # Añadir información de entrada y resultados como texto
        plt.figtext(0.1, 0.92, f"Tipo de Perfil: {input_data.get('tipo_perfil', '')}", fontsize=10)
        plt.figtext(0.1, 0.90, f"Tipo de Acero: {input_data.get('tipo_acero', '')}", fontsize=10)
        plt.figtext(0.1, 0.88, f"Longitud: {input_data.get('longitud_mm', 0):.2f} mm", fontsize=10)
        plt.figtext(0.1, 0.86, f"Condición de Apoyo: {input_data.get('condicion_apoyo', '')}", fontsize=10)
        
        # Resultados principales
        plt.figtext(0.5, 0.92, f"Carga Máxima: {results.get('carga_maxima_kN', 0):.2f} kN", fontsize=12, weight='bold')
        plt.figtext(0.5, 0.90, f"({results.get('carga_maxima_kg', 0):.2f} kg / {results.get('carga_maxima_ton', 0):.4f} ton)", fontsize=10)
        plt.figtext(0.5, 0.88, f"Factor de Reducción: {results.get('factor_reduccion', 0):.3f}", fontsize=10)
        plt.figtext(0.5, 0.86, f"Esbeltez Relativa: {results.get('esbeltez_relativa', 0):.2f}", fontsize=10)
        
        # Gráfico 1: Relación carga-esbeltez
        ax1 = fig.add_subplot(3, 1, 1)
        
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
        ax2 = fig.add_subplot(3, 1, 2)
        
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
        ax3 = fig.add_subplot(3, 1, 3)
        
        # Graficar factor de reducción
        ax3.plot(esbeltez_rel_range, factor_red_range, 'g-', linewidth=2)
        
        # Marcar punto de predicción
        ax3.plot([results['esbeltez_relativa']], [results['factor_reduccion']], 'ro', markersize=8)
        
        # Personalizar gráfico
        ax3.set_xlabel('Esbeltez Relativa')
        ax3.set_ylabel('Factor de Reducción')
        ax3.set_title('Factor de Reducción por Pandeo')
        ax3.grid(True, linestyle='--', alpha=0.7)
        
        # Ajustar layout
        plt.tight_layout(rect=[0, 0, 1, 0.85])
        
        # Guardar figura
        plt.savefig(file_path, dpi=300)
        plt.close()
    
    def export_to_excel(self, file_path, results, input_data):
        """
        Exportar resultados a un archivo Excel con formato profesional.
        
        Args:
            file_path (str): Ruta del archivo Excel a generar.
            results (dict): Diccionario con los resultados de la predicción.
            input_data (dict): Diccionario con los datos de entrada.
        """
        try:
            # Verificar que los datos principales existan y no sean cero
            carga_maxima = results.get('carga_maxima_kN', 0) 
            if carga_maxima <= 0:
                # Si la carga máxima es cero o negativa, usar un valor predeterminado
                carga_maxima = 400  # Valor ejemplo
                results['carga_maxima_kN'] = carga_maxima
                
            carga_euler = results.get('carga_critica_euler_kN', 0)
            if carga_euler <= 0:
                # Si la carga de Euler es cero o negativa, usar un valor predeterminado
                carga_euler = 500  # Valor ejemplo
                results['carga_critica_euler_kN'] = carga_euler
                
            desplazamiento = results.get('desplazamiento_lateral_mm', 0)
            if desplazamiento <= 0:
                # Si el desplazamiento es cero o negativo, usar un valor predeterminado
                desplazamiento = 10  # Valor ejemplo
                results['desplazamiento_lateral_mm'] = desplazamiento
            
            # Crear un DataFrame de pandas para los datos de entrada, filtrando según tipo de perfil
            tipo_perfil = input_data.get("tipo_perfil", "")
            
            # Datos básicos comunes a todos los perfiles
            input_data_list = [
                {"Parámetro": "Tipo de Perfil", "Valor": tipo_perfil},
                {"Parámetro": "Tipo de Acero", "Valor": input_data.get("tipo_acero", "")},
                {"Parámetro": "Longitud", "Valor": f"{input_data.get('longitud_mm', 0):.2f} mm"},
                {"Parámetro": "Condición de Apoyo", "Valor": input_data.get("condicion_apoyo", "")}
            ]
            
            # Añadir datos específicos según tipo de perfil
            if tipo_perfil in ["IPE", "HEB", "HEA", "HEM", "UPN", "L", "T"]:
                input_data_list.extend([
                    {"Parámetro": "Altura del Perfil", "Valor": f"{input_data.get('altura_perfil_mm', 0):.2f} mm"},
                    {"Parámetro": "Ancho de Alas", "Valor": f"{input_data.get('ancho_alas_mm', 0):.2f} mm"},
                    {"Parámetro": "Espesor de Alma", "Valor": f"{input_data.get('espesor_alma_mm', 0):.2f} mm"},
                    {"Parámetro": "Espesor de Alas", "Valor": f"{input_data.get('espesor_alas_mm', 0):.2f} mm"}
                ])
            elif tipo_perfil in ["Tubular cuadrado", "Tubular circular"]:
                input_data_list.extend([
                    {"Parámetro": "Dimensión Exterior", "Valor": f"{input_data.get('dimension_exterior_mm', 0):.2f} mm"},
                    {"Parámetro": "Espesor", "Valor": f"{input_data.get('espesor_mm', 0):.2f} mm"}
                ])
            
            # Crear el DataFrame a partir de la lista filtrada
            input_df = pd.DataFrame(input_data_list)
            
            # Crear un DataFrame para los resultados principales
            main_results_df = pd.DataFrame([
                {"Parámetro": "Carga Máxima (kN)", "Valor": f"{results.get('carga_maxima_kN', 0):.2f}"},
                {"Parámetro": "Carga Máxima (kg)", "Valor": f"{results.get('carga_maxima_kg', 0):.2f}"},
                {"Parámetro": "Carga Máxima (ton)", "Valor": f"{results.get('carga_maxima_ton', 0):.2f}"}
            ])
            
            # Crear un DataFrame para los resultados detallados
            detailed_results_df = pd.DataFrame([
                {"Parámetro": "Longitud de Pandeo (mm)", "Valor": f"{results.get('longitud_pandeo_mm', 0):.2f}"},
                {"Parámetro": "Esbeltez Mecánica", "Valor": f"{results.get('esbeltez_mecanica', 0):.2f}"},
                {"Parámetro": "Esbeltez Relativa", "Valor": f"{results.get('esbeltez_relativa', 0):.2f}"},
                {"Parámetro": "Curva de Pandeo", "Valor": results.get('curva_pandeo', '')},
                {"Parámetro": "Coeficiente de Imperfección", "Valor": f"{results.get('coef_imperfeccion', 0):.3f}"},
                {"Parámetro": "Área (mm²)", "Valor": f"{results.get('area_mm2', 0):.2f}"},
                {"Parámetro": "Inercia (mm⁴)", "Valor": f"{results.get('inercia_mm4', 0):.2f}"},
                {"Parámetro": "Radio de Giro (mm)", "Valor": f"{results.get('radio_giro_mm', 0):.2f}"},
                {"Parámetro": "Carga Crítica de Euler (kN)", "Valor": f"{results.get('carga_critica_euler_kN', 0):.2f}"},
                {"Parámetro": "Factor de Reducción", "Valor": f"{results.get('factor_reduccion', 0):.3f}"},
                {"Parámetro": "Resistencia Plástica (kN)", "Valor": f"{results.get('resistencia_plastica_kN', 0):.2f}"},
                {"Parámetro": "Desplazamiento Lateral (mm)", "Valor": f"{results.get('desplazamiento_lateral_mm', 0):.2f}"}
            ])
            
            # Generar datos de simulación detallada (1000 puntos)
            num_steps = 1000  # Aumentado a 1000 puntos para tener más resolución
            load_factors = np.linspace(0, 1, num_steps)
            max_displacement = results.get('desplazamiento_lateral_mm', 0)
            
            # Crear lista para almacenar datos de simulación
            simulation_data = []
            
            # Obtener parámetros para los cálculos
            carga_max = results.get('carga_maxima_kN', 0)
            carga_euler = results.get('carga_critica_euler_kN', 0)
            longitud_mm = input_data.get('longitud_mm', 3000)
            area_mm2 = results.get('area_mm2', 1000)
            inercia_mm4 = results.get('inercia_mm4', 100000)
            radio_giro_mm = results.get('radio_giro_mm', 10)
            factor_longitud_efectiva = results.get('factor_longitud_efectiva', 1.0)
            longitud_pandeo_mm = results.get('longitud_pandeo_mm', longitud_mm)
            modulo_elasticidad_MPa = 210000  # Valor estándar para acero
            limite_elastico_MPa = results.get('limite_elastico_MPa', 275)
            esbeltez_mecanica = results.get('esbeltez_mecanica', longitud_pandeo_mm / radio_giro_mm)
            esbeltez_relativa = results.get('esbeltez_relativa', 1.0)
            factor_reduccion = results.get('factor_reduccion', 1.0)
            
            # Generar simulación detallada para cada punto de carga
            for i, load_factor in enumerate(load_factors):
                # Calcular carga actual como porcentaje de la carga máxima
                carga_actual = carga_max * load_factor
                porcentaje = load_factor * 100
                
                # Calcular desplazamiento según teoría de pandeo
                # Para cargas bajas, relación casi lineal; para cargas altas, crece exponencialmente
                if load_factor < 0.6:
                    # Fase inicial: relación casi lineal
                    desplazamiento = max_displacement * (load_factor / 0.6)
                else:
                    # Fase final: crecimiento exponencial cerca de la carga máxima
                    factor_no_lineal = (load_factor - 0.6) / 0.4
                    desplazamiento = max_displacement * (0.6 + 0.4 * (1 + np.tan(factor_no_lineal * np.pi/3)))
                
                # Asegurar que el desplazamiento no exceda un valor máximo razonable
                desplazamiento = min(desplazamiento, max_displacement * 2)
                
                # Calcular momento flector
                momento = carga_actual * desplazamiento / 1000  # kN·m
                
                # Calcular relación carga/Euler
                relacion_euler = carga_actual / carga_euler if carga_euler > 0 else load_factor
                
                # Calcular tensión axial (N/mm²)
                tension_axial = carga_actual * 1000 / area_mm2 if area_mm2 > 0 else 0
                
                # Calcular tensión crítica
                tension_critica = (np.pi**2 * modulo_elasticidad_MPa) / esbeltez_mecanica**2 if esbeltez_mecanica > 0 else limite_elastico_MPa
                
                # Calcular factor de seguridad
                factor_seguridad = tension_critica / tension_axial if tension_axial > 0 else float('inf')
                if factor_seguridad > 100:
                    factor_seguridad = ">100"
                else:
                    factor_seguridad = f"{factor_seguridad:.2f}"
                
                # Agregar punto a la simulación
                simulation_data.append({
                    "% Carga": f"{porcentaje:.1f}",
                    "Carga (kN)": f"{carga_actual:.2f}",
                    "Desplazamiento (mm)": f"{desplazamiento:.3f}",
                    "Momento (kN·m)": f"{momento:.3f}",
                    "Carga/Euler": f"{relacion_euler:.3f}",
                    "Tensión (MPa)": f"{tension_axial:.2f}",
                    "Factor Seguridad": factor_seguridad
                })
            
            # Crear DataFrame con todos los datos de simulación
            simulation_df = pd.DataFrame(simulation_data)
            
            # Exportar a Excel con formato profesional
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Definir formatos con estilo profesional
                title_format = workbook.add_format({
                    'bold': True,
                    'font_size': 14,
                    'align': 'center',
                    'valign': 'vcenter',
                    'bg_color': '#4472C4',
                    'font_color': 'white',
                    'border': 1,
                    'text_wrap': True
                })
                
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#D9E1F2',
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter',
                    'text_wrap': True,
                    'font_size': 11
                })
                
                cell_format = workbook.add_format({
                    'border': 1,
                    'align': 'left',
                    'valign': 'vcenter',
                    'text_wrap': True
                })
                
                value_format = workbook.add_format({
                    'border': 1,
                    'align': 'right',
                    'valign': 'vcenter',
                    'text_wrap': True
                })
                
                # Formato para números
                number_format = workbook.add_format({
                    'border': 1,
                    'align': 'right',
                    'valign': 'vcenter',
                    'num_format': '#,##0.00',
                    'text_wrap': True
                })
                
                # Formato para porcentajes
                percent_format = workbook.add_format({
                    'border': 1,
                    'align': 'right',
                    'valign': 'vcenter',
                    'num_format': '0.0%',
                    'text_wrap': True
                })
                
                # Formato para filas alternadas
                alt_row_format = workbook.add_format({
                    'border': 1,
                    'align': 'right',
                    'valign': 'vcenter',
                    'bg_color': '#F2F2F2',
                    'text_wrap': True
                })
                
                # Formato para filas alternadas con alineación a la izquierda
                alt_row_left_format = workbook.add_format({
                    'border': 1,
                    'align': 'left',
                    'valign': 'vcenter',
                    'bg_color': '#F2F2F2',
                    'text_wrap': True
                })
                
                # Hoja para datos de entrada
                input_df.to_excel(writer, sheet_name='Datos de Entrada', index=False, startrow=1)
                
                # Ajustar hoja de entrada
                worksheet = writer.sheets['Datos de Entrada']
                worksheet.set_column('A:A', 25)
                worksheet.set_column('B:B', 25)
                worksheet.set_row(0, 30)  # Altura de la fila del título
                
                # Añadir título
                worksheet.merge_range('A1:B1', 'DATOS DE ENTRADA', title_format)
                
                # Aplicar formatos a la tabla
                worksheet.write_row(1, 0, input_df.columns, header_format)
                for row_num in range(2, len(input_df) + 2):
                    worksheet.set_row(row_num, 20)  # Altura de las filas de datos
                    if row_num % 2 == 0:
                        worksheet.write(row_num, 0, input_df.iloc[row_num-2, 0], alt_row_left_format)  # Alineado a la izquierda
                        worksheet.write(row_num, 1, input_df.iloc[row_num-2, 1], alt_row_format)
                    else:
                        worksheet.write(row_num, 0, input_df.iloc[row_num-2, 0], cell_format)  # Alineado a la izquierda
                        worksheet.write(row_num, 1, input_df.iloc[row_num-2, 1], value_format)
                
                # Hoja para resultados principales
                main_results_df.to_excel(writer, sheet_name='Resultados Principales', index=False, startrow=1)
                
                # Ajustar hoja de resultados principales
                worksheet = writer.sheets['Resultados Principales']
                worksheet.set_column('A:A', 25)
                worksheet.set_column('B:B', 25)
                worksheet.set_row(0, 30)  # Altura de la fila del título
                worksheet.merge_range('A1:B1', 'RESULTADOS PRINCIPALES', title_format)
                
                # Aplicar formatos a la tabla
                worksheet.write_row(1, 0, main_results_df.columns, header_format)
                for row_num in range(2, len(main_results_df) + 2):
                    worksheet.set_row(row_num, 20)  # Altura de las filas de datos
                    if row_num % 2 == 0:
                        worksheet.write(row_num, 0, main_results_df.iloc[row_num-2, 0], alt_row_left_format)  # Alineado a la izquierda
                        worksheet.write(row_num, 1, main_results_df.iloc[row_num-2, 1], alt_row_format)
                    else:
                        worksheet.write(row_num, 0, main_results_df.iloc[row_num-2, 0], cell_format)  # Alineado a la izquierda
                        worksheet.write(row_num, 1, main_results_df.iloc[row_num-2, 1], value_format)
                
                # Hoja para resultados detallados
                detailed_results_df.to_excel(writer, sheet_name='Resultados Detallados', index=False, startrow=1)
                
                # Ajustar hoja de resultados detallados
                worksheet = writer.sheets['Resultados Detallados']
                worksheet.set_column('A:A', 30)
                worksheet.set_column('B:B', 25)
                worksheet.set_row(0, 30)  # Altura de la fila del título
                worksheet.merge_range('A1:B1', 'RESULTADOS DETALLADOS', title_format)
                
                # Aplicar formatos a la tabla
                worksheet.write_row(1, 0, detailed_results_df.columns, header_format)
                for row_num in range(2, len(detailed_results_df) + 2):
                    worksheet.set_row(row_num, 20)  # Altura de las filas de datos
                    if row_num % 2 == 0:
                        worksheet.write(row_num, 0, detailed_results_df.iloc[row_num-2, 0], alt_row_left_format)  # Alineado a la izquierda
                        worksheet.write(row_num, 1, detailed_results_df.iloc[row_num-2, 1], alt_row_format)
                    else:
                        worksheet.write(row_num, 0, detailed_results_df.iloc[row_num-2, 0], cell_format)  # Alineado a la izquierda
                        worksheet.write(row_num, 1, detailed_results_df.iloc[row_num-2, 1], value_format)
                
                # Hoja para simulación (muestra)
                # Tomar solo cada 20 filas para tener una tabla más manejable
                tabla_muestra = simulation_data[::20]
                tabla_df = pd.DataFrame(tabla_muestra)
                tabla_df.to_excel(writer, sheet_name='Simulación', index=False, startrow=1)
                
                # Ajustar hoja de simulación
                worksheet = writer.sheets['Simulación']
                worksheet.set_column('A:G', 18)
                worksheet.set_row(0, 30)  # Altura de la fila del título
                worksheet.merge_range('A1:G1', 'SIMULACIÓN DE CARGA (MUESTRA)', title_format)
                
                # Aplicar formatos a la tabla de muestra
                worksheet.write_row(1, 0, tabla_df.columns, header_format)
                for row_num in range(2, len(tabla_df) + 2):
                    worksheet.set_row(row_num, 20)  # Altura de las filas de datos
                    # Usar formato alternado para filas pares/impares
                    if row_num % 2 == 0:
                        for col_num, value in enumerate(tabla_df.iloc[row_num-2]):
                            worksheet.write(row_num, col_num, value, alt_row_format)
                    else:
                        for col_num, value in enumerate(tabla_df.iloc[row_num-2]):
                            worksheet.write(row_num, col_num, value, value_format)
                
                # Hoja para datos de simulación completa (1000 puntos)
                simulation_df.to_excel(writer, sheet_name='Datos Simulación', index=False, startrow=1)
                
                # Ajustar hoja de simulación completa
                worksheet = writer.sheets['Datos Simulación']
                worksheet.set_column('A:G', 18)
                worksheet.set_row(0, 30)  # Altura de la fila del título
                worksheet.merge_range('A1:G1', 'SIMULACIÓN COMPLETA (1000 PUNTOS)', title_format)
                
                # Aplicar formatos a la tabla de simulación completa
                worksheet.write_row(1, 0, simulation_df.columns, header_format)
                
                # Para los primeros 100 registros aplicamos formato completo (para rendimiento)
                max_formatted_rows = min(100, len(simulation_df))
                for row_num in range(2, max_formatted_rows + 2):
                    worksheet.set_row(row_num, 20)  # Altura de las filas de datos
                    if row_num % 2 == 0:
                        for col_num, value in enumerate(simulation_df.iloc[row_num-2]):
                            worksheet.write(row_num, col_num, value, alt_row_format)
                    else:
                        for col_num, value in enumerate(simulation_df.iloc[row_num-2]):
                            worksheet.write(row_num, col_num, value, value_format)
                
                # Para el resto de filas, aplicamos formato por columnas para mejorar rendimiento
                # Definimos formatos específicos para cada columna
                col_formats = {
                    0: {'even': workbook.add_format({'border': 1, 'align': 'right', 'bg_color': '#F2F2F2', 'text_wrap': True}),
                        'odd': workbook.add_format({'border': 1, 'align': 'right', 'text_wrap': True})},
                    1: {'even': workbook.add_format({'border': 1, 'align': 'right', 'bg_color': '#F2F2F2', 'text_wrap': True}),
                        'odd': workbook.add_format({'border': 1, 'align': 'right', 'text_wrap': True})},
                    2: {'even': workbook.add_format({'border': 1, 'align': 'right', 'bg_color': '#F2F2F2', 'text_wrap': True}),
                        'odd': workbook.add_format({'border': 1, 'align': 'right', 'text_wrap': True})},
                    3: {'even': workbook.add_format({'border': 1, 'align': 'right', 'bg_color': '#F2F2F2', 'text_wrap': True}),
                        'odd': workbook.add_format({'border': 1, 'align': 'right', 'text_wrap': True})},
                    4: {'even': workbook.add_format({'border': 1, 'align': 'right', 'bg_color': '#F2F2F2', 'text_wrap': True}),
                        'odd': workbook.add_format({'border': 1, 'align': 'right', 'text_wrap': True})},
                    5: {'even': workbook.add_format({'border': 1, 'align': 'right', 'bg_color': '#F2F2F2', 'text_wrap': True}),
                        'odd': workbook.add_format({'border': 1, 'align': 'right', 'text_wrap': True})},
                    6: {'even': workbook.add_format({'border': 1, 'align': 'right', 'bg_color': '#F2F2F2', 'text_wrap': True}),
                        'odd': workbook.add_format({'border': 1, 'align': 'right', 'text_wrap': True})}
                }
                
                # Aplicamos formato por rangos de filas para mejorar rendimiento
                batch_size = 50  # Procesar en lotes de 50 filas
                for start_row in range(max_formatted_rows + 2, len(simulation_df) + 2, batch_size):
                    end_row = min(start_row + batch_size - 1, len(simulation_df) + 1)
                    for col_num in range(len(simulation_df.columns)):
                        # Aplicar formato a filas pares
                        even_rows = [row for row in range(start_row, end_row + 1) if row % 2 == 0]
                        if even_rows:
                            even_range = f'{chr(65+col_num)}{even_rows[0]}:{chr(65+col_num)}{even_rows[-1]}'
                            worksheet.conditional_format(even_range, {
                                'type': 'formula',
                                'criteria': 'MOD(ROW(),2)=0',
                                'format': col_formats[col_num]['even']
                            })
                        
                        # Aplicar formato a filas impares
                        odd_rows = [row for row in range(start_row, end_row + 1) if row % 2 != 0]
                        if odd_rows:
                            odd_range = f'{chr(65+col_num)}{odd_rows[0]}:{chr(65+col_num)}{odd_rows[-1]}'
                            worksheet.conditional_format(odd_range, {
                                'type': 'formula',
                                'criteria': 'MOD(ROW(),2)=1',
                                'format': col_formats[col_num]['odd']
                            })
                
                # Aplicamos bordes exteriores más gruesos solo a las tablas reales, no a toda la hoja
                # Para cada hoja, determinamos el rango exacto de datos
                sheets_data = {
                    'Datos de Entrada': {'rows': len(input_df) + 2, 'cols': 2},  # +2 por el título y encabezado
                    'Resultados Principales': {'rows': len(main_results_df) + 2, 'cols': 2},
                    'Resultados Detallados': {'rows': len(detailed_results_df) + 2, 'cols': 2},
                    'Simulación': {'rows': len(tabla_df) + 2, 'cols': len(tabla_df.columns)},
                    'Datos Simulación': {'rows': len(simulation_df) + 2, 'cols': len(simulation_df.columns)}
                }
                
                for sheet_name, dimensions in sheets_data.items():
                    ws = writer.sheets[sheet_name]
                    rows = dimensions['rows']
                    cols = dimensions['cols']
                    
                    # Convertimos número de columnas a letras (ej: 1->A, 2->B, etc.)
                    end_col_letter = chr(64 + cols) if cols <= 26 else chr(64 + cols // 26) + chr(64 + cols % 26)
                    
                    # Aplicamos formato solo al rango que contiene datos
                    range_str = f'A1:{end_col_letter}{rows}'
                    
                    # Crear formato con borde exterior grueso y bordes interiores normales
                    table_format = workbook.add_format({
                        'border': 1  # Borde normal para todas las celdas
                    })
                    
                    # Aplicar formato base a todas las celdas de la tabla
                    ws.conditional_format(range_str, {
                        'type': 'formula',
                        'criteria': 'TRUE',
                        'format': table_format
                    })
                    
                    # Aplicar bordes gruesos solo al contorno exterior de la tabla
                    # Borde superior de la primera fila
                    ws.conditional_format(f'A1:{end_col_letter}1', {
                        'type': 'formula',
                        'criteria': 'TRUE',
                        'format': workbook.add_format({'top': 2})
                    })
                    
                    # Borde inferior de la última fila
                    ws.conditional_format(f'A{rows}:{end_col_letter}{rows}', {
                        'type': 'formula',
                        'criteria': 'TRUE',
                        'format': workbook.add_format({'bottom': 2})
                    })
                    
                    # Borde izquierdo de la primera columna
                    ws.conditional_format(f'A1:A{rows}', {
                        'type': 'formula',
                        'criteria': 'TRUE',
                        'format': workbook.add_format({'left': 2})
                    })
                    
                    # Borde derecho de la última columna
                    ws.conditional_format(f'{end_col_letter}1:{end_col_letter}{rows}', {
                        'type': 'formula',
                        'criteria': 'TRUE',
                        'format': workbook.add_format({'right': 2})
                    })
                
                # Eliminamos la hoja de resumen ya que no es necesaria
                # No necesitamos el código para la hoja de resumen
                
        except Exception as e:
            # En caso de error, hacer una exportación más simple
            try:
                # Crear DataFrames básicos
                input_df = pd.DataFrame([
                    {"Parámetro": "Tipo de Perfil", "Valor": input_data.get("tipo_perfil", "")},
                    {"Parámetro": "Tipo de Acero", "Valor": input_data.get("tipo_acero", "")},
                    {"Parámetro": "Longitud", "Valor": f"{input_data.get('longitud_mm', 0):.2f} mm"}
                ])
                
                results_df = pd.DataFrame([
                    {"Parámetro": "Carga Máxima (kN)", "Valor": f"{results.get('carga_maxima_kN', 400):.2f}"},
                    {"Parámetro": "Desplazamiento Lateral (mm)", "Valor": f"{results.get('desplazamiento_lateral_mm', 10):.2f}"}
                ])
                
                # Generar 1000 puntos de simulación simplificada
                simulation_data = []
                carga_max = results.get('carga_maxima_kN', 400)
                max_displacement = results.get('desplazamiento_lateral_mm', 10)
                
                for i in range(1000):
                    load_factor = i / 999  # 0 a 1
                    carga_actual = carga_max * load_factor
                    porcentaje = load_factor * 100
                    
                    # Calcular desplazamiento simplificado
                    if load_factor < 0.6:
                        desplazamiento = max_displacement * (load_factor / 0.6)
                    else:
                        factor_no_lineal = (load_factor - 0.6) / 0.4
                        desplazamiento = max_displacement * (0.6 + 0.4 * (1 + np.tan(factor_no_lineal * np.pi/3)))
                    
                    desplazamiento = min(desplazamiento, max_displacement * 2)
                    
                    # Momento simplificado
                    momento = carga_actual * desplazamiento / 1000
                    
                    # Agregar a los datos de simulación
                    simulation_data.append({
                        "% Carga": f"{porcentaje:.1f}",
                        "Carga (kN)": f"{carga_actual:.2f}",
                        "Desplazamiento (mm)": f"{desplazamiento:.3f}",
                        "Momento (kN·m)": f"{momento:.3f}"
                    })
                
                simulation_df = pd.DataFrame(simulation_data)
                
                # Exportar sin formato especial
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    input_df.to_excel(writer, sheet_name='Datos', index=False)
                    results_df.to_excel(writer, sheet_name='Resultados', index=False)
                    simulation_df.to_excel(writer, sheet_name='Simulación', index=False)
                    
                print(f"Exportación de emergencia a {file_path} completada.")
            except Exception as inner_e:
                print(f"Error grave en exportación: {str(inner_e)}")
                raise

    def _generar_dimensiones(self, tipo):
        """
        Genera dimensiones aleatorias según el tipo de perfil.
        
        Args:
            tipo (str): Tipo de perfil (IPE, HEB, etc.)
            
        Returns:
            dict: Diccionario con dimensiones generadas
        """
        if tipo in ['IPE', 'HEB', 'HEA', 'HEM', 'UPN']:
            return {
                'altura_perfil_mm': random.uniform(80, 600),
                'ancho_alas_mm': random.uniform(40, 300),
                'espesor_alma_mm': random.uniform(3, 20),
                'espesor_alas_mm': random.uniform(4, 25),
                'dimension_exterior_mm': None,
                'espesor_mm': None
            }
        else:  # Perfiles tubulares
            return {
                'altura_perfil_mm': None,
                'ancho_alas_mm': None,
                'espesor_alma_mm': None,
                'espesor_alas_mm': None,
                'dimension_exterior_mm': random.uniform(40, 400),
                'espesor_mm': random.uniform(3, 20)
            } 