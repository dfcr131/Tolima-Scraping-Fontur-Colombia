from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re

# === Configuración del navegador ===
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# === Lista de palabras clave a buscar ===
keywords = [
    "hoteles Chaparral Tolima",
    "restaurantes Chaparral Tolima",
    "parques Chaparral Tolima",
    "museos Chaparral Tolima",
    "atracciones turísticas Chaparral Tolima"
]

all_data = []

# === Función para hacer scroll en el panel izquierdo (lista de resultados) ===
def scroll_left_panel():
    attempts = 0
    last_count = 0
    while attempts < 5:  # se detiene cuando no carga más
        places = driver.find_elements(By.CLASS_NAME, "hfpxzc")
        count = len(places)
        if count == last_count:
            attempts += 1
        else:
            attempts = 0
            last_count = count
        if places:
            driver.execute_script("arguments[0].scrollIntoView();", places[-1])
        time.sleep(1.5)

# === Función para hacer scroll en el panel derecho (ficha del lugar) ===
def scroll_right_panel(panel):
    last_height = -1
    while True:
        driver.execute_script("arguments[0].scrollBy(0, 500)", panel)
        time.sleep(0.8)
        new_height = driver.execute_script("return arguments[0].scrollTop", panel)
        if new_height == last_height:  # ya no hay más que cargar
            break
        last_height = new_height

# === Recorrer todas las palabras clave ===
for query in keywords:
    print(f"🔹 Buscando: {query}")
    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/"
    driver.get(url)
    time.sleep(4)

    # Hacer scroll para cargar todos los lugares
    scroll_left_panel()
    places = driver.find_elements(By.CLASS_NAME, "hfpxzc")
    print(f"  → Lugares detectados: {len(places)}")

    for idx, place in enumerate(places, start=1):
        try:
            name = place.get_attribute("aria-label")
            if not name:
                continue

            # Clic en el lugar
            driver.execute_script("arguments[0].click();", place)

            # Esperar que el nombre del panel derecho coincida
            try:
                WebDriverWait(driver, 10).until(
                    EC.text_to_be_present_in_element((By.CLASS_NAME, "DUwDvf"), name)
                )
            except:
                print(f"⚠ El nombre no coincidió para {name}, reintentando...")
                time.sleep(2)

            # Esperar que aparezca el panel derecho
            right_panel = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.Nv2PK"))
            )

            # Scroll en el panel derecho para cargar todo
            scroll_right_panel(right_panel)
            time.sleep(1)

            # Esperar a que cambie la URL para tomar coords
            WebDriverWait(driver, 10).until(lambda d: "/@" in d.current_url)
            coords_url = driver.current_url.split("/@")[1].split(",")[:2]
            lat, lon = coords_url

            # Extraer datos
            try:
                category = driver.find_element(By.CLASS_NAME, "DkEaL").text
            except:
                category = ""

            try:
                address = driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"]').text
            except:
                address = ""

            try:
                rating = driver.find_element(By.CLASS_NAME, "MW4etd").text
            except:
                rating = ""

            try:
                reviews = driver.find_element(By.CLASS_NAME, "UY7F9").text
            except:
                reviews = ""

            try:
                hours = driver.find_element(By.CLASS_NAME, "OqCZI").text
            except:
                hours = ""

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

            print(f"    ✔ {idx}/{len(places)}: {name}")

            time.sleep(1.2)  # espera corta entre lugares

        except Exception as e:
            print(f"    ❌ Error en lugar {idx}: {e}")
            continue

# === Convertir a DataFrame y limpiar ===
df = pd.DataFrame(all_data)
df.drop_duplicates(subset=["Nombre", "Dirección"], inplace=True)

# Limpieza
df = df.replace({r'[]': ''}, regex=True)
df["Reseñas"] = df["Reseñas"].astype(str).apply(lambda x: re.sub(r"\D", "", x))
df["Reseñas"] = df["Reseñas"].replace("", "0").astype(int)
df["Horarios"] = df["Horarios"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
df["Dirección"] = df["Dirección"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()

# === Guardar CSV ===
df.to_csv("turismo_chaparral_maps.csv", index=False, encoding="utf-8-sig")
driver.quit()

print(f"✅ CSV unificado generado con {len(df)} registros: turismo_chaparral_maps.csv")
