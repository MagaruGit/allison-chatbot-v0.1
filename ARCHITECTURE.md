# Arquitectura del Sistema de Copiloto con IA + RAG + PostGIS
## Sistema de Infraestructura y Planeación Territorial - Gobierno

---

## 📋 Índice

1. [Visión General del Sistema](#visión-general-del-sistema)
2. [Arquitectura de Componentes](#arquitectura-de-componentes)
3. [Módulos del Sistema](#módulos-del-sistema)
4. [Flujos de Datos](#flujos-de-datos)
5. [Stack Tecnológico](#stack-tecnológico)
6. [Seguridad y Cumplimiento](#seguridad-y-cumplimiento)
7. [Escalabilidad y Despliegue](#escalabilidad-y-despliegue)

---

## 🎯 Visión General del Sistema

### Objetivo
Desarrollar un sistema de copiloto inteligente que asista a funcionarios gubernamentales en la toma de decisiones sobre infraestructura y planeación territorial, utilizando:
- **IA Generativa** para análisis y recomendaciones
- **RAG (Retrieval Augmented Generation)** para acceso contextual a documentación
- **PostGIS** para análisis geoespacial avanzado
- **Agentes SQL** para consultas inteligentes de bases de datos

### Casos de Uso Principales
1. **Consultas de Normativa**: "¿Qué dice el POT sobre construcción en zona rural?"
2. **Análisis Geoespacial**: "Mostrar zonas de riesgo a 500m de ríos principales"
3. **Estadísticas de Infraestructura**: "Total de vías terciarias por municipio"
4. **Recomendaciones**: "Priorizar proyectos de vías según necesidades y presupuesto"
5. **Alertas Territoriales**: "Identificar áreas con alto riesgo de deslizamiento"

---

## 🏗️ Arquitectura de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Streamlit   │  │  Mapbox GL   │  │  Dashboard   │          │
│  │     UI       │  │     Maps     │  │   Analytics  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATION LAYER                         │
│  ┌────────────────────────────────────────────────────────┐     │
│  │           AI Copilot Orchestrator (LangChain)          │     │
│  │  • Intent Detection • Context Management • Response    │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        PROCESSING LAYER                          │
│ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌──────────────┐    │
│ │    RAG    │ │ SQL Agent │ │    Geo    │ │   Security   │    │
│ │  Retrieval│ │  PostGIS  │ │ Analytics │ │     Layer    │    │
│ └───────────┘ └───────────┘ └───────────┘ └──────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                              │
│ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌──────────────┐    │
│ │  ChromaDB │ │ PostgreSQL│ │  PostGIS  │ │  File Store  │    │
│ │  (Vector) │ │  + PostGIS│ │ Geo Index │ │   (S3/Local) │    │
│ └───────────┘ └───────────┘ └───────────┘ └──────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      INGESTION PIPELINE                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   PDFs   │  │   CSVs   │  │   APIs   │  │ Shapefiles│       │
│  │Documents │  │  Tabular │  │  External│  │    GIS    │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Módulos del Sistema

### **Módulo 1: Ingestion Pipeline**
**Directorio**: `/modules/ingestion/`

#### Responsabilidades
- Cargar y procesar documentos de múltiples fuentes (PDFs, CSVs, APIs, Shapefiles)
- Transformar datos a formatos estructurados
- Generar embeddings vectoriales para documentos
- Cargar datos geoespaciales a PostGIS
- Validar calidad y completitud de datos

#### Inputs
- Documentos PDF (normativas, POT, estudios)
- Archivos CSV (estadísticas, inventarios)
- Shapefiles/GeoJSON (mapas, capas GIS)
- APIs externas (IGAC, DANE, etc.)

#### Outputs
- Vectores en ChromaDB (documentos embeddeados)
- Registros en PostgreSQL (datos estructurados)
- Geometrías en PostGIS (datos geoespaciales)
- Logs de ingesta y metadatos

#### Componentes
```
ingestion/
├── __init__.py
├── document_processor.py      # Procesamiento de PDFs/DOCs
├── csv_processor.py            # Procesamiento de tablas
├── gis_processor.py            # Procesamiento de datos GIS
├── api_fetcher.py              # Integración con APIs externas
├── vector_embedder.py          # Generación de embeddings
├── data_validator.py           # Validación de datos
└── orchestrator.py             # Orquestación de pipeline
```

---

### **Módulo 2: RAG Retrieval System**
**Directorio**: `/modules/rag/`

#### Responsabilidades
- Búsqueda semántica en base de conocimiento
- Recuperación de contexto relevante
- Re-ranking de documentos
- Gestión de memoria conversacional
- Síntesis de respuestas con contexto

#### Inputs
- Query del usuario (texto natural)
- Historial de conversación
- Filtros opcionales (fecha, tipo, ubicación)

#### Outputs
- Documentos relevantes recuperados
- Contexto enriquecido para el LLM
- Metadatos de fuentes
- Score de relevancia

#### Componentes
```
rag/
├── __init__.py
├── retriever.py                # Motor de búsqueda vectorial
├── reranker.py                 # Re-ranking con modelo
├── context_manager.py          # Gestión de contexto
├── memory.py                   # Memoria conversacional
├── prompt_templates.py         # Templates de prompts
└── response_synthesizer.py    # Síntesis de respuestas
```

---

### **Módulo 3: SQL Agent (PostGIS)**
**Directorio**: `/modules/sql_agent/`

#### Responsabilidades
- Convertir lenguaje natural a consultas SQL/PostGIS
- Ejecutar queries complejas de forma segura
- Realizar análisis geoespaciales (intersecciones, buffers, etc.)
- Validar y sanitizar consultas
- Formatear resultados para presentación

#### Inputs
- Pregunta en lenguaje natural
- Esquema de base de datos
- Parámetros de seguridad

#### Outputs
- Consultas SQL generadas
- Resultados de ejecución
- Datos geoespaciales (GeoJSON)
- Explicación de la consulta

#### Componentes
```
sql_agent/
├── __init__.py
├── query_generator.py          # NL → SQL con LLM
├── postgis_functions.py        # Funciones geoespaciales
├── query_validator.py          # Validación y sanitización
├── executor.py                 # Ejecución segura de queries
├── result_formatter.py         # Formateo de resultados
└── schema_manager.py           # Gestión de esquemas
```

---

### **Módulo 4: Geo-Analytics Engine**
**Directorio**: `/modules/geo_analytics/`

#### Responsabilidades
- Análisis espacial avanzado (proximidad, densidad, accesibilidad)
- Cálculos de métricas territoriales
- Detección de patrones geoespaciales
- Generación de mapas y visualizaciones
- Análisis predictivo geoespacial

#### Inputs
- Datos geoespaciales (PostGIS)
- Parámetros de análisis
- Capas de referencia

#### Outputs
- Métricas calculadas
- Mapas generados (GeoJSON/PNG)
- Análisis de patrones
- Recomendaciones territoriales

#### Componentes
```
geo_analytics/
├── __init__.py
├── spatial_analysis.py         # Análisis espacial
├── proximity_analyzer.py       # Análisis de proximidad
├── risk_assessment.py          # Evaluación de riesgos
├── accessibility_calculator.py # Cálculo de accesibilidad
├── map_generator.py            # Generación de mapas
└── metrics_calculator.py       # Métricas territoriales
```

---

### **Módulo 5: Frontend Layer**
**Directorio**: `/modules/frontend/`

#### Responsabilidades
- Interface de chat conversacional
- Visualización de mapas interactivos
- Dashboards de estadísticas
- Exportación de reportes
- Gestión de sesiones de usuario

#### Inputs
- Interacciones del usuario
- Respuestas del backend
- Datos para visualización

#### Outputs
- Interface HTML/CSS/JS
- Mapas interactivos
- Gráficos y tablas
- Documentos exportados

#### Componentes
```
frontend/
├── __init__.py
├── main_app.py                 # App principal Streamlit
├── chat_interface.py           # Interface de chat
├── map_viewer.py               # Visor de mapas
├── dashboard.py                # Dashboards analíticos
├── export_handler.py           # Exportación de datos
└── components/
    ├── sidebar.py
    ├── header.py
    └── footer.py
```

---

### **Módulo 6: Security & Authentication**
**Directorio**: `/modules/security/`

#### Responsabilidades
- Autenticación de usuarios
- Control de acceso basado en roles (RBAC)
- Auditoría de acciones
- Encriptación de datos sensibles
- Rate limiting y prevención de ataques
- Gestión de API keys y secretos

#### Inputs
- Credenciales de usuario
- Tokens de sesión
- Requests HTTP

#### Outputs
- Tokens de autenticación
- Permisos de usuario
- Logs de auditoría
- Alertas de seguridad

#### Componentes
```
security/
├── __init__.py
├── auth.py                     # Autenticación
├── rbac.py                     # Control de acceso
├── encryption.py               # Encriptación
├── audit_logger.py             # Auditoría
├── rate_limiter.py             # Rate limiting
└── secrets_manager.py          # Gestión de secretos
```

---

## 🔄 Flujos de Datos

### Flujo 1: Consulta Simple (RAG)
```
Usuario → Frontend → Orchestrator → RAG Retrieval → ChromaDB
                           ↓
                      LLM (GPT-4) ← Contexto
                           ↓
                    Frontend ← Respuesta
```

### Flujo 2: Consulta SQL/Geo
```
Usuario → Frontend → Orchestrator → SQL Agent → Query Generator (LLM)
                           ↓
                    PostGIS/PostgreSQL ← SQL Query
                           ↓
                    Result Formatter → Frontend
```

### Flujo 3: Análisis Geoespacial
```
Usuario → Frontend → Orchestrator → Geo-Analytics Engine
                           ↓
                    PostGIS (datos) + Algoritmos
                           ↓
                    Map Generator + Metrics
                           ↓
                    Frontend (Mapbox GL)
```

### Flujo 4: Ingesta de Datos
```
Fuente de Datos → Ingestion Pipeline → Processors
                           ↓
            ┌──────────────┼──────────────┐
            ↓              ↓               ↓
       ChromaDB      PostgreSQL        PostGIS
      (vectores)     (tabular)         (geo)
```

---

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.10+**: Lenguaje principal
- **FastAPI**: API REST (alternativa a Streamlit para producción)
- **LangChain**: Orquestación de LLMs y agentes
- **OpenAI GPT-4**: Modelo de lenguaje principal
- **Anthropic Claude** (opcional): Modelo alternativo

### Bases de Datos
- **PostgreSQL 14+**: Base de datos relacional
- **PostGIS 3.3+**: Extensión geoespacial
- **ChromaDB**: Base de datos vectorial para RAG
- **Redis**: Cache y gestión de sesiones

### Procesamiento de Datos
- **Pandas**: Manipulación de datos tabulares
- **GeoPandas**: Procesamiento de datos geoespaciales
- **PyPDF2/PyMuPDF**: Extracción de texto de PDFs
- **Sentence-Transformers**: Generación de embeddings

### Frontend
- **Streamlit**: Prototipado rápido
- **React + TypeScript** (producción): Interface moderna
- **Mapbox GL JS**: Visualización de mapas
- **Plotly/D3.js**: Gráficos interactivos

### DevOps & Infraestructura
- **Docker**: Containerización
- **Kubernetes**: Orquestación (producción)
- **GitHub Actions**: CI/CD
- **AWS/GCP**: Cloud hosting
- **Nginx**: Reverse proxy y balanceo

### Seguridad
- **OAuth 2.0 / SAML**: Autenticación SSO
- **JWT**: Tokens de sesión
- **Keycloak**: Identity management
- **HashiCorp Vault**: Gestión de secretos

---

## 🔒 Seguridad y Cumplimiento

### Principios de Seguridad
1. **Defensa en Profundidad**: Múltiples capas de seguridad
2. **Principio de Menor Privilegio**: Acceso mínimo necesario
3. **Zero Trust**: Verificación continua
4. **Auditoría Completa**: Logs de todas las operaciones

### Controles Implementados
- ✅ Autenticación multi-factor (MFA)
- ✅ Encriptación en tránsito (TLS 1.3)
- ✅ Encriptación en reposo (AES-256)
- ✅ Sanitización de inputs (SQL injection prevention)
- ✅ Rate limiting por usuario/IP
- ✅ Auditoría de accesos y cambios
- ✅ Backup automático y disaster recovery

### Cumplimiento Normativo
- **Ley de Protección de Datos Personales (Colombia)**
- **Gobierno Digital** (Decreto 1008/2018)
- **Estándares de Seguridad** (ISO 27001)

---

## 📈 Escalabilidad y Despliegue

### Arquitectura de Despliegue

#### Desarrollo
```
Docker Compose
├── app (Streamlit)
├── postgres + postgis
├── chromadb
└── redis
```

#### Producción
```
Kubernetes Cluster
├── Ingress (Nginx)
├── Frontend Pods (React)
├── API Pods (FastAPI)
├── Worker Pods (Celery)
├── PostgreSQL (Managed Service)
├── ChromaDB (StatefulSet)
└── Redis (Managed Service)
```

### Estrategia de Escalado
- **Horizontal**: Múltiples réplicas de servicios stateless
- **Vertical**: Más recursos para PostgreSQL/PostGIS
- **Cache**: Redis para queries frecuentes
- **CDN**: Assets estáticos y mapas pre-renderizados

### Monitoreo
- **Prometheus + Grafana**: Métricas del sistema
- **ELK Stack**: Logs centralizados
- **Sentry**: Tracking de errores
- **DataDog**: APM (Application Performance Monitoring)

---

## 📊 Métricas de Éxito

### KPIs Técnicos
- Latencia de respuesta < 2 segundos (p95)
- Disponibilidad > 99.5%
- Tasa de error < 0.1%
- Throughput > 100 queries/minuto

### KPIs de Negocio
- Tiempo de análisis territorial reducido en 70%
- Satisfacción de usuarios > 4.5/5
- Adopción por 80% de funcionarios objetivo
- ROI positivo en 12 meses

---

## 🚀 Roadmap de Implementación

### Fase 1: MVP (3 meses)
- ✅ Módulo de ingesta básico
- ✅ RAG con documentos normativos
- ✅ Frontend Streamlit
- ✅ Despliegue en Docker

### Fase 2: Expansión (3 meses)
- 🔄 SQL Agent + PostGIS
- 🔄 Geo-Analytics básico
- 🔄 Autenticación y RBAC
- 🔄 APIs REST

### Fase 3: Producción (3 meses)
- 🔜 Frontend React avanzado
- 🔜 Análisis predictivo
- 🔜 Integración con sistemas gubernamentales
- 🔜 Despliegue Kubernetes

### Fase 4: Optimización (ongoing)
- 🔜 Machine Learning para recomendaciones
- 🔜 Modelos fine-tuned
- 🔜 Móvil/Progressive Web App
- 🔜 Integraciones adicionales

---

## 📚 Referencias y Recursos

### Documentación Técnica
- [LangChain Documentation](https://python.langchain.com/)
- [PostGIS Manual](https://postgis.net/documentation/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [Streamlit Documentation](https://docs.streamlit.io/)

### Repositorios de Referencia
- `modules/` - Implementación de módulos
- `docs/cursor-prompts/` - Prompts para generación de código
- `tests/` - Suite de pruebas
- `deployment/` - Configuración de despliegue

---

**Versión**: 1.0.0  
**Fecha**: 2026-02-04  
**Autor**: Equipo de Arquitectura - Allison AI Copilot  
**Estado**: Diseño Aprobado
