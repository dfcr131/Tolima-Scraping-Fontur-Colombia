from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import re

# === Configuración del navegador ===
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# === Lista de palabras clave a buscar ===
keywords = [
    "hoteles Ibagué Tolima",
    "restaurantes Ibagué Tolima",
    "parques Ibagué Tolima",
    "museos Ibagué Tolima",
    "atracciones turísticas Ibagué Tolima"
]

all_data = []
seen_places = set()

# === Función para hacer scroll completo basado en cantidad de lugares cargados ===
def scroll_panel_completo():
    try:
        scrollable_div = driver.find_element(By.CLASS_NAME, "m6QErb")
    except:
        return

    seen_count = 0
    same_count = 0

    while True:
        # Obtener todos los lugares visibles
        places = driver.find_elements(By.CLASS_NAME, "hfpxzc")
        current_count = len(places)

        if current_count == seen_count:
            same_count += 1
            if same_count >= 5:  # Terminar si no hay cambios tras 5 intentos
                break
        else:
            same_count = 0

        seen_count = current_count

        if places:
            # Scroll hasta el último lugar visible
            driver.execute_script("arguments[0].scrollIntoView(true);", places[-1])
        time.sleep(2)

# === Iterar por cada palabra clave ===
for query in keywords:
    print(f"🔹 Buscando: {query}")
    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/"
    driver.get(url)
    time.sleep(5)

    # Scroll completo del panel lateral
    scroll_panel_completo()

    # Extraer lugares
    places = driver.find_elements(By.CLASS_NAME, "hfpxzc")
    print(f"  → Lugares detectados: {len(places)}")

    for idx, place in enumerate(places):
        try:
            name = place.get_attribute("aria-label")
            if not name or name in seen_places:
                continue
            seen_places.add(name)

            # Click para abrir ficha
            driver.execute_script("arguments[0].click();", place)
            time.sleep(3)

            # Categoría
            try:
                category = driver.find_element(By.CLASS_NAME, "DkEaL").text
            except:
                category = ""

            # Dirección
            try:
                address = driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"]').text
            except:
                address = ""

            # Rating
            try:
                rating = driver.find_element(By.CLASS_NAME, "MW4etd").text
            except:
                rating = ""

            # Reseñas
            try:
                reviews = driver.find_element(By.CLASS_NAME, "UY7F9").text
            except:
                reviews = "0"

            # Horarios
            try:
                hours = driver.find_element(By.CLASS_NAME, "OqCZI").text
            except:
                hours = ""

            # Coordenadas desde URL
            try:
                coords_url = driver.current_url.split("/@")[1].split(",")[:2]
                lat, lon = coords_url
            except:
                lat, lon = ("", "")

            all_data.append({
                "Nombre": name,
                "Categoría": category,
                "Dirección": address,
                "Lat": lat,
                "Lon": lon,
                "Rating": rating,
                "Reseñas": reviews,
                "Horarios": hours
            })
        except Exception as e:
            print(f"⚠️ Error en lugar {idx} ({name}): {e}")
            continue

# === Convertir a DataFrame y eliminar duplicados ===
df = pd.DataFrame(all_data)
df.drop_duplicates(subset=["Nombre", "Dirección"], inplace=True)

# === Limpiar datos ===
df = df.replace({r'[]': ''}, regex=True)
df["Reseñas"] = df["Reseñas"].astype(str).apply(lambda x: re.sub(r"\D", "", x))
df["Reseñas"] = df["Reseñas"].replace("", "0").astype(int)
df["Horarios"] = df["Horarios"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
df["Dirección"] = df["Dirección"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()

# === Guardar CSV unificado ===
df.to_csv("turismo_ibague_maps.csv", index=False, encoding="utf-8-sig")

driver.quit()
print(f"✅ CSV unificado generado con {len(df)} registros: turismo_ibague_maps.csv")
