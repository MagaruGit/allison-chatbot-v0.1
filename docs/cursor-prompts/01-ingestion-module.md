# Prompt para Módulo de Ingesta de Datos

## 📋 Contexto del Proyecto
Estás desarrollando el **Módulo de Ingestion Pipeline** para un sistema de copiloto con IA para infraestructura y planeación territorial del gobierno de Antioquia. Este módulo es responsable de cargar, procesar y transformar datos de múltiples fuentes (PDFs, CSVs, Shapefiles, APIs) para alimentar un sistema RAG + PostGIS.

## 🎯 Objetivo del Módulo
Crear un pipeline robusto de ingesta de datos que:
1. Procese documentos PDF (normativas, POT, estudios técnicos)
2. Cargue y valide archivos CSV (inventarios, estadísticas)
3. Importe datos geoespaciales (Shapefiles, GeoJSON)
4. Consuma APIs externas (IGAC, DANE)
5. Genere embeddings vectoriales para RAG
6. Cargue datos a PostgreSQL + PostGIS + ChromaDB

## 📁 Estructura de Archivos a Generar

```
modules/ingestion/
├── __init__.py
├── config.py                   # Configuración del módulo
├── document_processor.py       # Procesamiento de PDFs/DOCs
├── csv_processor.py            # Procesamiento de tablas
├── gis_processor.py            # Procesamiento de datos GIS
├── api_fetcher.py              # Integración con APIs externas
├── vector_embedder.py          # Generación de embeddings
├── data_validator.py           # Validación de datos
├── orchestrator.py             # Orquestación de pipeline
└── utils/
    ├── __init__.py
    ├── file_utils.py
    ├── text_cleaner.py
    └── logger.py
```

## 🔧 Especificaciones Técnicas

### 1. document_processor.py

**Propósito**: Extraer y procesar texto de documentos PDF y Word.

**Funcionalidades requeridas**:
```python
class DocumentProcessor:
    """
    Procesa documentos (PDF, DOCX) y extrae contenido estructurado.
    """
    
    def __init__(self, embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Inicializa el procesador con modelo de embeddings."""
        pass
    
    def process_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Extrae texto, metadatos y estructura de un PDF.
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            {
                'text': str,
                'metadata': dict,
                'pages': List[dict],
                'chunks': List[str]
            }
        """
        pass
    
    def process_docx(self, file_path: str) -> Dict[str, Any]:
        """Procesa documentos Word."""
        pass
    
    def chunk_document(self, text: str, chunk_size: int = 1000, 
                      overlap: int = 200) -> List[str]:
        """
        Divide el documento en chunks con overlap para RAG.
        Usa RecursiveCharacterTextSplitter de LangChain.
        """
        pass
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extrae metadatos del documento:
        - Autor, fecha de creación
        - Título, categoría
        - Número de páginas
        """
        pass
```

**Dependencias**:
- PyMuPDF (fitz) para PDFs
- python-docx para Word
- langchain_text_splitters.RecursiveCharacterTextSplitter
- pydantic para validación de datos

**Casos de prueba**:
```python
# Test 1: Procesar PDF de normativa
pdf_result = processor.process_pdf("data/POT_Antioquia_2024.pdf")
assert pdf_result['text'] is not None
assert len(pdf_result['chunks']) > 0

# Test 2: Chunking con overlap
chunks = processor.chunk_document(long_text, chunk_size=500, overlap=100)
assert all(len(c) <= 600 for c in chunks)  # Verificar tamaño
```

---

### 2. csv_processor.py

**Propósito**: Cargar, limpiar y validar datos tabulares CSV.

**Funcionalidades requeridas**:
```python
class CSVProcessor:
    """
    Procesa archivos CSV con datos de infraestructura y estadísticas.
    """
    
    def __init__(self, db_connection_string: str):
        """Inicializa con conexión a PostgreSQL."""
        pass
    
    def load_csv(self, file_path: str, encoding: str = 'utf-8-sig') -> pd.DataFrame:
        """
        Carga CSV con manejo robusto de encodings.
        Detecta automáticamente delimitadores.
        """
        pass
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia datos:
        - Normaliza nombres de columnas (lowercase, sin tildes)
        - Elimina filas duplicadas
        - Maneja valores nulos
        - Normaliza texto (tildes, espacios)
        """
        pass
    
    def infer_schema(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Infiere tipos de datos SQL para cada columna.
        Returns: {'column_name': 'VARCHAR(255)', ...}
        """
        pass
    
    def load_to_postgres(self, df: pd.DataFrame, table_name: str, 
                        if_exists: str = 'replace') -> bool:
        """
        Carga DataFrame a PostgreSQL.
        Crea tabla automáticamente si no existe.
        """
        pass
    
    def validate_data(self, df: pd.DataFrame, schema: Dict) -> List[str]:
        """
        Valida datos contra esquema esperado.
        Returns: Lista de errores encontrados.
        """
        pass
```

