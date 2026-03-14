import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
from datetime import datetime, timedelta

# ======================================
# CONFIGURACIÓN DE PÁGINA Y UI (UX/UI)
# ======================================
st.set_page_config(
    page_title="Workshift Analytics Pro",
    page_icon="📊",
    layout="wide"
)

# Estilos inspirados en VS Code Dark (Tus preferencias originales)
st.markdown("""
    <style>
    .stApp { background-color: #1e1e1e; color: #d4d4d4; }
    [data-testid="stSidebar"] { background-color: #252526; border-right: 1px solid #3c3c3c; }
    [data-testid="stMetricValue"] { color: #dcdcaa !important; font-weight: bold; font-size: 1.8rem; }
    [data-testid="stMetricLabel"] { color: #9cdcfe !important; }
    h1, h2, h3 { color: #569cd6 !important; font-family: 'Segoe UI', sans-serif; }
    .stTabs [role="tab"] { color: #c586c0; font-size: 16px; }
    .stTabs [role="tab"][aria-selected="true"] { color: #d4d4d4; border-bottom: 2px solid #569cd6; }
    div[data-testid="stForm"] { border: 1px solid #3c3c3c; border-radius: 8px; padding: 20px; }
    button[kind="primary"] { background-color: #0e639c !important; border: none; width: 100%; }
    .stDataFrame { border: 1px solid #3c3c3c; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

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
        if not os.path.exists(self.db_path):
            return pd.DataFrame()
        with self._get_connection() as conn:
            df = pd.read_sql("SELECT * FROM Registro", conn)
        
        if not df.empty:
            df["Fecha"] = pd.to_datetime(df["Fecha"])
            df["Duracion"] = pd.to_timedelta(df["Duracion"])
            df["Horas"] = df["Duracion"].dt.total_seconds() / 3600
        return df

    def delete_records(self, ids):
        if not ids: return
        with self._get_connection() as conn:
            conn.executemany("DELETE FROM Registro WHERE id=?", [(int(i),) for i in ids])

# Instancia del controlador
api = WorkshiftManager()

# ======================================
# SIDEBAR: ENTRADA DE DATOS
# ======================================
st.sidebar.title("⚙️ Configuración")
with st.sidebar.form("nueva_actividad", clear_on_submit=True):
    st.subheader("➕ Registrar Actividad")
    f_input = st.date_input("Fecha", datetime.now())
    p_input = st.text_input("Proyecto", placeholder="Ej: PedidosYa BizOps")
    t_input = st.text_input("Tarea", placeholder="Ej: Automatización Python")
    
    col_h, col_m = st.columns(2)
    h_val = col_h.number_input("Horas", 0, 24, 1)
    m_val = col_m.number_input("Minutos", 0, 59, 0)
    
    if st.form_submit_button("Guardar Registro", type="primary"):
        if p_input and t_input:
            duracion_td = timedelta(hours=h_val, minutes=m_val)
            api.save_entry(f_input, p_input, t_input, duracion_td)
            st.toast("✅ Registro exitoso", icon="🚀")
            st.rerun()
        else:
            st.error("Por favor completa Proyecto y Tarea.")

# ======================================
# CUERPO PRINCIPAL
# ======================================
st.title("📊 Workshift Analytics")
df_master = api.load_all()

if df_master.empty:
    st.info("Aún no hay datos registrados. Comienza agregando una actividad en el panel izquierdo.")
else:
    # Filtros Globales en Sidebar
    proyectos_unicos = df_master["Proyecto"].unique()
    seleccionados = st.sidebar.multiselect("Filtrar por Proyecto", proyectos_unicos, default=proyectos_unicos)
    df = df_master[df_master["Proyecto"].isin(seleccionados)]

    tab_dash, tab_data = st.tabs(["📈 Dashboard de Rendimiento", "🗄 Gestión de Base de Datos"])

    with tab_dash:
        # SECCIÓN 1: MÉTRICAS CLAVE
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tareas Totales", len(df))
        m2.metric("Proyectos Activos", df["Proyecto"].nunique())
        m3.metric("Horas Acumuladas", f"{df['Horas'].sum():.1f}h")
        
        # Lógica de Racha (Continuidad de días)
        fechas_log = sorted(df_master["Fecha"].dt.date.unique(), reverse=True)
        racha_cont = 0
        current_check = datetime.now().date()
        for f in fechas_log:
            if f == current_check or f == current_check - timedelta(days=1):
                racha_cont += 1
                current_check = f
            else: break
        m4.metric("Racha Actual", f"{racha_cont} Días", delta="🔥")

        st.divider()

        # SECCIÓN 2: DASHBOARD DE 4 GRÁFICOS
        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)

        with row1_col1:
            st.subheader("1. Jerarquía Proyecto / Tarea")
            fig1 = px.sunburst(df, path=['Proyecto', 'Tarea'], values='Horas',
                               color_discrete_sequence=px.colors.qualitative.Pastel,
                               template="plotly_dark")
            fig1.update_layout(margin=dict(t=10, l=0, r=0, b=0), height=350)
            st.plotly_chart(fig1, use_container_width=True)

        with row1_col2:
            st.subheader("2. Esfuerzo por Proyecto")
            df_bar = df.groupby("Proyecto")["Horas"].sum().reset_index().sort_values("Horas", ascending=True)
            fig2 = px.bar(df_bar, x="Horas", y="Proyecto", orientation='h',
                          color="Horas", color_continuous_scale="Blues",
                          template="plotly_dark")
            fig2.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        with row2_col1:
            st.subheader("3. Intensidad Diaria (Histórico)")
            df_daily = df.groupby(df["Fecha"].dt.date)["Horas"].sum().reset_index()
            fig3 = px.area(df_daily, x="Fecha", y="Horas",
                           color_discrete_sequence=["#569cd6"],
                           template="plotly_dark")
            fig3.update_layout(height=300)
            st.plotly_chart(fig3, use_container_width=True)

        with row2_col2:
            st.subheader("4. Productividad Semanal")
            df['Semana'] = df['Fecha'].dt.isocalendar().week
            df_sem = df.groupby('Semana')['Horas'].sum().reset_index()
            df_sem['Semana'] = df_sem['Semana'].apply(lambda x: f"Sem {x}")
            fig4 = px.bar(df_sem, x="Semana", y="Horas",
                          color_discrete_sequence=["#c586c0"],
                                template="plotly_dark")
            fig4.update_layout(height=300)
            st.plotly_chart(fig4, use_container_width=True)

    with tab_data:
        st.subheader("🗄 Explorador de Registros")
        st.markdown("Selecciona los registros que desees eliminar permanentemente.")
        
        df_crud = df.copy()
        df_crud.insert(0, "Eliminar", False)
        
        # Editor de datos optimizado
        response = st.data_editor(
            df_crud,
            column_config={
                "id": None, # Ocultamos el ID para limpieza visual
                "Eliminar": st.column_config.CheckboxColumn("Borrar", default=False),
                "Horas": st.column_config.NumberColumn(format="%.2f h"),
                "Fecha": st.column_config.DateColumn("Fecha"),
                "Duracion": st.column_config.TextColumn("Duración Raw")
            },
            disabled=["id", "Fecha", "Proyecto", "Tarea", "Duracion", "Horas"],
            hide_index=True,
            use_container_width=True,
            key="data_editor_main"
        )

        if st.button("🗑️ Eliminar seleccionados", type="secondary"):
            ids_to_del = response[response["Eliminar"] == True]["id"].tolist()
            if ids_to_del:
                api.delete_records(ids_to_del)
                st.success(f"Se han eliminado {len(ids_to_del)} registros.")
                st.rerun()
            else:
                st.warning("No hay registros seleccionados para eliminar.")

# Footer informativo
st.sidebar.divider()
st.sidebar.caption(f"Nicolás Cano | Workshift Analytics v2.1")