# Prompt para Módulo RAG (Retrieval Augmented Generation)

## 📋 Contexto del Proyecto
Estás desarrollando el **Módulo RAG (Retrieval Augmented Generation)** para un sistema de copiloto con IA para infraestructura y planeación territorial. Este módulo es responsable de realizar búsquedas semánticas en la base de conocimiento, recuperar contexto relevante y sintetizar respuestas enriquecidas usando LLMs.

## 🎯 Objetivo del Módulo
Crear un sistema RAG robusto que:
1. Realice búsqueda semántica eficiente en ChromaDB
2. Re-rankee documentos por relevancia
3. Gestione memoria conversacional (historial de chat)
4. Enriquezca el contexto con metadatos
5. Genere respuestas coherentes usando GPT-4
6. Maneje diferentes tipos de consultas (normativas, estadísticas, geo)

## 📁 Estructura de Archivos a Generar

```
modules/rag/
├── __init__.py
├── config.py                   # Configuración del módulo
├── retriever.py                # Motor de búsqueda vectorial
├── reranker.py                 # Re-ranking de resultados
├── context_manager.py          # Gestión de contexto
├── memory.py                   # Memoria conversacional
├── prompt_templates.py         # Templates de prompts
├── response_synthesizer.py    # Síntesis de respuestas
└── utils/
    ├── __init__.py
    ├── text_utils.py
    └── logger.py
```

## 🔧 Especificaciones Técnicas

### 1. retriever.py

**Propósito**: Realizar búsqueda semántica en ChromaDB con filtros avanzados.

**Funcionalidades requeridas**:
```python
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from pydantic import BaseModel

class RetrievalResult(BaseModel):
    """Modelo para resultado de búsqueda."""
    document: str
    metadata: Dict[str, Any]
    score: float
    source: str

class SemanticRetriever:
    """
    Motor de búsqueda semántica sobre ChromaDB.
    """
    
    def __init__(self, 
                 chroma_path: str = "chroma_db",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 collection_name: str = "documents"):
        """
        Inicializa retriever con modelo de embeddings.
        
        Args:
            chroma_path: Ruta a base de datos ChromaDB
            embedding_model: Modelo para embeddings
            collection_name: Nombre de colección por defecto
        """
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model
        )
        self.vectorstore = Chroma(
            persist_directory=chroma_path,
            embedding_function=self.embeddings,
            collection_name=collection_name
        )
    
    def retrieve(self, 
                query: str, 
                k: int = 5,
                filters: Optional[Dict[str, Any]] = None) -> List[RetrievalResult]:
        """
        Realiza búsqueda semántica.
        
        Args:
            query: Consulta del usuario
            k: Número de documentos a recuperar
            filters: Filtros de metadatos (ej: {'source': 'POT', 'year': 2024})
            
        Returns:
            Lista de resultados ordenados por relevancia
        """
        pass
    
    def retrieve_with_scores(self, query: str, k: int = 5) -> List[tuple]:
        """
        Recupera documentos con scores de similitud.
        
        Returns:
            Lista de tuplas (Document, score)
        """
        pass
    
    def max_marginal_relevance_search(self, 
                                     query: str, 
                                     k: int = 5,
                                     fetch_k: int = 20,
                                     lambda_mult: float = 0.5) -> List[RetrievalResult]:
        """
        MMR search para diversidad de resultados.
        Evita redundancia recuperando documentos diversos pero relevantes.
        
        Args:
            query: Consulta
            k: Documentos finales a retornar
            fetch_k: Candidatos iniciales
            lambda_mult: Balance relevancia vs diversidad (0-1)
        """
        pass
    
    def similarity_search_with_threshold(self,
                                        query: str,
                                        threshold: float = 0.7,
                                        k: int = 10) -> List[RetrievalResult]:
        """
        Búsqueda con umbral de similitud mínimo.
        Solo retorna documentos con score > threshold.
        """
        pass
    
    def hybrid_search(self, 
                     query: str,
                     k: int = 5,
                     alpha: float = 0.5) -> List[RetrievalResult]:
        """
        Búsqueda híbrida: combina búsqueda semántica + keyword.
        
        Args:
            alpha: Peso de búsqueda semántica (0=solo keyword, 1=solo semántica)
        """
        pass
```

**Dependencias**:
- langchain-community
- chromadb
- sentence-transformers
- numpy

