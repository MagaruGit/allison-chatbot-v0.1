# Prompt para Módulo SQL Agent + PostGIS

## 📋 Contexto del Proyecto
Estás desarrollando el **Módulo SQL Agent** para un sistema de copiloto con IA que convierte consultas en lenguaje natural a queries SQL/PostGIS. Este módulo permite a usuarios no técnicos realizar consultas complejas sobre bases de datos relacionales y geoespaciales de forma conversacional.

## 🎯 Objetivo del Módulo
Crear un agente SQL inteligente que:
1. Convierta lenguaje natural a SQL/PostGIS seguro
2. Ejecute queries de forma controlada y validada
3. Realice análisis geoespaciales (buffers, intersecciones, proximidad)
4. Formatee resultados de forma comprensible
5. Explique las queries generadas
6. Maneje esquemas complejos automáticamente

## 📁 Estructura de Archivos a Generar

```
modules/sql_agent/
├── __init__.py
├── config.py                   # Configuración del módulo
├── query_generator.py          # NL → SQL con LLM
├── postgis_functions.py        # Funciones geoespaciales
├── query_validator.py          # Validación y sanitización
├── executor.py                 # Ejecución segura de queries
├── result_formatter.py         # Formateo de resultados
├── schema_manager.py           # Gestión de esquemas DB
└── utils/
    ├── __init__.py
    ├── sql_utils.py
    └── logger.py
```

## 🔧 Especificaciones Técnicas

### 1. query_generator.py

**Propósito**: Convertir lenguaje natural a SQL usando LLM.

**Funcionalidades requeridas**:
```python
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from typing import Dict, Any, Optional

class SQLQueryGenerator:
    """
    Convierte consultas en lenguaje natural a SQL usando LLM.
    """
    
    def __init__(self,
                 db_uri: str,
                 llm_model: str = "gpt-4",
                 temperature: float = 0.0):
        """
        Args:
            db_uri: URI de conexión a PostgreSQL/PostGIS
            llm_model: Modelo de LLM a usar
            temperature: 0 para queries determinísticas
        """
        self.db = SQLDatabase.from_uri(db_uri)
        self.llm = ChatOpenAI(model_name=llm_model, temperature=temperature)
        self.chain = create_sql_query_chain(self.llm, self.db)
    
    def generate_query(self, 
                      natural_language: str,
                      table_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Genera query SQL desde lenguaje natural.
        
        Args:
            natural_language: Consulta en lenguaje natural
            table_hint: Sugerencia de tabla (opcional)
            
        Returns:
            {
                'sql': str,
                'explanation': str,
                'tables_used': List[str],
                'query_type': str  # SELECT, INSERT, UPDATE, DELETE
            }
        """
        pass
    
    def generate_postgis_query(self,
                              spatial_query: str,
                              geometry_column: str = "geometry") -> Dict[str, Any]:
        """
        Genera query PostGIS para análisis geoespacial.
        
        Ejemplos:
        - "municipios a menos de 10km de Medellín"
        - "área total de zonas protegidas"
        - "vías que intersectan con ríos"
        """
        pass
    
    def add_spatial_context(self, query: str) -> str:
        """
        Enriquece query SQL estándar con contexto espacial.
        Agrega JOINs geoespaciales cuando sea necesario.
        """
        pass
    
    def optimize_query(self, sql: str) -> str:
        """
        Optimiza query SQL:
        - Agrega índices sugeridos
        - Reescribe subqueries ineficientes
        - Limita resultados si no hay LIMIT
        """
        pass
    
    def explain_query(self, sql: str) -> str:
        """
        Genera explicación en lenguaje natural de lo que hace el SQL.
        """
        pass
```

**Prompt Template para LLM**:
```python
SQL_GENERATION_PROMPT = """Eres un experto en SQL y PostGIS para bases de datos de infraestructura territorial.

Esquema de la base de datos:
{schema}

Tablas disponibles:
{tables}

Ejemplos de queries:
{examples}

Instrucciones:
1. Genera SQL válido para PostgreSQL 14+ con PostGIS 3.3+
2. Usa SOLO tablas y columnas que existen en el esquema
3. Para consultas espaciales, usa funciones PostGIS (ST_Distance, ST_Intersects, etc.)
4. Siempre agrega LIMIT si no se especifica (máx 1000 registros)
5. Usa nombres de columnas exactos (case-sensitive)
6. Sanitiza inputs para prevenir SQL injection

Consulta del usuario: {query}

Genera el SQL:
"""
```

