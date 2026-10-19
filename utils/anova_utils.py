"""Funciones reutilizables para el análisis de un Diseño Completamente al Azar."""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import IO

import numpy as np
import pandas as pd
from scipy.stats import studentized_range
from statsmodels.formula.api import ols
from statsmodels.regression.linear_model import RegressionResultsWrapper
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def cargar_datos(archivo: str | Path | IO[bytes] | IO[str]) -> pd.DataFrame:
    """Carga datos desde un archivo CSV o un libro de Excel XLSX.

    Args:
        archivo: Ruta o archivo abierto en formato CSV o XLSX.

    Returns:
        DataFrame con los datos leídos.

    Raises:
        ValueError: Si la extensión no corresponde a CSV o XLSX.
    """
    # Paso 1: se identifica la extensión para elegir el lector correspondiente.
    # Regla de lectura: CSV detecta entre coma y punto y coma; XLSX usa read_excel.
    es_ruta = isinstance(archivo, (str, Path))
    nombre_archivo = archivo if es_ruta else getattr(archivo, "name", "")
    extension = Path(str(nombre_archivo)).suffix.lower() if nombre_archivo else ""

    # Paso 2: se deja que pandas detecte el separador CSV o lea el libro Excel.
    if extension == ".csv" or (not es_ruta and not extension):
        return pd.read_csv(archivo, sep=None, engine="python")
    if extension == ".xlsx":
        return pd.read_excel(archivo)

    raise ValueError("Formato no compatible. Usa un archivo CSV o XLSX.")


def validar_dca(df: pd.DataFrame, col_trat: str, col_resp: str) -> list[str]:
    """Valida las columnas y las réplicas requeridas para un DCA.

    Args:
        df: Datos que contienen tratamientos y respuesta.
        col_trat: Nombre de la columna de tratamientos.
        col_resp: Nombre de la columna de respuesta.

    Returns:
        Lista de errores en español; queda vacía si los datos son válidos.
    """
    errores: list[str] = []

    # Paso 1: se confirma que existan las variables que entrarán al modelo.
    columnas_faltantes = [col for col in (col_trat, col_resp) if col not in df.columns]
    if columnas_faltantes:
        return [f"Faltan las columnas requeridas: {', '.join(columnas_faltantes)}."]

    # Paso 2: se detectan datos faltantes en las variables del análisis.
    if df[[col_trat, col_resp]].isna().any().any():
        errores.append("Hay datos faltantes en la columna de tratamientos o respuesta.")

    # Paso 3: la respuesta debe ser numérica para calcular medias y sumas de cuadrados.
    if not pd.api.types.is_numeric_dtype(df[col_resp]):
        errores.append(f"La columna de respuesta '{col_resp}' no es numérica.")

    # Paso 4: k es el número de tratamientos; un DCA necesita k >= 2.
    if df[col_trat].nunique(dropna=True) < 2:
        errores.append("Se requieren al menos 2 tratamientos.")

    # Paso 5: n_i es el número de réplicas del tratamiento i; se requiere n_i >= 2.
    replicas = df.groupby(col_trat, observed=True, dropna=True).size()
    if not replicas.empty and (replicas < 2).any():
        errores.append("Cada tratamiento debe tener al menos 2 réplicas.")

    return errores


def ajustar_dca(
    df: pd.DataFrame, col_trat: str, col_resp: str
) -> RegressionResultsWrapper:
    """Ajusta el modelo de un factor para un Diseño Completamente al Azar.

    Args:
        df: Datos del ensayo.
        col_trat: Nombre de la columna de tratamientos.
        col_resp: Nombre de la columna de respuesta.

    Returns:
        Modelo OLS ajustado.

    Raises:
        ValueError: Si los datos no cumplen las condiciones mínimas del DCA.
    """
    # Paso 1: se detiene el ajuste si la estructura de los datos no es válida.
    errores = validar_dca(df, col_trat, col_resp)
    if errores:
        raise ValueError(" ".join(errores))

    # Paso 2: Q protege nombres con espacios o caracteres especiales.
    # Fórmula: Y_ij = mu + efecto_i + error_ij.
    respuesta = json.dumps(col_resp, ensure_ascii=False)
    tratamiento = json.dumps(col_trat, ensure_ascii=False)
    formula = f"Q({respuesta}) ~ C(Q({tratamiento}))"

    # Paso 3: OLS estima la media general y los efectos de tratamiento.
    return ols(formula, data=df).fit()