**Casos de prueba**:
```python
# Test 1: Búsqueda básica
retriever = SemanticRetriever()
results = retriever.retrieve("normativa sobre construcción rural", k=5)
assert len(results) == 5
assert all(hasattr(r, 'score') for r in results)

# Test 2: Búsqueda con filtros
results = retriever.retrieve(
    "artículo sobre zonas protegidas",
    k=3,
    filters={'source': 'POT', 'year': 2024}
)
assert len(results) <= 3
assert all(r.metadata['source'] == 'POT' for r in results)

# Test 3: MMR search
results = retriever.max_marginal_relevance_search(
    "infraestructura vial",
    k=5,
    lambda_mult=0.7
)
assert len(results) == 5
# Verificar diversidad (no todos deben ser idénticos)
```

---

### 2. reranker.py

**Propósito**: Re-rankear documentos recuperados usando modelo cross-encoder para mejorar precisión.

**Funcionalidades requeridas**:
```python
from sentence_transformers import CrossEncoder
import numpy as np

class DocumentReranker:
    """
    Re-rankea documentos usando modelo cross-encoder para mayor precisión.
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Inicializa reranker con modelo cross-encoder.
        Cross-encoders son más precisos pero más lentos que bi-encoders.
        """
        self.model = CrossEncoder(model_name)
    
    def rerank(self, 
              query: str, 
              documents: List[str],
              top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Re-rankea lista de documentos.
        
        Args:
            query: Consulta original
            documents: Lista de textos a re-rankear
            top_k: Top K documentos a retornar
            
        Returns:
            Lista ordenada de {
                'text': str,
                'score': float,
                'rank': int
            }
        """
        pass
    
    def rerank_with_metadata(self,
                            query: str,
                            results: List[RetrievalResult],
                            top_k: int = 5) -> List[RetrievalResult]:
        """
        Re-rankea resultados preservando metadatos.
        """
        pass
    
    def batch_rerank(self,
                    queries: List[str],
                    documents_list: List[List[str]],
                    top_k: int = 5) -> List[List[Dict]]:
        """
        Re-rankea múltiples queries en batch (más eficiente).
        """
        pass
    
    def compute_relevance_scores(self,
                                query: str,
                                documents: List[str]) -> np.ndarray:
        """
        Calcula scores de relevancia para todos los documentos.
        Returns: Array de scores normalizados (0-1)
        """
        pass
```

**Dependencias**:
- sentence-transformers
- numpy
- torch

**Casos de prueba**:
```python
# Test 1: Reranking básico
reranker = DocumentReranker()
docs = ["doc1 relevante", "doc2 no relevante", "doc3 muy relevante"]
reranked = reranker.rerank("documento relevante", docs, top_k=2)
assert len(reranked) == 2
assert reranked[0]['score'] > reranked[1]['score']

# Test 2: Reranking con metadatos
results = [RetrievalResult(...), ...]
reranked = reranker.rerank_with_metadata("query", results, top_k=3)
assert all(hasattr(r, 'metadata') for r in reranked)
```

---

### 3. context_manager.py

**Propósito**: Gestionar contexto para el LLM, ensamblando información relevante.

**Funcionalidades requeridas**:
```python
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Context:
    """Contexto ensamblado para el LLM."""
    query: str
    retrieved_documents: List[Dict[str, Any]]
    conversation_history: List[Dict[str, str]]
    metadata: Dict[str, Any]
    system_prompt: str
    max_tokens: int

class ContextManager:
    """
    Gestiona el contexto para el LLM, ensamblando información relevante.
    """
    
    def __init__(self, max_context_length: int = 4000):
        """
        Args:
            max_context_length: Longitud máxima del contexto en tokens
        """
        self.max_context_length = max_context_length
    
    def build_context(self,
                     query: str,
                     retrieved_docs: List[RetrievalResult],
                     conversation_history: List[Dict] = None,
                     additional_context: Dict = None) -> Context:
        """
        Ensambla contexto completo para el LLM.
        
        Args:
            query: Consulta del usuario
            retrieved_docs: Documentos recuperados
            conversation_history: Historial de conversación
            additional_context: Contexto adicional (ej: datos de usuario)
            
        Returns:
            Objeto Context con toda la información
        """
        pass
    
    def format_documents(self, 
                        docs: List[RetrievalResult]) -> str:
        """
        Formatea documentos recuperados para el prompt.
        
        Returns:
            String formateado tipo:
            '''
            Documento 1 (Fuente: POT, Score: 0.95):
            [contenido]
            
            Documento 2 (Fuente: Estudio, Score: 0.87):
            [contenido]
            '''
        """
        pass
    
    def truncate_context(self, 
                        context: str, 
                        max_tokens: int = None) -> str:
        """
        Trunca contexto si excede max_tokens.
        Prioriza: query > documentos recientes > historial antiguo
        """
        pass
    
    def add_metadata_to_context(self,
                               context: str,
                               metadata: Dict[str, Any]) -> str:
        """
        Enriquece contexto con metadatos relevantes.
        Ej: ubicación del usuario, fecha, rol, etc.
        """
        pass
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estima número de tokens (aproximación: 1 token ≈ 4 caracteres).
        Para mayor precisión, usar tiktoken de OpenAI.
        """
        pass
```

