import pandas as pd
import glob
import os

# Buscar todos los CSV en la carpeta actual
csv_files = glob.glob("*.csv")

dfs = []
for file in csv_files:
    try:
        df = pd.read_csv(file)
        
        # Si no existe la columna Ciudad, la creamos según el nombre del archivo
        if "Ciudad" not in df.columns:
            if "chaparral" in file.lower():
                df["Ciudad"] = "Chaparral"
            elif "ibague" in file.lower():
                df["Ciudad"] = "Ibagué"
            elif "prado" in file.lower():
                df["Ciudad"] = "Prado"
            else:
                df["Ciudad"] = os.path.splitext(file)[0]  # nombre del archivo como fallback
        
        dfs.append(df)
    except Exception as e:
        print(f"⚠️ Error al leer {file}: {e}")

# Unir todos los DataFrames
if dfs:
    final_df = pd.concat(dfs, ignore_index=True)

    # Guardar en CSV
    final_csv = "atracciones_tolima_compilado.csv"
    final_df.to_csv(final_csv, index=False, encoding="utf-8")

    # Guardar en Excel
    final_excel = "atracciones_tolima_compilado.xlsx"
    final_df.to_excel(final_excel, index=False, engine="openpyxl")

    print(f"✅ Archivos creados: {final_csv}, {final_excel}")
else:
    print("❌ No se encontraron archivos CSV en la carpeta.")
