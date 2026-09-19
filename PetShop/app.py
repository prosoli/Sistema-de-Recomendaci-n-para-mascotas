from pathlib import Path
import os

import pandas as pd
import streamlit as st

# Permite encontrar productos.csv aunque la aplicación se ejecute desde otra carpeta
os.chdir(Path(__file__).parent)

try:
    from recomendador import recomendar
except ModuleNotFoundError:
    # Compatible con el archivo actualmente abierto: recomendacion.py
    from recomendacion import recomendar


ruta_catalogo = Path(__file__).parent / "productos.csv"
tipos_mascota = (
    pd.read_csv(ruta_catalogo)["tipo_mascota"]
    .dropna()
    .astype(str)
    .str.strip()
    .drop_duplicates()
    .tolist()
)


st.set_page_config(
    page_title="Petly | Recomendaciones para mascotas",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

        :root {
            --ink: #263238;
            --muted: #6d7b78;
            --cream: #fbf8f2;
            --surface: #ffffff;
            --line: #e9e5dc;
            --orange: #e8784f;
            --orange-dark: #c95f3d;
            --sage: #dfece3;
            --sage-dark: #547363;
            --blue: #e6f0f4;
        }

        .stApp {
            background: var(--cream);
            color: var(--ink);
            font-family: 'DM Sans', sans-serif;
        }

        [data-testid="stHeader"] { background: transparent; }
        .block-container { max-width: 1120px; padding: 2.5rem 2rem 4rem; }
        h1, h2, h3 { font-family: 'Plus Jakarta Sans', sans-serif; color: var(--ink); }
        h2 { font-size: 1.35rem; margin: 0; }
        p { color: var(--muted); }

        .brand-row { display: flex; align-items: center; gap: .65rem; margin-bottom: 2rem; }
        .brand-mark { background: var(--orange); color: white; border-radius: 12px; width: 38px; height: 38px; display: grid; place-items: center; font-size: 1.2rem; }
        .brand-name { color: var(--ink); font-weight: 800; font-size: 1.05rem; letter-spacing: -.02em; }

        .hero { background: linear-gradient(115deg, #f2ded0 0%, #f7e9db 52%, #e2eee6 100%); border: 1px solid rgba(255,255,255,.7); border-radius: 24px; padding: 2.7rem 3rem; margin-bottom: 1.35rem; position: relative; overflow: hidden; }
        .hero:after { content: ''; position: absolute; width: 190px; height: 190px; border-radius: 50%; background: rgba(255,255,255,.24); right: 7%; top: -65px; }
        .eyebrow { color: var(--orange-dark); font-size: .76rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin: 0 0 .75rem; }
        .hero h1 { font-size: clamp(2.2rem, 5vw, 4rem); letter-spacing: -.06em; line-height: 1; margin: 0 0 .8rem; max-width: 680px; }
        .hero p { color: #52605d; font-size: 1.05rem; margin: 0; max-width: 540px; line-height: 1.6; }

        .section-card { background: var(--surface); border: 1px solid var(--line); border-radius: 18px; padding: 1.45rem 1.55rem 1.15rem; margin: 1.25rem 0 1.8rem; box-shadow: 0 8px 24px rgba(44, 55, 51, .04); }
        .section-title { display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-bottom: 1rem; }
        .section-kicker { color: var(--muted); font-size: .85rem; margin: .25rem 0 0; }
        label { color: var(--ink) !important; font-weight: 600 !important; font-size: .88rem !important; }
        div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { border-color: var(--line); border-radius: 10px; background: #fff; }
        div[data-baseweb="select"] > div:focus-within, div[data-baseweb="input"] > div:focus-within { border-color: var(--orange); box-shadow: 0 0 0 1px var(--orange); }

        div.stButton { display: flex; justify-content: center; margin-top: .35rem; }
        div.stButton > button { width: auto; min-width: 245px; border: 0; border-radius: 11px; background: var(--orange); color: white; font-weight: 700; padding: .72rem 1.35rem; transition: all .2s ease; }
        div.stButton > button:hover { background: var(--orange-dark); color: white; transform: translateY(-1px); }

        .results-head { display: flex; align-items: end; justify-content: space-between; margin: .4rem 0 1rem; border-bottom: 1px solid var(--line); padding-bottom: .85rem; }
        .results-count { color: var(--muted); font-size: .85rem; }
        .product-card { background: var(--surface); border: 1px solid var(--line); border-radius: 16px; padding: 1.2rem; height: 100%; box-shadow: 0 7px 20px rgba(44, 55, 51, .045); }
        .product-top { display: flex; justify-content: space-between; gap: .75rem; align-items: start; margin-bottom: 1rem; }
        .product-icon { width: 42px; height: 42px; display: grid; place-items: center; border-radius: 12px; background: var(--blue); color: #50717b; font-size: 1.25rem; }
        .product-card h3 { font-size: 1.05rem; margin: 0 0 .25rem; }
        .product-meta { color: var(--muted); font-size: .82rem; margin: 0; }
        .compatibility { background: var(--sage); color: var(--sage-dark); border-radius: 999px; padding: .35rem .6rem; font-weight: 700; font-size: .78rem; white-space: nowrap; }
        .product-details { display: grid; grid-template-columns: 1fr 1fr; gap: .7rem; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); padding: .8rem 0; margin-bottom: .9rem; }
        .detail-label { display: block; color: var(--muted); font-size: .75rem; margin-bottom: .15rem; }
        .detail-value { color: var(--ink); font-weight: 700; font-size: .88rem; }
        .reason-title { color: var(--ink); font-size: .82rem; font-weight: 700; margin-bottom: .4rem; }
        .reason { color: var(--muted); font-size: .8rem; line-height: 1.55; margin: 0; }
        .empty-state { text-align: center; background: var(--surface); border: 1px dashed #d7d2c6; border-radius: 16px; padding: 2rem; }
        .empty-state h3 { font-size: 1.05rem; margin: 0 0 .35rem; }
        .empty-state p { margin: 0; font-size: .9rem; }
        .footer { border-top: 1px solid var(--line); color: var(--muted); font-size: .78rem; text-align: center; margin-top: 3rem; padding-top: 1.2rem; }

        @media (max-width: 640px) {
            .block-container { padding: 1.4rem 1rem 3rem; }
            .hero { padding: 2rem 1.35rem; }
            .hero h1 { font-size: 2.4rem; }
            .section-card { padding: 1.1rem; }
            .results-head { align-items: start; flex-direction: column; gap: .25rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="brand-row">
        <div class="brand-mark">🐾</div>
        <div class="brand-name">Petly</div>
    </div>
    <section class="hero">
        <p class="eyebrow">Recomendaciones pensadas para ellos</p>
        <h1>Encuentra lo que tu mascota necesita.</h1>
        <p>Cuéntanos un poco sobre ella y descubre productos seleccionados para acompañar cada etapa.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-card">
        <div class="section-title">
            <div>
                <h2>Cuéntanos sobre tu mascota</h2>
                <p class="section-kicker">Usaremos estos datos para personalizar la selección.</p>
            </div>
        </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)
with col1:
    tipo = st.selectbox("Tipo de mascota", tipos_mascota)
with col2:
    edad = st.selectbox("Edad", ["Cachorro", "Adulto", "Senior"])
with col3:
    compras = st.multiselect(
        "¿Qué compraste recientemente?",
        ["Alimentación", "Juguetes", "Higiene", "Accesorios", "Salud"],
        placeholder="Selecciona una o más opciones",
    )

if st.button("Encontrar productos ideales", type="primary"):
    recomendaciones = recomendar(tipo, edad, compras)
    st.session_state["recomendaciones"] = recomendaciones

st.markdown("</div>", unsafe_allow_html=True)

recomendaciones = st.session_state.get("recomendaciones")
if recomendaciones is not None:
    st.markdown(
        f'<div class="results-head"><h2>Recomendaciones para ti</h2><span class="results-count">{len(recomendaciones)} productos encontrados</span></div>',
        unsafe_allow_html=True,
    )

    if recomendaciones:
        for inicio in range(0, len(recomendaciones), 2):
            columnas = st.columns(2, gap="medium")
            for indice, recomendacion in enumerate(recomendaciones[inicio:inicio + 2]):
                producto = recomendacion.get("producto", "Producto recomendado")
                puntaje = recomendacion.get("puntaje", 0)
                marca = recomendacion.get("marca", "Selección PetMatch")
                categoria = recomendacion.get("categoria", "Recomendado para tu mascota")

                with columnas[indice]:
                    st.markdown(
                        f"""
                        <article class="product-card">
                            <div class="product-top">
                                <div style="display:flex; gap:.7rem; align-items:center;">
                                    <div class="product-icon">✦</div>
                                    <div><h3>{producto}</h3><p class="product-meta">{marca}</p></div>
                                </div>
                                <span class="compatibility">{puntaje}% compatible</span>
                            </div>
                            <div class="product-details">
                                <div><span class="detail-label">Categoría</span><span class="detail-value">{categoria}</span></div>
                            </div>
                        </article>
                        """,
                        unsafe_allow_html=True,
                    )
    else:
        st.markdown(
            """
            <div class="empty-state">
                <h3>Aún no encontramos una coincidencia.</h3>
                <p>Prueba con otra combinación de edad, tipo de mascota o compras recientes.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        """
        <div class="empty-state">
            <h3>Tu selección personalizada empieza aquí</h3>
            <p>Completa el perfil de tu mascota para ver productos recomendados.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="footer">Petly · Recomendaciones simples para cuidar mejor a quienes más quieres.</div>', unsafe_allow_html=True) 