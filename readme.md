# 📊 Workshift Analytics Pro

Aplicación de escritorio basada en web desarrollada con Python y Streamlit. Diseñada para profesionales de Operaciones (BizOps) y desarrolladores que necesitan seguimiento granular de productividad, permitiendo visualizar la distribución del tiempo entre múltiples proyectos y tareas.

---

## 🚀 Características

**Registro inteligente**
- Selectbox con autocompletado: proyectos y tareas se sugieren desde el historial existente.
- Las tareas se filtran automáticamente según el proyecto seleccionado.
- Opción "➕ Nuevo..." para crear proyectos y tareas nuevas sin salir del flujo.

**Dashboard de métricas (6 indicadores)**
- Tareas Totales · Proyectos Activos · Horas Acumuladas · Racha Actual
- Promedio Diario · Promedio Semanal

**Visualización 360° (6 gráficos)**
- Sunburst: jerarquía Proyecto → Tarea
- Bar horizontal: esfuerzo acumulado por proyecto
- Area: intensidad de trabajo diaria
- Bar: productividad semanal
- Bar por día de la semana: patrón de actividad Lun–Dom
- Línea acumulada: progreso total de horas a lo largo del tiempo

**Gestión de datos**
- Editor de tabla con eliminación masiva por checkbox.
- Filtro global por proyecto que afecta todas las métricas y gráficos en tiempo real.

**Tema adaptativo**
- Soporta dark y light mode nativo de Streamlit. Cambiable desde `≡ → Settings`.

---

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.10+ |
| Interfaz | Streamlit 1.55 |
| Gráficos | Plotly Express |
| Base de datos | SQLite3 |
| Procesamiento | Pandas |
| Assets | Pillow |

---

## 💻 Instalación y uso

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/workshift-analytics.git
cd workshift-analytics

# Crear entorno virtual e instalar dependencias
python -m venv env
env\Scripts\activate
pip install -r requirements.txt

# Ejecutar
streamlit run app.py
```

La app se abre automáticamente en `http://localhost:8501`.

**Inicio rápido en Windows:** doble clic en `run_app.bat` — activa el entorno e inicia Streamlit en un solo paso. Se puede crear un acceso directo en el escritorio apuntando al `.bat`.

---

## 📖 Arquitectura

**Data Layer — `WorkshiftManager`**
Clase que encapsula todas las operaciones SQLite. `Duracion` se guarda como string de `timedelta`; la columna `Horas` (float) se deriva al cargar y no se persiste en la DB.

**Caché**
- `@st.cache_resource`: instancia singleton del manager.
- `@st.cache_data(ttl=30)`: datos del DataFrame. Se invalida con `load_data.clear()` tras cada escritura o borrado.

**Migración de esquema**
`import.py` es un script puntual para reconstruir la tabla `Registro` si el esquema cambió. Ejecutar manualmente solo cuando sea necesario.

---

## 📥 Automatización de inicio (Windows)

1. Localizar `run_app.bat` en la raíz del proyecto.
2. Clic derecho → "Enviar a" → "Escritorio (crear acceso directo)".
3. (Opcional) Renombrar el acceso directo y cambiar el ícono en Propiedades.

---

Desarrollado por **Nicolás Andrés Cano Leal** · LiveOps & BizOps | Python Backend Developer | Data Automation
