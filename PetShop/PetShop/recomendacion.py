import pandas as pd


def recomendar(tipo, edad, compras):

    productos = pd.read_csv("productos.csv")

    recomendaciones = []

    for _, producto in productos.iterrows():

        # No recomendar otra especie
        if producto["tipo_mascota"] != tipo:
            continue


        puntaje = 0


        # Coincidencia mascota
        puntaje += 5


        # Coincidencia edad
        if producto["edad_recomendada"] == edad:
            puntaje += 5


        # Compras previas
        if producto["categoria"] in compras:
            puntaje += 3


        recomendaciones.append(
            {
                "producto": producto["nombre"],
                "puntaje": puntaje
            }
        )


    recomendaciones.sort(
        key=lambda x: x["puntaje"],
        reverse=True
    )


    return recomendaciones[:10]