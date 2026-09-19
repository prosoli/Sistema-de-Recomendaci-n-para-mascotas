import re
import unicodedata

import streamlit as st

try:
    from recomendador import recomendar
except ModuleNotFoundError:
    from recomendacion import recomendar


TIPOS_MASCOTA = {
    "perro": "Perro",
    "gato": "Gato",
    "ave": "Ave",
    "conejo": "Conejo",
    "pez": "Pez",
    "hamster": "Hamster",
    "reptil": "Reptil",
}

EDADES = {
    "cachorro": "Cachorro",
    "adulto": "Adulto",
    "senior": "Senior",
}

CATEGORIAS = {
    "alimentacion": "Alimentacion",
    "alimento": "Alimentacion",
    "comida": "Alimentacion",
    "pienso": "Alimentacion",
    "juguete": "Juguetes",
    "juguetes": "Juguetes",
    "higiene": "Higiene",
    "shampoo": "Higiene",
    "accesorio": "Accesorios",
    "accesorios": "Accesorios",
    "salud": "Salud",
    "medicina": "Salud",
}


def _normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(
        caracter for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )


def _extraer_datos(texto, perfil):
    texto_normalizado = _normalizar(texto)

    for clave, valor in TIPOS_MASCOTA.items():
        if re.search(rf"\b{re.escape(clave)}\b", texto_normalizado):
            perfil["tipo_mascota"] = valor
            break

    for clave, valor in EDADES.items():
        if re.search(rf"\b{re.escape(clave)}\b", texto_normalizado):
            perfil["edad"] = valor
            break

    categorias = set(perfil.get("compras_previas", []))
    for clave, valor in CATEGORIAS.items():
        if re.search(rf"\b{re.escape(clave)}\b", texto_normalizado):
            categorias.add(valor)
    perfil["compras_previas"] = sorted(categorias)


def _respuesta_para_perfil(perfil):
    if not perfil.get("tipo_mascota"):
        return (
            "¡Hola! Soy PetMatch Assistant 🐾.\n\n"
            "Te ayudaré a encontrar productos ideales para tu mascota.\n\n"
            "Primero dime qué mascota tienes. Por ejemplo: "
            "'Tengo un perro'."
        )

    if not perfil.get("edad"):
        return (
            f"Perfecto 🐾. Entendí que tienes un {perfil['tipo_mascota'].lower()}.\n\n"
            "¿Qué edad tiene tu mascota? Puedes responder: cachorro, adulto o senior."
        )

    if "compras_confirmadas" not in perfil:
        return (
            f"Excelente. Tu mascota es un {perfil['tipo_mascota'].lower()} "
            f"{perfil['edad'].lower()}.\n\n"
            "¿Has comprado algún producto anteriormente? Puedes escribir categorías "
            "como alimentación, juguetes, higiene, accesorios o salud. "
            "Si no has comprado nada, escribe 'ninguna'."
        )

    recomendaciones = recomendar(
        perfil["tipo_mascota"],
        perfil["edad"],
        perfil["compras_previas"],
    )
    perfil["recomendaciones"] = recomendaciones

    resumen_compras = ", ".join(perfil["compras_previas"]) or "ninguna categoría"
    respuesta = (
        "Según la información que me diste:\n\n"
        f"🐾 Tienes un {perfil['tipo_mascota'].lower()} {perfil['edad'].lower()}.\n"
        f"Tus compras anteriores indican interés en {resumen_compras.lower()}.\n\n"
    )

    if not recomendaciones:
        return respuesta + (
            "No encontré productos compatibles con esa combinación en el catálogo."
        )

    respuesta += "Encontré estos productos recomendados:\n\n"
    for indice, recomendacion in enumerate(recomendaciones, start=1):
        explicacion = recomendacion.get(
            "explicacion",
            "Coincide con el tipo y la edad seleccionados.",
        )
        respuesta += (
            f"{indice}. {recomendacion['producto']} "
            f"(puntaje: {recomendacion['puntaje']})\n"
            f"   ¿Por qué? {explicacion}\n"
        )
    return respuesta


def render_chatbot():
    """Renderiza el asistente de compra basado en reglas dentro de Streamlit."""
    if "chat_abierto" not in st.session_state:
        st.session_state.chat_abierto = False
    if "chat_mensajes" not in st.session_state:
        st.session_state.chat_mensajes = []
    if "chat_perfil" not in st.session_state:
        st.session_state.chat_perfil = {"compras_previas": []}

    st.markdown(
        """
        <style>
            .chat-launcher ~ div[data-testid="stButton"] button,
            .chat-launcher + div[data-testid="stButton"] button {
                position: fixed;
                right: 1.5rem;
                bottom: 1.5rem;
                z-index: 999;
                width: 3.5rem;
                height: 3.5rem;
                border-radius: 50%;
                background: #e8784f;
                color: white;
                border: 0;
                font-size: 1.35rem;
                box-shadow: 0 8px 22px rgba(80, 65, 55, .22);
            }
            .chat-panel {
                background: #fffdf9;
                border: 1px solid #e9e5dc;
                border-radius: 18px;
                padding: 1rem;
                margin: 1.5rem 0;
                box-shadow: 0 10px 26px rgba(44, 55, 51, .08);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="chat-launcher">', unsafe_allow_html=True)
    if st.button("🐾", key="chat_toggle", help="Abrir PetMatch Assistant"):
        st.session_state.chat_abierto = not st.session_state.chat_abierto
    st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state.chat_abierto:
        return

    with st.container():
        st.markdown('<div class="chat-panel">', unsafe_allow_html=True)
        st.subheader("PetMatch Assistant 🐾")
        st.caption(
            "Puedes preguntarme: 'Tengo un gato senior', "
            "'Tengo un perro cachorro' o 'Compré alimento'."
        )

        if not st.session_state.chat_mensajes:
            mensaje_inicial = _respuesta_para_perfil(st.session_state.chat_perfil)
            st.session_state.chat_mensajes.append(
                {"rol": "assistant", "contenido": mensaje_inicial}
            )

        for mensaje in st.session_state.chat_mensajes:
            with st.chat_message(mensaje["rol"]):
                st.markdown(mensaje["contenido"])

        entrada = st.chat_input("Escribe aquí tu respuesta...", key="chat_input")
        if entrada:
            st.session_state.chat_mensajes.append(
                {"rol": "user", "contenido": entrada}
            )
            perfil = st.session_state.chat_perfil
            texto_normalizado = _normalizar(entrada)
            _extraer_datos(entrada, perfil)

            compras_mencionadas = any(
                palabra in texto_normalizado
                for palabra in ("ninguna", "ninguno", "no he", "no tengo")
            ) or bool(perfil["compras_previas"])

            if compras_mencionadas:
                perfil["compras_previas"] = []
                _extraer_datos(entrada, perfil)
                perfil["compras_confirmadas"] = True

            respuesta = _respuesta_para_perfil(perfil)
            st.session_state.chat_mensajes.append(
                {"rol": "assistant", "contenido": respuesta}
            )
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)