"""Herramientas para revisar los supuestos de un Diseño Completamente al Azar."""

from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from statsmodels.regression.linear_model import RegressionResultsWrapper


def residuos_y_ajustados(
	modelo: RegressionResultsWrapper,
) -> tuple[pd.Series, pd.Series]:
	"""Obtiene los residuos y valores ajustados del modelo DCA.

	Args:
		modelo: Modelo OLS ajustado para el diseño.

	Returns:
		Tupla con las series de residuos y valores ajustados.
	"""
	# Paso 1: el residuo e_i = y_i - y estimado_i representa el error no explicado.
	residuos = pd.Series(modelo.resid, name="Residuos")

	# Paso 2: el valor ajustado es la respuesta estimada para cada unidad experimental.
	ajustados = pd.Series(modelo.fittedvalues, name="Valores ajustados")
	return residuos, ajustados


def prueba_shapiro(
	residuos: Sequence[float] | pd.Series | np.ndarray,
) -> tuple[float, float, str]:
	"""Evalúa la normalidad de los residuos mediante Shapiro-Wilk.

	Args:
		residuos: Residuos del modelo DCA.

	Returns:
		Estadístico W, p-valor y conclusión en español con alfa 0.05.

	Raises:
		ValueError: Si hay menos de tres residuos válidos o valores no finitos.
	"""
	# Paso 1: se convierten residuos a números y se excluyen valores no disponibles.
	valores = np.asarray(residuos, dtype=float)
	valores = valores[np.isfinite(valores)]
	if valores.size < 3:
		raise ValueError("Shapiro-Wilk requiere al menos 3 residuos válidos.")

	# Paso 2: H0 propone normalidad; W cercano a 1 y p >= 0.05 no dan evidencia contra ella.
	estadistico, p_valor = stats.shapiro(valores)
	if p_valor < 0.05:
		conclusion = (
			"Se rechaza la normalidad de los residuos al 5%; revisa el ajuste y "
			"considera el contexto experimental."
		)
	else:
		conclusion = (
			"No se detecta evidencia suficiente para rechazar la normalidad de los "
			"residuos al 5%; esto no demuestra que sean normales."
		)
	return float(estadistico), float(p_valor), conclusion


def prueba_levene(
	df: pd.DataFrame, col_trat: str, col_resp: str
) -> tuple[float, float, str]:
	"""Evalúa igualdad de varianzas entre tratamientos con Levene centrado en mediana.

	Args:
		df: Datos del ensayo.
		col_trat: Nombre de la columna de tratamientos.
		col_resp: Nombre de la columna de respuesta.

	Returns:
		Estadístico de Levene, p-valor y conclusión en español con alfa 0.05.

	Raises:
		ValueError: Si faltan columnas o no hay grupos suficientes con réplicas válidas.
	"""
	# Paso 1: se confirma que las dos variables estén disponibles para agrupar y comparar.
	if col_trat not in df.columns or col_resp not in df.columns:
		raise ValueError("No se encontraron las columnas de tratamiento y respuesta.")

	# Paso 2: cada grupo aporta sus respuestas; se necesita al menos dos grupos replicados.
	grupos = [
		grupo[col_resp].dropna().to_numpy(dtype=float)
		for _, grupo in df.groupby(col_trat, observed=True)
	]
	grupos = [grupo[np.isfinite(grupo)] for grupo in grupos]
	grupos = [grupo for grupo in grupos if grupo.size >= 2]
	if len(grupos) < 2:
		raise ValueError("Levene requiere al menos 2 tratamientos con 2 réplicas válidas.")

	# Paso 3: H0 plantea varianzas iguales; center='median' es robusto ante asimetría.
	estadistico, p_valor = stats.levene(*grupos, center="median")
	if p_valor < 0.05:
		conclusion = (
			"Se rechaza la igualdad de varianzas al 5%; hay evidencia de variabilidad "
			"distinta entre tratamientos."
		)
	else:
		conclusion = (
			"No se detecta evidencia suficiente para rechazar la igualdad de varianzas "
			"al 5%; esto no demuestra que las varianzas sean idénticas."
		)
	return float(estadistico), float(p_valor), conclusion


def grafico_residuos_vs_ajustados(
	residuos: Sequence[float] | pd.Series | np.ndarray,
	ajustados: Sequence[float] | pd.Series | np.ndarray,
) -> go.Figure:
	"""Construye el gráfico de residuos frente a valores ajustados.

	Args:
		residuos: Residuos del modelo DCA.
		ajustados: Valores ajustados del modelo DCA.

	Returns:
		Gráfico Plotly para revisar patrones y dispersión de los residuos.
	"""
	# Paso 1: se organizan cada residuo y su valor ajustado para examinar patrones.
	datos_grafico = pd.DataFrame(
		{
			"Valores ajustados": np.asarray(ajustados, dtype=float),
			"Residuos": np.asarray(residuos, dtype=float),
		}
	)

	# Paso 2: una nube alrededor de cero sin forma sistemática es compatible con varianza constante.
	figura = px.scatter(
		datos_grafico,
		x="Valores ajustados",
		y="Residuos",
		labels={"Valores ajustados": "Valores ajustados", "Residuos": "Residuos"},
	)
	figura.add_hline(y=0, line_dash="dash", line_color="gray")
	figura.update_layout(title="Residuos frente a valores ajustados")
	return figura


def grafico_qq(residuos: Sequence[float] | pd.Series | np.ndarray) -> go.Figure:
	"""Construye un gráfico Q-Q normal para los residuos del modelo.

	Args:
		residuos: Residuos del modelo DCA.

	Returns:
		Gráfico Plotly para comparar cuantiles observados y normales teóricos.
	"""
	# Paso 1: probplot ordena residuos y obtiene los cuantiles teóricos normales.
	cuantiles, recta = stats.probplot(np.asarray(residuos, dtype=float), dist="norm")
	cuantiles_teoricos, cuantiles_observados = cuantiles
	pendiente, intercepto, _ = recta
	valores_recta = pendiente * cuantiles_teoricos + intercepto

	# Paso 2: cercanía de puntos a la recta sirve como diagnóstico visual de normalidad.
	figura = go.Figure()
	figura.add_trace(
		go.Scatter(
			x=cuantiles_teoricos,
			y=cuantiles_observados,
			mode="markers",
			name="Residuos observados",
		)
	)
	figura.add_trace(
		go.Scatter(
			x=cuantiles_teoricos,
			y=valores_recta,
			mode="lines",
			name="Referencia normal",
		)
	)
	figura.update_layout(
		title="Gráfico Q-Q de los residuos",
		xaxis_title="Cuantiles teóricos normales",
		yaxis_title="Cuantiles observados de los residuos",
	)
	return figura