def tabla_anova(modelo: RegressionResultsWrapper) -> pd.DataFrame:
    """Calcula la tabla ANOVA tipo II y agrega la fila de variación total.

    Args:
        modelo: Modelo OLS previamente ajustado para un DCA.

    Returns:
        Tabla con las columnas Fuente, gl, SC, CM, F y p-valor.
    """
    # Paso 1: ANOVA tipo II separa la variación de tratamientos y el error.
    anova = anova_lm(modelo, typ=2)
    fila_error = next(indice for indice in anova.index if str(indice) == "Residual")
    fila_tratamientos = next(indice for indice in anova.index if indice != fila_error)

    # Paso 2: se recuperan grados de libertad, sumas de cuadrados y prueba F.
    gl_tratamientos = float(anova.loc[fila_tratamientos, "df"])
    sc_tratamientos = float(anova.loc[fila_tratamientos, "sum_sq"])
    gl_error = float(anova.loc[fila_error, "df"])
    sc_error = float(anova.loc[fila_error, "sum_sq"])

    # Paso 3: CM = SC / gl; la suma total es SCTratamientos + SCError.
    filas = [
        {
            "Fuente": "Tratamientos",
            "gl": gl_tratamientos,
            "SC": sc_tratamientos,
            "F": float(anova.loc[fila_tratamientos, "F"]),
            "p-valor": float(anova.loc[fila_tratamientos, "PR(>F)"]),
        },
        {
            "Fuente": "Error",
            "gl": gl_error,
            "SC": sc_error,
            "F": np.nan,
            "p-valor": np.nan,
        },
        {
            "Fuente": "Total",
            "gl": gl_tratamientos + gl_error,
            "SC": sc_tratamientos + sc_error,
            "F": np.nan,
            "p-valor": np.nan,
        },
    ]
    tabla = pd.DataFrame(filas)
    tabla["CM"] = tabla["SC"] / tabla["gl"]
    return tabla[["Fuente", "gl", "SC", "CM", "F", "p-valor"]]


def resumen_tratamientos(
    df: pd.DataFrame, col_trat: str, col_resp: str
) -> pd.DataFrame:
    """Resume el número de réplicas y la respuesta por tratamiento.

    Args:
        df: Datos del ensayo.
        col_trat: Nombre de la columna de tratamientos.
        col_resp: Nombre de la columna de respuesta.

    Returns:
        DataFrame con n, total, media y desviación estándar por tratamiento.
    """
    # Paso 1: se agrupan observaciones para describir la respuesta de cada tratamiento.
    # Fórmulas: total = sum(y); media = total/n; s = sqrt(sum((y-media)^2)/(n-1)).
    resumen = (
        df.groupby(col_trat, observed=True)[col_resp]
        .agg(
            n="count",
            total="sum",
            media="mean",
            **{"desviación estándar": "std"},
        )
        .reset_index()
    )

    # Paso 2: se conservan los nombres pedidos y se ordenan por tratamiento.
    return resumen[[col_trat, "n", "total", "media", "desviación estándar"]]


def coeficiente_variacion(
    modelo: RegressionResultsWrapper, df: pd.DataFrame, col_resp: str
) -> float:
    """Calcula el coeficiente de variación experimental en porcentaje.

    Args:
        modelo: Modelo OLS previamente ajustado para un DCA.
        df: Datos del ensayo.
        col_resp: Nombre de la columna de respuesta.

    Returns:
        Coeficiente de variación como porcentaje.

    Raises:
        ValueError: Si la media general es cero o no es finita.
    """
    # Paso 1: CME es la media cuadrática del error residual del modelo.
    cme = float(modelo.mse_resid)

    # Paso 2: se calcula la media general observada de la respuesta.
    media_general = float(df[col_resp].mean())
    if not np.isfinite(media_general) or media_general == 0:
        raise ValueError("La media general debe ser finita y distinta de cero.")

    # Paso 3: CV = sqrt(CME) / media general * 100; expresa error relativo.
    return float(np.sqrt(cme) / media_general * 100)