**Dependencias**:
- langchain
- langchain-openai
- sqlalchemy
- psycopg2-binary

**Casos de prueba**:
```python
# Test 1: Query simple
generator = SQLQueryGenerator("postgresql://...")
result = generator.generate_query("Total de vías por municipio")
assert 'SELECT' in result['sql'].upper()
assert result['query_type'] == 'SELECT'

# Test 2: Query espacial
result = generator.generate_postgis_query(
    "municipios a menos de 5km de Medellín"
)
assert 'ST_Distance' in result['sql'] or 'ST_DWithin' in result['sql']

# Test 3: Explicación
explanation = generator.explain_query(result['sql'])
assert len(explanation) > 0
```

---

### 2. postgis_functions.py

**Propósito**: Librería de funciones PostGIS pre-construidas para análisis comunes.

**Funcionalidades requeridas**:
```python
from typing import List, Dict, Any, Tuple
import geopandas as gpd

class PostGISFunctions:
    """
    Funciones geoespaciales pre-construidas para análisis comunes.
    """
    
    def __init__(self, db_connection):
        """
        Args:
            db_connection: Conexión SQLAlchemy a PostGIS
        """
        self.conn = db_connection
    
    def buffer_analysis(self,
                       table: str,
                       geom_column: str,
                       buffer_distance: float,
                       units: str = "meters") -> gpd.GeoDataFrame:
        """
        Crea buffer alrededor de geometrías.
        
        Args:
            table: Nombre de tabla
            geom_column: Columna de geometría
            buffer_distance: Distancia del buffer
            units: 'meters', 'kilometers', 'degrees'
            
        Returns:
            GeoDataFrame con geometrías bufferadas
        """
        sql = f"""
        SELECT *, 
               ST_Buffer({geom_column}::geography, {buffer_distance})::geometry as buffer_geom
        FROM {table}
        """
        return gpd.read_postgis(sql, self.conn, geom_col='buffer_geom')
    
    def proximity_analysis(self,
                          source_table: str,
                          target_table: str,
                          max_distance: float,
                          units: str = "meters") -> gpd.GeoDataFrame:
        """
        Encuentra features dentro de distancia máxima.
        
        Ejemplo: "Encuentra escuelas a menos de 2km de cada municipio"
        """
        sql = f"""
        SELECT 
            s.*,
            t.id as target_id,
            ST_Distance(s.geometry::geography, t.geometry::geography) as distance_m
        FROM {source_table} s
        CROSS JOIN LATERAL (
            SELECT id, geometry
            FROM {target_table} t
            WHERE ST_DWithin(
                s.geometry::geography, 
                t.geometry::geography, 
                {max_distance}
            )
            ORDER BY s.geometry <-> t.geometry
            LIMIT 10
        ) t
        """
        return gpd.read_postgis(sql, self.conn, geom_col='geometry')
    
    def intersection_analysis(self,
                             table1: str,
                             table2: str,
                             output_table: Optional[str] = None) -> gpd.GeoDataFrame:
        """
        Encuentra intersecciones entre dos capas.
        
        Ejemplo: "Vías que cruzan zonas protegidas"
        """
        sql = f"""
        SELECT 
            t1.id as id1,
            t2.id as id2,
            ST_Intersection(t1.geometry, t2.geometry) as geometry,
            ST_Area(ST_Intersection(t1.geometry, t2.geometry)) as intersection_area
        FROM {table1} t1
        JOIN {table2} t2 ON ST_Intersects(t1.geometry, t2.geometry)
        WHERE ST_IsValid(t1.geometry) AND ST_IsValid(t2.geometry)
        """
        gdf = gpd.read_postgis(sql, self.conn, geom_col='geometry')
        
        if output_table:
            gdf.to_postgis(output_table, self.conn, if_exists='replace')
        
        return gdf
    
    def area_calculation(self,
                        table: str,
                        geom_column: str = "geometry",
                        group_by: Optional[str] = None) -> pd.DataFrame:
        """
        Calcula áreas de polígonos.
        
        Args:
            table: Tabla con polígonos
            geom_column: Columna de geometría
            group_by: Columna para agrupar (ej: 'municipio')
        """
        if group_by:
            sql = f"""
            SELECT 
                {group_by},
                SUM(ST_Area({geom_column}::geography)) / 1000000 as area_km2,
                COUNT(*) as count
            FROM {table}
            GROUP BY {group_by}
            ORDER BY area_km2 DESC
            """
        else:
            sql = f"""
            SELECT 
                id,
                ST_Area({geom_column}::geography) / 1000000 as area_km2
            FROM {table}
            """
        
        return pd.read_sql(sql, self.conn)
    
    def centroid_extraction(self,
                           table: str,
                           geom_column: str = "geometry") -> gpd.GeoDataFrame:
        """
        Extrae centroides de polígonos.
        Útil para cálculos de distancia entre áreas.
        """
        sql = f"""
        SELECT 
            *,
            ST_Centroid({geom_column}) as centroid
        FROM {table}
        """
        return gpd.read_postgis(sql, self.conn, geom_col='centroid')
    
    def nearest_neighbor(self,
                        point_table: str,
                        target_table: str,
                        k: int = 5) -> gpd.GeoDataFrame:
        """
        Encuentra K vecinos más cercanos para cada punto.
        
        Args:
            point_table: Tabla de puntos de origen
            target_table: Tabla de features objetivo
            k: Número de vecinos a encontrar
        """
        sql = f"""
        SELECT DISTINCT ON (p.id)
            p.*,
            t.id as nearest_id,
            ST_Distance(p.geometry::geography, t.geometry::geography) as distance_m
        FROM {point_table} p
        CROSS JOIN LATERAL (
            SELECT id, geometry
            FROM {target_table} t
            ORDER BY p.geometry <-> t.geometry
            LIMIT {k}
        ) t
        """
        return gpd.read_postgis(sql, self.conn, geom_col='geometry')
    
    def accessibility_analysis(self,
                              source_table: str,
                              facility_table: str,
                              max_distance: float = 5000) -> pd.DataFrame:
        """
        Análisis de accesibilidad: qué % de población tiene acceso a servicios.
        
        Ejemplo: "% de población con acceso a hospitales a menos de 5km"
        """
        sql = f"""
        WITH accessible AS (
            SELECT 
                s.id,
                s.poblacion,
                CASE 
                    WHEN EXISTS (
                        SELECT 1 FROM {facility_table} f
                        WHERE ST_DWithin(
                            s.geometry::geography,
                            f.geometry::geography,
                            {max_distance}
                        )
                    ) THEN 1
                    ELSE 0
                END as has_access
            FROM {source_table} s
        )
        SELECT 
            SUM(poblacion) FILTER (WHERE has_access = 1) as poblacion_con_acceso,
            SUM(poblacion) as poblacion_total,
            ROUND(
                100.0 * SUM(poblacion) FILTER (WHERE has_access = 1) / SUM(poblacion),
                2
            ) as porcentaje_acceso
        FROM accessible
        """
        return pd.read_sql(sql, self.conn)
```

