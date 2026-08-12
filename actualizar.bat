@echo off
REM actualizar.bat - Corre el motor y deja el MAESTRO.xlsx en la carpeta compartida.
REM Se ejecuta solo todos los dias. No hay que abrirlo ni tocarlo.
REM Rutas configuradas para la laptop de Sol.
REM Si se instala en otra maquina, ajustar estas dos lineas.

REM ---------------------------------------------------------------------------
REM CONFIGURAR ESTAS DOS LINEAS Y NADA MAS
set PROYECTO=C:\BaseDatos
set DESTINO=G:\Unidades compartidas\Archivos\Internacional
REM ---------------------------------------------------------------------------
set PROYECTO=C:\Users\USUARIA\base-datos-internacional
set DESTINO=C:\Users\USUARIA\OneDrive - CONSULTORA\Internacional
REM ---------------------------------------------------------------------------

set LOG=%PROYECTO%\ultima_corrida.log

echo ===== %date% %time% ===== >> "%LOG%"
cd /d "%PROYECTO%" || (echo ERROR: no existe la carpeta del proyecto >> "%LOG%" & exit /b 1)

python motor.py >> "%LOG%" 2>&1
if errorlevel 1 (echo ERROR: el motor fallo >> "%LOG%" & exit /b 1)

copy /Y "salidas\MAESTRO.xlsx" "%DESTINO%\MAESTRO.xlsx" >> "%LOG%" 2>&1
if errorlevel 1 (
  echo ERROR: no se pudo copiar - revisar que el archivo no este abierto en Excel >> "%LOG%"
) else (
  echo OK: MAESTRO.xlsx actualizado en la carpeta compartida >> "%LOG%"
)
