FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# NOTA: La API Key de OpenAI se configura en Render como variable de entorno
# NO incluir secrets en el Dockerfile

# Copiar archivos de requisitos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Crear directorio .streamlit y archivo de configuración
RUN mkdir -p /app/.streamlit && \
    echo '[general]' > /app/.streamlit/secrets.toml && \
    echo 'OPENAI_API_KEY = ""' >> /app/.streamlit/secrets.toml

# Exponer el puerto (Render usa la variable de entorno PORT)
EXPOSE 8501

# Comando para ejecutar la aplicación
# Es CRUCIAL usar --server.address=0.0.0.0 para que Render pueda acceder
CMD sh -c 'streamlit run app/main.py --server.port=${PORT:-8501} --server.address=0.0.0.0'