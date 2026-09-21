import sys
from pathlib import Path
import unittest


PROYECTO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROYECTO / "PetShop"))

from chatbot import extraer_datos, respuesta_para_perfil  # noqa: E402
from historial import crear_perfil_con_historial  # noqa: E402


class ChatbotTests(unittest.TestCase):
    def test_extrae_perfil_completo(self):
        perfil = extraer_datos(
            "Tengo un gato senior pequeño y compré productos de salud",
            {"compras_previas": []},
        )
        self.assertEqual(perfil["tipo_mascota"], "Gato")
        self.assertEqual(perfil["edad"], "Senior")
        self.assertEqual(perfil["tamano"], "Pequeño")
        self.assertEqual(perfil["compras_previas"], ["Salud"])
        self.assertTrue(perfil["compras_confirmadas"])

    def test_chatbot_entrega_diez_recomendaciones(self):
        perfil = {
            "tipo_mascota": "Conejo",
            "edad": "Cachorro",
            "compras_previas": [],
            "compras_confirmadas": True,
        }
        respuesta = respuesta_para_perfil(perfil)
        self.assertIn("10 recomendaciones", respuesta)
        self.assertIn("₡", respuesta)
        self.assertEqual(len(perfil["recomendaciones"]), 10)

    def test_historial_de_tienda_evitar_pregunta_de_compras(self):
        perfil = crear_perfil_con_historial()
        perfil.update({"tipo_mascota": "Perro", "edad": "Adulto"})
        respuesta = respuesta_para_perfil(perfil)
        self.assertNotIn("¿Qué categorías has comprado", respuesta)
        self.assertIn("10 recomendaciones", respuesta)
        self.assertTrue(perfil["compras_confirmadas"])
        self.assertTrue(perfil["compras_previas"])


if __name__ == "__main__":
    unittest.main()
