import pandas as pd
import os

def buscar_datos_vias(consulta):
    csv_folder = "data_vias_limpia"
    if not os.path.exists(csv_folder):
        return "Folder not found"
        
    palabras_clave = consulta.lower().split()
    stop_words = ['el', 'la', 'los', 'las', 'de', 'en', 'y', 'a', 'que', 'es', 'un', 'una', 'cual', 'cuales', 'dame', 'muestrame', 'informacion', 'sobre']
    palabras_clave = [p for p in palabras_clave if p not in stop_words and len(p) > 2]
    
    print(f"Query: '{consulta}' -> Keywords: {palabras_clave}")
    
    if not palabras_clave:
        return "No keywords"

    coincidencias = []
    
    for csv_file in os.listdir(csv_folder):
        if not csv_file.endswith('.csv'):
            continue
            
        file_path = os.path.join(csv_folder, csv_file)
        try:
            df = pd.read_csv(file_path)
            
            def calcular_score(row):
                row_str = " ".join(row.astype(str)).lower()
                return sum(1 for palabra in palabras_clave if palabra in row_str)

            df_search = df.copy()
            df_search['score'] = df_search.apply(calcular_score, axis=1)
            
            filas_encontradas = df_search[df_search['score'] > 0].sort_values('score', ascending=False)
            
            if not filas_encontradas.empty:
                print(f"  File {csv_file}: Found {len(filas_encontradas)} matches. Top score: {filas_encontradas.iloc[0]['score']}")
                for _, row in filas_encontradas.head(3).iterrows():
                    info = f"FUENTE: {csv_file} (Relevancia: {row['score']})\n"
                    for col, val in row.items():
                        if col != 'score' and pd.notna(val) and str(val).strip() != "":
                            info += f"- {col}: {val}\n"
                    coincidencias.append(info)
                    
        except Exception as e:
            print(f"Error leyendo {csv_file}: {e}")
            continue

    if coincidencias:
        return "\n".join(coincidencias[:5])
    else:
        return "No matches found"

# Test cases
print("--- TEST 1 ---")
print(buscar_datos_vias("estado de la via en amalfi"))
print("\n--- TEST 2 ---")
print(buscar_datos_vias("vias en el norte"))
print("\n--- TEST 3 ---")
print(buscar_datos_vias("tunel toyo"))
