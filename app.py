import streamlit as st
import pandas as pd
import time
from datetime import datetime
import pytz
from pymongo import MongoClient
import plotly.express as px  # Agregado para las gráficas de Plotly

# Configuración
tz = pytz.timezone("America/Bogota")
mongo_uri = "mongodb+srv://elieceruiz_admin:fPydI3B73ijAukEz@cluster0.rqzim65.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
db = client["registro_enfoque"]
coleccion = db["historial"]

# Función para cargar datos
def cargar_datos():
    datos = list(coleccion.find({}, {"_id": 0}))
    if datos:
        return pd.DataFrame(datos)
    else:
        return pd.DataFrame(columns=["Actividad", "Inicio", "Fin", "Duración", "Estado"])

df_hist = cargar_datos()

st.set_page_config(page_title="Gestor de Enfoque", layout="centered", initial_sidebar_state="collapsed")
st.title("Gestor de Enfoque y Pausa Activa")

tab1, tab2 = st.tabs(["Enfoque / Pausa", "Historial y Progreso"])

# ----------------- TAB 1 -----------------
with tab1:
    st.subheader("Configura tu sesión")
    unidad = st.radio("¿Trabajar en minutos o segundos?", ["minutos", "segundos"])
    factor = 60 if unidad == "minutos" else 1
    actividad = st.text_input("¿Qué actividad vas a realizar?")
    tiempo_enfoque = st.number_input(f"¿Cuánto tiempo de enfoque ({unidad})?", min_value=1)
    tiempo_pausa = st.number_input(f"¿Cuánto tiempo de pausa activa ({unidad})?", min_value=1)
    tomar_pausa = st.checkbox("¿Tomar pausa activa después?")

    if st.button("Iniciar sesión de enfoque") and actividad:
        tiempo_total = tiempo_enfoque * factor
        barra = st.progress(0)
        mensaje = st.empty()
        inicio = datetime.now(tz)

        for i in range(tiempo_total):
            barra.progress((i + 1) / tiempo_total)
            mensaje.markdown(f"Enfoque: **{i+1}/{tiempo_total}** segundos")
            time.sleep(1)

        fin = datetime.now(tz)
        duracion = str(fin - inicio).split(".")[0]
        st.success("¡Tiempo de enfoque finalizado!")
        st.balloons()
        st.markdown(
            '<audio autoplay><source src="https://actions.google.com/sounds/v1/alarms/spaceship_alarm.ogg" type="audio/ogg"></audio>',
            unsafe_allow_html=True,
        )

        nuevo_enfoque = {
            "Actividad": actividad,
            "Inicio": inicio.strftime("%Y-%m-%d %H:%M:%S"),
            "Fin": fin.strftime("%Y-%m-%d %H:%M:%S"),
            "Duración": duracion,
            "Estado": "Enfoque"
        }
        coleccion.insert_one(nuevo_enfoque)

        if tomar_pausa:
            barra_pausa = st.progress(0)
            mensaje_pausa = st.empty()
            inicio_pausa = datetime.now(tz)

            for i in range(tiempo_pausa * factor):
                barra_pausa.progress((i + 1) / (tiempo_pausa * factor))
                mensaje_pausa.markdown(f"Pausa: **{i+1}/{tiempo_pausa * factor}** segundos")
                time.sleep(1)

            fin_pausa = datetime.now(tz)
            duracion_pausa = str(fin_pausa - inicio_pausa).split(".")[0]
            st.success("¡Fin de la pausa activa!")
            st.markdown(
                '<audio autoplay><source src="https://actions.google.com/sounds/v1/alarms/spaceship_alarm.ogg" type="audio/ogg"></audio>',
                unsafe_allow_html=True,
            )

            nueva_pausa = {
                "Actividad": actividad,
                "Inicio": inicio_pausa.strftime("%Y-%m-%d %H:%M:%S"),
                "Fin": fin_pausa.strftime("%Y-%m-%d %H:%M:%S"),
                "Duración": duracion_pausa,
                "Estado": "Pausa Activa"
            }
            coleccion.insert_one(nueva_pausa)

        st.success("Sesión guardada correctamente.")

# ----------------- TAB 2 -----------------
with tab2:
    st.subheader("Historial de sesiones")
    df_hist = cargar_datos()
    if not df_hist.empty:
        df_hist["Inicio"] = pd.to_datetime(df_hist["Inicio"])
        fig = px.bar(df_hist, x="Actividad", y="Duración", color="Estado", title="Duración de Enfoques y Pausas")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_hist.sort_values(by="Inicio", ascending=False))
    else:
        st.info("Aún no hay sesiones registradas.")