**Dependencias**:
- pandas
- sqlalchemy
- chardet (detección de encoding)
- unicodedata (normalización)

**Casos de prueba**:
```python
# Test 1: Cargar CSV con diferentes encodings
df = processor.load_csv("data/vias_antioquia.csv")
assert df is not None
assert len(df) > 0

# Test 2: Limpieza de datos
df_clean = processor.clean_dataframe(df_raw)
assert df_clean.columns.str.islower().all()
assert df_clean.duplicated().sum() == 0

# Test 3: Carga a PostgreSQL
success = processor.load_to_postgres(df, "vias_inventario")
assert success == True
```

---

### 3. gis_processor.py

**Propósito**: Procesar datos geoespaciales (Shapefiles, GeoJSON) y cargarlos a PostGIS.

**Funcionalidades requeridas**:
```python
class GISProcessor:
    """
    Procesa datos geoespaciales y los carga a PostGIS.
    """
    
    def __init__(self, postgis_connection: str):
        """Inicializa con conexión a PostGIS."""
        self.engine = create_engine(postgis_connection)
    
    def load_shapefile(self, shapefile_path: str) -> gpd.GeoDataFrame:
        """
        Carga Shapefile a GeoDataFrame.
        Maneja diferentes proyecciones (CRS).
        """
        pass
    
    def load_geojson(self, geojson_path: str) -> gpd.GeoDataFrame:
        """Carga GeoJSON a GeoDataFrame."""
        pass
    
    def reproject(self, gdf: gpd.GeoDataFrame, target_crs: str = 'EPSG:4326') -> gpd.GeoDataFrame:
        """
        Reproyecta geometrías al CRS objetivo.
        Por defecto, WGS84 (EPSG:4326) para web maps.
        """
        pass
    
    def validate_geometries(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Valida y repara geometrías:
        - Elimina geometrías inválidas
        - Repara polígonos con buffer(0)
        - Elimina geometrías vacías
        """
        pass
    
    def load_to_postgis(self, gdf: gpd.GeoDataFrame, table_name: str, 
                       if_exists: str = 'replace', index: bool = True) -> bool:
        """
        Carga GeoDataFrame a PostGIS.
        Crea índices espaciales (GIST) automáticamente.
        """
        pass
    
    def create_spatial_index(self, table_name: str, geom_column: str = 'geometry'):
        """Crea índice espacial GIST en tabla de PostGIS."""
        pass
```

**Dependencias**:
- geopandas
- shapely
- fiona
- pyproj
- sqlalchemy + geoalchemy2

**Casos de prueba**:
```python
# Test 1: Cargar Shapefile
gdf = processor.load_shapefile("data/municipios_antioquia.shp")
assert gdf.crs is not None
assert len(gdf) > 0

# Test 2: Reproyección
gdf_wgs84 = processor.reproject(gdf, target_crs='EPSG:4326')
assert gdf_wgs84.crs.to_string() == 'EPSG:4326'

# Test 3: Validación de geometrías
gdf_valid = processor.validate_geometries(gdf)
assert gdf_valid.geometry.is_valid.all()

# Test 4: Carga a PostGIS
success = processor.load_to_postgis(gdf, "municipios")
assert success == True
```

---

### 4. vector_embedder.py

**Propósito**: Generar embeddings vectoriales para documentos y cargarlos a ChromaDB.

**Funcionalidades requeridas**:
```python
class VectorEmbedder:
    """
    Genera embeddings y los almacena en ChromaDB para RAG.
    """
    
    def __init__(self, 
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 chroma_path: str = "chroma_db"):
        """
        Inicializa con modelo de embeddings y ruta de ChromaDB.
        Usa HuggingFaceEmbeddings de LangChain.
        """
        pass
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Genera embeddings para lista de textos.
        Returns: Array de shape (n_texts, embedding_dim)
        """
        pass
    
    def create_collection(self, collection_name: str, 
                         documents: List[str], 
                         metadatas: List[Dict]) -> bool:
        """
        Crea colección en ChromaDB con documentos embeddeados.
        
        Args:
            collection_name: Nombre de la colección (ej: "normativas")
            documents: Lista de textos
            metadatas: Lista de diccionarios con metadatos
        """
        pass
    
    def add_documents(self, collection_name: str, 
                     documents: List[str], 
                     metadatas: List[Dict]) -> bool:
        """Agrega documentos a colección existente."""
        pass
    
    def search(self, collection_name: str, query: str, k: int = 5) -> List[Dict]:
        """
        Búsqueda semántica en colección.
        Returns: Lista de documentos con scores.
        """
        pass
    
    def delete_collection(self, collection_name: str) -> bool:
        """Elimina colección completa."""
        pass
```

