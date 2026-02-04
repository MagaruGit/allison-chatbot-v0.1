# Guía de Integración e Implementación

## 📋 Documento de Integración del Sistema Completo

Este documento proporciona una guía paso a paso para implementar y conectar todos los módulos del sistema de copiloto con IA + RAG + PostGIS para infraestructura y planeación territorial.

---

## 🎯 Roadmap de Implementación

### Fase 1: Fundamentos (Semanas 1-4)

#### Semana 1: Setup del Proyecto
- [ ] Configurar repositorio Git y estructura de carpetas
- [ ] Setup de entorno virtual Python
- [ ] Instalar dependencias base
- [ ] Configurar Docker y Docker Compose
- [ ] Setup de bases de datos (PostgreSQL + PostGIS, ChromaDB)

```bash
# Estructura de directorios
mkdir -p modules/{ingestion,rag,sql_agent,geo_analytics,frontend,security}
mkdir -p data/{documents,csvs,shapefiles}
mkdir -p tests/{unit,integration}
mkdir -p logs
mkdir -p deployment/{docker,kubernetes}
```

#### Semana 2: Módulo de Ingesta
- [ ] Implementar document_processor.py
- [ ] Implementar csv_processor.py
- [ ] Implementar gis_processor.py
- [ ] Implementar vector_embedder.py
- [ ] Tests unitarios del módulo
- [ ] Ingesta de datos iniciales

#### Semana 3: Módulo RAG
- [ ] Implementar retriever.py
- [ ] Implementar reranker.py
- [ ] Implementar context_manager.py
- [ ] Implementar memory.py
- [ ] Implementar prompt_templates.py
- [ ] Tests del pipeline RAG completo

#### Semana 4: Módulo SQL Agent
- [ ] Implementar query_generator.py
- [ ] Implementar postgis_functions.py
- [ ] Implementar query_validator.py
- [ ] Implementar executor.py
- [ ] Tests de queries SQL/PostGIS

---

### Fase 2: Análisis y Visualización (Semanas 5-8)

#### Semana 5: Módulo Geo-Analytics
- [ ] Implementar spatial_analysis.py
- [ ] Implementar proximity_analyzer.py
- [ ] Implementar risk_assessment.py
- [ ] Implementar accessibility_calculator.py
- [ ] Tests de análisis espaciales

#### Semana 6: Módulo Geo-Analytics (cont.)
- [ ] Implementar map_generator.py
- [ ] Implementar metrics_calculator.py
- [ ] Integrar con PostGIS
- [ ] Tests de generación de mapas

#### Semana 7: Módulo Frontend
- [ ] Implementar main_app.py
- [ ] Implementar chat_interface.py
- [ ] Implementar map_viewer.py
- [ ] Componentes UI reutilizables

#### Semana 8: Módulo Frontend (cont.)
- [ ] Implementar dashboard.py
- [ ] Implementar export_handler.py
- [ ] Integración con backend
- [ ] Tests de UI

---

### Fase 3: Seguridad y Producción (Semanas 9-12)

#### Semana 9: Módulo de Seguridad
- [ ] Implementar auth.py
- [ ] Implementar rbac.py
- [ ] Implementar audit_logger.py
- [ ] Implementar rate_limiter.py
- [ ] Tests de seguridad

#### Semana 10: Integración Completa
- [ ] Integrar todos los módulos
- [ ] Orquestador principal
- [ ] Tests de integración end-to-end
- [ ] Performance testing

#### Semana 11: Despliegue
- [ ] Configurar Docker/Kubernetes
- [ ] CI/CD con GitHub Actions
- [ ] Setup de monitoring (Prometheus, Grafana)
- [ ] Setup de logging (ELK Stack)

#### Semana 12: Lanzamiento
- [ ] Pruebas de aceptación de usuario (UAT)
- [ ] Documentación final
- [ ] Capacitación de usuarios
- [ ] Lanzamiento a producción

---

## 🔗 Integración de Módulos

### 1. Orquestador Principal

Crea `app/orchestrator.py` que coordine todos los módulos:

