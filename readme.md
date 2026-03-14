# 📊 Workshift Analytics Pro
Workshift Analytics es una aplicación de escritorio basada en web desarrollada con Python y Streamlit. Está diseñada para profesionales de Operaciones (BizOps) y desarrolladores que necesitan un seguimiento granular de su productividad, permitiendo visualizar la distribución del tiempo entre múltiples proyectos y tareas técnicas.
-----------------------------------
## 🚀 Características Principales
- Registro Inteligente: Interfaz rápida para ingresar horas y minutos dedicados a proyectos específicos.

- Visualización 360°: Dashboard dinámico con 4 tipos de gráficos:

- Sunburst Chart: Análisis jerárquico de Proyecto > Tarea.

- Bar Chart: Comparativa de carga horaria por proyecto.

- Area Chart: Tendencia de intensidad de trabajo diaria.

- Weekly Chart: Productividad acumulada por semana.

- Sistema de Racha (Streak): Gamificación de la productividad mediante el conteo de días consecutivos de actividad.

- Gestión de Datos CRUD: Editor de datos integrado para modificar o eliminar registros de forma masiva.

- Persistencia Robusta: Almacenamiento local mediante SQLite con gestión automática de conexiones.

## 🛠️ Stack Tecnológico

- Lenguaje: Python 3.10+

- Interfaz: Streamlit

- Gráficos: Plotly Express

- Base de Datos: SQLite3

- Procesamiento de Datos: Pandas

## 📋 Requisitos Previos
Asegúrate de tener instaladas las dependencias necesarias:
```
Bash
pip install streamlit pandas plotly
```
💻 Instalación y Uso

Clonar el repositorio:
```
Bash
git clone https://github.com/tu-usuario/workshift-analytics.git
cd workshift-analytics
```

Ejecutar la aplicación:
```
Bash
streamlit run main.py
```
Acceso:
La aplicación se abrirá automáticamente en tu navegador predeterminado en http://localhost:8501.


## 📥 Automatización de Inicio (Windows)
Para facilitar el acceso diario, el proyecto incluye un script de automatización .bat. Esto permite ejecutar la aplicación como si fuera un programa nativo de Windows con un solo clic.

- Configuración del Acceso Directo:
Localiza el archivo run_app.bat en la carpeta raíz del proyecto.

- Haz clic derecho sobre él y selecciona "Enviar a" > "Escritorio (crear acceso directo)".

- (Opcional) Cambia el nombre del acceso directo a "Workshift Analytics" y cámbiale el icono por uno de gráfico de barras en las propiedades.

Cómo funciona el .bat:

- El script realiza las siguientes acciones automáticamente:

- Verifica el entorno de Python.

- Activa las librerías necesarias.

- Lanza el servidor de Streamlit en segundo plano.

- Abre tu navegador predeterminado en la dirección del Dashboard.

## 📖 Cómo funciona el programa
1. Capa de Datos (Persistence Layer)
El programa utiliza una clase controladora llamada WorkshiftManager que encapsula todas las operaciones SQL. Esto garantiza que la lógica de la base de datos esté separada de la interfaz de usuario (siguiendo principios de Clean Architecture).

2. Dashboard y Lógica de Negocio
Cálculo de Horas: El sistema transforma automáticamente los objetos timedelta de Python en valores flotantes de horas para permitir cálculos matemáticos precisos en los gráficos.

Filtros Dinámicos: Al filtrar un proyecto en el sidebar, todos los cálculos de métricas y gráficos se recalculan en tiempo real gracias al estado de sesión de Streamlit.

3. Interfaz de Usuario (UX/UI)
Se ha implementado un diseño Dark Mode personalizado mediante inyección de CSS, optimizando la legibilidad para entornos de desarrollo y reduciendo la fatiga visual.

Desarrollado por Nicolás Andrés Cano Leal LiveOps & BizOps | Python Backend Developer | Data Automation