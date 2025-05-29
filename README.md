# PANDEO ML

![Pandeo ML Logo](app/assets/icon.png)

## Descripción

PANDEO ML es una aplicación avanzada para la predicción del fenómeno de pandeo en elementos estructurales de acero. Utiliza modelos de aprendizaje automático entrenados con datos generados a partir de principios físicos y ecuaciones fundamentales de la teoría de pandeo, lo que permite obtener predicciones precisas y rápidas sin necesidad de realizar análisis por elementos finitos complejos.

La aplicación está diseñada para ingenieros estructurales, arquitectos y profesionales del sector de la construcción que necesitan evaluar rápidamente el comportamiento de elementos comprimidos bajo diferentes condiciones de carga y restricciones.

## Características

- **Predicción precisa**: Modelo predictivo basado en CatBoost entrenado con datos de simulaciones.
- **Interfaz gráfica intuitiva**: Interfaz de usuario desarrollada con PyQt5, fácil de usar y accesible.
- **Visualización 3D**: Visualización interactiva del fenómeno de pandeo mediante PyVista.
- **Múltiples perfiles**: Soporte para diferentes tipos de perfiles estructurales (IPE, HEB, UPN, tubulares, etc.).
- **Simulación física**: Simulación del comportamiento estructural bajo diferentes condiciones.
- **Exportación de resultados**: Posibilidad de exportar los resultados en formato PDF e imagen.
- **Personalización**: Configuración y guardado de parámetros de análisis.

## Rendimiento del modelo

El modelo predictivo de PANDEO ML ha sido entrenado y validado con un extenso conjunto de datos generados a partir de simulaciones numéricas y cálculos analíticos basados en principios físicos. El modelo alcanza un coeficiente de determinación (R²) de **0.98**, lo que indica una alta precisión en la predicción del comportamiento a pandeo.

Este alto valor de R² demuestra que el modelo explica aproximadamente el 98% de la variabilidad en los datos de prueba, asegurando que las predicciones sean confiables para aplicaciones de ingeniería estructural.

Otras métricas de rendimiento incluyen:
- Error cuadrático medio (RMSE): 0.015
- Error absoluto medio (MAE): 0.011
- Precisión en la clasificación del modo de fallo: 96%

## Instalación

### Requisitos previos

- Python 3.8 o superior
- Pip (gestor de paquetes de Python)

### Instalación de dependencias

```bash
# Clonar el repositorio
git clone https://github.com/felixruizm/pandeo-ml.git
cd pandeo-ml

# Instalar dependencias
pip install -r requirements.txt
```

### Instalación opcional de PyVista (para visualización 3D)

```bash
pip install pyvista pyvistaqt
```

## Uso

### Iniciar la aplicación

```bash
python -m app.main
```

### Flujo de trabajo básico

1. **Entrada de datos**: 
   - Seleccione el tipo de perfil y sus dimensiones
   - Especifique las propiedades del material
   - Configure las condiciones de contorno y longitud

2. **Cálculo**: 
   - Presione el botón "Calcular" para ejecutar la predicción
   - La aplicación utiliza el modelo de aprendizaje automático para estimar el comportamiento a pandeo

3. **Resultados**: 
   - Visualice los resultados detallados de la predicción
   - Consulte los valores clave como carga crítica, coeficiente de pandeo, etc.

4. **Visualización**:
   - Explore la representación 3D del fenómeno de pandeo
   - Ajuste parámetros de visualización para mejor comprensión

5. **Exportación**:
   - Exporte los resultados a PDF o imagen para documentación

## Arquitectura del proyecto

```
pandeo-ml/
├── app/                      # Código fuente principal
│   ├── assets/               # Recursos gráficos e iconos
│   ├── components/           # Componentes de la interfaz de usuario
│   ├── config/               # Archivos de configuración
│   ├── exports/              # Directorio para archivos exportados
│   ├── models/               # Modelos predictivos
│   ├── static/               # Archivos estáticos
│   ├── utils/                # Utilidades y herramientas
│   └── main.py               # Punto de entrada principal
├── modelo_pandeo_acero_catboost.joblib  # Modelo entrenado
├── modelo_predictivo_pandeo_acero.ipynb # Notebook de desarrollo del modelo
├── requirements.txt          # Dependencias del proyecto
└── README.md                 # Documentación
```

## Fundamentos teóricos

La aplicación se basa en la teoría de pandeo de Euler y sus extensiones para el análisis de elementos comprimidos. El fenómeno de pandeo ocurre cuando un elemento estructural sometido a compresión axial alcanza un estado crítico de inestabilidad, provocando una deformación lateral.

El modelo predictivo considera:

- **Propiedades geométricas**: Momentos de inercia, radios de giro, área de la sección
- **Propiedades del material**: Módulo de elasticidad, límite elástico
- **Condiciones de contorno**: Coeficientes de longitud efectiva
- **Esbeltez**: Relación entre longitud efectiva y radio de giro

## Desarrollo

### Tecnologías utilizadas

- **PyQt5**: Framework para la interfaz gráfica
- **CatBoost**: Biblioteca de aprendizaje automático para el modelo predictivo
- **PyVista**: Biblioteca para visualización 3D
- **NumPy/SciPy**: Bibliotecas científicas para cálculos
- **Pandas**: Manipulación y análisis de datos
- **Matplotlib**: Generación de gráficos

### Contribución

Si desea contribuir al proyecto, siga estos pasos:

1. Haga un fork del repositorio
2. Cree una rama para su característica (`git checkout -b feature/nueva-caracteristica`)
3. Realice sus cambios y haga commit (`git commit -m 'Añadir nueva característica'`)
4. Haga push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abra un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulte el archivo `LICENSE` para más detalles.

## Autor

**Félix Ruiz M.**

## Contacto

Para preguntas o sugerencias, puede contactar al autor o abrir un issue en el repositorio.

## Agradecimientos

- A la comunidad de código abierto por las herramientas y bibliotecas utilizadas
- A los investigadores y académicos en el campo de la ingeniería estructural 