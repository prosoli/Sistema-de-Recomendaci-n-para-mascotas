"""Historial de compras que la tienda mantiene para el cliente activo.

En producción estos datos vendrían del sistema de ventas, CRM o facturación.
El prototipo usa registros locales para demostrar la integración sin pedirle al
cliente que seleccione manualmente sus compras anteriores.
"""

from __future__ import annotations


CLIENTE_ACTUAL_ID = "C-1042"

CLIENTES = {
    "C-1042": {
        "nombre": "Cliente frecuente",
        "compras_previas": ["Alimentacion", "Higiene"],
    },
    "C-2085": {
        "nombre": "Cliente ocasional",
        "compras_previas": ["Juguetes", "Accesorios"],
    },
    "C-3107": {
        "nombre": "Cliente nuevo",
        "compras_previas": [],
    },
}


def obtener_cliente(cliente_id: str = CLIENTE_ACTUAL_ID) -> dict:
    """Devuelve una copia del registro asociado a la sesión de tienda."""
    cliente_resuelto = cliente_id if cliente_id in CLIENTES else CLIENTE_ACTUAL_ID
    registro = CLIENTES[cliente_resuelto]
    return {
        "id": cliente_resuelto,
        "nombre": registro["nombre"],
        "compras_previas": list(registro["compras_previas"]),
    }


def crear_perfil_con_historial(cliente_id: str = CLIENTE_ACTUAL_ID) -> dict:
    """Crea un perfil con el historial personal registrado para el cliente."""
    cliente = obtener_cliente(cliente_id)
    return {
        "cliente_id": cliente["id"],
        "compras_previas": cliente["compras_previas"],
        "compras_confirmadas": True,
    }