```python
from modules.ingestion import IngestionOrchestrator
from modules.rag import RAGPipeline
from modules.sql_agent import SQLAgentPipeline
from modules.geo_analytics import GeoAnalyticsPipeline
from modules.security import AuthenticationManager, RBACManager, AuditLogger

class AllisonOrchestrator:
    """
    Orquestador principal del sistema Allison.
    Coordina todos los módulos y maneja el flujo de datos.
    """
    
    def __init__(self, config: Dict[str, Any]):
        # Seguridad
        self.auth_manager = AuthenticationManager(config['security']['secret_key'])
        self.rbac_manager = RBACManager()
        self.audit_logger = AuditLogger(config['db_connection'])
        
        # Procesamiento
        self.ingestion = IngestionOrchestrator(config['ingestion'])
        self.rag = RAGPipeline(config['rag'])
        self.sql_agent = SQLAgentPipeline(config['sql_agent'])
        self.geo_analytics = GeoAnalyticsPipeline(config['geo_analytics'])
    
    def process_user_query(self, 
                          query: str, 
                          user_token: str) -> Dict[str, Any]:
        """
        Procesa consulta de usuario end-to-end.
        
        Flujo:
        1. Autenticación y autorización
        2. Detección de tipo de consulta
        3. Enrutamiento al módulo apropiado
        4. Auditoría
        5. Respuesta al usuario
        """
        try:
            # 1. Autenticación
            user = self.auth_manager.verify_token(user_token)
            
            # 2. Detectar tipo de consulta
            query_type = self._detect_query_type(query)
            
            # 3. Verificar permisos
            required_permission = self._get_required_permission(query_type)
            if not self.rbac_manager.check_permission(user, required_permission):
                raise PermissionDeniedError()
            
            # 4. Procesar según tipo
            if query_type == 'document':
                response = self.rag.query(query)
            elif query_type == 'sql':
                response = self.sql_agent.query(query)
            elif query_type == 'geospatial':
                response = self.geo_analytics.analyze({'query': query})
            else:
                response = self._handle_generic_query(query)
            
            # 5. Auditoría
            self.audit_logger.log_query_execution(
                user=user,
                query_type=query_type,
                query=query,
                success=True
            )
            
            return {
                'success': True,
                'data': response,
                'query_type': query_type
            }
        
        except Exception as e:
            self.audit_logger.log_query_execution(
                user=user,
                query_type=query_type,
                query=query,
                success=False,
                error=str(e)
            )
            return {
                'success': False,
                'error': str(e)
            }
    
    def _detect_query_type(self, query: str) -> str:
        """
        Detecta tipo de consulta usando modelo de clasificación.
        """
        # Implementar con LLM o modelo clasificador
        keywords_sql = ['total', 'cuántos', 'cantidad', 'lista']
        keywords_geo = ['mapa', 'cerca', 'distancia', 'zona', 'área']
        
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in keywords_sql):
            return 'sql'
        elif any(kw in query_lower for kw in keywords_geo):
            return 'geospatial'
        else:
            return 'document'
    
    def _get_required_permission(self, query_type: str):
        """Mapea tipo de consulta a permiso requerido."""
        permissions_map = {
            'document': Permission.READ_DOCUMENTS,
            'sql': Permission.EXECUTE_SQL,
            'geospatial': Permission.VIEW_MAPS
        }
        return permissions_map.get(query_type, Permission.READ_DATA)
```

---

### 2. Configuración Centralizada

Crea `config/config.yaml`:

