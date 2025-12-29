import os
import time
import pandas as pd
import unicodedata
import difflib
import streamlit as st
from tqdm import tqdm
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

# Configuración de rutas
DATA_PATH = "data"
DB_PATH = "chroma_db"

# Configurar API Key de OpenAI
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
else:
    # Fallback for local development if not using secrets.toml, but better to warn
    # os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
    pass

def buscar_datos_vias(consulta):
    """
    Busca en los archivos CSV de vías información relevante.
    """
    try:
        csv_folder = "data_vias_limpia"
        if not os.path.exists(csv_folder):
            return ""
            
        def normalize(text):
            if not isinstance(text, str):
                text = str(text)
            return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').lower().strip()

        palabras_clave = normalize(consulta).split()
        # Filtrar palabras comunes
        stop_words = ['el', 'la', 'los', 'las', 'de', 'en', 'y', 'a', 'que', 'es', 'un', 'una', 'cual', 'cuales', 'dame', 'muestrame', 'informacion', 'sobre', 'del', 'por']
        palabras_clave = [p for p in palabras_clave if p not in stop_words and len(p) > 2]
        
        if not palabras_clave:
            return ""

        coincidencias = []
        
        # --- LÓGICA DE ANÁLISIS ESTADÍSTICO (CONTEOS Y TOTALES) ---
        # Detectar si el usuario pide totales o cantidades
        keywords_estadisticas = ['total', 'cantidad', 'cuantos', 'numero', 'suma', 'cuantas', 'cuanto']
        pide_estadistica = any(k in normalize(consulta) for k in keywords_estadisticas)
        
        if pide_estadistica:
            try:
                # Cargar lista de municipios para identificar de cuál se habla
                municipios_path = os.path.join(csv_folder, "Municipios_decodificado.csv")
                municipio_detectado = None
                subregion_detectada = None
                
                if os.path.exists(municipios_path):
                    df_mun = pd.read_csv(municipios_path, encoding='utf-8-sig')
                    # Buscar si algún municipio está en la consulta
                    for mun in df_mun['MPIO_NOMBRE'].dropna().unique():
                        if normalize(str(mun)) in normalize(consulta):
                            municipio_detectado = str(mun)
                            break
                
                # Detectar subregión si no hay municipio
                if not municipio_detectado:
                    # Lista de subregiones de Antioquia
                    subregiones_antioquia = ['Urabá', 'Bajo Cauca', 'Nordeste', 'Norte', 'Occidente', 
                                            'Oriente', 'Suroeste', 'Valle de Aburrá', 'Magdalena Medio']
                    for subregion in subregiones_antioquia:
                        if normalize(subregion) in normalize(consulta):
                            subregion_detectada = subregion
                            break
                
                if municipio_detectado:
                    # Caso 1: Conteo y Sumas de NECESIDADES
                    if 'necesidad' in normalize(consulta):
                        necesidades_path = os.path.join(csv_folder, "Base_Necesidades.csv")
                        if os.path.exists(necesidades_path):
                            df_nec = pd.read_csv(necesidades_path, encoding='utf-8-sig')
                            # Filtrar por municipio (normalizando para evitar errores de tildes)
                            # Crear columna temporal normalizada para el filtro
                            df_nec['mun_norm'] = df_nec['MUNICIPIO'].apply(lambda x: normalize(str(x)) if pd.notna(x) else "")
                            mun_target_norm = normalize(municipio_detectado)
                            
                            df_filtered = df_nec[df_nec['mun_norm'] == mun_target_norm]
                            conteo = df_filtered.shape[0]
                            
                            info_stat = f"ESTADÍSTICA OFICIAL: El municipio de {municipio_detectado} tiene un total de {conteo} necesidades registradas en la base de datos."
                            
                            # --- LÓGICA DE SUMA FINANCIERA ---
                            # Detectar si piden dinero/aportes
                            keywords_dinero = ['aporte', 'inversion', 'costo', 'valor', 'presupuesto', 'dinero', 'plata', 'cuanto']
                            if any(k in normalize(consulta) for k in keywords_dinero):
                                col_target = None
                                nombre_concepto = "valor total"
                                
                                # Determinar qué columna sumar
                                if 'aporte' in normalize(consulta) or 'gobernacion' in normalize(consulta):
                                    col_target = 'APORTE GOB'
                                    nombre_concepto = "Aporte Total de la Gobernación"
                                elif 'valor' in normalize(consulta) or 'costo' in normalize(consulta) or 'presupuesto' in normalize(consulta):
                                    col_target = 'VALOR NECESIDAD SIF'
                                    nombre_concepto = "Valor Total de las Necesidades (SIF)"
                                
                                if col_target and col_target in df_filtered.columns:
                                    # Función para limpiar moneda
                                    def clean_money(val):
                                        try:
                                            if pd.isna(val): return 0.0
                                            return float(str(val).replace('$', '').replace(',', '').strip())
                                        except:
                                            return 0.0
                                    
                                    total_sum = df_filtered[col_target].apply(clean_money).sum()
                                    
                                    # Verificar si todos los valores son idénticos (posible indicador municipal)
                                    valores = df_filtered[col_target].apply(clean_money).tolist()
                                    valores = [v for v in valores if v > 0]
                                    es_valor_repetido = False
                                    if len(valores) > 1 and len(set(valores)) == 1:
                                        es_valor_repetido = True
                                    
                                    info_stat += f"\n- {nombre_concepto}: ${total_sum:,.2f}"
                                    
                                    if es_valor_repetido:
                                        val_unico = valores[0]
                                        info_stat += f"\n  (Nota: El valor ${val_unico:,.2f} se repite en los {len(valores)} registros encontrados. Verifique si este es un indicador municipal constante o un aporte por proyecto)."
                                    else:
                                        info_stat += f"\n  (Calculado sumando los valores de los {len(valores)} registros encontrados)."
                            
                            coincidencias.append({'text': info_stat, 'score': 999}) # Score altísimo para que salga primero
                            
                    # Caso 2: Conteo de VÍAS (Ejemplo)
                    elif 'via' in normalize(consulta) or 'carretera' in normalize(consulta):
                        # Buscar en terciarias por defecto
                        vias_path = os.path.join(csv_folder, "Red_vial_terciaria_decodificado.csv")
                        if os.path.exists(vias_path):
                            df_vias = pd.read_csv(vias_path, encoding='utf-8-sig')
                            df_vias['mun_norm'] = df_vias['MUNICIPIO'].apply(lambda x: normalize(str(x)) if pd.notna(x) else "")
                            mun_target_norm = normalize(municipio_detectado)
                            conteo = df_vias[df_vias['mun_norm'] == mun_target_norm].shape[0]
                            
                            info_stat = f"ESTADÍSTICA OFICIAL: El municipio de {municipio_detectado} tiene un total de {conteo} vías terciarias registradas."
                            coincidencias.append({'text': info_stat, 'score': 999})

                    # Caso 3: Conteo de RADICADOS / SOLICITUDES
                    elif 'radicado' in normalize(consulta) or 'solicitud' in normalize(consulta):
                        radicados_path = os.path.join(csv_folder, "Base_Radicados.csv")
                        if os.path.exists(radicados_path):
                            df_rad = pd.read_csv(radicados_path, encoding='utf-8-sig')
                            df_rad['mun_norm'] = df_rad['MUNICIPIO'].apply(lambda x: normalize(str(x)) if pd.notna(x) else "")
                            mun_target_norm = normalize(municipio_detectado)
                            conteo = df_rad[df_rad['mun_norm'] == mun_target_norm].shape[0]
                            
                            info_stat = f"ESTADÍSTICA OFICIAL: El municipio de {municipio_detectado} tiene un total de {conteo} radicados/solicitudes registrados."
                            coincidencias.append({'text': info_stat, 'score': 999})

                elif subregion_detectada:
                    # Caso: Estadísticas por SUBREGIÓN
                    # Caso 1: Conteo y Sumas de NECESIDADES
                    if 'necesidad' in normalize(consulta):
                        necesidades_path = os.path.join(csv_folder, "Base_Necesidades.csv")
                        if os.path.exists(necesidades_path):
                            df_nec = pd.read_csv(necesidades_path, encoding='utf-8-sig')
                            # Filtrar por subregión (normalizando para evitar errores de tildes)
                            df_nec['subregion_norm'] = df_nec['SUBREGION'].apply(lambda x: normalize(str(x)) if pd.notna(x) else "")
                            subregion_target_norm = normalize(subregion_detectada)
                            
                            df_filtered = df_nec[df_nec['subregion_norm'] == subregion_target_norm]
                            conteo = df_filtered.shape[0]
                            
                            info_stat = f"ESTADÍSTICA OFICIAL: La subregión de {subregion_detectada} tiene un total de {conteo} necesidades registradas en la base de datos."
                            
                            # --- LÓGICA DE SUMA FINANCIERA ---
                            keywords_dinero = ['aporte', 'inversion', 'costo', 'valor', 'presupuesto', 'dinero', 'plata', 'cuanto']
                            if any(k in normalize(consulta) for k in keywords_dinero):
                                col_target = None
                                nombre_concepto = "valor total"
                                
                                # Determinar qué columna sumar
                                if 'aporte' in normalize(consulta) or 'gobernacion' in normalize(consulta):
                                    col_target = 'APORTE GOB'
                                    nombre_concepto = "Aporte Total de la Gobernación"
                                elif 'valor' in normalize(consulta) or 'costo' in normalize(consulta) or 'presupuesto' in normalize(consulta):
                                    col_target = 'VALOR NECESIDAD SIF'
                                    nombre_concepto = "Valor Total de las Necesidades (SIF)"
                                
                                if col_target and col_target in df_filtered.columns:
                                    # Función para limpiar moneda
                                    def clean_money(val):
                                        try:
                                            if pd.isna(val): return 0.0
                                            return float(str(val).replace('$', '').replace(',', '').strip())
                                        except:
                                            return 0.0
                                    
                                    total_sum = df_filtered[col_target].apply(clean_money).sum()
                                    
                                    info_stat += f"\n- {nombre_concepto}: ${total_sum:,.2f}"
                            
                            coincidencias.append({'text': info_stat, 'score': 999})
                    
                    # Caso 2: Conteo de VÍAS por subregión
                    elif 'via' in normalize(consulta) or 'carretera' in normalize(consulta):
                        vias_path = os.path.join(csv_folder, "Red_vial_terciaria_decodificado.csv")
                        if os.path.exists(vias_path):
                            df_vias = pd.read_csv(vias_path, encoding='utf-8-sig')
                            if 'SUBREGION' in df_vias.columns:
                                df_vias['subregion_norm'] = df_vias['SUBREGION'].apply(lambda x: normalize(str(x)) if pd.notna(x) else "")
                                subregion_target_norm = normalize(subregion_detectada)
                                conteo = df_vias[df_vias['subregion_norm'] == subregion_target_norm].shape[0]
                                
                                info_stat = f"ESTADÍSTICA OFICIAL: La subregión de {subregion_detectada} tiene un total de {conteo} vías terciarias registradas."
                                coincidencias.append({'text': info_stat, 'score': 999})
                    
                    # Caso 3: Conteo de RADICADOS / SOLICITUDES por subregión
                    elif 'radicado' in normalize(consulta) or 'solicitud' in normalize(consulta):
                        radicados_path = os.path.join(csv_folder, "Base_Radicados.csv")
                        if os.path.exists(radicados_path):
                            df_rad = pd.read_csv(radicados_path, encoding='utf-8-sig')
                            if 'SUBREGION' in df_rad.columns:
                                df_rad['subregion_norm'] = df_rad['SUBREGION'].apply(lambda x: normalize(str(x)) if pd.notna(x) else "")
                                subregion_target_norm = normalize(subregion_detectada)
                                conteo = df_rad[df_rad['subregion_norm'] == subregion_target_norm].shape[0]
                                
                                info_stat = f"ESTADÍSTICA OFICIAL: La subregión de {subregion_detectada} tiene un total de {conteo} radicados/solicitudes registrados."
                                coincidencias.append({'text': info_stat, 'score': 999})

                else:
                    # Caso General: Totales Globales (Sin municipio ni subregión específica)
                    if 'necesidad' in normalize(consulta):
                        necesidades_path = os.path.join(csv_folder, "Base_Necesidades.csv")
                        if os.path.exists(necesidades_path):
                            df_nec = pd.read_csv(necesidades_path, encoding='utf-8-sig')
                            conteo = df_nec.shape[0]
                            info_stat = f"ESTADÍSTICA GLOBAL: En total, hay {conteo} necesidades registradas en todo el departamento de Antioquia."
                            coincidencias.append({'text': info_stat, 'score': 999})
                            
                    elif 'radicado' in normalize(consulta) or 'solicitud' in normalize(consulta):
                        radicados_path = os.path.join(csv_folder, "Base_Radicados.csv")
                        if os.path.exists(radicados_path):
                            df_rad = pd.read_csv(radicados_path, encoding='utf-8-sig')
                            conteo = df_rad.shape[0]
                            info_stat = f"ESTADÍSTICA GLOBAL: En total, hay {conteo} radicados/solicitudes registrados en todo el departamento."
                            coincidencias.append({'text': info_stat, 'score': 999})

            except Exception as e:
                print(f"Error calculando estadísticas: {e}")

        # --- LÓGICA DE LISTADO (RADICADOS Y PROYECTOS) ---
        # Detectar si el usuario pide listar radicados o proyectos de un municipio o subregión
        keywords_listado = ['cuales', 'que radicados', 'que proyectos', 'lista', 'listado', 'dame los radicados', 'muestrame los radicados']
        pide_listado = any(k in normalize(consulta) for k in keywords_listado)
        
        if pide_listado:
            try:
                # Identificar municipio (reutilizamos lógica anterior o buscamos de nuevo)
                municipios_path = os.path.join(csv_folder, "Municipios_decodificado.csv")
                municipio_detectado = None
                subregion_detectada = None
                
                if os.path.exists(municipios_path):
                    df_mun = pd.read_csv(municipios_path, encoding='utf-8-sig')
                    for mun in df_mun['MPIO_NOMBRE'].dropna().unique():
                        if normalize(str(mun)) in normalize(consulta):
                            municipio_detectado = str(mun)
                            break
                
                # Detectar subregión si no hay municipio
                if not municipio_detectado:
                    subregiones_antioquia = ['Urabá', 'Bajo Cauca', 'Nordeste', 'Norte', 'Occidente', 
                                            'Oriente', 'Suroeste', 'Valle de Aburrá', 'Magdalena Medio']
                    for subregion in subregiones_antioquia:
                        if normalize(subregion) in normalize(consulta):
                            subregion_detectada = subregion
                            break
                
                if municipio_detectado:
                    mun_target_norm = normalize(municipio_detectado)
                    
                    # Listar RADICADOS
                    if 'radicado' in normalize(consulta):
                        radicados_path = os.path.join(csv_folder, "Base_Radicados.csv")
                        if os.path.exists(radicados_path):
                            df_rad = pd.read_csv(radicados_path, encoding='utf-8-sig')
                            df_rad['mun_norm'] = df_rad['MUNICIPIO'].apply(lambda x: normalize(str(x)) if pd.notna(x) else "")
                            
                            # Filtrar
                            resultados = df_rad[df_rad['mun_norm'] == mun_target_norm]
                            
                            if not resultados.empty:
                                info_list = f"LISTADO DE RADICADOS PARA {municipio_detectado}:\n"
                                # Tomar los primeros 10 para no saturar
                                for idx, row in resultados.head(10).iterrows():
                                    rad = row.get('RADICADO', 'S/N')
                                    proy = row.get('PROYECTOS', 'Sin descripción')
                                    fecha = row.get('FECHA', '')
                                    info_list += f"- Radicado: {rad} | Fecha: {fecha} | Proyecto: {proy}\n"
                                
                                if len(resultados) > 10:
                                    info_list += f"... y {len(resultados)-10} más."
                                    
                                coincidencias.append({'text': info_list, 'score': 998})

                    # Listar PROYECTOS/NECESIDADES
                    elif 'proyecto' in normalize(consulta) or 'necesidad' in normalize(consulta):
                        necesidades_path = os.path.join(csv_folder, "Base_Necesidades.csv")
                        if os.path.exists(necesidades_path):
                            df_nec = pd.read_csv(necesidades_path, encoding='utf-8-sig')
                            df_nec['mun_norm'] = df_nec['MUNICIPIO'].apply(lambda x: normalize(str(x)) if pd.notna(x) else "")
                            
                            resultados = df_nec[df_nec['mun_norm'] == mun_target_norm]
                            
                            if not resultados.empty:
                                info_list = f"LISTADO DE PROYECTOS/NECESIDADES PARA {municipio_detectado}:\n"
                                for idx, row in resultados.head(10).iterrows():
                                    nec = row.get('NECESIDAD', 'Sin descripción')
                                    fase = row.get('FASE PROYECTO', 'No definida')
                                    
                                    # Mapeo de fase
                                    try:
                                        fase_num = int(float(fase))
                                        mapa_fases = {1: "Perfil", 2: "Prefactibilidad", 3: "Factibilidad"}
                                        if fase_num in mapa_fases:
                                            fase = f"{fase_num} ({mapa_fases[fase_num]})"
                                    except:
                                        pass
                                        
                                    info_list += f"- Proyecto: {nec} | Fase: {fase}\n"
                                
                                if len(resultados) > 10:
                                    info_list += f"... y {len(resultados)-10} más."
                                    
                                coincidencias.append({'text': info_list, 'score': 998})

                elif subregion_detectada:
                    subregion_target_norm = normalize(subregion_detectada)
                    
                    # Listar RADICADOS por subregión
                    if 'radicado' in normalize(consulta):
                        radicados_path = os.path.join(csv_folder, "Base_Radicados.csv")
                        if os.path.exists(radicados_path):
                            df_rad = pd.read_csv(radicados_path, encoding='utf-8-sig')
                            if 'SUBREGION' in df_rad.columns:
                                df_rad['subregion_norm'] = df_rad['SUBREGION'].apply(lambda x: normalize(str(x)) if pd.notna(x) else "")
                                
                                # Filtrar
                                resultados = df_rad[df_rad['subregion_norm'] == subregion_target_norm]
                                
                                if not resultados.empty:
                                    info_list = f"LISTADO DE RADICADOS PARA LA SUBREGIÓN {subregion_detectada}:\n"
                                    # Tomar los primeros 10 para no saturar
                                    for idx, row in resultados.head(10).iterrows():
                                        rad = row.get('RADICADO', 'S/N')
                                        proy = row.get('PROYECTOS', 'Sin descripción')
                                        fecha = row.get('FECHA', '')
                                        mun = row.get('MUNICIPIO', '')
                                        info_list += f"- Radicado: {rad} | Municipio: {mun} | Fecha: {fecha} | Proyecto: {proy}\n"
                                    
                                    if len(resultados) > 10:
                                        info_list += f"... y {len(resultados)-10} más."
                                        
                                    coincidencias.append({'text': info_list, 'score': 998})

                    # Listar PROYECTOS/NECESIDADES por subregión
                    elif 'proyecto' in normalize(consulta) or 'necesidad' in normalize(consulta):
                        necesidades_path = os.path.join(csv_folder, "Base_Necesidades.csv")
                        if os.path.exists(necesidades_path):
                            df_nec = pd.read_csv(necesidades_path, encoding='utf-8-sig')
                            df_nec['subregion_norm'] = df_nec['SUBREGION'].apply(lambda x: normalize(str(x)) if pd.notna(x) else "")
                            
                            resultados = df_nec[df_nec['subregion_norm'] == subregion_target_norm]
                            
                            if not resultados.empty:
                                info_list = f"LISTADO DE PROYECTOS/NECESIDADES PARA LA SUBREGIÓN {subregion_detectada}:\n"
                                for idx, row in resultados.head(10).iterrows():
                                    nec = row.get('NECESIDAD', 'Sin descripción')
                                    fase = row.get('FASE PROYECTO', 'No definida')
                                    mun = row.get('MUNICIPIO', '')
                                    
                                    # Mapeo de fase
                                    try:
                                        fase_num = int(float(fase))
                                        mapa_fases = {1: "Perfil", 2: "Prefactibilidad", 3: "Factibilidad"}
                                        if fase_num in mapa_fases:
                                            fase = f"{fase_num} ({mapa_fases[fase_num]})"
                                    except:
                                        pass
                                        
                                    info_list += f"- Proyecto: {nec} | Municipio: {mun} | Fase: {fase}\n"
                                
                                if len(resultados) > 10:
                                    info_list += f"... y {len(resultados)-10} más."
                                    
                                coincidencias.append({'text': info_list, 'score': 998})

            except Exception as e:
                print(f"Error listando datos: {e}")

        # Priorizar archivos de vías y bases de datos generales
        archivos_vias = [f for f in os.listdir(csv_folder) if (f.startswith('Red_vial') or f.startswith('Base_')) and f.endswith('.csv')]
        
        # Si no hay archivos de vías, buscar en todos (fallback)
        if not archivos_vias:
            archivos_vias = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]

        for csv_file in archivos_vias:
            file_path = os.path.join(csv_folder, csv_file)
            try:
                # Leer CSV con pandas para facilitar búsqueda
                # Usar encoding utf-8-sig para manejar correctamente caracteres latinos
                try:
                    df = pd.read_csv(file_path, encoding='utf-8-sig')
                except UnicodeDecodeError:
                    df = pd.read_csv(file_path, encoding='latin-1')
                
                # --- NUEVA LÓGICA DE PUNTUACIÓN BASADA EN SIMILITUD DE NOMBRE ---
                # El usuario quiere exactitud en el nombre de la vía.
                # Ignoramos columnas como INICIO, FIN, OBSERVACIONES para el cálculo del score.
                
                scores = []
                query_norm = normalize(consulta)
                
                for idx, row in df.iterrows():
                    current_score = 0
                    
                    # 1. Búsqueda en NOMBRE, CÓDIGO y OTROS IDENTIFICADORES (Prioridad Máxima)
                    name_val = ""
                    if 'NOMBRE_VIA' in row: name_val = str(row['NOMBRE_VIA'])
                    elif 'MPIO_NOMBRE' in row: name_val = str(row['MPIO_NOMBRE'])
                    elif 'VERE_NOMBRE' in row: name_val = str(row['VERE_NOMBRE'])
                    elif 'PROYECTOS' in row: name_val = str(row['PROYECTOS']) # Nuevo
                    elif 'NECESIDAD' in row: name_val = str(row['NECESIDAD']) # Nuevo
                    
                    code_val = ""
                    if 'CODIGO_VIA' in row: code_val = str(row['CODIGO_VIA'])
                    elif 'RADICADO' in row: code_val = str(row['RADICADO']) # Nuevo
                    elif 'ID_RADICADOS' in row: code_val = str(row['ID_RADICADOS']) # Nuevo
                    elif 'RADICADOS ASOCIADOS' in row: code_val = str(row['RADICADOS ASOCIADOS']) # Nuevo para Base_Necesidades
                    
                    # Combinar nombre y código para la búsqueda
                    search_targets = []
                    if name_val and name_val.lower() != 'nan': search_targets.append(name_val)
                    if code_val and code_val.lower() != 'nan': search_targets.append(code_val)
                    
                    for target in search_targets:
                        target_norm = normalize(target)
                        
                        # Coincidencia EXACTA de código o nombre (Score muy alto)
                        # IMPORTANTE: Para radicados largos, la coincidencia exacta es clave
                        if target_norm == query_norm:
                            current_score += 200
                        
                        # Coincidencia EXACTA de una palabra clave con el target (Vital para IDs/Radicados)
                        # Si una de las palabras buscadas es EXACTAMENTE el código/radicado
                        elif any(p == target_norm for p in palabras_clave):
                            current_score += 500

                        # Si el target contiene el query (ej: "2024..." en "2024..., 2025...")
                        # Esto es vital para RADICADOS ASOCIADOS que pueden ser listas
                        elif query_norm in target_norm and len(query_norm) > 5: # Solo si el query es largo (evitar matches con "1", "2")
                             current_score += 150
                        
                        # Similitud de secuencia
                        sim = difflib.SequenceMatcher(None, query_norm, target_norm).ratio()
                        if sim > 0.6: 
                            current_score += sim * 100
                        
                        # Coincidencia de subcadena general
                        if query_norm in target_norm or target_norm in query_norm:
                             current_score += 50
                             
                        # Coincidencia de palabras clave
                        matches = sum(1 for p in palabras_clave if p in target_norm)
                        current_score += matches * 10

                    # 2. Búsqueda en UBICACIÓN (Prioridad Media)
                    loc_val = ""
                    if 'MUNICIPIO' in row: loc_val = str(row['MUNICIPIO'])
                    elif 'SUBREGION' in row: loc_val = str(row['SUBREGION'])
                    
                    if loc_val and loc_val.lower() != 'nan':
                        loc_norm = normalize(loc_val)
                        if query_norm in loc_norm or loc_norm in query_norm:
                            current_score += 30
                        matches = sum(1 for p in palabras_clave if p in loc_norm)
                        current_score += matches * 5
                        
                    scores.append(current_score)

                # Asignar scores y filtrar
                df['score'] = scores
                # Solo mostramos resultados con score > 0
                filas_encontradas = df[df['score'] > 0].sort_values('score', ascending=False)
                
                if not filas_encontradas.empty:
                    # Tomar hasta 5 registros por archivo si tienen buena puntuación
                    top_rows = filas_encontradas.head(5)
                    
                    for _, row in top_rows.iterrows():
                        nombre_archivo_limpio = csv_file.replace('_decodificado.csv', '').replace('_', ' ')
                        info = f"FUENTE: {nombre_archivo_limpio} (Relevancia: {row['score']:.2f})\n"
                        
                        # Columnas a excluir (técnicas o redundantes)
                        cols_excluidas = ['OBJECTID', 'Shape__Length', 'Shape__Area', 'GlobalID', 'score', 'Shape', 'FID']
                        
                        for col, val in row.items():
                            # Mostrar todas las columnas que no estén excluidas y tengan valor
                            if col not in cols_excluidas and pd.notna(val) and str(val).strip() != "":
                                # Formatear un poco el nombre de la columna para que sea más legible
                                col_nombre = col.replace('_', ' ').title()
                                
                                # Mapeo de Fases del Proyecto
                                if col == 'FASE PROYECTO':
                                    try:
                                        fase_num = int(float(val))
                                        mapa_fases = {
                                            1: "Perfil",
                                            2: "Prefactibilidad",
                                            3: "Factibilidad"
                                        }
                                        if fase_num in mapa_fases:
                                            val = f"{fase_num} ({mapa_fases[fase_num]})"
                                    except (ValueError, TypeError):
                                        pass
                                
                                # Formato Moneda para columnas financieras
                                cols_moneda_keywords = ['VALOR', 'PRESUPUESTO', 'COSTO', 'APORTE', 'SOBRANTE', 'DEUDA', 'INGRESOS', 'GASTOS', 'AHORRO', 'CAPACIDAD MAXIMA']
                                exclude_keywords = ['PORCENTAJE', 'INDICADOR', 'SOBRE EL TOTAL', 'LIMITE', 'LÍMITE']
                                
                                if any(k in col.upper() for k in cols_moneda_keywords) and not any(ex in col.upper() for ex in exclude_keywords):
                                    try:
                                        # Intentar convertir a float y formatear
                                        val_float = float(str(val).replace(',', '').replace('$', ''))
                                        val = f"${val_float:,.2f}"
                                    except (ValueError, TypeError):
                                        pass

                                info += f"- {col_nombre}: {val}\n"
                                
                        coincidencias.append({'text': info, 'score': row['score']})
                        
            except Exception as e:
                print(f"Error leyendo {csv_file}: {e}")
                continue

        if coincidencias:
            # Ordenar todas las coincidencias de todos los archivos por score descendente
            coincidencias.sort(key=lambda x: x['score'], reverse=True)
            
            # Tomar las top 7 globales
            top_coincidencias = [c['text'] for c in coincidencias[:7]]
            
            respuesta = "\n[DATOS DETALLADOS DE VÍAS ENCONTRADOS]:\n"
            respuesta += "\n------------------------------\n".join(top_coincidencias)
            return respuesta
        else:
            return ""

    except Exception as e:
        print(f"Error buscando datos de vías: {e}")
        return ""

