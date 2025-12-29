import json
import csv
import os
import re
import requests

def procesar_har():
    # Nombre exacto del archivo que ya está en la carpeta data
    ruta_har = r"C:\Users\User\Downloads\experience.arcgis.com.har"
    ruta_csv = os.path.join("data", "catalogo_capas.csv")

    if not os.path.exists(ruta_har):
        print(f"❌ No encontré el archivo en: {ruta_har}")
        return

    print(f"📂 Leyendo archivo HAR: {ruta_har} (esto puede tardar unos segundos)...")
    
    try:
        with open(ruta_har, 'r', encoding='utf-8', errors='ignore') as f:
            har_data = json.load(f)
    except Exception as e:
        print(f"Error leyendo el JSON del HAR: {e}")
        return

    urls_procesadas = set()
    capas_finales = []

    print("🔍 Buscando capas de ArcGIS en las URLs del tráfico...")

    entries = har_data.get('log', {}).get('entries', [])
    
    # Regex para encontrar URLs de capas (FeatureServer/X o MapServer/X)
    # Captura todo hasta el número de capa
    patron = re.compile(r"(https?://.*?/(?:FeatureServer|MapServer)/\d+)")

    for entry in entries:
        url = entry['request']['url']
        match = patron.search(url)
        
        if match:
            layer_url = match.group(1)
            
            if layer_url not in urls_procesadas:
                urls_procesadas.add(layer_url)
                print(f"  -> Encontrada posible capa: {layer_url}")
                
                # Intentar obtener el nombre real consultando el servicio
                try:
                    print(f"     Consultando metadatos...")
                    resp = requests.get(f"{layer_url}?f=json", timeout=5)
                    if resp.status_code == 200:
                        meta = resp.json()
                        nombre = meta.get('name', 'Sin Nombre')
                        id_capa = meta.get('id', layer_url.split('/')[-1])
                        
                        capas_finales.append({
                            'Nombre_Capa': nombre,
                            'ID': id_capa,
                            'URL_Servicio': layer_url
                        })
                        print(f"     ✅ Nombre: {nombre}")
                    else:
                        print(f"     ⚠️ No se pudo obtener nombre (Status {resp.status_code})")
                        # Agregar igual con nombre genérico
                        capas_finales.append({
                            'Nombre_Capa': f"Capa {layer_url.split('/')[-1]}",
                            'ID': layer_url.split('/')[-1],
                            'URL_Servicio': layer_url
                        })
                except Exception as e:
                    print(f"     ❌ Error consultando metadatos: {e}")
                    # Agregar igual
                    capas_finales.append({
                        'Nombre_Capa': f"Capa {layer_url.split('/')[-1]}",
                        'ID': layer_url.split('/')[-1],
                        'URL_Servicio': layer_url
                    })

    print(f"✅ ¡Éxito! Se encontraron {len(capas_finales)} capas únicas.")

    # Guardar en CSV
    if capas_finales:
        with open(ruta_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Nombre_Capa', 'ID', 'URL_Servicio']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(capas_finales)
        print(f"📄 Archivo guardado en: {ruta_csv}")
    else:
        print("⚠️ No se encontraron capas.")

if __name__ == "__main__":
    procesar_har()
