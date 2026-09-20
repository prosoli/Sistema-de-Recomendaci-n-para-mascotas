"""Recomendador de contenido implementado desde cero.

El modelo transforma las caracteristicas categoricas del catalogo en vectores
one-hot ponderados y calcula la similitud coseno sin usar scikit-learn. El tipo
de mascota y la etapa de vida son restricciones estrictas. Para completar la
cesta solo admite productos marcados explicitamente para todas las edades.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import unicodedata

import numpy as np
import pandas as pd


RUTA_CATALOGO = Path(__file__).parent / "productos.csv"
CAMPOS = ("tipo_mascota", "edad_recomendada", "tamano", "categoria", "nivel_precio")
PESOS = {
    "tipo_mascota": 5.0,
    "edad_recomendada": 3.0,
    "tamano": 1.5,
    "categoria": 2.5,
    "nivel_precio": 0.5,
}
CATEGORIAS_SENSIBLES_EDAD = {"alimentacion", "salud"}
TOKENS_ETAPA = (
    "puppy", "cachorro", "junior", "kitten", "juvenil", "baby", "young",
    "adult", "adulto", "senior", "mature", "ageing", "7+", "8+", "12+",
)

# El CSV original usaba cifras de demostracion similares a dolares. Para la
# version costarricense se interpretan como miles de colones y se redondean a
# centenas. Los productos contrastados con comercios locales tienen un precio
# de referencia explicito (setiembre de 2026).
PRECIOS_CRC_VERIFICADOS = {
    "Purina Pro Plan Puppy Razas Medianas": 19050,
    "Pro Plan Senior 7+ Cat 3 kg": 19950,
}


def _normalizar(valor: object) -> str:
    """Convierte texto a una representacion comparable y sin tildes."""
    if pd.isna(valor):
        return ""
    texto = str(valor).strip().lower()
    return "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caracter) != "Mn"
    )


@dataclass(frozen=True)
class PerfilUsuario:
    tipo_mascota: str
    edad: str
    compras_previas: tuple[str, ...] = ()
    tamano: str = ""
    nivel_precio: str = ""
    prioridad: str = ""


class RecomendadorContenido:
    """Modelo KNN de contenido con codificacion y coseno propios."""

    def __init__(self, productos: pd.DataFrame):
        self.productos = productos.reset_index(drop=True).copy()
        self.vocabulario: list[tuple[str, str]] = []
        self.indice: dict[tuple[str, str], int] = {}
        self._ajustar_vocabulario()
        self.vectores_productos = np.vstack(
            [self._vector_producto(fila) for _, fila in self.productos.iterrows()]
        )

    def _ajustar_vocabulario(self) -> None:
        for campo in CAMPOS:
            valores = sorted({_normalizar(valor) for valor in self.productos[campo]})
            for valor in valores:
                clave = (campo, valor)
                self.indice[clave] = len(self.vocabulario)
                self.vocabulario.append(clave)

    def _vector_vacio(self) -> np.ndarray:
        return np.zeros(len(self.vocabulario), dtype=float)

    def _activar(self, vector: np.ndarray, campo: str, valor: object) -> None:
        posicion = self.indice.get((campo, _normalizar(valor)))
        if posicion is not None:
            vector[posicion] = np.sqrt(PESOS[campo])

    def _vector_producto(self, producto: pd.Series) -> np.ndarray:
        vector = self._vector_vacio()
        for campo in CAMPOS:
            self._activar(vector, campo, producto[campo])
        return vector

    def _vector_perfil(self, perfil: PerfilUsuario) -> tuple[np.ndarray, np.ndarray]:
        vector = self._vector_vacio()
        mascara = np.zeros(len(self.vocabulario), dtype=bool)
        campos_activos: dict[str, list[str]] = {
            "tipo_mascota": [perfil.tipo_mascota],
            "edad_recomendada": [perfil.edad],
        }
        if perfil.tamano:
            campos_activos["tamano"] = [perfil.tamano]
        categorias_preferidas = list(perfil.compras_previas)
        if perfil.prioridad:
            categorias_preferidas.append(perfil.prioridad)
        if categorias_preferidas:
            campos_activos["categoria"] = categorias_preferidas
        if perfil.nivel_precio:
            campos_activos["nivel_precio"] = [perfil.nivel_precio]

        for campo, valores in campos_activos.items():
            for valor in valores:
                posicion = self.indice.get((campo, _normalizar(valor)))
                if posicion is not None:
                    vector[posicion] = np.sqrt(PESOS[campo])
            for posicion, (campo_vector, _) in enumerate(self.vocabulario):
                if campo_vector == campo:
                    mascara[posicion] = True
        return vector, mascara

    @staticmethod
    def _coseno(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
        norma = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
        if norma == 0:
            return 0.0
        return float(np.dot(vector_a, vector_b) / norma)

    def recomendar(self, perfil: PerfilUsuario, limite: int = 10) -> list[dict]:
        vector_usuario, mascara = self._vector_perfil(perfil)
        tipo = _normalizar(perfil.tipo_mascota)
        edad = _normalizar(perfil.edad)
        tamano = _normalizar(perfil.tamano)
        nivel_precio = _normalizar(perfil.nivel_precio)
        prioridad = _normalizar(perfil.prioridad)
        compras = {_normalizar(categoria) for categoria in perfil.compras_previas}
        candidatos: list[dict] = []

        for posicion, producto in self.productos.iterrows():
            if _normalizar(producto["tipo_mascota"]) != tipo:
                continue
            edad_exacta = _normalizar(producto["edad_recomendada"]) == edad
            edad_universal = _normalizar(producto["edad_recomendada"]) == "todas las edades"
            categoria = _normalizar(producto["categoria"])
            if not (edad_exacta or edad_universal):
                continue

            # Se compara contra el vector completo del producto. Así, un perfil
            # con pocos datos no obtiene artificialmente 100 % en todo.
            vector_producto = self.vectores_productos[posicion]
            similitud = self._coseno(vector_usuario, vector_producto)

            coincide_tamano = bool(tamano and _normalizar(producto["tamano"]) == tamano)
            coincide_precio = bool(
                nivel_precio and _normalizar(producto["nivel_precio"]) == nivel_precio
            )
            coincide_prioridad = bool(prioridad and categoria == prioridad)
            coincide_compra = categoria in compras

            # La similitud coseno aporta la mayor parte. Los bonos expresan
            # reglas de negocio transparentes y evitan puntajes saturados.
            puntaje = 55 + similitud * 32
            puntaje += 6 if edad_exacta else 2
            puntaje += 4 if coincide_tamano else 0
            puntaje += 3 if coincide_precio else 0
            puntaje += 6 if coincide_prioridad else 0
            puntaje += 3 if coincide_compra else 0
            puntaje = int(round(max(55, min(98, puntaje))))

            motivos = [f"es para {producto['tipo_mascota'].lower()}"]
            if edad_exacta:
                motivos.append(f"coincide con la etapa {producto['edad_recomendada'].lower()}")
            else:
                motivos.append("está clasificado para todas las edades")
            if coincide_tamano:
                motivos.append("coincide con el tamaño indicado")
            if coincide_prioridad:
                motivos.append(f"responde a tu prioridad de {producto['categoria'].lower()}")
            if coincide_compra:
                motivos.append(f"se relaciona con tus compras de {producto['categoria'].lower()}")
            if coincide_precio:
                motivos.append("encaja con el presupuesto elegido")

            candidatos.append(
                {
                    "id_producto": int(producto["id_producto"]),
                    "producto": str(producto["nombre"]),
                    "marca": str(producto["marca"]),
                    "tipo_mascota": str(producto["tipo_mascota"]),
                    "categoria": str(producto["categoria"]),
                    "edad_recomendada": str(producto["edad_recomendada"]),
                    "tamano": str(producto["tamano"]),
                    "nivel_precio": str(producto["nivel_precio"]),
                    "precio": float(producto["precio"]),
                    "descripcion": str(producto["descripcion"]),
                    "puntaje": puntaje,
                    "similitud": round(similitud, 4),
                    "coincidencia_edad": edad_exacta,
                    "edad_universal": edad_universal,
                    "coincidencia_tamano": coincide_tamano,
                    "coincidencia_prioridad": coincide_prioridad,
                    "explicacion": "Recomendado porque " + ", ".join(motivos) + ".",
                }
            )

        candidatos.sort(
            key=lambda item: (
                item["coincidencia_edad"],
                item["puntaje"],
                -item["precio"],
            ),
            reverse=True,
        )

        # Reordenamiento tipo MMR: mantiene relevancia, pero penaliza repetir
        # demasiadas veces la misma categoría o marca en la cesta.
        unicos: list[dict] = []
        nombres_vistos: set[str] = set()
        categorias_usadas: dict[str, int] = {}
        marcas_usadas: dict[str, int] = {}
        restantes = candidatos.copy()
        while restantes and len(unicos) < limite:
            def valor_diverso(item: dict) -> tuple[float, int, float]:
                categoria_item = _normalizar(item["categoria"])
                marca_item = _normalizar(item["marca"])
                penalizacion = categorias_usadas.get(categoria_item, 0) * 4.5
                penalizacion += marcas_usadas.get(marca_item, 0) * 1.5
                if prioridad and categoria_item == prioridad:
                    penalizacion *= 0.45
                return (
                    item["puntaje"] - penalizacion,
                    int(item["coincidencia_edad"]),
                    -item["precio"],
                )

            candidato = max(restantes, key=valor_diverso)
            restantes.remove(candidato)
            nombre = _normalizar(candidato["producto"])
            if nombre in nombres_vistos:
                continue
            nombres_vistos.add(nombre)
            categoria_item = _normalizar(candidato["categoria"])
            marca_item = _normalizar(candidato["marca"])
            categorias_usadas[categoria_item] = categorias_usadas.get(categoria_item, 0) + 1
            marcas_usadas[marca_item] = marcas_usadas.get(marca_item, 0) + 1
            unicos.append(candidato)
        return unicos


def cargar_catalogo(ruta: Path = RUTA_CATALOGO) -> pd.DataFrame:
    productos = pd.read_csv(ruta)
    nombres = productos["nombre"].map(_normalizar)
    uso_general_declarado = productos["subcategoria"].map(_normalizar).eq("uso general")
    sin_etapa_en_nombre = ~nombres.map(
        lambda nombre: any(token in nombre for token in TOKENS_ETAPA)
    )
    categoria_general = ~productos["categoria"].map(_normalizar).isin(
        CATEGORIAS_SENSIBLES_EDAD
    )
    productos_generales = uso_general_declarado | (categoria_general & sin_etapa_en_nombre)
    productos.loc[productos_generales, "edad_recomendada"] = "Todas las edades"
    productos.loc[productos_generales, "descripcion"] = productos.loc[
        productos_generales
    ].apply(
        lambda fila: (
            f"{fila['nombre']} apto para {str(fila['tipo_mascota']).lower()} "
            "de cualquier etapa."
        ),
        axis=1,
    )
    productos["precio"] = (productos["precio"].astype(float) * 1000 / 100).round() * 100
    for nombre, precio_crc in PRECIOS_CRC_VERIFICADOS.items():
        productos.loc[productos["nombre"] == nombre, "precio"] = precio_crc
    return productos


_MODELO = RecomendadorContenido(cargar_catalogo())


def recomendar(
    tipo_mascota: str,
    edad_recomendada: str,
    compras_previas: list[str] | tuple[str, ...] | None,
    tamano: str | None = None,
    nivel_precio: str | None = None,
    prioridad: str | None = None,
    limite: int = 10,
) -> list[dict]:
    """API publica compatible con la version original del proyecto."""
    perfil = PerfilUsuario(
        tipo_mascota=tipo_mascota,
        edad=edad_recomendada,
        compras_previas=tuple(compras_previas or ()),
        tamano=tamano or "",
        nivel_precio=nivel_precio or "",
        prioridad=prioridad or "",
    )
    return _MODELO.recomendar(perfil, limite=limite)
