import requests
import json
import pandas as pd
import os
import time
import re

# Configuración
OUTPUT_DIR = "data_vias_limpia"
CATALOGO_CSV = os.path.join("data", "catalogo_capas.csv")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def cargar_capas_desde_csv():
    capas = []
    if os.path.exists(CATALOGO_CSV):
        try:
            df = pd.read_csv(CATALOGO_CSV)
            for _, row in df.iterrows():
                # Limpiar nombre para archivo
                nombre_limpio = re.sub(r'[^\w\s-]', '', str(row['Nombre_Capa'])).strip().replace(' ', '_')
                capas.append({
                    "nombre": nombre_limpio,
                    "url": row['URL_Servicio']
                })
            print(f"Cargadas {len(capas)} capas desde el catálogo.")
        except Exception as e:
            print(f"Error leyendo catálogo: {e}")
    else:
        print("No se encontró el catálogo CSV.")
    return capas

def obtener_mapeo_dominios(url_capa):
    """Obtiene el diccionario de mapeo {campo: {codigo: descripcion}}"""
    print(f"Obteniendo metadatos de: {url_capa}")
    try:
        response = requests.get(f"{url_capa}?f=json", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        mapeo = {}
        for field in data.get('fields', []):
            if field.get('domain') and 'codedValues' in field['domain']:
                nombre_campo = field['name']
                valores = {cv['code']: cv['name'] for cv in field['domain']['codedValues']}
                mapeo[nombre_campo] = valores
                print(f"  - Dominio encontrado para '{nombre_campo}': {len(valores)} valores")
        return mapeo
    except Exception as e:
        print(f"Error obteniendo metadatos: {e}")
        return {}

def descargar_y_procesar(capa):
    nombre = capa["nombre"]
    url = capa["url"]
    
    output_file = os.path.join(OUTPUT_DIR, f"{nombre}_decodificado.csv")
    if os.path.exists(output_file):
        print(f"El archivo {output_file} ya existe. Saltando descarga.")
        return

    # 1. Obtener mapeos de dominio
    mapeos = obtener_mapeo_dominios(url)
    
    # 2. Descargar datos (Features) con paginación
    print(f"Descargando datos de: {nombre}...")
    all_features = []
    offset = 0
    record_count = 2000
    
    while True:
        try:
            query_url = f"{url}/query"
            params = {
                "where": "1=1",
                "outFields": "*",
                "f": "json",
                "resultRecordCount": record_count,
                "resultOffset": offset
            }
            
            response = requests.get(query_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            features = data.get('features', [])
            if not features:
                break
                
            all_features.extend(features)
            print(f"  - Descargados {len(features)} registros (Total: {len(all_features)})")
            
            if len(features) < record_count:
                break
                
            offset += record_count
            
        except Exception as e:
            print(f"Error descargando lote: {e}")
            break
    
    if not all_features:
        return

    # 3. Procesar y reemplazar dominios
    registros_procesados = []
    for feat in all_features:
        atributos = feat.get('attributes', {})
        nuevo_registro = {}
        
        for k, v in atributos.items():
            # Si el campo tiene dominio y el valor está en el mapeo, reemplazar
            if k in mapeos and v in mapeos[k]:
                nuevo_registro[k] = mapeos[k][v]
            else:
                nuevo_registro[k] = v
        
        registros_procesados.append(nuevo_registro)
        
    # 4. Guardar a CSV
    try:
        df = pd.DataFrame(registros_procesados)
        
        # Seleccionar columnas relevantes si se desea limpiar más
        # Por ahora guardamos todo pero con valores decodificados
        
        output_file = os.path.join(OUTPUT_DIR, f"{nombre}_decodificado.csv")
        # Usar utf-8-sig para asegurar compatibilidad con Excel y caracteres latinos
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"  - Guardado en: {output_file}")
        
    except Exception as e:
        print(f"Error guardando {nombre}: {e}")

def main():
    print("Iniciando descarga y procesamiento de dominios...")
    capas = cargar_capas_desde_csv()
    
    if not capas:
        print("No hay capas para procesar.")
        return

    for capa in capas:
        descargar_y_procesar(capa)
        time.sleep(1) # Pausa respetuosa
    print("\nProceso completado.")

if __name__ == "__main__":
    main()
