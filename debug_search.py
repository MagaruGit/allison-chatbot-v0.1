from app.rag import buscar_datos_vias

query = "Vía Terciaria Santa Rosa De Los Palmares - Pueblo Nuevo"
print(f"Query: {query}")
result = buscar_datos_vias(query)
print("\nResult:")
print(result)