def buscar_capa_gis(consulta):
    """
    Busca en el catálogo de capas la URL más relevante para la consulta.
    """
    try:
        csv_path = os.path.join(DATA_PATH, "catalogo_capas.csv")
        if not os.path.exists(csv_path):
            return ""
            
        # Cargar el catálogo
        df = pd.read_csv(csv_path)
        
        # Búsqueda simple de palabras clave
        palabras_clave = consulta.lower().split()
        
        # Filtrar el DataFrame buscando coincidencias en el nombre de la capa
        # Buscamos si ALGUNA de las palabras clave está en el nombre de la capa
        resultados = df[df['Nombre_Capa'].apply(lambda x: any(word in str(x).lower() for word in palabras_clave))]
        
        if not resultados.empty:
            # Retornar las top 3 coincidencias
            top_resultados = resultados.head(3)
            respuesta = "\n[INFORMACIÓN DE CAPAS GEOGRÁFICAS ENCONTRADA]:\n"
            for index, row in top_resultados.iterrows():
                respuesta += f"- Capa: {row['Nombre_Capa']}\n  URL: {row['URL_Servicio']}\n"
            return respuesta
        else:
            return ""
            
    except Exception as e:
        print(f"Error consultando catálogo GIS: {e}")
        return ""

def load_documents():
    """Carga documentos desde el directorio de datos (TXT y PDF)."""
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
    
    documents = []
    
    # Cargar archivos TXT
    txt_loader = DirectoryLoader(DATA_PATH, glob="*.txt", loader_cls=TextLoader)
    txt_docs = txt_loader.load()
    documents.extend(txt_docs)
    
    # Cargar archivos PDF
    pdf_loader = DirectoryLoader(DATA_PATH, glob="*.pdf", loader_cls=PyPDFLoader)
    pdf_docs = pdf_loader.load()
    documents.extend(pdf_docs)
    
    # Si no hay documentos, crear ejemplo
    if not documents:
        with open(os.path.join(DATA_PATH, "ejemplo.txt"), "w", encoding="utf-8") as f:
            f.write("Este es un documento de ejemplo para el chatbot local. ChromaDB almacenará esto.")
        # Recargar para incluir el ejemplo
        txt_loader = DirectoryLoader(DATA_PATH, glob="*.txt", loader_cls=TextLoader)
        documents.extend(txt_loader.load())
        
    return documents