**Dependencias**:
- tiktoken (token counting)
- dataclasses

**Casos de prueba**:
```python
# Test 1: Build context
manager = ContextManager(max_context_length=2000)
context = manager.build_context(
    query="¿Qué dice el POT sobre zonas rurales?",
    retrieved_docs=results,
    conversation_history=history
)
assert context.query is not None
assert len(context.retrieved_documents) > 0

# Test 2: Truncate context
long_context = "a" * 10000
truncated = manager.truncate_context(long_context, max_tokens=500)
assert manager.estimate_tokens(truncated) <= 500
```

---

### 4. memory.py

**Propósito**: Gestionar memoria conversacional y historial de chat.

**Funcionalidades requeridas**:
```python
from typing import List, Dict, Optional
from collections import deque
from datetime import datetime

class ConversationMemory:
    """
    Gestiona memoria conversacional para mantener contexto entre turnos.
    """
    
    def __init__(self, 
                 max_history: int = 10,
                 memory_type: str = "buffer"):
        """
        Args:
            max_history: Número máximo de turnos a recordar
            memory_type: 'buffer', 'summary', o 'sliding_window'
        """
        self.messages: deque = deque(maxlen=max_history)
        self.memory_type = memory_type
        self.summary = None
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """
        Agrega mensaje al historial.
        
        Args:
            role: 'user', 'assistant', o 'system'
            content: Contenido del mensaje
            metadata: Metadatos opcionales (timestamp, fuentes, etc.)
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self.messages.append(message)
    
    def get_history(self, 
                   last_n: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Recupera historial de conversación.
        
        Args:
            last_n: Número de mensajes recientes (None = todos)
        """
        pass
    
    def get_formatted_history(self, format_type: str = "openai") -> List[Dict]:
        """
        Formatea historial para API del LLM.
        
        Args:
            format_type: 'openai', 'anthropic', o 'plain'
        """
        pass
    
    def clear(self):
        """Limpia el historial completo."""
        self.messages.clear()
        self.summary = None
    
    def summarize_history(self, llm) -> str:
        """
        Genera resumen del historial usando LLM.
        Útil para conversaciones muy largas.
        """
        pass
    
    def prune_history(self, keep_recent: int = 5):
        """
        Poda el historial manteniendo solo los mensajes más recientes.
        """
        pass
    
    def search_history(self, keyword: str) -> List[Dict]:
        """
        Busca mensajes en el historial que contengan keyword.
        """
        pass
    
    def export_history(self, format: str = "json") -> str:
        """
        Exporta historial en formato especificado (json, csv, txt).
        """
        pass
```

**Dependencias**:
- collections
- json
- datetime

**Casos de prueba**:
```python
# Test 1: Add and retrieve messages
memory = ConversationMemory(max_history=5)
memory.add_message("user", "Hola")
memory.add_message("assistant", "Hola, ¿cómo puedo ayudarte?")
history = memory.get_history()
assert len(history) == 2

# Test 2: Max history enforcement
for i in range(10):
    memory.add_message("user", f"Mensaje {i}")
assert len(memory.messages) == 5  # Solo los últimos 5

# Test 3: Formatted history
formatted = memory.get_formatted_history(format_type="openai")
assert all(isinstance(m, dict) for m in formatted)
assert all('role' in m and 'content' in m for m in formatted)
```

---

### 5. prompt_templates.py

**Propósito**: Definir templates de prompts para diferentes tipos de consultas.

