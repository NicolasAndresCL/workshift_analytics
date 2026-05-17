import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime, timedelta
from PIL import Image

# ======================================
# CONFIGURACIÓN DE PÁGINA
# ======================================
page_icon = Image.open("image/logo_nc.ico")
st.set_page_config(
    page_title="Workshift Analytics Pro",
    page_icon=page_icon,
    layout="wide"
)

# Adaptar gráficos Plotly al tema activo de Streamlit
try:
    is_dark = st.context.theme.base == "dark"
except AttributeError:
    is_dark = True
plotly_template = "plotly_dark" if is_dark else "plotly_white"

# ======================================
# LÓGICA DE PERSISTENCIA (Data Layer)
# ======================================
class WorkshiftManager:
    def __init__(self, db_path="workshift.db"):
        self.db_path = db_path
        self._create_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS Registro (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Fecha TEXT,
                    Proyecto TEXT,
                    Tarea TEXT,
                    Duracion TEXT
                )
            """)

    def save_entry(self, fecha, proyecto, tarea, duracion):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO Registro (Fecha, Proyecto, Tarea, Duracion) VALUES (?, ?, ?, ?)",
                (str(fecha), proyecto.strip(), tarea.strip(), str(duracion))
            )

    def load_all(self):
        with self._get_connection() as conn:
            df = pd.read_sql("SELECT * FROM Registro", conn)

        if not df.empty:
            df["Fecha"] = pd.to_datetime(df["Fecha"])
            df["Duracion"] = pd.to_timedelta(df["Duracion"])
            df["Horas"] = df["Duracion"].dt.total_seconds() / 3600
        return df

    def delete_records(self, ids):
        if not ids:
            return
        placeholders = ",".join("?" * len(ids))
        with self._get_connection() as conn:
            conn.execute(
                f"DELETE FROM Registro WHERE id IN ({placeholders})",
                [int(i) for i in ids]
            )

# ======================================
# INSTANCIA Y CACHÉ
# ======================================
@st.cache_resource
def get_manager():
    return WorkshiftManager()

api = get_manager()

@st.cache_data(ttl=30)
def load_data():
    return api.load_all()

# ======================================
# SIDEBAR
# ======================================
logo = Image.open("image/logo_nc.jpg")
st.sidebar.image(logo, width=130)
st.sidebar.title("⚙️ Configuración")
st.sidebar.caption("Cambia el tema desde el menú ≡ → Settings")
st.sidebar.divider()

with st.sidebar.form("nueva_actividad", clear_on_submit=True):
    st.subheader("➕ Registrar Actividad")
    f_input = st.date_input("Fecha", datetime.now())
    p_input = st.text_input("Proyecto", placeholder="Ej: PedidosYa BizOps")
    t_input = st.text_input("Tarea", placeholder="Ej: Automatización Python")

    col_h, col_m = st.columns(2)
    h_val = col_h.number_input("Horas", 0, 24, 1)
    m_val = col_m.number_input("Minutos", 0, 59, 0)

    if st.form_submit_button("Guardar Registro", type="primary"):
        if not p_input or not t_input:
            st.error("Por favor completa Proyecto y Tarea.")
        elif h_val == 0 and m_val == 0:
            st.error("La duración no puede ser 0 horas y 0 minutos.")
        else:
            duracion_td = timedelta(hours=h_val, minutes=m_val)
            api.save_entry(f_input, p_input, t_input, duracion_td)
            load_data.clear()
            st.toast("✅ Registro exitoso", icon="🚀")
            st.rerun()

# ======================================
# CUERPO PRINCIPAL
# ======================================
st.title("📊 Workshift Analytics")
st.caption("Seguimiento de actividades y productividad por proyecto")
st.divider()

df_master = load_data()

if df_master.empty:
    st.info("Aún no hay datos registrados. Comienza agregando una actividad en el panel izquierdo.")
else:
    # Filtro global
    proyectos_unicos = df_master["Proyecto"].unique()
    seleccionados = st.sidebar.multiselect("Filtrar por Proyecto", proyectos_unicos, default=proyectos_unicos)
    df = df_master[df_master["Proyecto"].isin(seleccionados)]

    tab_dash, tab_data = st.tabs(["📈 Dashboard de Rendimiento", "🗄 Gestión de Registros"])

    with tab_dash:
        # MÉTRICAS CLAVE
        with st.container(border=True):
            m1, m2, m3, m4 = st.columns(4)

            m1.metric("Tareas Totales", len(df))
            m2.metric("Proyectos Activos", df["Proyecto"].nunique())
            m3.metric("Horas Acumuladas", f"{df['Horas'].sum():.1f} h")

            fechas_log = sorted(df_master["Fecha"].dt.date.unique(), reverse=True)
            racha_cont = 0
            current_check = datetime.now().date()
            for f in fechas_log:
                if f == current_check or f == current_check - timedelta(days=1):
                    racha_cont += 1
                    current_check = f
                else:
                    break
            m4.metric("Racha Actual", f"{racha_cont} días", delta="🔥 activa" if racha_cont > 0 else None)

        st.divider()

        # GRÁFICOS
        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)

        with row1_col1:
            with st.container(border=True):
                st.subheader("Jerarquía Proyecto / Tarea")
                fig1 = px.sunburst(df, path=["Proyecto", "Tarea"], values="Horas",
                                   color_discrete_sequence=px.colors.qualitative.Pastel,
                                   template=plotly_template)
                fig1.update_layout(margin=dict(t=10, l=0, r=0, b=0), height=350)
                st.plotly_chart(fig1, use_container_width=True)

        with row1_col2:
            with st.container(border=True):
                st.subheader("Esfuerzo por Proyecto")
                df_bar = df.groupby("Proyecto")["Horas"].sum().reset_index().sort_values("Horas", ascending=True)
                fig2 = px.bar(df_bar, x="Horas", y="Proyecto", orientation="h",
                              color="Horas", color_continuous_scale="Blues",
                              template=plotly_template)
                fig2.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

        with row2_col1:
            with st.container(border=True):
                st.subheader("Intensidad Diaria")
                df_daily = df.groupby(df["Fecha"].dt.date)["Horas"].sum().reset_index()
                fig3 = px.area(df_daily, x="Fecha", y="Horas",
                               color_discrete_sequence=["#0e639c"],
                               template=plotly_template)
                fig3.update_layout(height=300)
                st.plotly_chart(fig3, use_container_width=True)

        with row2_col2:
            with st.container(border=True):
                st.subheader("Productividad Semanal")
                df_sem = df.copy()
                df_sem["Semana"] = df_sem["Fecha"].dt.isocalendar().week
                df_sem = df_sem.groupby("Semana")["Horas"].sum().reset_index()
                df_sem["Semana"] = df_sem["Semana"].apply(lambda x: f"Sem {x}")
                fig4 = px.bar(df_sem, x="Semana", y="Horas",
                              color_discrete_sequence=["#0e639c"],
                              template=plotly_template)
                fig4.update_layout(height=300)
                st.plotly_chart(fig4, use_container_width=True)

    with tab_data:
        with st.container(border=True):
            st.subheader("🗄 Explorador de Registros")
            st.caption("Marca los registros que desees eliminar y confirma con el botón.")

            df_crud = df.copy()
            df_crud.insert(0, "Eliminar", False)

            response = st.data_editor(
                df_crud,
                column_config={
                    "id": None,
                    "Eliminar": st.column_config.CheckboxColumn("Borrar", default=False),
                    "Horas": st.column_config.NumberColumn(format="%.2f h"),
                    "Fecha": st.column_config.DateColumn("Fecha"),
                    "Duracion": st.column_config.TextColumn("Duración Raw"),
                },
                disabled=["id", "Fecha", "Proyecto", "Tarea", "Duracion", "Horas"],
                hide_index=True,
                use_container_width=True,
                key="data_editor_main"
            )

            if st.button("🗑️ Eliminar seleccionados", type="secondary"):
                ids_to_del = response[response["Eliminar"]]["id"].tolist()
                if ids_to_del:
                    api.delete_records(ids_to_del)
                    load_data.clear()
                    st.success(f"Se eliminaron {len(ids_to_del)} registros.")
                    st.rerun()
                else:
                    st.warning("No hay registros seleccionados.")

# Footer
st.sidebar.divider()
st.sidebar.caption("Nicolás Cano · Workshift Analytics v2.3")