**Dependencias**:
- geopandas
- sqlalchemy
- shapely

**Casos de prueba**:
```python
# Test 1: Buffer analysis
postgis = PostGISFunctions(engine)
result = postgis.buffer_analysis("municipios", "geometry", 1000)
assert len(result) > 0
assert 'buffer_geom' in result.columns

# Test 2: Area calculation
areas = postgis.area_calculation("municipios", group_by="subregion")
assert 'area_km2' in areas.columns

# Test 3: Proximity analysis
proximal = postgis.proximity_analysis(
    "escuelas", "municipios", max_distance=2000
)
assert 'distance_m' in proximal.columns
```

---

### 3. query_validator.py

**Propósito**: Validar y sanitizar queries SQL antes de ejecutar.

**Funcionalidades requeridas**:
```python
import sqlparse
from typing import List, Optional
import re

class QueryValidator:
    """
    Valida y sanitiza queries SQL para prevenir inyecciones y errores.
    """
    
    def __init__(self, allowed_tables: Optional[List[str]] = None):
        """
        Args:
            allowed_tables: Lista de tablas permitidas (None = todas)
        """
        self.allowed_tables = allowed_tables
        self.forbidden_keywords = [
            'DROP', 'TRUNCATE', 'DELETE', 'INSERT', 'UPDATE',
            'ALTER', 'CREATE', 'GRANT', 'REVOKE'
        ]
    
    def validate(self, sql: str) -> Dict[str, Any]:
        """
        Valida query SQL completa.
        
        Returns:
            {
                'valid': bool,
                'errors': List[str],
                'warnings': List[str],
                'sanitized_sql': str
            }
        """
        errors = []
        warnings = []
        
        # Check 1: Forbidden keywords
        if self._has_forbidden_keywords(sql):
            errors.append("Query contiene operaciones prohibidas (DROP, DELETE, etc.)")
        
        # Check 2: SQL injection patterns
        if self._has_injection_patterns(sql):
            errors.append("Posible intento de SQL injection detectado")
        
        # Check 3: Table access validation
        if self.allowed_tables and not self._validate_tables(sql):
            errors.append("Query accede a tablas no autorizadas")
        
        # Check 4: Syntax validation
        if not self._is_valid_syntax(sql):
            errors.append("Sintaxis SQL inválida")
        
        # Check 5: Performance warnings
        perf_warnings = self._check_performance(sql)
        warnings.extend(perf_warnings)
        
        sanitized = self._sanitize(sql)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'sanitized_sql': sanitized
        }
    
    def _has_forbidden_keywords(self, sql: str) -> bool:
        """Detecta keywords prohibidos."""
        sql_upper = sql.upper()
        return any(keyword in sql_upper for keyword in self.forbidden_keywords)
    
    def _has_injection_patterns(self, sql: str) -> bool:
        """
        Detecta patrones comunes de SQL injection.
        """
        injection_patterns = [
            r";\s*DROP",
            r"--\s*$",
            r"'\s*OR\s*'1'\s*=\s*'1",
            r"'\s*OR\s*1\s*=\s*1",
            r"UNION\s+SELECT",
            r"xp_cmdshell",
            r"exec\s*\("
        ]
        return any(re.search(pattern, sql, re.IGNORECASE) for pattern in injection_patterns)
    
    def _validate_tables(self, sql: str) -> bool:
        """Valida que solo se acceda a tablas permitidas."""
        parsed = sqlparse.parse(sql)[0]
        tables_in_query = self._extract_tables(parsed)
        return all(table in self.allowed_tables for table in tables_in_query)
    
    def _extract_tables(self, parsed_sql) -> List[str]:
        """Extrae nombres de tablas del SQL parseado."""
        # Implementar usando sqlparse
        pass
    
    def _is_valid_syntax(self, sql: str) -> bool:
        """Valida sintaxis SQL básica."""
        try:
            parsed = sqlparse.parse(sql)
            return len(parsed) > 0
        except:
            return False
    
    def _check_performance(self, sql: str) -> List[str]:
        """
        Detecta potenciales problemas de performance.
        """
        warnings = []
        sql_upper = sql.upper()
        
        if 'SELECT *' in sql_upper:
            warnings.append("Usar SELECT * puede afectar performance. Especifica columnas.")
        
        if 'LIMIT' not in sql_upper and 'SELECT' in sql_upper:
            warnings.append("Query sin LIMIT puede retornar demasiados registros.")
        
        if sql_upper.count('JOIN') > 5:
            warnings.append("Query con muchos JOINs puede ser lento.")
        
        return warnings
    
    def _sanitize(self, sql: str) -> str:
        """
        Sanitiza query SQL:
        - Remueve comentarios maliciosos
        - Normaliza espacios
        - Agrega LIMIT si falta
        """
        # Remover comentarios peligrosos
        sanitized = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sanitized = re.sub(r'/\*.*?\*/', '', sanitized, flags=re.DOTALL)
        
        # Normalizar espacios
        sanitized = ' '.join(sanitized.split())
        
        # Agregar LIMIT si falta en SELECT
        if 'SELECT' in sanitized.upper() and 'LIMIT' not in sanitized.upper():
            sanitized += ' LIMIT 1000'
        
        return sanitized
```

