# Diagramas de Arquitectura del Sistema Allison

## 🏗️ Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CAPA DE PRESENTACIÓN                              │
│                                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Chat UI    │  │ Map Viewer   │  │  Dashboard   │  │   Export     │   │
│  │  (Streamlit) │  │   (Folium)   │  │   (Plotly)   │  │   Handler    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↕
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAPA DE ORQUESTACIÓN                                 │
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    Allison Orchestrator                                │  │
│  │  • Intent Detection  • Routing  • Context Management                  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↕
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CAPA DE PROCESAMIENTO                                  │
│                                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │     RAG     │  │ SQL Agent   │  │    Geo      │  │  Security   │       │
│  │  Pipeline   │  │  + PostGIS  │  │  Analytics  │  │   Layer     │       │
│  │             │  │             │  │             │  │             │       │
│  │ • Retriever │  │ • Generator │  │ • Spatial   │  │ • Auth      │       │
│  │ • Reranker  │  │ • Validator │  │ • Risk      │  │ • RBAC      │       │
│  │ • Memory    │  │ • Executor  │  │ • Access    │  │ • Audit     │       │
│  │ • Synth     │  │ • Formatter │  │ • Maps      │  │ • Encrypt   │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↕
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CAPA DE DATOS                                      │
│                                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │  ChromaDB   │  │ PostgreSQL  │  │   PostGIS   │  │    Redis    │       │
│  │  (Vectors)  │  │  (Tabular)  │  │ (Geospatial)│  │   (Cache)   │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↕
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CAPA DE INGESTA                                        │
│                                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │     PDFs    │  │    CSVs     │  │  Shapefiles │  │     APIs    │       │
│  │  Documents  │  │   Tabular   │  │     GIS     │  │   External  │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de Datos: Consulta de Usuario

```
┌──────────┐
│ Usuario  │
└────┬─────┘
     │ "¿Qué dice el POT sobre zonas rurales?"
     ↓
┌────────────────┐
│   Frontend     │
│  Chat Interface│
└────┬───────────┘
     │ query + user_token
     ↓
┌────────────────────┐
│   Orchestrator     │
│ 1. Authenticate    │──→ Security Module
│ 2. Detect Intent   │
│ 3. Route Request   │
└────┬───────────────┘
     │ tipo: 'document'
     ↓
┌─────────────────────────┐
│    RAG Pipeline         │
│ 1. Retrieve (ChromaDB)  │──→ ChromaDB
│ 2. Rerank               │
│ 3. Build Context        │
│ 4. LLM Generate         │──→ OpenAI GPT-4
│ 5. Add to Memory        │
└────┬────────────────────┘
     │ response + sources
     ↓
┌────────────────┐
│   Frontend     │
│  Display Answer│
└────┬───────────┘
     │ "Según el POT artículo 15..."
     ↓
┌──────────┐
│ Usuario  │
└──────────┘
```

---

## 🗺️ Flujo de Datos: Consulta Geoespacial

```
┌──────────┐
│ Usuario  │
└────┬─────┘
     │ "Mostrar municipios a 10km de Medellín"
     ↓
┌────────────────┐
│   Frontend     │
│  Chat Interface│
└────┬───────────┘
     │ query
     ↓
┌────────────────────┐
│   Orchestrator     │
│ tipo: 'geospatial' │
└────┬───────────────┘
     │
     ↓
┌────────────────────────┐
│  Geo Analytics         │
│ 1. Load Medellín point │──→ PostGIS
│ 2. Buffer 10km         │
│ 3. Intersect municipios│──→ PostGIS
│ 4. Generate map        │
└────┬───────────────────┘
     │ GeoDataFrame + map
     ↓
┌────────────────┐
│   Frontend     │
│  Map Viewer    │
│ Display map    │──→ Folium (Interactive)
└────┬───────────┘
     │ Mapa interactivo
     ↓
┌──────────┐
│ Usuario  │
└──────────┘
```

---

## 💾 Flujo de Ingesta de Datos

