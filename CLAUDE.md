# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos esenciales

```bash
# Activar entorno virtual (siempre hacerlo primero)
env\Scripts\activate

# Ejecutar la aplicación
streamlit run app.py

# Ejecutar migración de base de datos (solo si hay cambios de esquema)
python import.py

# Instalar dependencias
pip install -r requirements.txt
```

En Windows también se puede usar `run_app.bat` para activar el entorno e iniciar Streamlit en un solo paso.

## Arquitectura

La aplicación es un único archivo `app.py` con tres responsabilidades bien delimitadas:

**Data Layer — `WorkshiftManager`**
Clase que encapsula todas las operaciones SQLite. La tabla `Registro` tiene columnas: `id`, `Fecha` (TEXT), `Proyecto` (TEXT), `Tarea` (TEXT), `Duracion` (TEXT). `Duracion` se persiste como string de `timedelta` y se convierte en `load_all()` a `pd.Timedelta` y luego a `Horas` (float). `Horas` no se guarda en la DB, se recalcula en cada carga. `Duracion` está oculta en la UI pero es la fuente de verdad; eliminarla de la DB rompería todas las métricas.

**Caché de Streamlit**
- `get_manager()` → `@st.cache_resource`: instancia singleton de `WorkshiftManager`.
- `load_data()` → `@st.cache_data(ttl=30)`: carga el DataFrame. Después de cualquier escritura o borrado se debe llamar `load_data.clear()` seguido de `st.rerun()`.

**Reset de widgets post-guardado**
No se puede modificar `st.session_state` de un widget después de renderizarlo. El patrón usado es un flag `_reset_duracion`: se activa en `True` al guardar, y al inicio del siguiente rerun (antes de renderizar widgets) se aplica el reset y se desactiva.

**UI — Sidebar**
- Logo + título + caption de tema.
- Registro de actividad: `selectbox` de Proyecto (proyectos existentes + "➕ Nuevo proyecto..."), `selectbox` de Tarea filtrado por proyecto seleccionado (tareas usadas en ese proyecto + "➕ Nueva tarea..."). Si se elige "nuevo", aparece un `text_input`. Duración en columnas Horas/Minutos.
- Filtro multiselect por proyecto (aparece solo cuando hay datos).

**UI — Dashboard (tab 1)**
6 métricas: Tareas Totales, Proyectos Activos, Horas Acumuladas, Racha Actual, Promedio Diario, Promedio Semanal.
- Racha usa `df_master` (sin filtro) para no romperse al filtrar proyectos.
- Promedio Semanal usa `strftime("%G-%V")` para identificar semanas únicas por año ISO, evitando colisiones entre años.

6 gráficos en 3 filas × 2 columnas:
| Fila | Izquierda | Derecha |
|---|---|---|
| 1 | Sunburst Proyecto/Tarea | Esfuerzo por Proyecto (bar h) |
| 2 | Intensidad Diaria (area) | Productividad Semanal (bar) |
| 3 | Actividad por Día de la Semana (bar) | Progreso Acumulado (line) |

**UI — Gestión de Registros (tab 2)**
`st.data_editor` con checkbox de eliminación masiva. Columnas `id` y `Duracion` ocultas con `None` en `column_config`.

El template de Plotly se adapta al tema activo de Streamlit mediante `st.context.theme.base` (`plotly_dark` / `plotly_white`). El archivo `.streamlit/config.toml` está vacío para que Streamlit use sus colores de fábrica y el toggle dark/light funcione libremente.

## Archivos de base de datos

| Archivo | Propósito |
|---|---|
| `workshift.db` | Base de datos principal (producción) |
| `base_test.db`, `mi_base.db`, `workshift_top.db` | Bases de datos de prueba/desarrollo |

`import.py` es un script de migración puntual para limpiar el esquema de `workshift.db`; no forma parte del flujo normal de la app.

## Assets requeridos

`image/logo_nc.ico` y `image/logo_nc.jpg` deben existir en el directorio `image/` antes de iniciar la app — se cargan con Pillow al arranque. Si faltan, la app falla inmediatamente.