**Funcionalidades requeridas**:
```python
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from typing import Dict, Any

class PromptTemplateManager:
    """
    Gestiona templates de prompts para diferentes tipos de consultas.
    """
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, PromptTemplate]:
        """Inicializa todos los templates de prompts."""
        return {
            'general': self._general_template(),
            'normativa': self._normativa_template(),
            'estadistica': self._estadistica_template(),
            'geoespacial': self._geoespacial_template(),
            'recomendacion': self._recomendacion_template()
        }
    
    def _general_template(self) -> ChatPromptTemplate:
        """
        Template para consultas generales.
        """
        system_message = """Eres Allison, un asistente IA especializado en infraestructura 
        y planeación territorial para la Gobernación de Antioquia. Tu objetivo es ayudar 
        a funcionarios gubernamentales con información precisa basada en documentos oficiales.
        
        Principios:
        - Basa tus respuestas SOLO en el contexto proporcionado
        - Si no sabes algo, di "No tengo información suficiente"
        - Cita las fuentes cuando sea posible
        - Sé conciso pero completo
        - Usa lenguaje claro y profesional
        """
        
        human_message = """Contexto relevante:
        {context}
        
        Pregunta del usuario: {question}
        
        Respuesta:"""
        
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
    
    def _normativa_template(self) -> ChatPromptTemplate:
        """
        Template especializado para consultas sobre normativa (POT, decretos, etc.).
        """
        system_message = """Eres un experto en normativa urbana y territorial de Antioquia.
        
        Cuando respondas sobre normativa:
        - Cita el artículo, decreto o resolución específica
        - Indica la vigencia de la norma
        - Explica en términos claros pero precisos
        - Si hay excepciones o casos especiales, menciónalos
        """
        
        human_message = """Documentos normativos relevantes:
        {context}
        
        Consulta normativa: {question}
        
        Análisis normativo:"""
        
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
    
    def _estadistica_template(self) -> ChatPromptTemplate:
        """
        Template para consultas estadísticas y de datos.
        """
        system_message = """Eres un analista de datos especializado en estadísticas 
        de infraestructura y territorio.
        
        Al responder consultas estadísticas:
        - Presenta números de forma clara
        - Usa tablas cuando sea apropiado
        - Compara datos cuando sea relevante
        - Menciona la fuente y fecha de los datos
        - Identifica tendencias o patrones importantes
        """
        
        human_message = """Datos disponibles:
        {context}
        
        Consulta estadística: {question}
        
        Análisis:"""
        
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
    
    def _geoespacial_template(self) -> ChatPromptTemplate:
        """
        Template para consultas geoespaciales.
        """
        system_message = """Eres un experto en análisis geoespacial y SIG.
        
        Al responder consultas geoespaciales:
        - Describe ubicaciones de forma clara
        - Menciona coordenadas cuando sea relevante
        - Explica análisis espaciales en términos comprensibles
        - Sugiere visualizaciones cuando sea apropiado
        """
        
        human_message = """Datos geoespaciales:
        {context}
        
        Consulta geoespacial: {question}
        
        Análisis espacial:"""
        
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
    
    def _recomendacion_template(self) -> ChatPromptTemplate:
        """
        Template para generar recomendaciones y sugerencias.
        """
        system_message = """Eres un asesor estratégico en infraestructura y planeación.
        
        Al dar recomendaciones:
        - Basa recomendaciones en datos y normativa
        - Considera múltiples factores (costo, impacto, viabilidad)
        - Prioriza opciones cuando sea relevante
        - Menciona riesgos o consideraciones importantes
        - Sé constructivo y orientado a soluciones
        """
        
        human_message = """Información disponible:
        {context}
        
        Solicitud de recomendación: {question}
        
        Recomendaciones:"""
        
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
    
    def get_template(self, template_type: str) -> ChatPromptTemplate:
        """
        Obtiene template por tipo.
        
        Args:
            template_type: 'general', 'normativa', 'estadistica', 
                          'geoespacial', 'recomendacion'
        """
        return self.templates.get(template_type, self.templates['general'])
    
    def format_prompt(self, 
                     template_type: str,
                     context: str,
                     question: str,
                     **kwargs) -> str:
        """
        Formatea un prompt completo.
        """
        template = self.get_template(template_type)
        return template.format(context=context, question=question, **kwargs)
    
    def detect_query_type(self, query: str) -> str:
        """
        Detecta automáticamente el tipo de consulta.
        
        Returns: 'normativa', 'estadistica', 'geoespacial', 'recomendacion', o 'general'
        """
        query_lower = query.lower()
        
        # Keywords para cada tipo
        normativa_keywords = ['pot', 'decreto', 'artículo', 'ley', 'norma', 'reglamento']
        estadistica_keywords = ['total', 'cantidad', 'cuántos', 'estadística', 'número']
        geo_keywords = ['mapa', 'ubicación', 'coordenadas', 'distancia', 'área', 'zona']
        recomendacion_keywords = ['recomienda', 'sugiere', 'qué hacer', 'mejor opción']
        
        if any(kw in query_lower for kw in normativa_keywords):
            return 'normativa'
        elif any(kw in query_lower for kw in estadistica_keywords):
            return 'estadistica'
        elif any(kw in query_lower for kw in geo_keywords):
            return 'geoespacial'
        elif any(kw in query_lower for kw in recomendacion_keywords):
            return 'recomendacion'
        else:
            return 'general'
```

