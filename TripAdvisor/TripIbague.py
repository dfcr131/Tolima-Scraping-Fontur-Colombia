import csv
from bs4 import BeautifulSoup

# Cargar el archivo HTML local
with open("tripadvisor_ibague_1.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

data = []

# Cada tarjeta está en un <article class="GTuVU XJlaI">
cards = soup.find_all("article", class_="GTuVU XJlaI")

for card in cards:
    # =====================
    # Nombre de la atracción
    # =====================
    name_div = card.find("div", class_="XfVdV o AIbhI")
    name = name_div.get_text(strip=True) if name_div else "N/A"

    # =====================
    # Calificación
    # =====================
    rating_tag = card.find("div", attrs={"data-automation": "bubbleRatingValue"})
    rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"

    # =====================
    # Número de reseñas
    # =====================
    reviews_tag = card.find("div", attrs={"data-automation": "bubbleReviewCount"})
    reviews = reviews_tag.get_text(strip=True).replace("(", "").replace(")", "") if reviews_tag else "0"

    # =====================
    # Etiquetas
    # =====================
    tags_divs = card.find_all("div", class_="biGQs _P ZNjnF")
    tags = []
    for div in tags_divs:
        # Evitar confundir con reviews
        if not div.has_attr("data-automation"):
            tags.append(div.get_text(strip=True))
    tags_text = ", ".join(tags)

    data.append({
        "Nombre": name,
        "Calificación": rating,
        "Número de Reseñas": reviews,
        "Etiquetas": tags_text
    })

# =====================
# Guardar resultados en CSV
# =====================
with open("atracciones_ibague.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Nombre", "Calificación", "Número de Reseñas", "Etiquetas"])
    writer.writeheader()
    writer.writerows(data)

print(f"✅ Extraídos {len(data)} registros y guardados en atracciones_ibague.csv")
