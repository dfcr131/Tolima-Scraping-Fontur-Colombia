import pandas as pd
import re

# === 1. Cargar tu archivo CSV original ===
# (asegúrate de poner el nombre correcto del archivo exportado de Maps)
df = pd.read_csv("turismo_chaparral_maps.csv")

# === 2. Eliminar caracteres especiales raros (, , ) ===
df = df.replace({r'[]': ''}, regex=True)

# === 3. Limpiar la columna "Reseñas" → dejar solo número ===
df["Reseñas"] = df["Reseñas"].astype(str).apply(lambda x: re.sub(r"\D", "", x))
df["Reseñas"] = df["Reseñas"].replace("", "0").astype(int)

# === 4. Normalizar horarios → quitar saltos de línea y espacios extra ===
df["Horarios"] = df["Horarios"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()

# === 5. Limpiar dirección → quitar saltos de línea y espacios extra ===
df["Dirección"] = df["Dirección"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()

# === 6. Guardar archivos limpios ===
# CSV limpio
df.to_csv("turismo_chaparral_maps_limpio.csv", index=False, encoding="utf-8-sig")



print("✅ Limpieza terminada")
print("📂 Archivos generados: ")
print(" - turismo_chaparral_maps_limpio.csv")
print(" - turismo_chaparral_maps_limpio.xlsx")
