# Instrucciones permanentes del repositorio

## Contexto del proyecto

- Este proyecto es una aplicación de Diseño Experimental desarrollada en Python y Streamlit para el curso de Diseño Experimental del programa de Ingeniería Agrícola de la Universidad de Sucre.

## Estructura del proyecto

- `app.py`: portada de la aplicación.
- `pages/`: una página por cada diseño experimental.
- `utils/`: funciones reutilizables; debe incluir `__init__.py`.
- `data/`: archivos CSV de ejemplo.
- `verificacion/`: scripts de R para verificación.

## Idioma y explicaciones

- Escribe en español todo el código, los comentarios, los docstrings y los mensajes de la interfaz.
- Incluye en cada paso estadístico un comentario que explique qué se calcula y por qué, dirigido a estudiantes de Ingeniería Agrícola.
- Añade type hints a todas las funciones y docstrings con estilo Google.

## Dependencias permitidas

- Usa únicamente estas librerías: `streamlit`, `pandas`, `numpy`, `scipy`, `statsmodels`, `plotly` y `openpyxl`.
- No agregues otras librerías sin pedir permiso.

## Análisis estadístico

- Ajusta los modelos de ANOVA con `statsmodels.formula.api.ols` y calcula la tabla con `statsmodels.stats.anova.anova_lm(typ=2)`.
- Realiza las comparaciones de Tukey con `statsmodels.stats.multicomp.pairwise_tukeyhsd`.
- No inventes resultados: todos los valores presentados deben provenir del cálculo correspondiente.

## Verificación

- Antes de terminar una tarea, ejecuta el código y corrige los errores que aparezcan.