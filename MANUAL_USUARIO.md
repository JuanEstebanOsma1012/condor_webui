# Manual de Usuario - HTCondor Web UI

## Índice

1. [Introducción](#introducción)
2. [Características Principales](#características-principales)
3. [Requisitos del Sistema](#requisitos-del-sistema)
4. [Instalación y Configuración](#instalación-y-configuración)
5. [Interfaz de Usuario](#interfaz-de-usuario)
6. [Modos de Envío de Trabajos](#modos-de-envío-de-trabajos)
7. [Tipos de Ejecución](#tipos-de-ejecución)
8. [Gestión de Clústeres](#gestión-de-clústeres)
9. [Visualización de Resultados](#visualización-de-resultados)
10. [API y Endpoints](#api-y-endpoints)
11. [Solución de Problemas](#solución-de-problemas)
12. [Ejemplos Prácticos](#ejemplos-prácticos)

---

## Introducción

**Grid App** es una aplicación web desarrollada en Flask que proporciona una interfaz gráfica intuitiva para la gestión y ejecución de trabajos computacionales en infraestructuras HTCondor distribuidas. La aplicación facilita el envío, monitoreo y análisis de resultados de trabajos tanto en entornos Vanilla como Parallel.

### Propósito

Esta aplicación está diseñada para:
- Simplificar el uso de HTCondor mediante una interfaz web amigable
- Permitir la ejecución de trabajos distribuidos y paralelos
- Facilitar la gestión de múltiples clústeres de forma centralizada
- Ofrecer visualización organizada de resultados de ejecución

---

## Características Principales

### ✨ **Funcionalidades Core**

- **Interfaz Web Responsiva**: Diseño moderno y adaptable a diferentes dispositivos
- **Soporte Multi-Universo**: Vanilla Grid y Parallel
- **Gestión Dinámica de Clústeres**: Detección automática y monitoreo de recursos
- **Ejecución Parametrizable**: Variables dinámicas en argumentos de ejecución
- **Monitoreo en Tiempo Real**: Estado de trabajos y progreso de ejecución
- **Visualización de Resultados**: Grid dinámico con previsualización de salidas

### 🎯 **Casos de Uso Soportados**

1. **Ejecución Distribuida con Parámetros Iguales (ESC-01)**
   - Múltiples ejecuciones con argumentos idénticos
   - Ideal para análisis estadísticos y validación de resultados

2. **Ejecución Distribuida con Parámetros Variables (ESC-02)**
   - Ejecuciones con variables parametrizables
   - Perfecto para barridos paramétricos y optimización

3. **Ejecución Paralela (ESC-03)**
   - Trabajos MPI multi-nodo
   - Adecuado para simulaciones de alta performance computing

---

## Requisitos del Sistema

### **Servidor (Backend)**
- **Sistema Operativo**: Linux (Ubuntu 18.04+ recomendado)
- **Python**: 3.6 o superior
- **HTCondor**: 8.8 o superior configurado y funcionando
- **Dependencias Python**:
  ```bash
  Flask>=2.0.0
  ```

### **Cliente (Frontend)**
- **Navegador Web**: Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **JavaScript**: Habilitado
- **Conexión de Red**: Acceso HTTP al servidor Flask

### **Infraestructura HTCondor**
- **Central Manager**: Configurado y accesible
- **Submit Nodes**: Al menos un nodo de envío configurado
- **Execute Nodes**: Nodos de ejecución disponibles
- **Networking**: Conectividad entre todos los componentes

---

## Instalación y Configuración

### **1. Preparación del Entorno**

```bash
# Clonar el repositorio
git clone https://github.com/JuanEstebanOsma1012/condor_webui.git
cd condor_webui

# Crear entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### **2. Configuración de HTCondor**

Asegúrese de que HTCondor esté correctamente instalado y configurado:

```bash
# Verificar estado de HTCondor
condor_status
condor_q

# Verificar configuración
condor_config_val SCHEDD_NAME
condor_config_val COLLECTOR_HOST
```

### **3. Configuración de la Aplicación**

Editar `app.py` para ajustar las rutas según su entorno:

```python
# Configurar ruta del proyecto
DEFAULT_PROJECT_FOLDER = '/ruta/a/su/proyecto/'

# Configurar inventario de clústeres en static/script.js
INVENTORY = ["IP_CLUSTER_1", "IP_CLUSTER_2", "IP_CLUSTER_3"];
DEFAULT_PORT = "44444";
```

### **4. Estructura de Directorios**

La aplicación creará automáticamente la siguiente estructura:

```
proyecto/
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias
├── templates/            # Plantillas HTML
│   ├── upload.html       # Página principal
│   └── results.html      # Página de resultados
├── static/              # Recursos estáticos
│   ├── styles.css       # Estilos principales
│   ├── results.css      # Estilos de resultados
│   └── script.js        # Lógica frontend
├── submits/             # Directorio de trabajos (auto-creado)
├── scripts/             # Scripts auxiliares
└── test/                # Suite de pruebas automatizadas
```

### **5. Ejecución de la Aplicación**

```bash
# Modo desarrollo
python app.py

# Modo producción (con Gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

La aplicación estará disponible en: `http://localhost:5000`

---

## Interfaz de Usuario

### **Página Principal (`/`)**

La interfaz principal presenta dos pestañas principales:

#### **🎛️ Pestaña "Guiado"**
Modo asistido para usuarios que prefieren una interfaz paso a paso:

- **Subir Binario**: Selector de archivo para el ejecutable
- **Argumentos Adicionales**: Campo de texto para parámetros de ejecución
- **Naturaleza del Trabajo**: Selección entre Vanilla y Parallel
- **Opciones de Distribución**: Configuración específica según el tipo
- **Selección de Clúster**: Dropdown dinámico con métricas en tiempo real

#### **⚙️ Pestaña "Personalizado"**
Modo avanzado para usuarios experimentados:

- **Subir Binario**: Archivo ejecutable
- **Subir Submit File**: Archivo `.sub` personalizado de HTCondor
- **Selección de Clúster**: Clúster de destino

### **Elementos de UI Dinámicos**

#### **Indicadores de Clúster**
```
IP_CLUSTER: {slots: X; éxito: Y; cola: Z}
```
- **slots**: Núcleos disponibles
- **éxito**: Trabajos completados exitosamente
- **cola**: Trabajos en espera

#### **Variables Parametrizables**
El sistema detecta automáticamente variables en formato `<VARIABLE>` en los argumentos:

```
Ejemplo: "programa <PARAM1> --iterations <PARAM2>"
```

---

## Modos de Envío de Trabajos

### **🎯 Modo Guiado**

Proceso paso a paso para envío asistido:

1. **Selección de Archivo Binario**
   - Formatos soportados: Ejecutables Linux (ELF), Scripts (.sh, .py, etc.)
   - El archivo se hace ejecutable automáticamente (chmod +x)

2. **Configuración de Argumentos**
   - Texto libre con soporte para variables especiales
   - Detección automática de patrones `<VARIABLE>`

3. **Selección de Tipo de Trabajo**
   - **Vanilla**: Para trabajos distribuidos independientes
   - **Parallel**: Para trabajos MPI que requieren comunicación entre nodos

4. **Configuración Específica por Tipo**
   - Ver secciones detalladas por tipo de ejecución

5. **Selección de Clúster**
   - Lista dinámica actualizada cada 10 segundos
   - Métricas en tiempo real para decisión informada

### **⚙️ Modo Personalizado**

Para usuarios avanzados que prefieren control total:

1. **Subir Ejecutable y Submit File**
   - Submit file debe seguir sintaxis estándar de HTCondor
   - Soporte completo para directivas HTCondor avanzadas

2. **Selección de Clúster**
   - Mismo sistema dinámico que modo guiado

---

## Tipos de Ejecución

### **🌐 Vanilla Grid Universe**

Ideal para trabajos independientes distribuidos en múltiples nodos.

#### **Configuración Automática Generada:**
```bash
universe = grid
remote_universe = vanilla  
grid_resource = condor CLUSTER_IP:PORT
executable = nombre_ejecutable
output = job_$(Process).out
error = job_$(Process).err
log = job.log
transfer_executable = YES
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
requirements = (Arch == "armv7l")
```

#### **Modos de Distribución:**

##### **📊 Repeticiones Iguales**
- **Propósito**: Ejecutar el mismo comando N veces
- **Configuración**: Número de repeticiones (1-1000)
- **Submit File Generado**:
  ```bash
  arguments = argumentos_especificados
  queue N  # Donde N = número de repeticiones
  ```
- **Casos de Uso**: Análisis Monte Carlo, validación estadística

##### **📈 Variables Parametrizables**
- **Propósito**: Ejecutar con diferentes valores de parámetros
- **Configuración**: Variable, valor inicial, final e incremento
- **Submit File Generado**:
  ```bash
  arguments = arg1 1 arg2
  queue 1
  arguments = arg1 3 arg2  
  queue 1
  arguments = arg1 5 arg2
  queue 1
  # ... etc
  ```
- **Casos de Uso**: Barridos paramétricos, optimización

### **⚡ Parallel Universe**

Para trabajos que requieren comunicación entre procesos (MPI).

#### **Configuración Requerida:**
- **Máquinas Requeridas**: Número de nodos
- **Núcleos por Máquina**: CPUs por nodo
- **Archivo de Entrada**: Datos de entrada (opcional)

#### **Submit File Generado:**
```bash
universe = parallel
executable = /usr/share/doc/condor/examples/openmpiscript
arguments = ejecutable archivo_entrada argumentos_adicionales
machine_count = N_MAQUINAS
request_cpus = N_CPUS
should_transfer_files = yes
when_to_transfer_output = ON_EXIT_OR_EVICT
transfer_input_files = ejecutable,archivo_entrada
log = job.log
output = job_$(NODE).out
error = job_$(NODE).err
+ParallelShutdownPolicy = "WAIT_FOR_NODE0"
environment = "PATH=/usr/lib64/openmpi/bin:$PATH;LD_LIBRARY_PATH=/usr/lib64/openmpi/lib:$LD_LIBRARY_PATH"
queue
```

---

## Gestión de Clústeres

### **🔄 Detección Automática**

La aplicación consulta automáticamente los clústeres configurados en el inventario:

```javascript
// Configuración en static/script.js
INVENTORY = ["172.30.27.35", "172.30.27.67", "172.30.28.31"];
DEFAULT_PORT = "44444";
```

### **📊 Métricas en Tiempo Real**

Para cada clúster disponible, se muestra:

- **Slots Disponibles**: Núcleos de procesamiento libres
- **Trabajos Exitosos**: Contador de trabajos completados
- **Cola de Trabajos**: Trabajos pendientes de ejecución

### **🔄 Actualización Automática**

- **Frecuencia**: Cada 10 segundos
- **Timeout**: 5 segundos por clúster
- **Fallback**: Clústeres no disponibles se omiten silenciosamente

---

## Visualización de Resultados

### **📊 Página de Resultados (`/results/<job_id>`)**

Después del envío exitoso, se redirige automáticamente a la página de resultados.

#### **Información del Trabajo**
- **ID del Trabajo**: Identificador único de 8 caracteres
- **ID del Clúster**: Número de clúster asignado por HTCondor
- **Tipo de Trabajo**: vanilla, parallel o custom
- **Ejecutable**: Nombre del archivo binario

#### **Estados de Trabajo**
```
- Idle: En cola esperando recursos
- Running: Ejecutándose activamente  
- Completed: Finalizado exitosamente
- Held: Suspendido (requiere intervención)
- Removed: Cancelado o eliminado
- Mixed: Múltiples trabajos en diferentes estados
```

#### **Grid de Resultados**

##### **Para Trabajos Vanilla:**
- Una tarjeta por cada ejecución (`job_0.out`, `job_1.out`, etc.)
- Previsualización del contenido de cada archivo
- Botón "Ver Completo" para vista modal

##### **Para Trabajos Parallel:**
- Una tarjeta principal (`job_0.out`)
- Salida consolidada de todos los nodos

### **⚡ Actualización en Tiempo Real**

- **Auto-refresh**: Cada 30 segundos
- **Botón Manual**: "Actualizar Estado" para refresh inmediato
- **Indicadores Visuales**: Colores según estado del trabajo

### **📁 Acceso a Archivos**

#### **Endpoint para Contenido**: `/output/<job_id>/<filename>`
- **Formato**: Texto plano
- **Encoding**: UTF-8 con manejo de errores
- **Streaming**: Para archivos grandes

---

## API y Endpoints

### **📡 Endpoints Principales**

#### **`GET /`**
- **Propósito**: Página principal de la aplicación
- **Respuesta**: HTML con interfaz de envío

#### **`POST /submit`**
- **Propósito**: Envío de trabajos
- **Content-Type**: `multipart/form-data`
- **Parámetros**:
  ```json
  {
    "binary-file": "archivo_ejecutable",
    "submit-file": "archivo_submit_opcional", 
    "input-file": "archivo_entrada_opcional",
    "config": "json_configuracion"
  }
  ```
- **Respuesta Exitosa**:
  ```json
  {
    "success": true,
    "job_id": "abc12345",
    "cluster_id": "12345",
    "message": "Trabajo enviado exitosamente"
  }
  ```
- **Respuesta Error**:
  ```json
  {
    "error": "Descripción del error"
  }
  ```

#### **`GET /results/<job_id>`**
- **Propósito**: Página de visualización de resultados
- **Respuesta**: HTML con grid dinámico de resultados

#### **`GET /output/<job_id>/<filename>`**
- **Propósito**: Obtener contenido de archivo de salida
- **Respuesta**: Texto plano con contenido del archivo

#### **`GET /job_status/<job_id>`**
- **Propósito**: Estado actual del trabajo
- **Respuesta**:
  ```json
  {
    "job_id": "abc12345",
    "cluster_id": "12345", 
    "statuses": ["Running", "Completed"],
    "overall_status": "Mixed"
  }
  ```

### **🔧 Estructura de Configuración JSON**

#### **Trabajo Vanilla con Repeticiones Iguales:**
```json
{
  "jobType": "vanilla",
  "vanillaMode": "equal", 
  "additionalArgs": "arg1 arg2 --param value",
  "equalOptions": {
    "repetitions": 5
  },
  "cluster": "172.30.27.35:44444"
}
```

#### **Trabajo Vanilla con Variables:**
```json
{
  "jobType": "vanilla",
  "vanillaMode": "range",
  "additionalArgs": "programa <PARAM1> --iterations <PARAM2>",
  "rangeOptions": {
    "allVariables": {
      "<PARAM1>": {
        "start": 1,
        "end": 10, 
        "increment": 2
      },
      "<PARAM2>": {
        "start": 100,
        "end": 1000,
        "increment": 100
      }
    }
  },
  "cluster": "172.30.27.35:44444"
}
```

#### **Trabajo Parallel:**
```json
{
  "jobType": "parallel",
  "additionalArgs": "--verbose --output-format csv",
  "parallelOptions": {
    "machinesCount": 4,
    "coresPerMachine": 8  
  },
  "cluster": "172.30.27.35:44444"
}
```

---

## Solución de Problemas

### **🚨 Problemas Comunes**

#### **Error: "Server not ready"**
- **Causa**: Aplicación Flask no está ejecutándose
- **Solución**: 
  ```bash
  cd /ruta/proyecto
  python app.py
  ```

#### **Error: "ChromeDriver not found" (Solo testing)**
- **Causa**: ChromeDriver no instalado para pruebas automatizadas
- **Solución**:
  ```bash
  sudo apt-get install chromium-chromedriver
  ```

#### **Error: "Error en condor_submit"**
- **Causa**: HTCondor no configurado correctamente
- **Diagnóstico**:
  ```bash
  condor_status
  condor_q
  condor_config_val SCHEDD_NAME
  ```

#### **Clústeres no aparecen en dropdown**
- **Causa**: IPs en `INVENTORY` no accesibles o puerto bloqueado
- **Diagnóstico**:
  ```bash
  # Verificar conectividad
  telnet IP_CLUSTER 44444
  
  # Verificar firewall
  sudo ufw status
  ```

#### **Archivos de salida no aparecen**
- **Causa**: Trabajos aún ejecutándose o falló transferencia
- **Diagnóstico**:
  ```bash
  condor_q CLUSTER_ID
  condor_history CLUSTER_ID
  ls submits/JOB_ID/
  ```

### **🔍 Debug y Logs**

#### **Logs de Aplicación**
```bash
# Ejecutar en modo debug
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

#### **Logs de HTCondor**
```bash
# Logs del Schedd
tail -f /var/log/condor/SchedLog

# Logs del Startd  
tail -f /var/log/condor/StartLog

# Estado detallado de trabajos
condor_q -better-analyze CLUSTER_ID
```

#### **Estructura de Archivos de Trabajo**
```
submits/abc12345/
├── job.sub              # Submit file generado
├── config.json          # Configuración original
├── job_info.json        # Información del trabajo
├── ejecutable           # Binario subido
├── job.log             # Log de HTCondor
├── job_0.out           # Salida estándar trabajo 0
├── job_0.err           # Salida error trabajo 0
└── ...                 # Más archivos según número de jobs
```

---

## Ejemplos Prácticos

### **📊 Ejemplo 1: Monte Carlo con Repeticiones Iguales**

#### **Objetivo**: Ejecutar simulación Monte Carlo 1000 veces

#### **Ejecutable** (`monte_carlo.py`):
```python
#!/usr/bin/env python3
import random
import sys

def monte_carlo_pi(n_samples):
    inside_circle = 0
    for _ in range(n_samples):
        x, y = random.random(), random.random()
        if x*x + y*y <= 1:
            inside_circle += 1
    return 4 * inside_circle / n_samples

if __name__ == "__main__":
    samples = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    pi_estimate = monte_carlo_pi(samples)
    print(f"Pi estimate: {pi_estimate}")
```

#### **Configuración Web**:
1. **Subir binario**: `monte_carlo.py`
2. **Argumentos**: `100000`
3. **Tipo**: Vanilla
4. **Modo**: Repeticiones iguales  
5. **Repeticiones**: 1000
6. **Clúster**: Seleccionar más favorable

#### **Resultado Esperado**: 1000 archivos `job_X.out` con estimaciones de π

### **📈 Ejemplo 2: Barrido Paramétrico**

#### **Objetivo**: Analizar convergencia con diferentes números de muestras

#### **Ejecutable** (`convergence_test.py`):
```python
#!/usr/bin/env python3
import sys
import time

def simulate(n_iterations, step_size):
    # Simulación que depende de parámetros
    result = 0
    for i in range(n_iterations):
        result += step_size * (i % 100)
    return result / n_iterations

if __name__ == "__main__":
    n_iter = int(sys.argv[1])
    step = float(sys.argv[2])
    
    start = time.time()
    result = simulate(n_iter, step)
    duration = time.time() - start
    
    print(f"Iterations: {n_iter}, Step: {step}")
    print(f"Result: {result:.6f}")
    print(f"Duration: {duration:.3f}s")
```

#### **Configuración Web**:
1. **Argumentos**: `<ITERATIONS> <STEP_SIZE>`
2. **Variable 1**: `<ITERATIONS>`
   - Inicial: 1000, Final: 10000, Incremento: 1000
3. **Variable 2**: `<STEP_SIZE>`  
   - Inicial: 0.1, Final: 1.0, Incremento: 0.1

#### **Resultado**: 100 trabajos (10 × 10) con todas las combinaciones

### **⚡ Ejemplo 3: Simulación MPI Paralela**

#### **Objetivo**: Simulación distribuida que requiere comunicación entre nodos

#### **Ejecutable** (`mpi_simulation.py`):
```python
#!/usr/bin/env python3
from mpi4py import MPI
import numpy as np
import sys

def parallel_computation(data_file, comm):
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    if rank == 0:
        # Proceso maestro
        with open(data_file, 'r') as f:
            data = [float(line.strip()) for line in f]
        
        # Distribuir datos
        chunk_size = len(data) // size
        chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
    else:
        chunks = None
    
    # Scatter data
    local_data = comm.scatter(chunks, root=0)
    
    # Proceso local
    local_result = sum(x**2 for x in local_data) if local_data else 0
    
    # Gather results  
    results = comm.gather(local_result, root=0)
    
    if rank == 0:
        total = sum(results)
        print(f"Total sum of squares: {total}")
        print(f"Processed by {size} processes")

if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    data_file = sys.argv[1] if len(sys.argv) > 1 else "input.dat"
    parallel_computation(data_file, comm)
```

#### **Archivo de Entrada** (`input.dat`):
```
1.5
2.3
4.7
8.1
# ... más datos
```

#### **Configuración Web**:
1. **Tipo**: Parallel
2. **Archivo entrada**: `input.dat`
3. **Máquinas**: 4
4. **Núcleos por máquina**: 2
5. **Argumentos**: `--verbose`

---

## Seguridad y Consideraciones

### **🔒 Aspectos de Seguridad**

#### **Validación de Archivos**
- Los archivos binarios se validan antes de la ejecución
- Solo se permiten tipos de archivo seguros
- Límites de tamaño configurables

#### **Aislamiento de Trabajos**
- Cada trabajo se ejecuta en directorio separado
- IDs únicos previenen colisiones
- Cleanup automático de archivos temporales

#### **Acceso a Resultados**
- Acceso restringido por ID de trabajo
- No listado de directorios permitido
- Sanitización de nombres de archivo

### **⚡ Optimización y Performance**

#### **Gestión de Recursos**
- Monitoreo dinámico de clústeres
- Selección inteligente de recursos
- Balanceo automático de carga

#### **Escalabilidad**
- Soporte para miles de trabajos concurrentes
- Gestión eficiente de memoria
- Streaming de archivos grandes

---

## Mantenimiento y Administración

### **🔧 Tareas de Mantenimiento Regulares**

#### **Limpieza de Archivos**
```bash
# Limpieza manual de trabajos antiguos
find submits/ -type d -mtime +30 -exec rm -rf {} \;

# Script automatizado (recomendado)
cat > cleanup.sh << 'EOF'
#!/bin/bash
SUBMIT_DIR="/ruta/proyecto/submits"
RETENTION_DAYS=30

find "$SUBMIT_DIR" -maxdepth 1 -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \;
echo "Cleaned jobs older than $RETENTION_DAYS days"
EOF

# Agregar a crontab
echo "0 2 * * * /ruta/cleanup.sh" | crontab -
```

#### **Monitoreo de Logs**
```bash
# Rotación de logs
logrotate /etc/logrotate.d/htcondor-webui

# Monitoreo de espacio en disco  
df -h /ruta/proyecto/submits/
```

### **📊 Métricas y Monitoreo**

#### **Estadísticas de Uso**
```bash
# Número de trabajos por día
find submits/ -name "job_info.json" -newermt "yesterday" | wc -l

# Trabajos por tipo
grep -r '"jobType"' submits/*/config.json | sort | uniq -c

# Tasa de éxito
grep -r '"cluster_id"' submits/*/job_info.json | wc -l
```

---

## Soporte y Recursos Adicionales

### **📚 Documentación Relacionada**
- [HTCondor Manual Oficial](https://htcondor.readthedocs.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Selenium Testing Guide](https://selenium-python.readthedocs.io/)

### **🐛 Reporte de Problemas**
Para reportar errores o solicitar nuevas características:
- **Repository**: [GitHub - condor_webui](https://github.com/JuanEstebanOsma1012/condor_webui)
- **Issues**: Utilizar las plantillas proporcionadas
- **Logs**: Incluir logs relevantes y configuración del entorno

### **🤝 Contribuciones**
Las contribuciones son bienvenidas siguiendo las pautas del proyecto:
1. Fork del repositorio
2. Crear rama para la característica
3. Incluir pruebas automatizadas  
4. Documentar cambios
5. Enviar Pull Request

---

## Apéndices

### **A. Configuración Avanzada de HTCondor**

#### **Submit Node Configuration** (`/etc/condor/config.d/submit.config`):
```bash
# Configuración básica submit node
DAEMON_LIST = MASTER, SCHEDD
FILESYSTEM_DOMAIN = $(FULL_HOSTNAME)
UID_DOMAIN = $(FULL_HOSTNAME)

# Seguridad
SEC_PASSWORD_FILE = /etc/condor/pool_password
SEC_DEFAULT_AUTHENTICATION = REQUIRED
SEC_DEFAULT_AUTHENTICATION_METHODS = PASSWORD
SEC_DEFAULT_INTEGRITY = REQUIRED
SEC_DEFAULT_ENCRYPTION = OPTIONAL

# Grid Universe
GRIDMANAGER_DEBUG = D_FULLDEBUG
ENABLE_GRID_MONITOR = TRUE
```

### **B. Scripts Auxiliares**

#### **Script de Monitoreo** (`monitor_clusters.sh`):
```bash
#!/bin/bash
# Monitoreo de estado de clústeres

CLUSTERS=("172.30.27.35" "172.30.27.67" "172.30.28.31")
PORT="44444"

for cluster in "${CLUSTERS[@]}"; do
    echo "=== Checking $cluster ==="
    
    # Test connectivity
    if timeout 5 bash -c "</dev/tcp/$cluster/$PORT"; then
        echo "✓ $cluster:$PORT is reachable"
        
        # Get cluster info
        curl -s --max-time 5 "http://$cluster:$PORT" | jq . || echo "Invalid JSON response"
    else
        echo "✗ $cluster:$PORT is not reachable"
    fi
    echo
done
```

---

**© 2025 HTCondor Web UI - Manual de Usuario v1.0**

*Este manual cubre la funcionalidad completa de la aplicación HTCondor Web UI. Para actualizaciones y versiones más recientes, consulte el repositorio oficial del proyecto.*
