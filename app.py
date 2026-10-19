AUTOR = "Escribe aquí tu nombre"

import streamlit as st

st.set_page_config(
    page_title="App de Diseño Experimental",
    page_icon="🌱",
    layout="wide",
)

st.title("App de Diseño Experimental")
st.subheader("Ingeniería Agrícola – Universidad de Sucre")
st.write(
    "El diseño experimental permite planificar ensayos agrícolas de manera "
    "ordenada, comparar tratamientos y obtener conclusiones confiables sobre "
    "cultivos, suelos y prácticas de manejo en el campo."
)

st.header("Módulos disponibles")
st.table(
    [
        {
            "Módulo": "DCA",
            "Nombre completo": "Diseño Completamente al Azar",
            "Cuándo se usa": "Cuando las unidades experimentales son homogéneas.",
            "Ejemplo agrícola": "Comparar temperaturas de secado con muestras homogéneas de yuca.",
            "Estado": "Disponible",
        },
        {
            "Módulo": "DBCA",
            "Nombre completo": "Diseño de Bloques Completos al Azar",
            "Cuándo se usa": "Cuando se puede agrupar la variabilidad en bloques homogéneos.",
            "Ejemplo agrícola": "Comparar fertilizantes formando bloques según la fertilidad del lote.",
            "Estado": "En construcción",
        },
        {
            "Módulo": "DCL",
            "Nombre completo": "Diseño de Cuadrado Latino",
            "Cuándo se usa": "Cuando se controlan dos fuentes de variación mediante filas y columnas.",
            "Ejemplo agrícola": "Evaluar variedades controlando gradientes del terreno en dos direcciones.",
            "Estado": "En construcción",
        },
        {
            "Módulo": "DPD",
            "Nombre completo": "Diseño de Parcelas Divididas",
            "Cuándo se usa": "Cuando dos factores se aplican en unidades experimentales de distinto tamaño.",
            "Ejemplo agrícola": "Comparar sistemas de riego en parcelas y dosis de abono en subparcelas.",
            "Estado": "En construcción",
        },
        {
            "Módulo": "Factoriales",
            "Nombre completo": "Diseños factoriales",
            "Cuándo se usa": "Cuando se estudian varios factores y sus posibles interacciones.",
            "Ejemplo agrícola": "Evaluar conjuntamente niveles de riego y nitrógeno en maíz.",
            "Estado": "En construcción",
        },
        {
            "Módulo": "RSM",
            "Nombre completo": "Metodología de Superficie de Respuesta",
            "Cuándo se usa": "Cuando se busca modelar y optimizar una respuesta con factores cuantitativos.",
            "Ejemplo agrícola": "Optimizar temperatura y tiempo de secado para la yuca.",
            "Estado": "En construcción",
        },
    ]
)

st.header("Instrucciones de uso")
st.markdown(
    """
1. Elige un módulo en el menú lateral.
2. Carga los datos del ensayo cuando la actividad esté disponible.
3. Revisa e interpreta los resultados del análisis.
4. Verifica los supuestos y compara con tu cálculo manual.
"""
)

st.warning(
    "Esta app apoya el aprendizaje. El estudiante interpreta los resultados, "
    "verifica supuestos y compara con su cálculo manual."
)

st.sidebar.header("Información del curso")
st.sidebar.write(f"Autor: {AUTOR}")
st.sidebar.write("Curso: Diseño Experimental")
st.sidebar.write("Semestre: 2026-2")