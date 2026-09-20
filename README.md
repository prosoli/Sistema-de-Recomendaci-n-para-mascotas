# Petly — recomendador de productos para mascotas

Petly es una aplicación educativa de Machine Learning que recomienda diez
productos según el tipo de mascota, su etapa de vida, tamaño, nivel de precio y
compras anteriores. Incluye un formulario visual y un chatbot guiado.

## Machine Learning desde cero

El proyecto usa un recomendador de contenido tipo KNN, sin `scikit-learn`:

1. Aprende el vocabulario de características del catálogo.
2. Codifica tipo, edad, tamaño, categoría y precio como vectores one-hot.
3. Pondera las características para dar prioridad a especie y edad.
4. Construye un vector de preferencias para el usuario.
5. Calcula manualmente la similitud coseno contra cada producto.
6. Ordena los vecinos más cercanos, elimina nombres repetidos y devuelve diez.

El modelo mantiene restricciones estrictas por especie y etapa de vida. Cuando
una combinación tiene pocos productos, solo puede completar con artículos
clasificados explícitamente para todas las edades; nunca utiliza productos de
otra etapa.

## Funciones

- Diez recomendaciones únicas y explicadas.
- Perfil por mascota, edad, tamaño, precio y compras previas.
- Prioridad principal y reordenamiento diverso por categoría y marca.
- Puntaje de afinidad de 0 a 99.
- Precio, categoría, descripción y motivo de cada resultado.
- Fotografías comerciales verificadas e imágenes ilustrativas identificadas.
- Chatbot basado en extracción de entidades y estado conversacional.
- Interfaz adaptable creada con Streamlit.
- Pruebas para las 18 combinaciones de especie y edad.

## Instalación

```powershell
git clone https://github.com/prosoli/Sistema-de-Recomendaci-n-para-mascotas.git
cd Sistema-de-Recomendaci-n-para-mascotas
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Ejecución

```powershell
python -m streamlit run PetShop\app.py
```

La aplicación estará disponible normalmente en `http://localhost:8501`.

La interfaz está localizada para Costa Rica: muestra colones, prioriza marcas
presentes en comercios locales y distingue los precios verificados de las
estimaciones del prototipo. Algunas fichas incluyen una fotografía y enlace a
la tienda costarricense utilizada como referencia.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

## Estructura

```text
PetShop/
  app.py              Interfaz Streamlit
  chatbot.py          Extracción de datos y conversación
  recomendacion.py    Modelo de contenido desde cero
  productos.csv       Catálogo de productos
tests/
  test_recomendacion.py
  test_chatbot.py
requirements.txt
```

## Nota académica

Este es un enfoque de aprendizaje no supervisado basado en contenido. No emplea
un modelo de lenguaje ni afirma calcular probabilidades clínicas: el porcentaje
mostrado es una puntuación de afinidad explicable obtenida a partir de la
similitud entre vectores.
