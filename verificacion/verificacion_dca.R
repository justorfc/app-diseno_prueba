# Verificación del Diseño Completamente al Azar para la humedad de yuca.
# Cada paso explica a estudiantes de Ingeniería Agrícola qué se calcula y por qué.
datos <- read.csv("../data/dca_mi_variante.csv", stringsAsFactors = FALSE) # Se leen los datos de humedad y secador para analizar las observaciones del ensayo.
# El factor identifica las categorías de secador y permite comparar sus medias.
modelo <- aov(humedad ~ factor(secador), data = datos) # Se ajusta un ANOVA de un factor para evaluar si la humedad media difiere entre secadores.
print(summary(modelo)) # Se imprime el resumen del ANOVA para revisar la variación explicada por los secadores frente al error experimental.
medias <- aggregate(humedad ~ secador, data = datos, FUN = mean) # Se calcula la humedad promedio de cada secador para describir su respuesta.
print(medias) # Se muestran las medias para facilitar la comparación descriptiva entre secadores.
cm_error <- deviance(modelo) / df.residual(modelo) # Se calcula el cuadrado medio del error: variación residual dividida entre sus grados de libertad.
media_general <- mean(datos$humedad) # Se calcula la media general como referencia para expresar el error en relación con la respuesta observada.
cv <- sqrt(cm_error) / media_general * 100 # Se expresa la desviación residual relativa a la media general como porcentaje de variabilidad experimental.
cat("Coeficiente de variación:", round(cv, 2), "%\n") # Se informa el CV para valorar la magnitud relativa del error del ensayo.
print(TukeyHSD(modelo)) # Se comparan todas las parejas de medias y se ajusta por comparaciones múltiples para identificar diferencias.