```
┌────────────┐
│  Fuentes   │
│  de Datos  │
└─────┬──────┘
      │
      ├─→ PDFs ──────────┐
      ├─→ CSVs ──────────┤
      ├─→ Shapefiles ────┤
      └─→ APIs ──────────┤
                         │
                         ↓
              ┌──────────────────────┐
              │ Ingestion Pipeline   │
              │ • Validate           │
              │ • Transform          │
              │ • Clean              │
              └──────────┬───────────┘
                         │
         ┌───────────────┼───────────────┐
         ↓               ↓               ↓
    ┌─────────┐    ┌──────────┐   ┌──────────┐
    │Document │    │   CSV    │   │   GIS    │
    │Processor│    │Processor │   │Processor │
    └────┬────┘    └────┬─────┘   └────┬─────┘
         │              │              │
         ↓              ↓              ↓
    ┌─────────┐    ┌──────────┐   ┌──────────┐
    │ Vector  │    │PostgreSQL│   │ PostGIS  │
    │Embedder │    │          │   │          │
    └────┬────┘    └────┬─────┘   └────┬─────┘
         │              │              │
         ↓              ↓              ↓
    ┌─────────┐    ┌──────────┐   ┌──────────┐
    │ChromaDB │    │PostgreSQL│   │ PostGIS  │
    │(Vectors)│    │ (Tables) │   │ (Geoms)  │
    └─────────┘    └──────────┘   └──────────┘
```

---

## 🔐 Flujo de Autenticación y Autorización

```
┌──────────┐
│ Usuario  │
└────┬─────┘
     │ username + password
     ↓
┌────────────────────────┐
│  Authentication Manager│
│ 1. Verify credentials  │──→ PostgreSQL (users table)
│ 2. Check active status │
│ 3. Generate JWT        │
└────┬───────────────────┘
     │ JWT token
     ↓
┌──────────┐
│ Usuario  │──→ Guarda token en sesión
└────┬─────┘
     │ Siguiente request + token
     ↓
┌────────────────────────┐
│     Orchestrator       │
│ 1. Verify JWT          │──→ Authentication Manager
│ 2. Extract user info   │
└────┬───────────────────┘
     │ User object
     ↓
┌────────────────────────┐
│    RBAC Manager        │
│ 1. Get user roles      │
│ 2. Check permissions   │──→ PostgreSQL (roles, permissions)
│ 3. Authorize action    │
└────┬───────────────────┘
     │ authorized=True
     ↓
┌────────────────────────┐
│   Process Request      │
└────┬───────────────────┘
     │
     ↓
┌────────────────────────┐
│    Audit Logger        │
│ Log action             │──→ PostgreSQL (audit_log)
└────────────────────────┘
```

---

## 📊 Arquitectura de Despliegue (Producción)

```
                    ┌──────────────┐
                    │    Internet  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Load Balancer│
                    │    (Nginx)    │
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐       ┌────▼────┐      ┌────▼────┐
    │Frontend │       │Frontend │      │Frontend │
    │  Pod 1  │       │  Pod 2  │      │  Pod 3  │
    └────┬────┘       └────┬────┘      └────┬────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────▼───────┐
                    │  API Service │
                    │ (Orchestrator)│
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐       ┌────▼────┐      ┌────▼────┐
    │   RAG   │       │   SQL   │      │   Geo   │
    │ Service │       │ Agent   │      │Analytics│
    └────┬────┘       └────┬────┘      └────┬────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐       ┌────▼────┐      ┌────▼────┐
    │ChromaDB │       │PostgreSQL│     │  Redis  │
    │(StatefulSet)    │(Managed) │     │(Managed)│
    └─────────┘       └──────────┘     └─────────┘
```

---

## 🔄 Pipeline RAG Detallado

```
┌──────────────┐
│ User Query   │
└──────┬───────┘
       │
       ↓
┌──────────────────┐
│  1. Retriever    │
│  • Embedding     │──→ Sentence Transformers
│  • Vector Search │──→ ChromaDB
│  • Top-K (10)    │
└──────┬───────────┘
       │ 10 documents
       ↓
┌──────────────────┐
│  2. Reranker     │
│  • Cross-Encoder│──→ MS-MARCO model
│  • Score docs   │
│  • Top-K (5)    │
└──────┬───────────┘
       │ 5 best documents
       ↓
┌──────────────────┐
│ 3. Context Mgr   │
│  • Format docs  │
│  • Add metadata │
│  • Truncate     │
└──────┬───────────┘
       │ formatted context
       ↓
┌──────────────────┐
│ 4. Memory        │
│  • Get history  │
│  • Add context  │
└──────┬───────────┘
       │ full context
       ↓
┌──────────────────┐
│ 5. Prompt Template│
│  • Select type  │
│  • Fill template│
└──────┬───────────┘
       │ prompt
       ↓
┌──────────────────┐
│ 6. LLM (GPT-4)   │
│  • Generate     │──→ OpenAI API
│  • Stream       │
└──────┬───────────┘
       │ answer
       ↓
┌──────────────────┐
│ 7. Response      │
│  • Add sources  │
│  • Compute conf │
│  • Update memory│
└──────┬───────────┘
       │
       ↓
┌──────────────┐
│ User         │
└──────────────┘
```

