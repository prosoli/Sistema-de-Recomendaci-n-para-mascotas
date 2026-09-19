from pathlib import Path
import unicodedata

import pandas as pd


def _normalizar(valor):
    """Normaliza texto para comparar categorías con o sin tildes."""
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().lower()
    return "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caracter) != "Mn"
    )


def recomendar(tipo_mascota, edad_recomendada, compras_previas, tamano=None):
    ruta_catalogo = Path(__file__).parent / "productos.csv"
    productos = pd.read_csv(ruta_catalogo)

    tipo_usuario = _normalizar(tipo_mascota)
    edad_usuario = _normalizar(edad_recomendada)
    compras = {_normalizar(compra) for compra in (compras_previas or [])}
    tamano_usuario = _normalizar(tamano)

    recomendaciones = []

    for _, producto in productos.iterrows():
        tipo_producto = _normalizar(producto["tipo_mascota"])
        edad_producto = _normalizar(producto["edad_recomendada"])
        tamano_producto = _normalizar(producto["tamano"])
        categoria_producto = _normalizar(producto["categoria"])

        # El tipo de mascota es obligatorio.
        if tipo_producto != tipo_usuario:
            continue

        # No se recomiendan productos de otra edad.
        if edad_producto != edad_usuario:
            continue

        puntaje = 50 + 30
        motivos = [
            f"es compatible con mascotas tipo {producto['tipo_mascota']}",
            f"coincide con la edad {producto['edad_recomendada']}",
        ]

        # El tamaño solo se evalúa si se proporciona.
        if tamano_usuario:
            if tamano_producto in (tamano_usuario, "todos"):
                puntaje += 15
                motivos.append("coincide con el tamaño seleccionado")
            else:
                puntaje -= 20
                motivos.append("presenta una compatibilidad de tamaño menor")

        # Compatible con categorías escritas con o sin tildes.
        if categoria_producto in compras:
            puntaje += 10
            motivos.append(
                f"relacionado con compras previas de {producto['categoria']}"
            )

        if _normalizar(producto["nivel_precio"]) == "premium":
            puntaje += 5
            motivos.append("es un producto premium")

        recomendaciones.append(
            {
                "producto": producto["nombre"],
                "marca": producto["marca"],
                "categoria": producto["categoria"],
                "puntaje": puntaje,
                "explicacion": "Recomendado porque " + " y ".join(motivos) + ".",
            }
        )

    recomendaciones.sort(
        key=lambda recomendacion: recomendacion["puntaje"],
        reverse=True,
    )

    return recomendaciones[:10]