**Dependencias**:
- chromadb
- langchain_community.embeddings.HuggingFaceEmbeddings
- sentence-transformers
- numpy

**Casos de prueba**:
```python
# Test 1: Generar embeddings
texts = ["Este es un documento de prueba", "Otro documento"]
embeddings = embedder.generate_embeddings(texts)
assert embeddings.shape == (2, 384)  # MiniLM dimension

# Test 2: Crear colección
docs = ["POT artículo 1", "POT artículo 2"]
metas = [{"source": "POT", "article": 1}, {"source": "POT", "article": 2}]
success = embedder.create_collection("test_collection", docs, metas)
assert success == True

# Test 3: Búsqueda semántica
results = embedder.search("test_collection", "normativa urbana", k=2)
assert len(results) == 2
assert 'text' in results[0]
assert 'score' in results[0]
```

---

### 5. api_fetcher.py

**Propósito**: Consumir APIs externas del gobierno (IGAC, DANE, etc.).

**Funcionalidades requeridas**:
```python
class APIFetcher:
    """
    Consume APIs externas para enriquecer datos del sistema.
    """
    
    def __init__(self, api_keys: Dict[str, str] = None):
        """Inicializa con API keys necesarias."""
        self.session = requests.Session()
        self.api_keys = api_keys or {}
    
    def fetch_igac_data(self, municipio_code: str) -> Dict[str, Any]:
        """
        Obtiene datos del IGAC (Instituto Geográfico Agustín Codazzi).
        
        Args:
            municipio_code: Código DANE del municipio
            
        Returns:
            Datos catastrales y geográficos
        """
        pass
    
    def fetch_dane_statistics(self, year: int, 
                              indicator: str) -> pd.DataFrame:
        """
        Obtiene estadísticas del DANE.
        
        Args:
            year: Año de consulta
            indicator: Indicador (ej: 'poblacion', 'pib')
        """
        pass
    
    def fetch_ideam_climate(self, station_id: str, 
                           start_date: str, 
                           end_date: str) -> pd.DataFrame:
        """
        Obtiene datos climáticos del IDEAM.
        """
        pass
    
    def retry_request(self, url: str, max_retries: int = 3) -> requests.Response:
        """
        Realiza request con reintentos exponenciales.
        Maneja rate limiting y timeouts.
        """
        pass
    
    def validate_response(self, response: requests.Response) -> bool:
        """Valida respuesta de API (status code, formato JSON)."""
        pass
```

**Dependencias**:
- requests
- pandas
- tenacity (retry logic)
- python-dotenv (API keys)

**Casos de prueba**:
```python
# Test 1: Fetch con retry
response = fetcher.retry_request("https://api.example.com/data")
assert response.status_code == 200

# Test 2: Validación de respuesta
is_valid = fetcher.validate_response(response)
assert is_valid == True

# Test 3: Fetch DANE (mock)
df = fetcher.fetch_dane_statistics(2024, "poblacion")
assert isinstance(df, pd.DataFrame)
```

---

### 6. orchestrator.py

**Propósito**: Orquestar el pipeline completo de ingesta.

**Funcionalidades requeridas**:
```python
class IngestionOrchestrator:
    """
    Orquesta el pipeline completo de ingesta de datos.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa con configuración del pipeline.
        Carga todos los procesadores necesarios.
        """
        self.doc_processor = DocumentProcessor()
        self.csv_processor = CSVProcessor(config['postgres_uri'])
        self.gis_processor = GISProcessor(config['postgis_uri'])
        self.vector_embedder = VectorEmbedder(config['chroma_path'])
        self.api_fetcher = APIFetcher(config.get('api_keys'))
        self.logger = setup_logger("ingestion")
    
    def ingest_directory(self, directory_path: str, 
                        file_types: List[str] = None) -> Dict[str, int]:
        """
        Ingesta todos los archivos de un directorio.
        
        Returns:
            {'pdfs_processed': 10, 'csvs_processed': 5, 'shapefiles_processed': 3}
        """
        pass
    
    def ingest_single_file(self, file_path: str) -> bool:
        """
        Ingesta un solo archivo, detectando automáticamente su tipo.
        """
        pass
    
    def ingest_from_api(self, api_name: str, params: Dict) -> bool:
        """
        Ingesta datos desde API externa.
        """
        pass
    
    def schedule_ingestion(self, cron_expression: str, 
                          source: str) -> bool:
        """
        Programa ingesta recurrente (ej: diaria, semanal).
        Usa APScheduler.
        """
        pass
    
    def get_ingestion_stats(self) -> Dict[str, Any]:
        """
        Retorna estadísticas de ingesta:
        - Total de documentos procesados
        - Total de registros en PostgreSQL
        - Total de geometrías en PostGIS
        - Total de vectores en ChromaDB
        """
        pass
```

