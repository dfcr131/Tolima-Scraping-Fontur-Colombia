
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

# === Configuración del navegador ===
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# === Búsquedas ===
keywords = ["museos Chaparral Tolima"]
all_data = []

# --- Funciones auxiliares ---
def scroll_left_panel():
    attempts = 0
    last_count = 0
    while attempts < 5:
        places = driver.find_elements(By.CLASS_NAME, "hfpxzc")
        count = len(places)
        if count == last_count:
            attempts += 1
        else:
            attempts = 0
            last_count = count
        if places:
            driver.execute_script("arguments[0].scrollIntoView();", places[-1])
        time.sleep(1.2)

def scroll_right_panel(panel):
    last_height = -1
    while True:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", panel)
        time.sleep(0.6)
        new_height = driver.execute_script("return arguments[0].scrollTop", panel)
        if new_height == last_height:
            break
        last_height = new_height

def safe_substr(s, n=20):
    clean = "".join(ch for ch in s if ch not in ['"', "'"]).strip()
    return clean[:n] if clean else s[:n]

def find_visible_text(container, xpaths, timeout=6):
    end = time.time() + timeout
    while time.time() < end:
        for xp in xpaths:
            try:
                el = container.find_element(By.XPATH, xp)
                txt = el.text.strip()
                if txt:
                    return txt
            except Exception:
                continue
        time.sleep(0.25)
    return ""

# === Scraping principal ===
for query in keywords:
    print(f"🔹 Buscando: {query}")
    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/"
    driver.get(url)
    time.sleep(4)

    # cargar la lista completa
    scroll_left_panel()
    time.sleep(1)
    places_count = len(driver.find_elements(By.CLASS_NAME, "hfpxzc"))
    print(f"  → Lugares detectados: {places_count}")

    for i in range(places_count):
        try:
            places = driver.find_elements(By.CLASS_NAME, "hfpxzc")
            if i >= len(places):
                print(f"    ⚠ El índice {i} ya no existe (lista reducida).")
                break
            place = places[i]

            name = place.get_attribute("aria-label")
            if not name:
                print(f"    ⚠ Elemento {i+1} sin aria-label, saltando.")
                continue

            # click seguro
            for attempt in range(3):
                try:
                    driver.execute_script("arguments[0].click();", place)
                    break
                except StaleElementReferenceException:
                    time.sleep(0.6)
                    places = driver.find_elements(By.CLASS_NAME, "hfpxzc")
                    place = places[i]

            # esperar carga
            WebDriverWait(driver, 8).until(lambda d: "/@" in d.current_url or "/place/" in d.current_url)

            # panel derecho
            try:
                right_panel = WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb"))
                )
            except:
                right_panel = driver.find_element(By.TAG_NAME, "body")

            scroll_right_panel(right_panel)
            time.sleep(0.6)

            # === Datos ===
            substr = safe_substr(name, 18)

            # Rating y reseñas
            rating = find_visible_text(right_panel, [
                ".//span[@class='MW4etd']",
                ".//span[@aria-hidden='true']"
            ], timeout=4)

            reviews = find_visible_text(right_panel, [
                ".//span[contains(text(),'reseña')]",
                ".//a[contains(text(),'reseña')]"
            ], timeout=4)

            if reviews:
                reviews = (
                    reviews.replace("reseñas", "")
                           .replace("reseña", "")
                           .replace("(", "")
                           .replace(")", "")
                           .strip()
                )

            # Categoría
            category = find_visible_text(right_panel, [
                ".//button[contains(@jsaction,'pane.rating.category')]",
                ".//div[contains(@class,'DkEaL')]"
            ], timeout=3)

            # Dirección
            address = find_visible_text(right_panel, [
                ".//button[@data-item-id='address']",
                ".//div[contains(@class,'rogA2c')]",
                ".//span[contains(@class,'Io6YTe')]"
            ], timeout=3)

            # Horarios
            hours = find_visible_text(right_panel, [
                ".//div[contains(@class,'OqCZI')]",
                ".//span[contains(text(),'Horario')]"
            ], timeout=3)

            # Coordenadas desde URL
            if "/@" in driver.current_url:
                coords = driver.current_url.split("/@")[1].split(",")[:2]
                lat, lon = coords
            else:
                lat, lon = "", ""

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

            print(f"    ✔ {i+1}/{places_count}: {name} → ⭐{rating} ({reviews})")
            time.sleep(0.9)

        except Exception as e:
            print(f"    ❌ Error en lugar {i+1}: {repr(e)}")
            time.sleep(0.8)
            continue

# Guardar CSV dinámico
df = pd.DataFrame(all_data)
filename = keywords[0].replace(" ", "_") + ".csv"
df.to_csv(filename, index=False, encoding="utf-8-sig")
print(f"\n✅ Scraping finalizado. Datos guardados en {filename}")
driver.quit()
