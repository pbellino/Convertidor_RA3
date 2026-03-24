# Convertidor RA-3

**Convertidor de datos binarios del reactor RA-3 a formato CSV.**

Esta herramienta permite procesar los archivos de salida del sistema de adquisición de datos del reactor RA-3, facilitando el análisis posterior en herramientas como Excel o MATLAB.

## Características
* **Portabilidad:** Ejecutables independientes para Windows y Linux (no requieren instalación de Python).
* **Simplicidad:** Conversión directa de binario SEAD a CSV.
* **Núcleo técnico:** Basado en la librería [CinePy](https://github.com/pbellino/CinePy/blob/7c11fd509e4d9918b5a9ab1fa9f9622612437839/modules/io_sead.py#L76)

##  Descarga y Uso (Usuarios)
No es necesario configurar un entorno de desarrollo para usar la herramienta:

1. Ir a la sección de [Releases](https://github.com/pbellino/Convertidor_RA3/releases).
2. Descargar el ejecutable correspondiente a tu sistema operativo (`.exe` para Windows o binario para Linux).
3. Ejecutar el programa desde la terminal o consola de comandos para procesar tus archivos.

---

##  Configuración para Desarrollo
Si deseas modificar el código o integrarlo en otros scripts, sigue estos pasos:

### 1. Requisitos previos
* Python 3.x instalado.
* Git (para clonar el repositorio).

### 2. Instalación
```bash
# Clonar el repositorio
git clone https://github.com/pbellino/Convertidor_RA3.git
cd Convertidor_RA3

# Configurar entorno virtual
python3 -m venv venv

# Activar entorno
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```