```yaml
# Configuración global del sistema Allison

app:
  name: "Allison - Copiloto IA Territorial"
  version: "1.0.0"
  environment: "production"  # development, staging, production

database:
  postgres:
    host: "${DB_HOST:localhost}"
    port: 5432
    database: "${DB_NAME:allison}"
    user: "${DB_USER:allison_user}"
    password: "${DB_PASSWORD}"
  
  postgis:
    host: "${DB_HOST:localhost}"
    port: 5432
    database: "${DB_NAME:allison}"
    user: "${DB_USER:allison_user}"
    password: "${DB_PASSWORD}"
    srid: 4326  # WGS84
  
  chromadb:
    path: "./chroma_db"
    collection_name: "documents"
  
  redis:
    host: "${REDIS_HOST:localhost}"
    port: 6379
    db: 0

ingestion:
  data_path: "./data"
  batch_size: 100
  chunk_size: 1000
  chunk_overlap: 200
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"

rag:
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  reranker_model: "cross-encoder/ms-marco-MiniLM-L-6-v2"
  llm_model: "gpt-4"
  llm_temperature: 0.3
  max_tokens: 1000
  retrieval_k: 5
  max_context_length: 4000
  max_history: 10

sql_agent:
  llm_model: "gpt-4"
  llm_temperature: 0.0
  max_query_time: 30
  max_results: 10000

geo_analytics:
  default_crs: "EPSG:4326"
  buffer_resolution: 16
  map_tiles: "OpenStreetMap"

frontend:
  title: "Allison - Gobernación de Antioquia"
  theme:
    primary_color: "#036E3A"
    background_color: "#FFFFFF"
    secondary_background_color: "#F0F2F6"
  
security:
  secret_key: "${SECRET_KEY}"
  jwt_algorithm: "HS256"
  token_expiry_hours: 24
  password_min_length: 12
  max_login_attempts: 5
  enable_mfa: false
  rate_limit:
    requests: 100
    window_seconds: 60

monitoring:
  prometheus:
    enabled: true
    port: 9090
  grafana:
    enabled: true
    port: 3000
  
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  format: "json"
  output: "both"  # console, file, both
  
openai:
  api_key: "${OPENAI_API_KEY}"
  organization: "${OPENAI_ORG_ID:}"
  
email:
  smtp_host: "${SMTP_HOST}"
  smtp_port: 587
  smtp_user: "${SMTP_USER}"
  smtp_password: "${SMTP_PASSWORD}"
  from_email: "allison@antioquia.gov.co"
```

---

### 3. Docker Compose

Crea `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL + PostGIS
  postgres:
    image: postgis/postgis:14-3.3
    container_name: allison-postgres
    environment:
      POSTGRES_DB: allison
      POSTGRES_USER: allison_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - allison-network
  
  # Redis
  redis:
    image: redis:7-alpine
    container_name: allison-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - allison-network
  
  # Aplicación principal
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: allison-app
    ports:
      - "8501:8501"
    environment:
      - DB_HOST=postgres
      - DB_NAME=allison
      - DB_USER=allison_user
      - DB_PASSWORD=${DB_PASSWORD}
      - REDIS_HOST=redis
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./data:/app/data
      - ./chroma_db:/app/chroma_db
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
    networks:
      - allison-network
  
  # Prometheus (monitoring)
  prometheus:
    image: prom/prometheus:latest
    container_name: allison-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./deployment/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - allison-network
  
  # Grafana (visualización)
  grafana:
    image: grafana/grafana:latest
    container_name: allison-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - allison-network

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  allison-network:
    driver: bridge
```

---

### 4. Tests de Integración

Crea `tests/integration/test_full_pipeline.py`:

```python
import pytest
from app.orchestrator import AllisonOrchestrator

class TestFullPipeline:
    """Tests de integración end-to-end."""
    
    @pytest.fixture
    def orchestrator(self):
        config = load_test_config()
        return AllisonOrchestrator(config)
    
    def test_document_query(self, orchestrator, test_user_token):
        """Test consulta de documentos (RAG)."""
        query = "¿Qué dice el POT sobre zonas rurales?"
        
        response = orchestrator.process_user_query(query, test_user_token)
        
        assert response['success'] == True
        assert response['query_type'] == 'document'
        assert 'answer' in response['data']
        assert len(response['data']['sources']) > 0
    
    def test_sql_query(self, orchestrator, test_user_token):
        """Test consulta SQL."""
        query = "Total de vías por municipio"
        
        response = orchestrator.process_user_query(query, test_user_token)
        
        assert response['success'] == True
        assert response['query_type'] == 'sql'
        assert 'results' in response['data']
    
    def test_geospatial_query(self, orchestrator, test_user_token):
        """Test consulta geoespacial."""
        query = "Mostrar municipios a menos de 10km de Medellín"
        
        response = orchestrator.process_user_query(query, test_user_token)
        
        assert response['success'] == True
        assert response['query_type'] == 'geospatial'
    
    def test_authentication_failure(self, orchestrator):
        """Test fallo de autenticación."""
        invalid_token = "invalid_token_12345"
        query = "Test query"
        
        response = orchestrator.process_user_query(query, invalid_token)
        
        assert response['success'] == False
        assert 'authentication' in response['error'].lower()
    
    def test_permission_denied(self, orchestrator, viewer_user_token):
        """Test permiso denegado."""
        # Usuario viewer intenta ejecutar SQL (no tiene permiso)
        query = "DROP TABLE users"
        
        response = orchestrator.process_user_query(query, viewer_user_token)
        
        assert response['success'] == False
        assert 'permission' in response['error'].lower()
```