**Dependencias**:
- langchain-core

**Casos de prueba**:
```python
# Test 1: Get template
manager = PromptTemplateManager()
template = manager.get_template('normativa')
assert template is not None

# Test 2: Format prompt
prompt = manager.format_prompt(
    'general',
    context="Documento X dice...",
    question="¿Qué dice sobre Y?"
)
assert "Documento X" in prompt

# Test 3: Detect query type
query_type = manager.detect_query_type("¿Cuántas vías hay en total?")
assert query_type == 'estadistica'
```

---

### 6. response_synthesizer.py

**Propósito**: Sintetizar respuestas finales usando LLM y contexto recuperado.

**Funcionalidades requeridas**:
```python
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any, Optional

class ResponseSynthesizer:
    """
    Sintetiza respuestas finales usando LLM y contexto.
    """
    
    def __init__(self,
                 model_name: str = "gpt-4",
                 temperature: float = 0.3,
                 max_tokens: int = 1000):
        """
        Args:
            model_name: Modelo de OpenAI a usar
            temperature: Creatividad del modelo (0-1)
            max_tokens: Tokens máximos en respuesta
        """
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.prompt_manager = PromptTemplateManager()
        self.context_manager = ContextManager()
    
    def synthesize(self,
                  query: str,
                  retrieved_docs: List[RetrievalResult],
                  conversation_history: List[Dict] = None,
                  query_type: str = None) -> Dict[str, Any]:
        """
        Sintetiza respuesta final.
        
        Args:
            query: Pregunta del usuario
            retrieved_docs: Documentos recuperados
            conversation_history: Historial de conversación
            query_type: Tipo de consulta (auto-detect si None)
            
        Returns:
            {
                'answer': str,
                'sources': List[Dict],
                'confidence': float,
                'query_type': str
            }
        """
        pass
    
    def synthesize_streaming(self,
                           query: str,
                           retrieved_docs: List[RetrievalResult],
                           conversation_history: List[Dict] = None):
        """
        Sintetiza respuesta en modo streaming (generador).
        Útil para UI con respuestas incrementales.
        
        Yields:
            Fragmentos de texto de la respuesta
        """
        pass
    
    def extract_sources(self, 
                       retrieved_docs: List[RetrievalResult]) -> List[Dict[str, Any]]:
        """
        Extrae y formatea fuentes citables.
        
        Returns:
            [
                {'title': 'POT Artículo 5', 'url': '...', 'excerpt': '...'},
                ...
            ]
        """
        pass
    
    def compute_confidence(self,
                          query: str,
                          answer: str,
                          retrieved_docs: List[RetrievalResult]) -> float:
        """
        Calcula score de confianza de la respuesta (0-1).
        
        Factores:
        - Similitud de documentos recuperados
        - Número de fuentes
        - Claridad de la respuesta
        """
        pass
    
    def add_citations(self, answer: str, sources: List[Dict]) -> str:
        """
        Agrega citas en formato [1], [2] a la respuesta.
        """
        pass
```

**Dependencias**:
- langchain-openai
- langchain-core

**Casos de prueba**:
```python
# Test 1: Synthesize response
synthesizer = ResponseSynthesizer()
response = synthesizer.synthesize(
    query="¿Qué dice el POT?",
    retrieved_docs=results
)
assert 'answer' in response
assert 'sources' in response
assert response['confidence'] > 0

# Test 2: Streaming
stream = synthesizer.synthesize_streaming(
    query="Explica la normativa",
    retrieved_docs=results
)
chunks = list(stream)
assert len(chunks) > 0

# Test 3: Extract sources
sources = synthesizer.extract_sources(results)
assert all('title' in s for s in sources)
```

---

## 📝 Instrucciones de Implementación

### Paso 1: Instalación de Dependencias
```bash
pip install langchain langchain-community langchain-openai \
            chromadb sentence-transformers torch \
            tiktoken numpy pydantic
```