**Dependencias**:
- sqlparse
- re

**Casos de prueba**:
```python
# Test 1: Query válida
validator = QueryValidator()
result = validator.validate("SELECT * FROM municipios LIMIT 10")
assert result['valid'] == True

# Test 2: Query con DROP
result = validator.validate("SELECT * FROM municipios; DROP TABLE users")
assert result['valid'] == False
assert any('prohibidas' in e for e in result['errors'])

# Test 3: SQL injection
result = validator.validate("SELECT * FROM users WHERE id = '1' OR '1'='1'")
assert result['valid'] == False

# Test 4: Sanitización
result = validator.validate("SELECT * FROM municipios -- comment")
assert '--' not in result['sanitized_sql']
```

---

### 4. executor.py

**Propósito**: Ejecutar queries SQL de forma segura con timeout y límites.

**Funcionalidades requeridas**:
```python
from sqlalchemy import create_engine, text
from contextlib import contextmanager
import pandas as pd
import geopandas as gpd
from typing import Union, Dict, Any

class SafeQueryExecutor:
    """
    Ejecuta queries SQL de forma segura con límites y timeouts.
    """
    
    def __init__(self,
                 db_uri: str,
                 timeout_seconds: int = 30,
                 max_rows: int = 10000):
        """
        Args:
            db_uri: URI de conexión
            timeout_seconds: Timeout para queries
            max_rows: Máximo de filas a retornar
        """
        self.engine = create_engine(db_uri)
        self.timeout = timeout_seconds
        self.max_rows = max_rows
        self.validator = QueryValidator()
    
    @contextmanager
    def _get_connection(self):
        """Context manager para conexiones seguras."""
        conn = self.engine.connect()
        try:
            # Set query timeout
            conn.execute(text(f"SET statement_timeout = {self.timeout * 1000}"))
            yield conn
        finally:
            conn.close()
    
    def execute(self, sql: str, params: Dict = None) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        """
        Ejecuta query SQL con validación y seguridad.
        
        Args:
            sql: Query SQL
            params: Parámetros para query parametrizada
            
        Returns:
            DataFrame o GeoDataFrame con resultados
            
        Raises:
            QueryValidationError: Si query no es válida
            QueryTimeoutError: Si query excede timeout
            QueryExecutionError: Si hay error en ejecución
        """
        # 1. Validar query
        validation = self.validator.validate(sql)
        if not validation['valid']:
            raise QueryValidationError(validation['errors'])
        
        # 2. Usar query sanitizada
        sanitized_sql = validation['sanitized_sql']
        
        try:
            with self._get_connection() as conn:
                # Detectar si es query geoespacial
                if self._is_spatial_query(sanitized_sql):
                    return gpd.read_postgis(
                        sanitized_sql,
                        conn,
                        geom_col='geometry',
                        params=params
                    )
                else:
                    return pd.read_sql(
                        sanitized_sql,
                        conn,
                        params=params
                    )
        
        except Exception as e:
            if 'timeout' in str(e).lower():
                raise QueryTimeoutError(f"Query excedió timeout de {self.timeout}s")
            else:
                raise QueryExecutionError(f"Error ejecutando query: {str(e)}")
    
    def execute_raw(self, sql: str) -> Any:
        """
        Ejecuta SQL sin retornar resultados (DDL, etc.).
        Solo para operaciones administrativas.
        """
        with self._get_connection() as conn:
            return conn.execute(text(sql))
    
    def _is_spatial_query(self, sql: str) -> bool:
        """Detecta si query retorna geometrías."""
        return 'geometry' in sql.lower() or 'st_' in sql.lower()
    
    def explain_query(self, sql: str) -> str:
        """
        Ejecuta EXPLAIN para analizar plan de ejecución.
        """
        explain_sql = f"EXPLAIN ANALYZE {sql}"
        with self._get_connection() as conn:
            result = conn.execute(text(explain_sql))
            return '\n'.join([row[0] for row in result])
    
    def get_query_stats(self, sql: str) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la query (filas estimadas, costo, etc.).
        """
        pass

class QueryValidationError(Exception):
    """Error de validación de query."""
    pass

class QueryTimeoutError(Exception):
    """Error de timeout."""
    pass

class QueryExecutionError(Exception):
    """Error de ejecución."""
    pass
```

