# HardenDisk v2.0

Diagnóstico, Limpieza y Seguridad del Sistema para Windows

HardenDisk es una **herramienta integral** diseñada para usuarios que buscan optimizar el rendimiento de sus unidades de almacenamiento y reforzar la seguridad de su sistema operativo. Con una interfaz moderna basada en customtkinter, permite realizar mantenimientos profundos con solo un par de clics.

## Características Principales

- Diagnóstico de Salud: Visualiza el estado de tus discos, particiones y uso de memoria en tiempo real.

- Limpieza Profunda: Elimina archivos temporales, caché de navegadores y residuos del sistema que ocupan espacio innecesario.

- Seguridad y Privacidad: Herramientas para verificar la integridad del sistema y gestionar la privacidad.

- Reportes Detallados: Genera informes completos del estado del hardware y software en formato .txt.

- Interfaz Moderna: Diseño gris azulado claro, intuitivo y optimizado para Windows 10/11.

- Ejecución con Privilegios: Integración nativa con UAC para realizar tareas administrativas sin errores.


## Instalación y Uso

### Para Usuarios (Instalador EXE):

1.- Descarga el archivo HardenDisk_Setup.exe.

2.- Ejecuta el instalador y sigue las instrucciones del asistente.

3.- Inicia la aplicación desde el acceso directo del escritorio (requerirá permisos de administrador para funcionar correctamente).


### Para Desarrolladores (Python)

Si prefieres ejecutarlo desde el código fuente, asegúrate de tener Python 3.10+ y sigue estos pasos:

Clonar el repositorio:

´´´bash
git clone [https://github.com/bleonethical/hardendisk.git](https://github.com/bleonethical/hardendisk.git)
cd hardendisk
´´´

Instalar dependencias necesarias:
´´´bash
pip install customtkinter psutil pillow
´´´

Ejecutar la aplicación:
´´´bash
python hardendisk.py
´´´

## Tecnologías Utilizadas

- Python 3.13 - Lenguaje principal.
- customTkinter - Interfaz de usuario moderna con estilo nativo.
- Psutil - Gestión y monitorización de recursos del sistema.
- Pillow (PIL) - Procesamiento de imágenes y renderizado de iconos en la UI.
- Inno Setup - Generación del instalador.

## Licencia

Este proyecto está bajo la Licencia MIT. Esto significa que puedes usar, copiar, modificar y distribuir el software libremente, siempre y cuando se incluya el aviso de copyright original. Consulta el archivo LICENSE.txt para más detalles.

## Descargo de Responsabilidad

HardenDisk realiza tareas de limpieza y modificación de archivos temporales del sistema. Aunque las operaciones han sido probadas para ser seguras, el desarrollador no se hace responsable de la pérdida accidental de datos o desajustes en el sistema. Se recomienda siempre tener un respaldo de su información importante antes de realizar limpiezas profundas.

**Desarrollado con ❤️ para la optimización de Windows.**
