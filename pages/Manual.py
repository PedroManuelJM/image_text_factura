import streamlit as st
import base64
from PIL import Image

st.title("Manual de uso")
st.write("Se carga una imagen y se extrae los datos correspondientes como: feha emisión, datos del cliente, datos de los productos (cantidad , unidad medida, descripción,valor unitario, precio total,monto total e IGV)")

# Cargar la imagen desde un archivo local
img = Image.open("/images/ejemplo.png")

# Mostrar la imagen
st.image(img, caption="Descripción de la imagen", use_column_width=True)