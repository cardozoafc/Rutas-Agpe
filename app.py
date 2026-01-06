import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================
st.set_page_config(
    page_title="AGPE EBSA - Mapa",
    layout="wide"
)

st.title("AGPE EBSA - Mapa de clientes")

# =========================
# BUSCADOR (VISIBLE ARRIBA)
# =========================
busqueda = st.text_input(
    "🔎 Buscar (nombre, cuenta, medidor, municipio, marca)",
    value=""
).strip().lower()

# =========================
# CARGAR DATOS
# =========================
ruta = "AGPE_EBSA_unificada.csv"
df = pd.read_csv(ruta)

# Normalizar nombres de columnas
df.columns = [c.strip().lower() for c in df.columns]

# Columnas obligatorias / opcionales
columnas = [
    "nombre_cliente",
    "cuenta",
    "municipio",
    "numero_medidor",
    "marca_medidor",
    "lat",
    "lon",
]

for col in columnas:
    if col not in df.columns:
        df[col] = ""

# =========================
# LIMPIAR COORDENADAS
# =========================
df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

df = df[
    df["lat"].between(-90, 90) &
    df["lon"].between(-180, 180)
].copy()

# =========================
# FILTRO DE BÚSQUEDA
# =========================
df_view = df.copy()

if busqueda:
    df_view = df[
        df["nombre_cliente"].astype(str).str.lower().str.contains(busqueda, na=False) |
        df["cuenta"].astype(str).str.contains(busqueda, na=False) |
        df["numero_medidor"].astype(str).str.contains(busqueda, na=False) |
        df["municipio"].astype(str).str.lower().str.contains(busqueda, na=False) |
        df["marca_medidor"].astype(str).str.lower().str.contains(busqueda, na=False)
    ]

if len(df_view) == 0:
    st.warning("⚠️ No hay resultados para esa búsqueda.")
    st.stop()

# =========================
# LINK GOOGLE MAPS
# =========================
df_view["url_ir"] = df_view.apply(
    lambda r: f"https://www.google.com/maps?q={r['lat']},{r['lon']}",
    axis=1
)

# =========================
# CREAR MAPA
# =========================
m = folium.Map(
    location=[df_view["lat"].mean(), df_view["lon"].mean()],
    zoom_start=9
)

for _, r in df_view.iterrows():
    popup_html = f"""
    <b>{r['nombre_cliente']}</b><br>
    Cuenta: {r['cuenta']}<br>
    Municipio: {r['municipio']}<br>
    Medidor: {r['numero_medidor']}<br>
    Marca: {r['marca_medidor']}<br><br>
    <a href="{r['url_ir']}" target="_blank"
       style="padding:6px 10px;
              background:#1f77b4;
              color:white;
              text-decoration:none;
              border-radius:5px;">
       IR (Google Maps)
    </a>
    """

    folium.Marker(
        location=[r["lat"], r["lon"]],
        tooltip=str(r["nombre_cliente"])[:40],
        popup=folium.Popup(popup_html, max_width=350),
        icon=folium.Icon(
            icon="flash",       # ⚡ rayo
            prefix="glyphicon",
            color="green"
        )
    ).add_to(m)

# =========================
# MOSTRAR MAPA
# =========================
st_folium(
    m,
    use_container_width=True,
    height=650
)