**Casos de prueba**:
```python
# Test 1: Ejecución exitosa
executor = SafeQueryExecutor("postgresql://...")
df = executor.execute("SELECT * FROM municipios LIMIT 10")
assert len(df) <= 10

# Test 2: Query inválida
with pytest.raises(QueryValidationError):
    executor.execute("DROP TABLE users")

# Test 3: Timeout
with pytest.raises(QueryTimeoutError):
    executor.execute("SELECT pg_sleep(60)")  # Excede timeout
```

---

### 5. result_formatter.py

**Propósito**: Formatear resultados de queries para presentación al usuario.

**Funcionalidades requeridas**:
```python
import pandas as pd
import json
from typing import Union, Dict, Any

class ResultFormatter:
    """
    Formatea resultados de queries SQL para diferentes usos.
    """
    
    def format_as_text(self, df: pd.DataFrame, max_rows: int = 50) -> str:
        """
        Formatea DataFrame como texto legible.
        
        Returns:
            String con tabla ASCII o descripción si hay muchas filas.
        """
        if len(df) == 0:
            return "No se encontraron resultados."
        
        if len(df) > max_rows:
            summary = f"Resultados: {len(df)} filas (mostrando primeras {max_rows})"
            return f"{summary}\n\n{df.head(max_rows).to_string()}"
        else:
            return df.to_string()
    
    def format_as_markdown(self, df: pd.DataFrame) -> str:
        """Formatea como tabla Markdown."""
        return df.to_markdown()
    
    def format_as_geojson(self, gdf: gpd.GeoDataFrame) -> Dict:
        """
        Formatea GeoDataFrame como GeoJSON para mapas.
        """
        return json.loads(gdf.to_json())
    
    def format_summary(self, df: pd.DataFrame) -> str:
        """
        Genera resumen estadístico de resultados.
        """
        summary = f"""
        📊 Resumen de Resultados:
        - Total de registros: {len(df)}
        - Columnas: {', '.join(df.columns)}
        - Tipos de datos: {df.dtypes.to_dict()}
        
        Estadísticas numéricas:
        {df.describe().to_string()}
        """
        return summary
    
    def format_for_llm(self, df: pd.DataFrame, max_rows: int = 20) -> str:
        """
        Formatea resultados de forma óptima para consumo por LLM.
        Incluye contexto y metadatos.
        """
        formatted = f"""
        Resultados de la consulta SQL:
        
        Total de filas: {len(df)}
        Columnas: {list(df.columns)}
        
        Datos (primeras {max_rows} filas):
        {df.head(max_rows).to_dict(orient='records')}
        """
        return formatted
```

