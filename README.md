# Chatbot RAG con OpenAI

Este proyecto implementa un chatbot utilizando:

- **Streamlit**: Para la interfaz de usuario.
- **ChromaDB**: Como base de datos vectorial para RAG (Retrieval Augmented Generation).
- **LangChain**: Para orquestar el flujo.
- **OpenAI (GPT-3.5)**: Como modelo de lenguaje.
- **HuggingFace/SentenceTransformers**: Para embeddings locales.

## Configuración

1.  Crear un entorno virtual:

    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

2.  Instalar dependencias:

    ```bash
    pip install -r requirements.txt
    ```

3.  Ejecutar la aplicación:
    ```bash
    streamlit run app/main.py
    ```