**Dependencias**:
- apscheduler (programación)
- logging
- pathlib
- typing

**Casos de prueba**:
```python
# Test 1: Ingesta de directorio
stats = orchestrator.ingest_directory("data/documents/")
assert stats['pdfs_processed'] > 0

# Test 2: Ingesta de archivo único
success = orchestrator.ingest_single_file("data/POT.pdf")
assert success == True

# Test 3: Obtener estadísticas
stats = orchestrator.get_ingestion_stats()
assert 'total_documents' in stats
```

---

## 📝 Instrucciones de Implementación

### Paso 1: Setup del Proyecto
```bash
# Crear directorio del módulo
mkdir -p modules/ingestion/utils

# Instalar dependencias
pip install pymupdf python-docx pandas geopandas chromadb \
            langchain-community langchain-text-splitters \
            sentence-transformers sqlalchemy geoalchemy2 \
            requests tenacity apscheduler pydantic
```

### Paso 2: Configuración
Crea `modules/ingestion/config.py`:
```python
from pydantic import BaseModel, Field
from typing import Optional

class IngestionConfig(BaseModel):
    """Configuración del módulo de ingesta."""
    
    postgres_uri: str = Field(..., description="PostgreSQL connection string")
    postgis_uri: str = Field(..., description="PostGIS connection string")
    chroma_path: str = Field(default="chroma_db", description="Ruta a ChromaDB")
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Modelo de embeddings"
    )
    chunk_size: int = Field(default=1000, description="Tamaño de chunks para RAG")
    chunk_overlap: int = Field(default=200, description="Overlap entre chunks")
    api_keys: Optional[dict] = Field(default=None, description="API keys externas")
    
    class Config:
        env_file = ".env"
```

### Paso 3: Implementar Cada Clase
Implementa cada archivo siguiendo las especificaciones arriba.

### Paso 4: Testing
Crea `tests/test_ingestion.py`:
```python
import pytest
from modules.ingestion import (
    DocumentProcessor, 
    CSVProcessor, 
    GISProcessor,
    VectorEmbedder,
    IngestionOrchestrator
)

def test_document_processor():
    processor = DocumentProcessor()
    result = processor.process_pdf("tests/fixtures/sample.pdf")
    assert result is not None
    assert len(result['chunks']) > 0

def test_csv_processor():
    processor = CSVProcessor("postgresql://...")
    df = processor.load_csv("tests/fixtures/sample.csv")
    assert df is not None

# ... más tests
```

### Paso 5: Logging y Monitoring
Implementa logging robusto:
```python
import logging
from pathlib import Path

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # File handler
    handler = logging.FileHandler(f"logs/{name}.log")
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(handler)
    
    return logger
```

---

## ✅ Criterios de Aceptación

### Funcionales
- ✅ Procesa correctamente PDFs con texto extraído
- ✅ Carga CSVs a PostgreSQL sin errores
- ✅ Importa Shapefiles a PostGIS con índices espaciales
- ✅ Genera embeddings y crea colecciones en ChromaDB
- ✅ Consume APIs externas con retry logic

### No Funcionales
- ✅ Manejo robusto de errores con logging
- ✅ Validación de datos en cada etapa
- ✅ Performance: procesa 100 PDFs en < 10 minutos
- ✅ Código documentado con docstrings
- ✅ Tests unitarios con coverage > 80%

---

## 🚀 Ejemplo de Uso

```python
from modules.ingestion import IngestionOrchestrator, IngestionConfig

# Configuración
config = IngestionConfig(
    postgres_uri="postgresql://user:pass@localhost/db",
    postgis_uri="postgresql://user:pass@localhost/db",
    chroma_path="./chroma_db",
    api_keys={"igac": "key123", "dane": "key456"}
)

# Inicializar orchestrator
orchestrator = IngestionOrchestrator(config.dict())

# Ingesta completa de directorio
stats = orchestrator.ingest_directory("data/documents/")
print(f"Procesados: {stats}")

# Ingesta programada (diaria a las 2 AM)
orchestrator.schedule_ingestion("0 2 * * *", source="data/documents/")
```

---

## 📚 Referencias

- [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [PostGIS Manual](https://postgis.net/documentation/)
- [GeoPandas User Guide](https://geopandas.org/en/stable/docs/user_guide.html)

---

**¿Listo para generar el código?** Copia este prompt completo en Cursor y pide:

> "Genera el módulo de ingesta completo siguiendo las especificaciones de este documento. Implementa todos los archivos con código production-ready, incluyendo manejo de errores, logging y documentación."
