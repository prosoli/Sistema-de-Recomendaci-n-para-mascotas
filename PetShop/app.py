"""Interfaz web de Petly."""

import base64
from html import escape
from pathlib import Path

import streamlit as st

from chatbot import render_chatbot
from historial import obtener_cliente
from recomendacion import cargar_catalogo, recomendar


BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "assets" / "petly-logo.png"

st.set_page_config(
    page_title="Petly · Una cesta hecha para ellos",
    page_icon=str(LOGO_PATH),
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def datos_catalogo():
    return cargar_catalogo()


def imagen_embebida(ruta: Path) -> str:
    return base64.b64encode(ruta.read_bytes()).decode("ascii")


catalogo = datos_catalogo()
cliente_actual = obtener_cliente()
compras_cliente = cliente_actual["compras_previas"]
logo_base64 = imagen_embebida(LOGO_PATH)
IMAGENES_CATEGORIA = {
    "Alimentacion": imagen_embebida(BASE_DIR / "assets" / "products" / "alimentacion.webp"),
    "Juguetes": imagen_embebida(BASE_DIR / "assets" / "products" / "juguetes.webp"),
    "Higiene": imagen_embebida(BASE_DIR / "assets" / "products" / "higiene.webp"),
    "Accesorios": imagen_embebida(BASE_DIR / "assets" / "products" / "accesorios.webp"),
    "Salud": imagen_embebida(BASE_DIR / "assets" / "products" / "salud.webp"),
}
orden_tipos = ["Perro", "Gato", "Ave", "Conejo", "Hamster", "Pez"]
tipos_disponibles = catalogo["tipo_mascota"].dropna().unique().tolist()
tipos = [tipo for tipo in orden_tipos if tipo in tipos_disponibles]
tamanos = sorted(catalogo["tamano"].dropna().unique().tolist())
categorias = sorted(catalogo["categoria"].dropna().unique().tolist())
niveles_precio = sorted(catalogo["nivel_precio"].dropna().unique().tolist())

ICONOS = {
    "Alimentacion": "🥣",
    "Juguetes": "🎾",
    "Higiene": "🫧",
    "Accesorios": "🧣",
    "Salud": "✚",
}
COLORES = {
    "Alimentacion": "#F7C96E",
    "Juguetes": "#EF8B6B",
    "Higiene": "#9ED7CB",
    "Accesorios": "#B9A7D6",
    "Salud": "#89B8A5",
}
PRODUCTOS_VERIFICADOS = {
    "Purina Pro Plan Puppy Razas Medianas": {
        "imagen": "https://petshop2gocr.com/wp-content/uploads/7501072210678_7-300x300.jpg",
        "fuente": "https://petshop2gocr.com/producto/pro-plan-cachorro-raza-mediana-optistart/",
        "tienda": "Pet Shop 2 Go CR",
    },
    "Pro Plan Senior 7+ Cat 3 kg": {
        "imagen": "https://petshop2gocr.com/wp-content/uploads/Diseno-sin-titulo-2025-09-23T175225.807-300x300.png",
        "fuente": "https://petshop2gocr.com/producto/pro-plan-senior-7-cat-3-kg/",
        "tienda": "Pet Shop 2 Go CR",
    },
}


def colones(valor: float) -> str:
    return f"₡{valor:,.0f}".replace(",", ".")


def visual_producto(item: dict, icono: str) -> str:
    verificado = PRODUCTOS_VERIFICADOS.get(item["producto"])
    if not verificado:
        imagen = IMAGENES_CATEGORIA.get(item["categoria"], "")
        return (
            f'<div class="product-visual illustrative"><img src="data:image/webp;base64,{imagen}" '
            f'alt="Imagen ilustrativa de {escape(item["categoria"])}">'
            '<span class="photo-note">Imagen ilustrativa</span></div>'
        )
    imagen = escape(verificado["imagen"], quote=True)
    fuente = escape(verificado["fuente"], quote=True)
    tienda = escape(verificado["tienda"])
    return (
        f'<div class="product-visual verified"><img src="{imagen}" alt="{escape(item["producto"])}">'
        f'<a href="{fuente}" target="_blank" rel="noopener">Foto y precio: {tienda} ↗</a></div>'
    )

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');
    :root { --forest:#123d33; --forest-2:#205f4d; --coral:#f47755; --apricot:#ffd2b5; --cream:#faf7ef; --paper:#fffdf8; --ink:#19352e; --muted:#687b75; --line:#dedfd6; --plum:#67465f; }
    .stApp { background:var(--cream); color:var(--ink); font-family:'DM Sans',sans-serif; }
    [data-testid="stHeader"] { background:transparent; height:1.2rem; }
    [data-testid="stToolbar"], #MainMenu { visibility:hidden; }
    .block-container { max-width:1180px; padding:1.3rem 2rem 4rem; }
    h1,h2,h3 { font-family:'Fraunces',serif; color:var(--ink); letter-spacing:-.025em; }
    p { color:var(--muted); }
    .nav { display:flex; justify-content:space-between; align-items:center; padding:.4rem 0 1.1rem; }
    .brand-lockup { display:flex; align-items:center; gap:.72rem; }
    .brand-lockup img { width:54px; height:54px; object-fit:contain; }
    .wordmark { font-family:'Fraunces'; font-weight:700; font-size:1.65rem; line-height:1; color:var(--forest); }
    .wordmark small { display:block; font-family:'DM Sans'; font-size:.62rem; letter-spacing:.16em; text-transform:uppercase; color:var(--coral); margin-top:.28rem; }
    .nav-note { color:var(--forest-2); font-weight:700; font-size:.78rem; border-bottom:2px solid var(--apricot); padding-bottom:.2rem; }
    .hero { display:grid; grid-template-columns:minmax(0,1.4fr) minmax(280px,.6fr); min-height:440px; border-radius:34px 34px 110px 34px; overflow:hidden; background:var(--forest); position:relative; }
    .hero-copy { padding:4rem 2rem 3.5rem 4rem; position:relative; z-index:2; }
    .hero-kicker { color:#ffb99e; font-size:.75rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; margin:0 0 .9rem; }
    .hero h1 { color:#fff8e9; font-size:clamp(3rem,6vw,5.3rem); line-height:.93; max-width:720px; margin:0 0 1.2rem; }
    .hero h1 em { color:#ff9b78; font-style:italic; }
    .hero-copy>p { color:#d9e6df; font-size:1.06rem; line-height:1.65; max-width:610px; margin:0 0 1.5rem; }
    .promise-row { display:flex; gap:.55rem; flex-wrap:wrap; }
    .promise { color:#e8f1ed; border:1px solid rgba(255,255,255,.18); background:rgba(255,255,255,.07); padding:.45rem .7rem; border-radius:999px; font-size:.75rem; }
    .hero-art { display:flex; align-items:center; justify-content:center; background:var(--apricot); border-radius:50% 0 0 50%; margin:-3rem -2rem -3rem 0; }
    .hero-art img { width:min(330px,88%); transform:rotate(2deg); filter:drop-shadow(0 18px 18px rgba(37,43,33,.14)); }
    .trust-strip { display:flex; justify-content:center; gap:2.2rem; flex-wrap:wrap; padding:1.15rem; color:var(--muted); font-size:.78rem; }
    .trust-strip b { color:var(--forest); font-size:.92rem; }
    .section-copy { display:grid; grid-template-columns:110px 1fr; gap:1.5rem; align-items:start; margin:2.5rem 0 1.2rem; }
    .section-number { color:var(--coral); font-family:'Fraunces'; font-size:3rem; line-height:1; }
    .section-copy h2 { margin:0 0 .4rem; font-size:2rem; }
    .section-copy p { margin:0; max-width:650px; }
    div[data-testid="stTabs"] { margin-top:.2rem; }
    div[data-testid="stTabs"] [role="tablist"] { background:#efeade; border-radius:999px; padding:.35rem; gap:.25rem; width:max-content; }
    div[data-testid="stTabs"] [role="tab"] { color:#66756f!important; opacity:1!important; border-radius:999px; padding:.55rem 1rem; }
    div[data-testid="stTabs"] [role="tab"] * { color:#66756f!important; opacity:1!important; font-weight:700; }
    div[data-testid="stTabs"] [role="tab"][aria-selected="true"] { background:var(--forest); }
    div[data-testid="stTabs"] [role="tab"][aria-selected="true"] * { color:#fff!important; }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"], div[data-testid="stTabs"] [data-baseweb="tab-border"] { display:none; }
    div[data-testid="stForm"] { background:var(--paper); border:1px solid var(--line)!important; border-radius:28px!important; padding:1.4rem 1.55rem .9rem!important; margin:1.2rem 0 1.5rem; box-shadow:0 15px 45px rgba(31,63,53,.07); }
    div[data-testid="stForm"] h3 { margin:0!important; font-size:1.35rem!important; line-height:1.25!important; white-space:normal!important; word-break:normal!important; }
    div[data-testid="stForm"] [data-testid="stCaptionContainer"] { margin-top:-.45rem; margin-bottom:.35rem; }
    label { color:var(--ink)!important; font-weight:700!important; font-size:.8rem!important; }
    div[data-baseweb="select"]>div { border:1px solid var(--line); border-radius:12px; background:#fff; min-height:46px; }
    div[data-testid="stFormSubmitButton"]>button { border:0; border-radius:13px; background:var(--coral); color:white; font-weight:800; padding:.78rem 1.2rem; box-shadow:0 7px 0 #c84f32; transition:.15s; }
    div[data-testid="stFormSubmitButton"]>button:hover { background:#df6242; color:white; transform:translateY(2px); box-shadow:0 5px 0 #b6462d; }
    .basket-head { display:flex; justify-content:space-between; align-items:end; margin:2.8rem 0 1rem; }
    .basket-head h2 { margin:0; font-size:2.15rem; }
    .basket-head p { margin:.25rem 0 0; }
    .basket-count { color:var(--forest); background:#e3f0ea; border-radius:999px; padding:.5rem .75rem; font-size:.75rem; font-weight:800; }
    .product { --accent:#9ed7cb; background:var(--paper); border:1px solid var(--line); border-radius:26px 26px 52px 26px; padding:1.25rem; min-height:510px; box-shadow:0 10px 30px rgba(31,63,53,.055); margin-bottom:1rem; position:relative; overflow:hidden; }
    .product:before { content:''; position:absolute; width:110px; height:110px; border-radius:50%; background:var(--accent); opacity:.2; right:-38px; top:-42px; }
    .product-top { display:flex; justify-content:space-between; align-items:start; position:relative; }
    .product-index { font-family:'Fraunces'; color:var(--accent); font-size:2rem; font-weight:700; }
    .category-icon { width:44px; height:44px; display:grid; place-items:center; border-radius:14px; background:var(--accent); font-size:1.2rem; }
    .product-visual { height:150px; margin:.55rem 0 .8rem; border-radius:18px; background:#fff; display:flex; align-items:center; justify-content:center; position:relative; overflow:hidden; border:1px solid #edece5; }
    .product-visual img { width:100%; height:100%; object-fit:cover; }
    .product-visual.verified img { object-fit:contain; mix-blend-mode:multiply; }
    .product-visual a { position:absolute; right:.55rem; bottom:.45rem; padding:.26rem .45rem; border-radius:999px; color:#fff!important; background:rgba(18,61,51,.88); font-size:.59rem; text-decoration:none; }
    .photo-note { position:absolute; left:.55rem; bottom:.45rem; padding:.26rem .45rem; border-radius:999px; color:#fff; background:rgba(18,61,51,.78); font-size:.58rem; font-weight:700; }
    .product h3 { font-size:1.25rem; line-height:1.15; margin:.7rem 0 .18rem; min-height:2.8rem; }
    .brand-name { color:var(--muted); font-size:.76rem; text-transform:uppercase; letter-spacing:.08em; }
    .price-score { display:flex; align-items:center; justify-content:space-between; margin:1rem 0 .65rem; }
    .price { font-family:'Fraunces'; font-size:1.55rem; color:var(--forest); }
    .score { color:var(--forest); background:#e7f1ec; border-radius:999px; padding:.34rem .55rem; font-weight:800; font-size:.72rem; }
    .bar { height:7px; background:#e9ece7; border-radius:8px; overflow:hidden; }
    .bar span { display:block; height:100%; background:var(--accent); border-radius:8px; }
    .tags { display:flex; gap:.35rem; flex-wrap:wrap; margin:.75rem 0; }
    .tag { border:1px solid var(--line); border-radius:999px; padding:.28rem .5rem; font-size:.67rem; color:#566b64; }
    .description { color:var(--muted); font-size:.78rem; line-height:1.45; margin:.65rem 0 .35rem; }
    .why { color:#35544b; font-size:.75rem; line-height:1.45; margin:0; }
    .general { display:inline-block; margin-top:.55rem; color:#9d552f; background:#fff0e7; border-radius:8px; padding:.25rem .45rem; font-size:.68rem; font-weight:700; }
    div[data-testid="stExpander"] { background:var(--paper); border-color:var(--line); border-radius:18px; }
    .chat-intro { display:grid; grid-template-columns:90px 1fr; gap:1rem; align-items:center; background:var(--forest); border-radius:26px 26px 70px 26px; padding:1.2rem 1.5rem; margin:1.2rem 0; }
    .chat-intro img { width:82px; }
    .chat-intro h3 { color:#fff; margin:0 0 .2rem; font-size:1.45rem; }
    .chat-intro p { color:#d7e5df; margin:0; font-size:.82rem; }
    div[data-testid="stChatMessage"] { background:var(--paper); border:1px solid var(--line); border-radius:18px 18px 30px 18px; }
    div[data-testid="stChatMessage"] p, div[data-testid="stChatMessage"] li, div[data-testid="stChatMessage"] strong { color:var(--ink)!important; }
    div[data-testid="stChatInput"], div[data-testid="stChatInput"]>div, div[data-testid="stChatInput"] [data-baseweb="base-input"], div[data-testid="stChatInput"] [data-baseweb="textarea"], div[data-testid="stChatInput"] textarea { background:#fff!important; }
    div[data-testid="stChatInput"] { border:2px solid #d7ddd8!important; border-radius:16px!important; box-shadow:0 8px 24px rgba(18,61,51,.07)!important; }
    div[data-testid="stChatInput"] textarea, div[data-testid="stChatInput"] textarea:focus { color:#19352e!important; -webkit-text-fill-color:#19352e!important; caret-color:#f47755!important; opacity:1!important; }
    div[data-testid="stChatInput"] textarea::placeholder { color:#81918c!important; -webkit-text-fill-color:#81918c!important; }
    div[data-testid="stChatInput"] button { background:var(--coral)!important; color:#fff!important; border-radius:12px!important; }
    div.stButton>button { border:1px solid var(--forest); border-radius:999px; color:var(--forest); background:transparent; font-weight:700; }
    div.stButton>button p { color:var(--forest)!important; }
    .footer { display:flex; justify-content:space-between; gap:1rem; color:var(--muted); border-top:1px solid var(--line); margin-top:2.5rem; padding-top:1.2rem; font-size:.73rem; }
    @media(max-width:760px){ .block-container{padding:1rem .85rem 3rem}.nav-note{display:none}.hero{grid-template-columns:1fr;border-radius:26px 26px 70px 26px}.hero-copy{padding:2.4rem 1.5rem}.hero-art{display:none}.section-copy{grid-template-columns:55px 1fr}.section-number{font-size:2rem}.trust-strip{gap:.8rem}.basket-head{align-items:start;flex-direction:column}.product{min-height:auto}div[data-testid="stTabs"] [role="tab"]{padding:.45rem .55rem;font-size:.72rem}.footer{flex-direction:column}}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <nav class="nav">
      <div class="brand-lockup"><img src="data:image/png;base64,{logo_base64}" alt="Logo Petly"><div class="wordmark">Petly<small>pet market</small></div></div>
      <div class="nav-note">Selecciones pensadas con cariño</div>
    </nav>
    <section class="hero">
      <div class="hero-copy">
        <p class="hero-kicker">Menos búsqueda. Más colitas felices.</p>
        <h1>Su próxima cosa <em>favorita</em> está aquí.</h1>
        <p>Cuéntanos cómo es tu compañero y armaremos una cesta con diez productos disponibles o comparables en el mercado de Costa Rica.</p>
        <div class="promise-row"><span class="promise">✓ Precios en colones</span><span class="promise">✓ 10 productos únicos</span><span class="promise">✓ Te contamos por qué</span></div>
      </div>
      <div class="hero-art"><img src="data:image/png;base64,{logo_base64}" alt="Perro y gato de Petly"></div>
    </section>
    <div class="trust-strip"><span><b>{len(catalogo)}</b> productos curados</span><span><b>🇨🇷</b> mercado costarricense</span><span><b>{len(categorias)}</b> formas de cuidarles</span><span><b>1</b> modelo transparente</span></div>
    <div class="section-copy"><span class="section-number">01</span><div><h2>¿Cómo quieres comprar hoy?</h2><p>Elige el formulario para ir directo al grano o conversa con Milo, nuestro asesor de tienda. Ambos consultan el mismo catálogo inteligente.</p></div></div>
    """,
    unsafe_allow_html=True,
)

tab_recomendador, tab_chatbot = st.tabs(
    ["Armar mi cesta", "Hablar con Milo"]
)

with tab_recomendador:
    with st.form("perfil_mascota"):
        st.subheader("🪄 El perfil de tu compañero")
        st.caption("Cada dato ayuda a afinar la selección.")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            tipo = st.selectbox("¿Quién te acompaña?", tipos)
        with col2:
            edad = st.selectbox("Etapa de vida", ["Cachorro", "Adulto", "Senior"])
        with col3:
            tamano_opcion = st.selectbox("Tamaño", ["Sin preferencia", *tamanos])
        with col4:
            precio_opcion = st.selectbox("Presupuesto", ["Cualquiera", *niveles_precio])
        prioridad_col, compras_col = st.columns([1, 2])
        with prioridad_col:
            prioridad_opcion = st.selectbox(
                "Necesidad principal",
                ["Selección equilibrada", *categorias],
                help="Tiene más peso que el historial y afina los primeros resultados.",
            )
        with compras_col:
            historial_texto = ", ".join(compras_cliente) or "Sin compras registradas"
            st.text_input(
                "Tu historial de compras",
                value=historial_texto,
                disabled=True,
                help=(
                    f"Cliente identificado: {cliente_actual['id']}. En producción, "
                    "el historial vendría del sistema de ventas o CRM."
                ),
            )
        enviado = st.form_submit_button("Armar una cesta para mi mascota →", use_container_width=True)

    if enviado:
        st.session_state["recomendaciones"] = recomendar(
            tipo,
            edad,
            compras_cliente,
            tamano=None if tamano_opcion == "Sin preferencia" else tamano_opcion,
            nivel_precio=None if precio_opcion == "Cualquiera" else precio_opcion,
            prioridad=None if prioridad_opcion == "Selección equilibrada" else prioridad_opcion,
            limite=10,
        )
        prioridad_texto = "cesta equilibrada" if prioridad_opcion == "Selección equilibrada" else prioridad_opcion.lower()
        st.session_state["perfil_actual"] = (
            f"{tipo} · {edad} · prioridad: {prioridad_texto} · "
            f"historial: {historial_texto.lower()}"
        )

    resultados = st.session_state.get("recomendaciones")
    if resultados:
        st.markdown(
            f'<div class="basket-head"><div><h2>Una cesta hecha para ellos</h2><p>{escape(st.session_state.get("perfil_actual", ""))}</p></div><span class="basket-count">{len(resultados)} hallazgos</span></div>',
            unsafe_allow_html=True,
        )
        for inicio in range(0, len(resultados), 2):
            columnas = st.columns(2, gap="medium")
            for desplazamiento, (columna, item) in enumerate(zip(columnas, resultados[inicio:inicio + 2])):
                icono = ICONOS.get(item["categoria"], "🐾")
                color = COLORES.get(item["categoria"], "#9ED7CB")
                numero = inicio + desplazamiento + 1
                etiqueta_general = "" if item["coincidencia_edad"] else '<span class="general">Apto para todas las edades</span>'
                visual = visual_producto(item, icono)
                with columna:
                    st.markdown(
                        f"""
                        <article class="product" style="--accent:{color}">
                          <div class="product-top"><span class="product-index">{numero:02}</span><div class="category-icon">{icono}</div></div>
                          {visual}
                          <h3>{escape(item['producto'])}</h3><div class="brand-name">por {escape(item['marca'])}</div>
                          <div class="price-score"><span class="price">{colones(item['precio'])}</span><span class="score">{item['puntaje']}% afinidad</span></div>
                          <div class="bar"><span style="width:{item['puntaje']}%"></span></div>
                          <div class="tags"><span class="tag">{escape(item['categoria'])}</span><span class="tag">{escape(item['edad_recomendada'])}</span><span class="tag">{escape(item['nivel_precio'])}</span></div>
                          <p class="description">{escape(item['descripcion'])}</p>
                          <p class="why"><b>Encaja porque:</b> {escape(item['explicacion'].replace('Recomendado porque ', ''))}</p>{etiqueta_general}
                        </article>
                        """,
                        unsafe_allow_html=True,
                    )

        st.caption("🇨🇷 Precios de referencia en colones costarricenses. Las fichas con enlace fueron contrastadas con comercios de Costa Rica; los demás valores son estimaciones para este prototipo educativo.")

    with st.expander("Así armamos la cesta · Conoce el modelo"):
        st.markdown(
            """
            Petly convierte tipo, edad, tamaño, prioridad, historial personal de compras y presupuesto en un vector
            *one-hot*. Después calcula manualmente la **similitud coseno** entre ese
            perfil y el vector completo de cada producto. Una segunda etapa de diversidad
            evita repetir demasiado la misma categoría o marca, quita nombres repetidos
            y entrega diez. Es un recomendador KNN de contenido construido
            desde cero; la afinidad es una puntuación explicable, no una probabilidad clínica.
            """
        )

with tab_chatbot:
    st.markdown(
        f"""
        <div class="chat-intro"><img src="data:image/png;base64,{logo_base64}" alt="Milo de Petly"><div><h3>Milo conoce el catálogo de memoria</h3><p>La tienda ya cargó tu historial. Solo cuéntale a Milo qué mascota tienes y su etapa de vida; él traerá diez opciones del mismo recomendador.</p></div></div>
        """,
        unsafe_allow_html=True,
    )
    render_chatbot()

st.markdown(
    '<div class="footer"><span>Petly Costa Rica · Productos que hacen sentido para ellos.</span><span>Precios referenciales · Recomendaciones transparentes, nunca consejos veterinarios.</span></div>',
    unsafe_allow_html=True,
)
