import sys
from pathlib import Path
import unittest


PROYECTO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROYECTO / "PetShop"))

from recomendacion import cargar_catalogo, recomendar  # noqa: E402


class RecomendadorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogo = cargar_catalogo()

    def test_entrega_diez_resultados_unicos_para_todos_los_perfiles(self):
        for tipo in self.catalogo["tipo_mascota"].unique():
            for edad in ("Cachorro", "Adulto", "Senior"):
                with self.subTest(tipo=tipo, edad=edad):
                    resultados = recomendar(tipo, edad, ["Accesorios"])
                    self.assertEqual(len(resultados), 10)
                    self.assertEqual(len({item["producto"].lower() for item in resultados}), 10)
                    self.assertTrue(all(item["tipo_mascota"] == tipo for item in resultados))
                    self.assertTrue(
                        all(
                            item["edad_recomendada"] in {edad, "Todas las edades"}
                            for item in resultados
                        )
                    )

    def test_no_relaja_edad_para_alimentacion_o_salud(self):
        resultados = recomendar("Ave", "Senior", [])
        for item in resultados:
            if not item["coincidencia_edad"]:
                self.assertNotIn(item["categoria"], {"Alimentacion", "Salud"})

    def test_compras_previas_priorizan_la_categoria(self):
        resultados = recomendar("Gato", "Senior", ["Salud"])
        self.assertEqual(resultados[0]["categoria"], "Salud")

    def test_normaliza_tildes_y_mayusculas(self):
        resultados = recomendar("PERRO", "cachorro", ["Alimentación"])
        self.assertEqual(len(resultados), 10)
        self.assertEqual(resultados[0]["categoria"], "Alimentacion")

    def test_precio_local_verificado_esta_en_colones(self):
        producto = self.catalogo.loc[
            self.catalogo["nombre"] == "Purina Pro Plan Puppy Razas Medianas"
        ].iloc[0]
        self.assertEqual(producto["precio"], 19050)

    def test_prioridad_afina_el_primer_resultado(self):
        resultados = recomendar(
            "Perro", "Cachorro", [], tamano="Mediano", prioridad="Juguetes"
        )
        self.assertEqual(resultados[0]["categoria"], "Juguetes")
        self.assertTrue(resultados[0]["coincidencia_prioridad"])

    def test_cesta_equilibrada_diversifica_categorias_y_puntajes(self):
        resultados = recomendar("Perro", "Cachorro", [])
        self.assertGreaterEqual(len({item["categoria"] for item in resultados}), 4)
        self.assertGreaterEqual(len({item["puntaje"] for item in resultados}), 2)


if __name__ == "__main__":
    unittest.main()
