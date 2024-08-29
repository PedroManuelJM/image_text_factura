import streamlit as st
from PIL import Image
import pytesseract
import re
import pandas as pd
import io

# Dividir la pantalla en dos columnas
col1, col2 = st.columns(2)

# Título de la aplicación en la primera columna

st.title("Extracción de datos de facturas con OCR")

# Subir una imagen en la segunda columna

uploaded_file = st.file_uploader("Elige una imagen de la factura", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Abrir la imagen
    img = Image.open(uploaded_file)
    
    # Dividir el área restante en dos columnas
    col1, col2 = st.columns(2)
    
    # Mostrar la imagen en la primera columna
 
    st.image(img, caption="Factura cargada", use_column_width=True)
    
    # Extraer texto usando OCR
    text = pytesseract.image_to_string(img, lang='spa')  # lang='spa' para español
    
    # Expresiones regulares para extraer los datos específicos
    senor_pattern = r"Señor\(es\)\s+(.+)"
    ruc_pattern = r"RUC\s*:\s*(\d+)"
    igv_pattern = r"IGV\s*:\s*S/\s*(\d+\.\d{2})"
    subtotal_pattern = r"Sub Total Ventas\s*:\s*S/\s*(\d+\.\d{2})"
    
    # Buscar las coincidencias
    senor_match = re.search(senor_pattern, text)
    ruc_match = re.search(ruc_pattern, text)
    igv_match = re.search(igv_pattern, text)
    subtotal_match = re.search(subtotal_pattern, text)
    
    # Extraer los datos si son encontrados
    senor = senor_match.group(1) if senor_match else "No encontrado"
    ruc = ruc_match.group(1) if ruc_match else "No encontrado"
    igv = float(igv_match.group(1)) if igv_match else 0.0
    subtotal = float(subtotal_match.group(1)) if subtotal_match else 0.0
    
    # Calcular el monto total con y sin IGV
    monto_total_sin_igv = subtotal
    monto_total_con_igv = subtotal + igv
    
    # Mostrar los resultados en la segunda columna

    st.subheader("Resultados Extraídos:")
    st.write(f"**Señor(es):** {senor}")
    st.write(f"**RUC:** {ruc}")
    st.write(f"**Subtotal (sin IGV):** S/ {monto_total_sin_igv:.2f}")
    st.write(f"**IGV:** S/ {igv:.2f}")
    st.write(f"**Monto Total (con IGV):** S/ {monto_total_con_igv:.2f}")
        
    # Buscar una posible fecha con errores similares a '0110472024'
    fecha_emision = re.search(r'Fecha de Emisión\s*:?(\d{2})[^\d]*(\d{2})[^\d]*(\d{4})', text)
        
    # Si se encuentra la fecha, reconstruirla
    if fecha_emision:
            dia = fecha_emision.group(1)
            mes = fecha_emision.group(2)
            año = fecha_emision.group(3)
            fecha = f"{dia}/{mes}/{año}"
            st.write(f"**Fecha de Emisión:** {fecha}")
    else:
            st.write("Fecha de Emisión no encontrada.")
        
     # Patrón para extraer cantidad, unidad, descripción y valor unitario
    pattern = r"(\d+\.\d{2})\s+(\w+)\s+([\w\s]+)\s+(\d+\.\d{2})"
        
    # Buscar las coincidencias
    matches = re.findall(pattern, text)
        
    # Lista para almacenar detalles de la compra
    detalles_compra = []
        
    # Mostrar los resultados y realizar la multiplicación
    if matches:
            st.subheader("Detalles de la Compra:")
            for match in matches:
                cantidad, unidad, descripcion, valor_unitario = match
                
                # Convertir los valores a flotantes para la multiplicación
                cantidad = float(cantidad)
                valor_unitario = float(valor_unitario)
                total = cantidad * valor_unitario
                
                st.write(f"**Cantidad:** {cantidad}")
                st.write(f"**Unidad de Medida:** {unidad}")
                st.write(f"**Descripción:** {descripcion.strip()}")
                st.write(f"**Valor Unitario:** S/ {valor_unitario:.2f}")
                st.write(f"**Total (Cantidad x Valor Unitario):** S/ {total:.2f}")
                st.write("---")
                
                detalles_compra.append({
                    "Cantidad": cantidad,
                    "Unidad de Medida": unidad,
                    "Descripción": descripcion.strip(),
                    "Valor Unitario": valor_unitario,
                    "Total": total
                })
    else:
            st.write("No se encontraron coincidencias en la descripción del producto.")
        
    # Crear texto para copiar al portapapeles
    datos_texto = f"Señor(es): {senor}\nRUC: {ruc}\nSubtotal (sin IGV): S/ {monto_total_sin_igv:.2f}\nIGV: S/ {igv:.2f}\nMonto Total (con IGV): S/ {monto_total_con_igv:.2f}\nFecha de Emisión: {fecha}\n"
    if detalles_compra:
            datos_texto += "\nDetalles de la Compra:\n"
            for item in detalles_compra:
                datos_texto += f"Cantidad: {item['Cantidad']}\nUnidad de Medida: {item['Unidad de Medida']}\nDescripción: {item['Descripción']}\nValor Unitario: S/ {item['Valor Unitario']:.2f}\nTotal: S/ {item['Total']:.2f}\n---\n"
        
    # Mostrar área de texto para copiar
    st.subheader("Copiar Datos")
    st.text_area("Datos extraídos:", datos_texto, height=300)
        
    # Exportar a CSV
    if st.button("Exportar a CSV"):
            df = pd.DataFrame(detalles_compra)
            csv = df.to_csv(index=False)
            st.download_button("Descargar CSV", csv, "detalles_compra.csv", "text/csv")