def tukey(
    df: pd.DataFrame, col_trat: str, col_resp: str, alfa: float = 0.05
) -> tuple[pd.DataFrame, float]:
    """Compara medias con Tukey y calcula la diferencia mínima significativa.

    Args:
        df: Datos del ensayo.
        col_trat: Nombre de la columna de tratamientos.
        col_resp: Nombre de la columna de respuesta.
        alfa: Nivel de significancia, entre 0 y 1.

    Returns:
        Tupla con la tabla de comparaciones en español y la DMS.

    Raises:
        ValueError: Si alfa o los datos no son válidos para el DCA.
    """
    # Paso 1: se comprueba alfa y la estructura antes de comparar medias.
    if not 0 < alfa < 1:
        raise ValueError("alfa debe estar entre 0 y 1.")
    errores = validar_dca(df, col_trat, col_resp)
    if errores:
        raise ValueError(" ".join(errores))

    # Paso 2: Tukey compara todas las parejas y ajusta el error familiar.
    resultado = pairwise_tukeyhsd(
        endog=df[col_resp], groups=df[col_trat], alpha=alfa
    )
    tabla_resultado = resultado.summary().data
    comparaciones = pd.DataFrame(tabla_resultado[1:], columns=tabla_resultado[0])
    comparaciones = comparaciones.rename(
        columns={
            "group1": "Tratamiento 1",
            "group2": "Tratamiento 2",
            "meandiff": "Diferencia de medias",
            "p-adj": "p-valor ajustado",
            "lower": "Límite inferior",
            "upper": "Límite superior",
            "reject": "Rechaza H0",
        }
    )
    for columna in (
        "Diferencia de medias",
        "p-valor ajustado",
        "Límite inferior",
        "Límite superior",
    ):
        comparaciones[columna] = pd.to_numeric(comparaciones[columna])
    comparaciones["Rechaza H0"] = comparaciones["Rechaza H0"].map(
        {"True": True, "False": False, True: True, False: False}
    )

    # Paso 3: CME proviene del modelo DCA; glE son los grados de libertad del error.
    modelo = ajustar_dca(df, col_trat, col_resp)
    cme = float(modelo.mse_resid)
    gl_error = float(modelo.df_resid)
    conteos = df.groupby(col_trat, observed=True).size()
    tratamientos = len(conteos)
    balanceado = conteos.nunique() == 1

    # Paso 4: q es el cuantil studentizado; r es n si hay balance, o su media armónica.
    if balanceado:
        replicas = float(conteos.iloc[0])
    else:
        replicas = float(tratamientos / (1 / conteos).sum())
        warnings.warn(
            "El diseño no está balanceado; la DMS calculada es aproximada.",
            UserWarning,
            stacklevel=2,
        )
    cuantil = float(studentized_range.ppf(1 - alfa, tratamientos, gl_error))

    # Paso 5: DMS = q(alfa; k; glE) * sqrt(CME / r).
    dms = cuantil * float(np.sqrt(cme / replicas))
    return comparaciones, float(dms)


def interpretar_dca(tabla: pd.DataFrame, alfa: float = 0.05) -> str:
    """Interpreta la prueba F de tratamientos de una tabla ANOVA.

    Args:
        tabla: Tabla generada por :func:`tabla_anova`.
        alfa: Nivel de significancia, entre 0 y 1.

    Returns:
        Interpretación sencilla de la decisión sobre las medias.

    Raises:
        ValueError: Si alfa no está entre 0 y 1 o falta la fila de tratamientos.
    """
    # Paso 1: alfa define el umbral de evidencia para evaluar H0: todas las medias son iguales.
    if not 0 < alfa < 1:
        raise ValueError("alfa debe estar entre 0 y 1.")
    if not {"Fuente", "p-valor"}.issubset(tabla.columns):
        raise ValueError("La tabla debe contener las columnas Fuente y p-valor.")

    # Paso 2: se compara el p-valor de tratamientos con alfa para decidir sobre H0.
    fila = tabla.loc[tabla["Fuente"] == "Tratamientos", "p-valor"]
    if fila.empty or pd.isna(fila.iloc[0]):
        raise ValueError("La tabla debe incluir un p-valor válido para Tratamientos.")
    p_valor = float(fila.iloc[0])

    # Paso 3: p < alfa indica evidencia de diferencias en al menos una media.
    if p_valor < alfa:
        return (
            "Se rechaza H0: hay evidencia de que no todas las medias de los "
            "tratamientos son iguales. La decisión debe considerar las comparaciones "
            "de medias y la importancia agrícola de las diferencias."
        )
    return (
        "No se rechaza H0: no hay evidencia suficiente para afirmar que las medias "
        "de los tratamientos sean diferentes. Esto no demuestra que sean idénticas."
    )