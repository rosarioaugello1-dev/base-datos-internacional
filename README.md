Cinco preguntas:

¿Qué hace y cuándo? Todos los días a las 9, baja 10 series diarias de FRED, genera el MAESTRO.xlsx y lo deja en la carpeta compartida de Drive.
¿Cómo agrego una serie? Agregar una fila a config_diarias.csv con el código de FRED, y una fórmula nueva en el Excel apuntando a la columna correspondiente.
¿Cómo lo corro a mano? cd C:\BaseDatos y python motor.py.
¿Dónde veo si funcionó? C:\BaseDatos\ultima_corrida.log, y la hoja _METADATOS del maestro (columna dias_de_atraso).
¿Qué quedó pendiente? La tabla de abajo.

5.3 Tabla de pendientes
Grupo: Oro, Plata, Cobre | Esfuerzo : media | Por qué: 	Requieren otra fuente
Grupo: Índices bursátiles (35) | Esfuerzo : Una tarde | Por qué: 	Necesitan un bajador nuevo (Stooq/Yahoo)
Grupo: Soja, Trigo, Maíz, Girasol | Esfuerzo : alta | Por qué: 		Precios de Rosario (Agrofy), sin API: scraper propio
Grupo: Litio | Esfuerzo : alta | Por qué: 	Fuente china, poco estandarizada
Grupo: Merval en USD, CCL, deflactado | Esfuerzo : alta | Por qué: 	No son series: son cálculos. Hay que bajar las series crudas y replicar la fórmula
Grupo: EMBI (67 series) | Esfuerzo : no resuelto | Por qué: 	JP Morgan es propietario. Decisión de negocio: cambiar de indicador o seguir a mano
Grupo: Mensuales y trimestrales | Esfuerzo : Fuera de alcance | Por qué: 	Se acordó priorizar diarias

5.5 Plan de emergencia
Si todo falla, copiar C:\BaseDatos a cualquier máquina con Python, correr python motor.py, y copiar el MAESTRO.xlsx resultante a la carpeta de Drive.