---

## 🚀 Comandos de Despliegue

### Desarrollo Local
```bash
# 1. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 2. Levantar servicios
docker-compose up -d

# 3. Ejecutar migraciones
python scripts/migrate_db.py

# 4. Cargar datos iniciales
python scripts/load_initial_data.py

# 5. Iniciar aplicación
streamlit run app/main.py
```

### Producción (Kubernetes)
```bash
# 1. Crear namespace
kubectl create namespace allison

# 2. Crear secrets
kubectl create secret generic allison-secrets \
  --from-env-file=.env.production \
  -n allison

# 3. Aplicar configuraciones
kubectl apply -f deployment/kubernetes/ -n allison

# 4. Verificar despliegue
kubectl get pods -n allison
kubectl logs -f deployment/allison-app -n allison
```

---

## 📊 Monitoreo y Observabilidad

### Métricas a Monitorear
- **Performance**: Latencia de queries, throughput
- **Disponibilidad**: Uptime, health checks
- **Errores**: Tasa de error, tipos de errores
- **Uso**: Queries por usuario, features más usados
- **Recursos**: CPU, memoria, disco, conexiones DB

### Dashboards de Grafana
1. **Dashboard General**: Overview del sistema
2. **Dashboard de Performance**: Latencias y throughput
3. **Dashboard de Seguridad**: Intentos de login, permisos denegados
4. **Dashboard de Uso**: Estadísticas de usuarios y queries

---

## ✅ Checklist de Lanzamiento

### Pre-lanzamiento
- [ ] Todos los módulos implementados y testeados
- [ ] Tests de integración pasando
- [ ] Performance testing completado
- [ ] Security audit completado
- [ ] Documentación técnica completa
- [ ] Documentación de usuario completa
- [ ] Backups configurados
- [ ] Monitoring y alertas configurados
- [ ] Plan de disaster recovery documentado

### Lanzamiento
- [ ] Deploy a ambiente de staging
- [ ] UAT con usuarios piloto
- [ ] Corrección de issues encontrados
- [ ] Deploy a producción
- [ ] Smoke tests en producción
- [ ] Capacitación de usuarios
- [ ] Anuncio de lanzamiento

### Post-lanzamiento
- [ ] Monitoreo activo 24/7 primera semana
- [ ] Recolección de feedback de usuarios
- [ ] Corrección de bugs críticos
- [ ] Optimizaciones de performance
- [ ] Planificación de features futuros

---

## 📚 Recursos Adicionales

### Documentación
- `/docs/architecture/` - Diagramas de arquitectura
- `/docs/api/` - Documentación de APIs
- `/docs/user-guide/` - Guía de usuario
- `/docs/admin-guide/` - Guía de administrador

### Scripts Útiles
- `scripts/backup_db.sh` - Backup de base de datos
- `scripts/migrate_db.py` - Migraciones de esquema
- `scripts/load_data.py` - Carga de datos
- `scripts/health_check.py` - Health check del sistema

---

## 🎓 Capacitación

### Para Usuarios Finales
1. **Introducción a Allison** (30 min)
2. **Chat y Consultas** (1 hora)
3. **Visualización de Mapas** (1 hora)
4. **Dashboards y Reportes** (1 hora)

### Para Administradores
1. **Arquitectura del Sistema** (2 horas)
2. **Gestión de Usuarios y Permisos** (1 hora)
3. **Ingesta de Datos** (2 horas)
4. **Monitoreo y Troubleshooting** (2 horas)
5. **Seguridad y Backups** (1 hora)

---

**Versión**: 1.0.0  
**Última actualización**: 2026-02-04