---

## 🗃️ Modelo de Datos: Base de Datos Relacional

```sql
-- Users and Authentication
users
├── id (PK)
├── email
├── username
├── password_hash
├── full_name
├── organization
├── is_active
├── created_at
└── last_login

roles
├── id (PK)
├── name
└── description

permissions
├── id (PK)
├── name
└── description

user_roles
├── user_id (FK)
└── role_id (FK)

role_permissions
├── role_id (FK)
└── permission_id (FK)

-- Audit Log
audit_log
├── id (PK)
├── timestamp
├── user_id (FK)
├── action
├── resource
├── resource_id
├── details (JSON)
├── ip_address
├── success
└── error_message

-- Infrastructure Data
municipios (PostGIS)
├── id (PK)
├── codigo_dane
├── nombre
├── subregion
├── poblacion
├── area_km2
└── geometry (MULTIPOLYGON)

vias (PostGIS)
├── id (PK)
├── codigo
├── tipo (primaria/secundaria/terciaria)
├── estado (bueno/regular/malo)
├── longitud_km
├── municipio_id (FK)
└── geometry (LINESTRING)

zonas_riesgo (PostGIS)
├── id (PK)
├── tipo_riesgo
├── nivel (bajo/medio/alto)
├── descripcion
└── geometry (POLYGON)

-- Vector Database (ChromaDB)
documents_collection
├── id
├── document
├── embedding (vector)
└── metadata
    ├── source
    ├── title
    ├── date
    ├── type
    └── page
```

---

## 🎯 Módulos y sus Responsabilidades

```
┌─────────────────────────────────────────────────────────────┐
│ INGESTION MODULE                                             │
├─────────────────────────────────────────────────────────────┤
│ Input:  PDFs, CSVs, Shapefiles, API responses              │
│ Output: Data in PostgreSQL, PostGIS, ChromaDB               │
│ Tasks:                                                       │
│  • Parse documents                                           │
│  • Clean and validate data                                   │
│  • Generate embeddings                                       │
│  • Load to databases                                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ RAG MODULE                                                   │
├─────────────────────────────────────────────────────────────┤
│ Input:  User query, conversation history                    │
│ Output: Contextual answer with sources                       │
│ Tasks:                                                       │
│  • Semantic search in ChromaDB                              │
│  • Rerank results                                            │
│  • Build context                                             │
│  • Generate answer with LLM                                  │
│  • Manage conversation memory                                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ SQL AGENT MODULE                                             │
├─────────────────────────────────────────────────────────────┤
│ Input:  Natural language query                              │
│ Output: SQL results, formatted data                          │
│ Tasks:                                                       │
│  • Convert NL to SQL using LLM                              │
│  • Validate and sanitize queries                            │
│  • Execute safely                                            │
│  • Format results                                            │
│  • Handle PostGIS functions                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ GEO-ANALYTICS MODULE                                         │
├─────────────────────────────────────────────────────────────┤
│ Input:  Spatial query, parameters                           │
│ Output: Analysis results, maps                               │
│ Tasks:                                                       │
│  • Spatial analysis (buffer, intersection)                   │
│  • Risk assessment                                           │
│  • Accessibility calculations                                │
│  • Generate interactive maps                                 │
│  • Calculate metrics                                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ FRONTEND MODULE                                              │
├─────────────────────────────────────────────────────────────┤
│ Input:  User interactions                                    │
│ Output: UI components, visualizations                        │
│ Tasks:                                                       │
│  • Render chat interface                                     │
│  • Display interactive maps                                  │
│  • Show dashboards                                           │
│  • Handle exports                                            │
│  • Manage sessions                                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ SECURITY MODULE                                              │
├─────────────────────────────────────────────────────────────┤
│ Input:  Credentials, tokens, requests                       │
│ Output: Auth tokens, permissions, audit logs                │
│ Tasks:                                                       │
│  • Authenticate users (JWT)                                  │
│  • Authorize actions (RBAC)                                  │
│  • Audit all operations                                      │
│  • Rate limiting                                             │
│  • Encrypt sensitive data                                    │
└─────────────────────────────────────────────────────────────┘
```

---

**Nota**: Todos estos diagramas están disponibles en formato visual en la documentación del proyecto.
