"""Chatbot guiado que reutiliza el recomendador de contenido."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import streamlit as st

from recomendacion import recomendar


TIPOS_MASCOTA = {
    "perro": "Perro",
    "gato": "Gato",
    "ave": "Ave",
    "pajaro": "Ave",
    "conejo": "Conejo",
    "pez": "Pez",
    "peces": "Pez",
    "hamster": "Hamster",
}
EDADES = {"cachorro": "Cachorro", "adulto": "Adulto", "senior": "Senior"}
TAMANOS = {
    "pequeno": "Pequeño",
    "pequena": "Pequeño",
    "mediano": "Mediano",
    "mediana": "Mediano",
    "grande": "Grande",
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
AVATAR_MILO = str(Path(__file__).parent / "assets" / "petly-logo.png")


def _colones(valor: float) -> str:
    return f"₡{valor:,.0f}".replace(",", ".")


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def _contiene(texto: str, palabra: str) -> bool:
    return bool(re.search(rf"\b{re.escape(palabra)}\b", texto))


def extraer_datos(texto: str, perfil: dict) -> dict:
    """Actualiza y devuelve el perfil con las entidades reconocidas."""
    normalizado = _normalizar(texto)
    for clave, valor in TIPOS_MASCOTA.items():
        if _contiene(normalizado, clave):
            perfil["tipo_mascota"] = valor
            break
    for clave, valor in EDADES.items():
        if _contiene(normalizado, clave):
            perfil["edad"] = valor
            break
    for clave, valor in TAMANOS.items():
        if _contiene(normalizado, clave):
            perfil["tamano"] = valor
            break

    categorias = set(perfil.get("compras_previas", []))
    encontro_categoria = False
    for clave, valor in CATEGORIAS.items():
        if _contiene(normalizado, clave):
            categorias.add(valor)
            encontro_categoria = True

    sin_compras = any(
        frase in normalizado
        for frase in ("ninguna", "ninguno", "no he comprado", "no compre", "nada")
    )
    if sin_compras:
        categorias.clear()
        perfil["compras_confirmadas"] = True
    elif encontro_categoria:
        perfil["compras_confirmadas"] = True
    perfil["compras_previas"] = sorted(categorias)
    return perfil


def respuesta_para_perfil(perfil: dict) -> str:
    if not perfil.get("tipo_mascota"):
        return "¡Hola! Soy **Milo, tu asesor Petly** 🐾. ¿Qué mascota tienes?"
    if not perfil.get("edad"):
        return (
            f"Entendí que tienes un **{perfil['tipo_mascota'].lower()}**. "
            "¿Es cachorro, adulto o senior?"
        )
    if not perfil.get("compras_confirmadas"):
        return (
            "¿Qué categorías has comprado recientemente? Puedes mencionar "
            "alimentación, juguetes, higiene, accesorios o salud. Si no has "
            "comprado nada, responde **ninguna**."
        )

    resultados = recomendar(
        perfil["tipo_mascota"],
        perfil["edad"],
        perfil.get("compras_previas", []),
        tamano=perfil.get("tamano"),
        limite=10,
    )
    perfil["recomendaciones"] = resultados
    compras = ", ".join(perfil.get("compras_previas", [])) or "sin compras anteriores"
    respuesta = (
        f"Preparé **{len(resultados)} recomendaciones** para tu "
        f"{perfil['tipo_mascota'].lower()} {perfil['edad'].lower()}, considerando "
        f"{compras.lower()}:\n\n"
    )
    for indice, item in enumerate(resultados, start=1):
        respuesta += (
            f"{indice}. **{item['producto']}** · {_colones(item['precio'])} · "
            f"{item['puntaje']}%\n   {item['explicacion']}\n"
        )
    return respuesta


def _reiniciar_chat() -> None:
    st.session_state.chat_mensajes = []
    st.session_state.chat_perfil = {"compras_previas": []}


def render_chatbot() -> None:
    """Renderiza un asistente conversacional determinista y explicable."""
    st.session_state.setdefault("chat_mensajes", [])
    st.session_state.setdefault("chat_perfil", {"compras_previas": []})

    cabecera, accion = st.columns([5, 1])
    with cabecera:
        st.subheader("Milo · asesor de tienda")
        st.caption("Cuéntame sobre tu mascota; completaré su perfil paso a paso.")
    with accion:
        st.button("Nueva charla", key="reiniciar_chat", on_click=_reiniciar_chat)

    if not st.session_state.chat_mensajes:
        st.session_state.chat_mensajes.append(
            {"rol": "assistant", "contenido": respuesta_para_perfil(st.session_state.chat_perfil)}
        )

    for mensaje in st.session_state.chat_mensajes:
        avatar = AVATAR_MILO if mensaje["rol"] == "assistant" else "🐾"
        with st.chat_message(mensaje["rol"], avatar=avatar):
            st.markdown(mensaje["contenido"])

    entrada = st.chat_input("Escribe aquí… por ejemplo: gato senior, compré salud", key="chat_input")
    if entrada:
        st.session_state.chat_mensajes.append({"rol": "user", "contenido": entrada})
        perfil = extraer_datos(entrada, st.session_state.chat_perfil)
        respuesta = respuesta_para_perfil(perfil)
        st.session_state.chat_mensajes.append({"rol": "assistant", "contenido": respuesta})
        st.rerun()
