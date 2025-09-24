import csv
from bs4 import BeautifulSoup

# Abrir HTML local de Prado
with open("tripadvisor_prado.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

data = []

# Buscar todas las calificaciones
ratings = soup.find_all("div", attrs={"data-automation": "bubbleRatingValue"})

for rating_tag in ratings:
    rating = rating_tag.get_text(strip=True)

    # Número de reseñas
    reviews_tag = rating_tag.find_next("div", attrs={"data-automation": "bubbleReviewCount"})
    reviews = reviews_tag.get_text(strip=True).replace("(", "").replace(")", "") if reviews_tag else "0"

    # Nombre (arriba de la calificación)
    name_tag = rating_tag.find_previous("div", class_="biGQs")
    name = name_tag.get_text(strip=True) if name_tag else "N/A"

    # Categoría oficial (si existe en HTML)
    category_tag = rating_tag.find_next("div", class_="biGQs _P ZNjnF")
    category = category_tag.get_text(strip=True) if category_tag else ""

    # Si no hay categoría, asignar una según el nombre
    if not category or category == "N/A":
        if any(word in name.lower() for word in ["hotel", "hostal", "mansion", "club"]):
            category = "Alojamiento"
        elif any(word in name.lower() for word in ["rio", "represa", "laguna"]):
            category = "Atracción Natural"
        else:
            category = "Otro"

    data.append({
        "Nombre": name,
        "Calificación": rating,
        "Número de Reseñas": reviews,
        "Etiqueta": category
    })

# Guardar en CSV
with open("atracciones_prado.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Nombre", "Calificación", "Número de Reseñas", "Categoría"])
    writer.writeheader()
    writer.writerows(data)

print("✅ CSV generado: atracciones_prado.csv")