### Paso 2: Configuración
Crea `modules/rag/config.py`:
```python
from pydantic import BaseModel, Field

class RAGConfig(BaseModel):
    """Configuración del módulo RAG."""
    
    chroma_path: str = Field(default="chroma_db")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    reranker_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2")
    llm_model: str = Field(default="gpt-4")
    llm_temperature: float = Field(default=0.3)
    max_tokens: int = Field(default=1000)
    retrieval_k: int = Field(default=5)
    max_context_length: int = Field(default=4000)
    max_history: int = Field(default=10)
```

### Paso 3: Implementar Pipeline RAG Completo
Crea `modules/rag/pipeline.py`:
```python
from modules.rag import (
    SemanticRetriever,
    DocumentReranker,
    ContextManager,
    ConversationMemory,
    ResponseSynthesizer
)

class RAGPipeline:
    """Pipeline completo de RAG."""
    
    def __init__(self, config: RAGConfig):
        self.retriever = SemanticRetriever(
            chroma_path=config.chroma_path,
            embedding_model=config.embedding_model
        )
        self.reranker = DocumentReranker(model_name=config.reranker_model)
        self.context_manager = ContextManager(max_context_length=config.max_context_length)
        self.memory = ConversationMemory(max_history=config.max_history)
        self.synthesizer = ResponseSynthesizer(
            model_name=config.llm_model,
            temperature=config.llm_temperature,
            max_tokens=config.max_tokens
        )
    
    def query(self, user_query: str, use_reranking: bool = True) -> Dict[str, Any]:
        """
        Procesa consulta completa usando pipeline RAG.
        """
        # 1. Retrieve
        retrieved_docs = self.retriever.retrieve(user_query, k=10)
        
        # 2. Rerank (opcional)
        if use_reranking:
            retrieved_docs = self.reranker.rerank_with_metadata(
                user_query, 
                retrieved_docs,
                top_k=5
            )
        
        # 3. Build context
        context = self.context_manager.build_context(
            query=user_query,
            retrieved_docs=retrieved_docs,
            conversation_history=self.memory.get_history()
        )
        
        # 4. Synthesize response
        response = self.synthesizer.synthesize(
            query=user_query,
            retrieved_docs=retrieved_docs,
            conversation_history=self.memory.get_history()
        )
        
        # 5. Update memory
        self.memory.add_message("user", user_query)
        self.memory.add_message("assistant", response['answer'])
        
        return response
```

### Paso 4: Testing
```python
# tests/test_rag.py
import pytest
from modules.rag import RAGPipeline, RAGConfig

def test_rag_pipeline():
    config = RAGConfig()
    pipeline = RAGPipeline(config)
    
    response = pipeline.query("¿Qué dice el POT sobre zonas rurales?")
    
    assert 'answer' in response
    assert 'sources' in response
    assert len(response['sources']) > 0
```

---

## ✅ Criterios de Aceptación

### Funcionales
- ✅ Búsqueda semántica con ChromaDB funciona correctamente
- ✅ Re-ranking mejora la precisión de resultados
- ✅ Memoria conversacional mantiene contexto entre turnos
- ✅ Diferentes templates para diferentes tipos de consultas
- ✅ Respuestas incluyen citas de fuentes

### No Funcionales
- ✅ Latencia < 3 segundos para consultas simples
- ✅ Latencia < 5 segundos con re-ranking
- ✅ Manejo robusto de errores
- ✅ Logging completo de operaciones
- ✅ Tests con coverage > 80%

---

## 🚀 Ejemplo de Uso

```python
from modules.rag import RAGPipeline, RAGConfig

# Configurar pipeline
config = RAGConfig(
    llm_model="gpt-4",
    retrieval_k=5,
    max_history=10
)
pipeline = RAGPipeline(config)

# Consulta 1
response = pipeline.query("¿Qué dice el POT sobre construcción rural?")
print(f"Respuesta: {response['answer']}")
print(f"Fuentes: {response['sources']}")
print(f"Confianza: {response['confidence']}")

# Consulta 2 (con contexto de conversación anterior)
response = pipeline.query("¿Y qué excepciones hay?")
print(response['answer'])  # El LLM recuerda el contexto
```

---

## 📚 Referencias

- [LangChain RAG](https://python.langchain.com/docs/use_cases/question_answering/)
- [ChromaDB](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [OpenAI API](https://platform.openai.com/docs/)

---

**¿Listo para generar el código?** Copia este prompt en Cursor y pide:

> "Genera el módulo RAG completo siguiendo las especificaciones. Implementa todos los archivos con código production-ready, incluyendo manejo de errores, logging, type hints y documentación completa."
