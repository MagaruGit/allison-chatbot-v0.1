import requests
import json

url = "https://services5.arcgis.com/K90UQIB09TmTjUL8/arcgis/rest/services/R10/FeatureServer/3?f=json"

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    print("Analizando campos y dominios para:", data.get('name', 'Capa desconocida'))
    
    campos_con_dominio = []
    for field in data.get('fields', []):
        if field.get('domain'):
            domain_info = field['domain']
            print(f"\nCampo: {field['name']} ({field['alias']})")
            print(f"  Tipo de dominio: {domain_info['type']}")
            print(f"  Nombre dominio: {domain_info.get('name')}")
            
            if 'codedValues' in domain_info:
                print("  Valores (primeros 5):")
                for val in domain_info['codedValues'][:5]:
                    print(f"    {val['code']} -> {val['name']}")
            campos_con_dominio.append(field['name'])
            
    if not campos_con_dominio:
        print("\nNo se encontraron campos con dominios.")
        
except Exception as e:
    print(f"Error: {e}")
