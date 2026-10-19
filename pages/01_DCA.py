from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.anova_utils import (
	ajustar_dca,
	cargar_datos,
	coeficiente_variacion,
	f_critica,
	interpretar_dca,
	resumen_tratamientos,
	tabla_anova,
	tukey,
	validar_dca,
)


@st.cache_data(show_spinner=False)
def cargar_archivo(archivo: Any) -> pd.DataFrame:
	"""Carga y conserva en caché el archivo seleccionado por el estudiante.

	Args:
		archivo: Archivo subido o ruta del archivo CSV de ejemplo.

	Returns:
		Datos del ensayo en un DataFrame.
	"""
	if hasattr(archivo, "seek"):
		archivo.seek(0)
	return cargar_datos(archivo)


st.title("Diseño Completamente al Azar (DCA)")
st.write(
	"El Diseño Completamente al Azar compara tratamientos cuando las unidades "
	"experimentales son homogéneas. En este ejemplo se analiza la humedad final "
	"(%, base húmeda) de yuca secada en cuatro secadores solares, con cuatro "
	"réplicas por secador."
)

archivo_subido = st.file_uploader(
	"Carga los datos del ensayo",
	type=["csv", "xlsx"],
	help="El archivo debe incluir una columna de tratamiento y otra de respuesta.",
)

if archivo_subido is None:
	st.caption("No se cargó un archivo; se usan los datos de ejemplo de los secadores solares.")
	archivo = str(Path("data") / "dca_secadores.csv")
else:
	archivo = archivo_subido

try:
	datos = cargar_archivo(archivo)
except Exception as error:
	st.error(f"No fue posible leer el archivo: {error}")
	st.stop()

if datos.empty or len(datos.columns) == 0:
	st.error("El archivo no contiene datos ni columnas para analizar.")
	st.stop()

columnas = list(datos.columns)
if len(columnas) < 2:
	st.error("El archivo debe tener al menos una columna de tratamiento y una de respuesta.")
	st.stop()

indice_tratamiento = columnas.index("secador") if "secador" in columnas else 0
col_trat = st.selectbox(
	"Columna de tratamiento",
	options=columnas,
	index=indice_tratamiento,
)
columnas_respuesta = [columna for columna in columnas if columna != col_trat]
respuestas_numericas = [
	columna
	for columna in columnas_respuesta
	if pd.api.types.is_numeric_dtype(datos[columna])
]
respuesta_predeterminada = (
	"humedad"
	if "humedad" in columnas_respuesta
	else respuestas_numericas[0]
	if respuestas_numericas
	else columnas_respuesta[0]
)
col_resp = st.selectbox(
	"Columna de respuesta",
	options=columnas_respuesta,
	index=columnas_respuesta.index(respuesta_predeterminada),
)
alfa = st.slider(
	"Nivel de significancia (alfa)",
	min_value=0.01,
	max_value=0.10,
	value=0.05,
	step=0.01,
)

errores = validar_dca(datos, col_trat, col_resp)
if errores:
	for error in errores:
		st.error(error)
	st.stop()
if col_trat == col_resp:
	st.error("Selecciona columnas distintas para tratamiento y respuesta.")
	st.stop()

modelo = ajustar_dca(datos, col_trat, col_resp)
anova = tabla_anova(modelo)
resumen = resumen_tratamientos(datos, col_trat, col_resp)
fila_tratamientos = anova.loc[anova["Fuente"] == "Tratamientos"].iloc[0]
fila_error = anova.loc[anova["Fuente"] == "Error"].iloc[0]
p_valor = float(fila_tratamientos["p-valor"])
cv = coeficiente_variacion(modelo, datos, col_resp)

tab_datos, tab_anova, tab_comparaciones, tab_graficos = st.tabs(
	["Datos", "ANOVA", "Comparaciones", "Gráficos"]
)

with tab_datos:
	st.subheader("Observaciones del ensayo")
	st.dataframe(datos, width="stretch", hide_index=True)
	st.subheader("Resumen por tratamiento")
	st.dataframe(resumen, width="stretch", hide_index=True)

with tab_anova:
	st.subheader("Análisis de varianza")
	formato_anova = anova.style.format(
		{
			"gl": "{:.4f}",
			"SC": "{:.4f}",
			"CM": "{:.4f}",
			"F": "{:.4f}",
			"p-valor": "{:.4f}",
		},
		na_rep="—",
	)
	st.dataframe(formato_anova, width="stretch", hide_index=True)

	valor_f_critico = f_critica(alfa, fila_tratamientos["gl"], fila_error["gl"])
	st.metric("F crítica", f"{valor_f_critico:.4f}")
	st.metric("Coeficiente de variación", f"{cv:.4f}%")

	interpretacion = interpretar_dca(anova, alfa)
	if p_valor < alfa:
		st.success(interpretacion)
	else:
		st.info(interpretacion)

with tab_comparaciones:
	st.subheader("Comparación de medias")
	if p_valor < alfa:
		comparaciones, dms = tukey(datos, col_trat, col_resp, alfa)
		st.dataframe(comparaciones, width="stretch", hide_index=True)
		st.metric("Diferencia mínima significativa (DMS)", f"{dms:.4f}")
	else:
		st.info(
			"No se realiza la prueba de Tukey porque el ANOVA no detectó "
			"diferencias significativas entre tratamientos al nivel alfa seleccionado."
		)

with tab_graficos:
	st.subheader("Distribución por tratamiento")
	grafico_cajas = px.box(
		datos,
		x=col_trat,
		y=col_resp,
		points="all",
		labels={col_trat: "Tratamiento", col_resp: "Respuesta"},
	)
	st.plotly_chart(grafico_cajas, width="stretch")

	st.subheader("Media por tratamiento")
	grafico_medias = px.bar(
		resumen,
		x=col_trat,
		y="media",
		error_y="desviación estándar",
		labels={
			col_trat: "Tratamiento",
			"media": "Media de la respuesta",
			"desviación estándar": "Desviación estándar",
		},
	)
	st.plotly_chart(grafico_medias, width="stretch")