# Sistema-de-Recomendaci-n-para-mascotas
Sistema de recomendaciones  basado en tipo de mascota, edad y  compras previas.  
# Petly - Pet Product Recommendation System

## Overview
Petly is a pet product recommendation system designed to help pet owners find the best products for their furry friends. By inputting their pet's type, age, and recent purchases, users can receive personalized product recommendations.

## Project Structure
```
PetShop
├── app.py               # Main Streamlit application for user interface
├── recomendacion.py     # Contains the recommendation logic
├── productos.csv        # Catalog of pet products
├── requirements.txt     # Lists project dependencies
└── README.md            # Documentation for the project
```

## Setup Instructions
1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd PetShop
   ```

2. **Install dependencies**:
   Make sure you have Python installed, then run:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application**:
   Start the Streamlit application with the following command:
   ```
   streamlit run app.py
   ```

## Usage
- Open your web browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`).
- Select the type of pet and age from the dropdown menus.
- Choose any recent purchases from the multi-select box.
- Click the "Generate Recommendations" button to view the top 10 recommended products along with their scores.