---

## 📝 Instrucciones de Implementación

### Paso 1: Instalación
```bash
pip install langchain langchain-openai sqlalchemy psycopg2-binary \
            geopandas pandas sqlparse
```

### Paso 2: Implementar Pipeline Completo
```python
# modules/sql_agent/pipeline.py
class SQLAgentPipeline:
    """Pipeline completo del agente SQL."""
    
    def __init__(self, config):
        self.generator = SQLQueryGenerator(config['db_uri'])
        self.validator = QueryValidator()
        self.executor = SafeQueryExecutor(config['db_uri'])
        self.formatter = ResultFormatter()
        self.postgis = PostGISFunctions(self.executor.engine)
    
    def query(self, natural_language: str) -> Dict[str, Any]:
        """Procesa consulta completa en lenguaje natural."""
        # 1. Generar SQL
        generated = self.generator.generate_query(natural_language)
        
        # 2. Validar
        validation = self.validator.validate(generated['sql'])
        if not validation['valid']:
            return {'error': validation['errors']}
        
        # 3. Ejecutar
        result_df = self.executor.execute(validation['sanitized_sql'])
        
        # 4. Formatear
        formatted = self.formatter.format_for_llm(result_df)
        
        return {
            'sql': generated['sql'],
            'explanation': generated['explanation'],
            'results': result_df,
            'formatted_results': formatted
        }
```

---

## ✅ Criterios de Aceptación

- ✅ Convierte NL a SQL con precisión > 85%
- ✅ Valida queries antes de ejecutar
- ✅ Previene SQL injection
- ✅ Funciones PostGIS funcionan correctamente
- ✅ Maneja timeouts y errores
- ✅ Formatea resultados de forma legible

---

**¿Listo?** Copia este prompt en Cursor y genera el módulo completo.
