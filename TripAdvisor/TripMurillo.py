import csv
from bs4 import BeautifulSoup
import re

# Cargar archivo HTML local
with open("tripadvisor_murillo.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

data = []

# Extraer el bloque de texto donde están las atracciones
text = soup.get_text("\n")

# Dividir por líneas
lines = [l.strip() for l in text.split("\n") if l.strip()]

i = 0
while i < len(lines):
    line = lines[i]

    # Buscar entradas tipo "31. Nombre"
    match = re.match(r"^\d+\.\s+(.*)", line)
    if match:
        name = match.group(1)

        # Inicializar datos
        rating = "N/A"
        reviews = "0"
        tags = "N/A"

        # Mirar las siguientes líneas
        j = i + 1
        while j < len(lines):
            next_line = lines[j]

            # Calificación (ej: "3,5")
            if re.match(r"^\d+,\d+$", next_line):
                rating = next_line
                j += 1
                continue

            # Reseñas (ej: "(2)")
            if re.match(r"^\(\d+\)$", next_line):
                reviews = next_line.strip("()")
                j += 1
                continue

            # Etiquetas (texto tipo "Cervecerías", "Parques infantiles", etc.)
            if not re.match(r"^\d+\.", next_line):
                tags = next_line
                j += 1
                continue

            break  # llega otra atracción
        i = j - 1

        data.append({
            "Nombre": name,
            "Calificación": rating,
            "Número de Reseñas": reviews,
            "Etiquetas": tags
        })
    i += 1

# Guardar en CSV
with open("atracciones_murillo.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Nombre", "Calificación", "Número de Reseñas", "Etiquetas"])
    writer.writeheader()
    writer.writerows(data)

print(f"✅ Extraídos {len(data)} registros y guardados en atracciones_murillo.csv")
