import pandas as pd
import os
import unicodedata

def buscar_datos_vias_debug(consulta):
    csv_folder = "data_vias_limpia"
    if not os.path.exists(csv_folder):
        return "Folder not found"
        
    def normalize(text):
        if not isinstance(text, str):
            text = str(text)
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').lower()

    palabras_clave = normalize(consulta).split()
    stop_words = ['el', 'la', 'los', 'las', 'de', 'en', 'y', 'a', 'que', 'es', 'un', 'una', 'cual', 'cuales', 'dame', 'muestrame', 'informacion', 'sobre', 'del', 'por']
    palabras_clave = [p for p in palabras_clave if p not in stop_words and len(p) > 2]
    
    print(f"Keywords: {palabras_clave}")

    coincidencias = []
    
    archivos_vias = [f for f in os.listdir(csv_folder) if f.startswith('Red_vial') and f.endswith('.csv')]

    for csv_file in archivos_vias:
        file_path = os.path.join(csv_folder, csv_file)
        try:
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='latin-1')
            
            # Debug: Print a sample row to check encoding
            # print(f"Sample from {csv_file}: {df.iloc[0]['NOMBRE_VIA']}")

            df_str = df.astype(str).apply(lambda x: ' '.join(x), axis=1).apply(normalize)
            
            def calcular_score_vectorizado(row_str):
                return sum(1 for palabra in palabras_clave if palabra in row_str)

            scores = df_str.apply(calcular_score_vectorizado)
            
            df['score'] = scores
            filas_encontradas = df[df['score'] > 0].sort_values('score', ascending=False)
            
            if not filas_encontradas.empty:
                print(f"\n--- Matches in {csv_file} ---")
                for _, row in filas_encontradas.head(5).iterrows():
                    print(f"Score: {row['score']}")
                    print(f"Via: {row.get('NOMBRE_VIA', 'N/A')}")
                    print(f"Codigo: {row.get('CODIGO_VIA', 'N/A')}")
                    print(f"Inicio: {row.get('INICIO', 'N/A')}")
                    print(f"Fin: {row.get('FIN', 'N/A')}")
                    print(f"Observaciones: {row.get('OBSERVACIONES', 'N/A')}")
                    print("-" * 20)
                    
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
            continue

buscar_datos_vias_debug("Vía Terciaria Santa Rosa De Los Palmares - Pueblo Nuevo")
