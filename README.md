# Aplicación de Diseño Experimental

Aplicación educativa desarrollada con Streamlit para apoyar el curso de Diseño
Experimental del programa de Ingeniería Agrícola de la Universidad de Sucre.
Permite explorar diseños experimentales y analizar datos agrícolas; sus
resultados deben interpretarse junto con los supuestos estadísticos y el
conocimiento del ensayo.

## Módulos y estado

| Módulo | Diseño | Estado |
| --- | --- | --- |
| DCA | Diseño Completamente al Azar | Disponible: carga de datos, resumen por tratamiento, ANOVA, comparaciones de Tukey, gráficos y diagnóstico de supuestos. |
| DBCA | Diseño de Bloques Completos al Azar | En construcción. |
| DCL | Diseño de Cuadrado Latino | En construcción. |
| DPD | Diseño de Parcelas Divididas | En construcción. |
| Factoriales | Diseños factoriales | En construcción. |
| RSM | Metodología de Superficie de Respuesta | En construcción. |

## Estructura del proyecto

```text
.
├── app.py                     # Portada y catálogo de módulos
├── pages/                     # Una página Streamlit por diseño
├── utils/                     # Funciones reutilizables de análisis y diagnóstico
├── data/                      # Datos CSV de ejemplo
├── verificacion/              # Scripts R de verificación estadística
├── requirements.txt           # Dependencias de Python
├── BITACORA_IA.md             # Plantilla para registrar el uso de IA
└── README.md
```

## Instalación y ejecución local

Se requiere Python 3.10 o superior. Desde la carpeta del proyecto, crea y activa
un entorno virtual e instala las dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

En Windows, activa el entorno con `.venv\Scripts\activate` en lugar de
`source .venv/bin/activate`. Luego inicia la aplicación:

```bash
streamlit run app.py
```

Streamlit mostrará en la terminal la dirección local para abrir la aplicación
en el navegador.

## Ejecución en GitHub Codespaces

1. Abre el repositorio en un Codespace.
2. En la terminal integrada, instala las dependencias:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Inicia la aplicación:

   ```bash
   streamlit run app.py
   ```

4. Abre el puerto que Codespaces notifique (por defecto, Streamlit usa el
   puerto `8501`) con la opción **Open in Browser**.

## Verificación estadística con R

La verificación del DCA puede ejecutarse opcionalmente si R está instalado.
Desde la raíz del proyecto, ejecuta:

```bash
cd verificacion
Rscript verificacion_dca.R
```

El script contrasta el análisis de humedad por secador usando ANOVA, medias,
coeficiente de variación y Tukey.

## Autor y uso de inteligencia artificial

- **Autor:** Justo Fuentes.
- **Uso de IA:** se utilizó IA generativa como apoyo en tareas de desarrollo y
  documentación. El autor revisa los cambios y debe verificar las salidas de la
  aplicación y los análisis con los datos y supuestos del ensayo. La IA no
  sustituye el criterio estadístico ni la validación académica.
