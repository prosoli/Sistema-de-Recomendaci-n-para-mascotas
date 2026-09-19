import streamlit as st
import pandas as pd
from recomendacion import recomendar

# Title of the application
st.title("Petly")

# Short description
st.write("Welcome to Petly! Find the perfect products for your furry friends based on their type, age, and your previous purchases.")

# Select box for pet type
tipo = st.selectbox("Select Pet Type:", ["Perro", "Gato", "Pájaro", "Reptil"])

# Select box for pet age
edad = st.selectbox("Select Pet Age:", ["Cachorro", "Adulto", "Senior"])

# Multi-select for recent purchases
compras = st.multiselect("Select Recent Purchases:", ["Comida", "Juguetes", "Accesorios", "Salud", "Higiene"])

# Button to generate recommendations
if st.button("Generate Recommendations"):
    recomendaciones = recomendar(tipo, edad, compras)
    
    # Display recommendations
    st.write("### Top 10 Recommended Products:")
    for rec in recomendaciones:
        st.write(f"{rec['producto']} - Score: {rec['puntaje']} 🐾")