def create_vector_db():
    """Crea la base de datos vectorial si no existe o la carga."""
    print("Cargando documentos...")
    documents = load_documents()
    if not documents:
        print("No se encontraron documentos.")
        return None
    
    print(f"Se encontraron {len(documents)} documentos. Procesando...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    # Embeddings de OpenAI (text-embedding-ada-002 es el estándar anterior)
    print("Generando embeddings con OpenAI...")
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    
    # Crear y persistir ChromaDB con barra de progreso
    print(f"Creando base de datos ChromaDB con {len(texts)} fragmentos...")
    
    # Procesar por lotes para mostrar progreso
    batch_size = 100
    total_batches = (len(texts) + batch_size - 1) // batch_size
    
    # Inicializar DB vacía primero
    db = Chroma(embedding_function=embeddings, persist_directory=DB_PATH)
    
    print("Iniciando indexación (esto puede tardar)...")
    for i in tqdm(range(0, len(texts), batch_size), desc="Indexando documentos", unit="lote"):
        batch = texts[i:i + batch_size]
        db.add_documents(batch)
        time.sleep(0.1) # Pequeña pausa para no saturar la API
        
    print("Base de datos creada exitosamente.")
    return db

def get_qa_chain():
    """Configura la cadena de preguntas y respuestas."""
    # Embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    
    # Cargar DB existente
    if os.path.exists(DB_PATH):
        db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    else:
        db = create_vector_db()
        if not db:
            return None 

    # Configurar LLM (OpenAI)
    try:
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0) # GPT-3.5-turbo
    except Exception as e:
        print(f"Error al conectar con OpenAI: {e}")
        return None

    retriever = db.as_retriever(search_kwargs={"k": 3})
    
    # Cargar contexto personal si existe
    personal_context = ""
    personal_context_path = os.path.join(DATA_PATH, "contexto_personal.txt")
    if os.path.exists(personal_context_path):
        try:
            with open(personal_context_path, "r", encoding="utf-8") as f:
                personal_context = f.read()
        except Exception as e:
            print(f"Error leyendo contexto personal: {e}")

    # Prompt personalizado para permitir respuestas generales
    template = f"""Eres Allison, la asistente virtual de la Secretaría de Infraestructura Física de la Gobernación de Antioquia.
    Tu misión es ayudar a consultar archivos y responder preguntas de manera profesional y amable.
    
    INFORMACIÓN SOBRE EL USUARIO Y SU ENTORNO (CONTEXTO PERSONAL):
    {personal_context}

    INSTRUCCIONES SOBRE MAPAS Y VÍAS:
    Si la pregunta se refiere a mapas, ubicación de vías o capas geográficas, revisa si hay información en la sección "CAPAS GEOGRÁFICAS" abajo.
    Si encuentras una URL relevante, proporciónala al usuario indicando que es la fuente oficial de datos geográficos.

    Usa los siguientes fragmentos de contexto recuperados para responder la pregunta al final.
    Si la respuesta no se encuentra en el contexto, responde utilizando tu propio conocimiento general para ayudar al usuario.

    Contexto recuperado:
    {{context}}

    Pregunta: {{question}}
    Respuesta:"""
    
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )
    
    return qa_chain
