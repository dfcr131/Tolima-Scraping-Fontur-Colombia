from bs4 import BeautifulSoup
import csv

# Cargar archivo HTML guardado de TripAdvisor
with open("tripadvisor_chaparral.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# Cada atracción está dentro de un <article class="GTuVU XJlaI">
attractions = soup.find_all("article", class_="GTuVU XJlaI")

data = []
for atr in attractions:
    # ======================
    # Nombre
    # ======================
    nombre_div = atr.find("div", class_="XfVdV o AIbhI")
    if nombre_div:
        # remover número (ej: "4.")
        span_num = nombre_div.find("span", class_="vAUKO")
        if span_num:
            span_num.extract()
        nombre = nombre_div.get_text(strip=True)
    else:
        nombre = "N/A"

    # ======================
    # Calificación
    # ======================
    calificacion_div = atr.find("div", {"data-automation": "bubbleRatingValue"})
    calificacion = calificacion_div.get_text(strip=True) if calificacion_div else "N/A"

    # ======================
    # Número de reseñas
    # ======================
    reseñas_div = atr.find("div", {"data-automation": "bubbleReviewCount"})
    num_reseñas = reseñas_div.get_text(strip=True).replace("(", "").replace(")", "") if reseñas_div else "N/A"

    # ======================
    # Etiquetas (ej: "Escapadas de un día")
    # ======================
    etiqueta_div = atr.find("div", class_="biGQs _P ZNjnF")
    etiquetas = etiqueta_div.get_text(strip=True) if etiqueta_div else "N/A"

    data.append([nombre, calificacion, num_reseñas, etiquetas])

# Guardar CSV
with open("atracciones_Chaparral.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Nombre", "Calificación", "Número de Reseñas", "Etiquetas"])
    writer.writerows(data)

print(f"✅ CSV generado con {len(data)} lugares")
