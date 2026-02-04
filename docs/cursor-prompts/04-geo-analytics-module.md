# Prompt para Módulo Geo-Analytics Engine

## 📋 Contexto del Proyecto
Estás desarrollando el **Módulo Geo-Analytics Engine** para un sistema de copiloto con IA que realiza análisis geoespaciales avanzados sobre infraestructura y territorio. Este módulo proporciona capacidades de análisis espacial, cálculo de métricas territoriales, evaluación de riesgos y generación de mapas.

## 🎯 Objetivo del Módulo
Crear un motor de análisis geoespacial que:
1. Realice análisis de proximidad y accesibilidad
2. Calcule métricas territoriales (densidad, cobertura, etc.)
3. Evalúe riesgos espaciales (deslizamientos, inundaciones)
4. Genere mapas y visualizaciones
5. Detecte patrones y anomalías espaciales
6. Proporcione recomendaciones basadas en análisis espacial

## 📁 Estructura de Archivos a Generar

```
modules/geo_analytics/
├── __init__.py
├── config.py                       # Configuración del módulo
├── spatial_analysis.py             # Análisis espacial general
├── proximity_analyzer.py           # Análisis de proximidad
├── risk_assessment.py              # Evaluación de riesgos
├── accessibility_calculator.py     # Cálculo de accesibilidad
├── density_analyzer.py             # Análisis de densidad
├── map_generator.py                # Generación de mapas
├── metrics_calculator.py           # Métricas territoriales
├── pattern_detector.py             # Detección de patrones
└── utils/
    ├── __init__.py
    ├── geom_utils.py
    ├── viz_utils.py
    └── logger.py
```

## 🔧 Especificaciones Técnicas

### 1. spatial_analysis.py

**Propósito**: Funciones de análisis espacial general.

**Funcionalidades requeridas**:
```python
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, Polygon, LineString
from typing import List, Dict, Any, Tuple

class SpatialAnalyzer:
    """
    Motor principal de análisis espacial.
    """
    
    def __init__(self, crs: str = "EPSG:4326"):
        """
        Args:
            crs: Sistema de coordenadas de referencia por defecto
        """
        self.crs = crs
    
    def calculate_distance_matrix(self,
                                  gdf1: gpd.GeoDataFrame,
                                  gdf2: gpd.GeoDataFrame,
                                  metric: str = "euclidean") -> np.ndarray:
        """
        Calcula matriz de distancias entre dos conjuntos de geometrías.
        
        Args:
            gdf1: Primer conjunto de geometrías
            gdf2: Segundo conjunto de geometrías
            metric: 'euclidean', 'haversine' (para lat/lon)
            
        Returns:
            Matriz NxM de distancias
        """
        pass
    
    def find_within_distance(self,
                            source_gdf: gpd.GeoDataFrame,
                            target_gdf: gpd.GeoDataFrame,
                            distance: float,
                            units: str = "meters") -> gpd.GeoDataFrame:
        """
        Encuentra features de target_gdf dentro de distancia de source_gdf.
        
        Returns:
            GeoDataFrame con pares (source_id, target_id, distance)
        """
        pass
    
    def spatial_join(self,
                    left_gdf: gpd.GeoDataFrame,
                    right_gdf: gpd.GeoDataFrame,
                    join_type: str = "intersects") -> gpd.GeoDataFrame:
        """
        Realiza spatial join entre dos GeoDataFrames.
        
        Args:
            join_type: 'intersects', 'contains', 'within', 'touches'
        """
        return gpd.sjoin(left_gdf, right_gdf, predicate=join_type)
    
    def calculate_overlaps(self,
                          gdf1: gpd.GeoDataFrame,
                          gdf2: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Calcula áreas de overlap entre dos capas de polígonos.
        
        Returns:
            GeoDataFrame con geometrías de overlap y áreas
        """
        pass
    
    def buffer_analysis(self,
                       gdf: gpd.GeoDataFrame,
                       distance: float,
                       dissolve: bool = False) -> gpd.GeoDataFrame:
        """
        Crea buffers alrededor de geometrías.
        
        Args:
            distance: Distancia del buffer en unidades del CRS
            dissolve: Si True, disuelve buffers solapados
        """
        buffered = gdf.copy()
        buffered['geometry'] = gdf.geometry.buffer(distance)
        
        if dissolve:
            buffered = buffered.dissolve()
        
        return buffered
    
    def convex_hull(self, gdf: gpd.GeoDataFrame) -> Polygon:
        """
        Calcula convex hull (envolvente convexa) de un conjunto de geometrías.
        """
        from shapely.ops import unary_union
        return unary_union(gdf.geometry).convex_hull
    
    def minimum_bounding_rectangle(self, gdf: gpd.GeoDataFrame) -> Polygon:
        """
        Calcula rectángulo envolvente mínimo.
        """
        from shapely.ops import unary_union
        return unary_union(gdf.geometry).envelope
    
    def simplify_geometries(self,
                           gdf: gpd.GeoDataFrame,
                           tolerance: float,
                           preserve_topology: bool = True) -> gpd.GeoDataFrame:
        """
        Simplifica geometrías para reducir complejidad.
        Útil para visualización y performance.
        """
        simplified = gdf.copy()
        simplified['geometry'] = gdf.geometry.simplify(
            tolerance,
            preserve_topology=preserve_topology
        )
        return simplified
```

**Casos de prueba**:
```python
# Test 1: Distance matrix
analyzer = SpatialAnalyzer()
points1 = gpd.GeoDataFrame(geometry=[Point(0, 0), Point(1, 1)])
points2 = gpd.GeoDataFrame(geometry=[Point(0, 1), Point(1, 0)])
matrix = analyzer.calculate_distance_matrix(points1, points2)
assert matrix.shape == (2, 2)

# Test 2: Buffer analysis
buffered = analyzer.buffer_analysis(points1, distance=0.5)
assert buffered.geometry.iloc[0].geom_type == 'Polygon'
```

---

### 2. proximity_analyzer.py

**Propósito**: Análisis de proximidad y vecindad.

**Funcionalidades requeridas**:
```python
import geopandas as gpd
from scipy.spatial import cKDTree
from typing import List, Dict, Any

class ProximityAnalyzer:
    """
    Análisis de proximidad espacial.
    """
    
    def nearest_neighbors(self,
                         source_gdf: gpd.GeoDataFrame,
                         target_gdf: gpd.GeoDataFrame,
                         k: int = 5) -> gpd.GeoDataFrame:
        """
        Encuentra los K vecinos más cercanos para cada feature.
        
        Returns:
            GeoDataFrame con columnas:
            - source_id
            - neighbor_ids (lista)
            - distances (lista)
        """
        pass
    
    def service_area_analysis(self,
                             facilities_gdf: gpd.GeoDataFrame,
                             service_radius: float,
                             population_gdf: gpd.GeoDataFrame = None) -> Dict[str, Any]:
        """
        Analiza áreas de servicio de instalaciones (hospitales, escuelas, etc.).
        
        Returns:
            {
                'service_areas': GeoDataFrame con polígonos de servicio,
                'covered_population': float (si population_gdf proporcionado),
                'coverage_percentage': float,
                'underserved_areas': GeoDataFrame
            }
        """
        pass
    
    def corridor_analysis(self,
                         line_gdf: gpd.GeoDataFrame,
                         buffer_distance: float,
                         points_gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """
        Análisis de corredor (ej: vías y servicios cercanos).
        
        Args:
            line_gdf: Vías u otras líneas
            buffer_distance: Distancia del corredor
            points_gdf: Puntos de interés
            
        Returns:
            {
                'corridor': GeoDataFrame con buffers de corredor,
                'points_within': GeoDataFrame con puntos dentro del corredor,
                'statistics': dict con métricas
            }
        """
        pass
    
    def travel_time_isochrones(self,
                              origin: Point,
                              travel_times: List[int],
                              network_gdf: gpd.GeoDataFrame,
                              speed_kmh: float = 50) -> gpd.GeoDataFrame:
        """
        Genera isocronas (áreas alcanzables en X minutos).
        Versión simplificada usando buffer circular.
        Para análisis avanzado, usar redes reales.
        
        Args:
            origin: Punto de origen
            travel_times: Lista de tiempos en minutos [5, 10, 15]
            network_gdf: Red vial (opcional, para versión avanzada)
            speed_kmh: Velocidad promedio
            
        Returns:
            GeoDataFrame con polígonos de isocronas
        """
        isochrones = []
        for minutes in travel_times:
            # Calcular distancia = velocidad * tiempo
            distance_km = (speed_kmh * minutes) / 60
            distance_m = distance_km * 1000
            
            # Crear buffer circular (simplificado)
            isochrone = {
                'time_minutes': minutes,
                'geometry': origin.buffer(distance_m / 111000)  # Aprox para lat/lon
            }
            isochrones.append(isochrone)
        
        return gpd.GeoDataFrame(isochrones, crs="EPSG:4326")
    
    def hotspot_analysis(self,
                        points_gdf: gpd.GeoDataFrame,
                        bandwidth: float = 1000) -> gpd.GeoDataFrame:
        """
        Análisis de puntos calientes (hotspots) usando Kernel Density.
        
        Args:
            points_gdf: Puntos a analizar (ej: accidentes, eventos)
            bandwidth: Radio de influencia en metros
            
        Returns:
            Raster o polígonos de densidad
        """
        pass
```

**Dependencias**:
- geopandas
- scipy
- numpy
- shapely

---

### 3. risk_assessment.py

**Propósito**: Evaluación de riesgos territoriales.

**Funcionalidades requeridas**:
```python
import geopandas as gpd
import pandas as pd
from typing import Dict, Any, List

class RiskAssessment:
    """
    Evaluación de riesgos territoriales.
    """
    
    def flood_risk_analysis(self,
                           area_gdf: gpd.GeoDataFrame,
                           rivers_gdf: gpd.GeoDataFrame,
                           elevation_data: np.ndarray = None,
                           buffer_distance: float = 100) -> gpd.GeoDataFrame:
        """
        Análisis de riesgo de inundación.
        
        Args:
            area_gdf: Áreas a evaluar
            rivers_gdf: Ríos y cuerpos de agua
            elevation_data: DEM (opcional)
            buffer_distance: Distancia de zona de riesgo
            
        Returns:
            GeoDataFrame con score de riesgo (0-1) por área
        """
        pass
    
    def landslide_risk_analysis(self,
                               area_gdf: gpd.GeoDataFrame,
                               slope_data: np.ndarray,
                               soil_gdf: gpd.GeoDataFrame = None) -> gpd.GeoDataFrame:
        """
        Análisis de riesgo de deslizamiento.
        
        Factores:
        - Pendiente del terreno
        - Tipo de suelo
        - Cobertura vegetal
        - Proximidad a fallas geológicas
        """
        pass
    
    def seismic_risk_analysis(self,
                             area_gdf: gpd.GeoDataFrame,
                             fault_lines_gdf: gpd.GeoDataFrame,
                             building_age_data: pd.DataFrame = None) -> gpd.GeoDataFrame:
        """
        Análisis de riesgo sísmico.
        """
        pass
    
    def multi_hazard_risk_score(self,
                               area_gdf: gpd.GeoDataFrame,
                               risk_layers: Dict[str, gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
        """
        Calcula score de riesgo multi-amenaza.
        
        Args:
            risk_layers: {
                'flood': gdf_with_risk_score,
                'landslide': gdf_with_risk_score,
                'seismic': gdf_with_risk_score
            }
            
        Returns:
            GeoDataFrame con score compuesto (0-1)
        """
        pass
    
    def vulnerable_population_analysis(self,
                                      risk_areas_gdf: gpd.GeoDataFrame,
                                      population_gdf: gpd.GeoDataFrame,
                                      vulnerability_factors: List[str]) -> Dict[str, Any]:
        """
        Identifica población vulnerable en zonas de riesgo.
        
        Args:
            risk_areas_gdf: Áreas de riesgo
            population_gdf: Datos de población
            vulnerability_factors: ['edad', 'ingreso', 'discapacidad']
            
        Returns:
            {
                'total_at_risk': int,
                'highly_vulnerable': int,
                'areas_priority': GeoDataFrame
            }
        """
        pass
```

---

### 4. accessibility_calculator.py

**Propósito**: Cálculo de métricas de accesibilidad a servicios.

**Funcionalidades requeridas**:
```python
import geopandas as gpd
import numpy as np
from typing import Dict, Any

class AccessibilityCalculator:
    """
    Calcula métricas de accesibilidad a servicios e infraestructura.
    """
    
    def calculate_2sfca(self,
                       demand_gdf: gpd.GeoDataFrame,
                       supply_gdf: gpd.GeoDataFrame,
                       threshold_distance: float,
                       population_field: str = 'population',
                       capacity_field: str = 'capacity') -> gpd.GeoDataFrame:
        """
        Two-Step Floating Catchment Area (2SFCA) method.
        Método estándar para medir accesibilidad a servicios.
        
        Args:
            demand_gdf: Áreas con población (demanda)
            supply_gdf: Facilidades/servicios (oferta)
            threshold_distance: Distancia máxima de acceso
            
        Returns:
            GeoDataFrame con accessibility_score por área
        """
        pass
    
    def gravity_model_accessibility(self,
                                   origin_gdf: gpd.GeoDataFrame,
                                   destination_gdf: gpd.GeoDataFrame,
                                   impedance_function: str = "exponential") -> gpd.GeoDataFrame:
        """
        Modelo gravitacional de accesibilidad.
        Considera distancia y atractivo de destinos.
        """
        pass
    
    def cumulative_opportunities(self,
                                origin_gdf: gpd.GeoDataFrame,
                                opportunities_gdf: gpd.GeoDataFrame,
                                max_distance: float) -> gpd.GeoDataFrame:
        """
        Cuenta oportunidades accesibles dentro de distancia máxima.
        
        Returns:
            GeoDataFrame con count de oportunidades por origen
        """
        pass
    
    def service_coverage_map(self,
                            services_gdf: gpd.GeoDataFrame,
                            service_radius: float,
                            study_area: Polygon) -> gpd.GeoDataFrame:
        """
        Genera mapa de cobertura de servicios.
        
        Returns:
            Grid con valores de cobertura (0-N servicios accesibles)
        """
        pass
    
    def equity_analysis(self,
                       accessibility_gdf: gpd.GeoDataFrame,
                       socioeconomic_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analiza equidad en acceso a servicios por grupos socioeconómicos.
        
        Returns:
            {
                'gini_coefficient': float,
                'disparities_by_group': dict,
                'priority_areas': GeoDataFrame
            }
        """
        pass
```

---

### 5. map_generator.py

**Propósito**: Generar mapas y visualizaciones.

**Funcionalidades requeridas**:
```python
import matplotlib.pyplot as plt
import folium
from folium import plugins
import geopandas as gpd
from typing import Dict, Any, List

class MapGenerator:
    """
    Generador de mapas estáticos e interactivos.
    """
    
    def create_static_map(self,
                         gdf: gpd.GeoDataFrame,
                         column: str = None,
                         cmap: str = "viridis",
                         title: str = "",
                         legend: bool = True) -> plt.Figure:
        """
        Crea mapa estático con Matplotlib.
        
        Args:
            gdf: GeoDataFrame a visualizar
            column: Columna para colorear (coropleta)
            cmap: Color map
            title: Título del mapa
            
        Returns:
            Figura de Matplotlib
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        if column:
            gdf.plot(column=column, cmap=cmap, legend=legend, ax=ax)
        else:
            gdf.plot(ax=ax)
        
        ax.set_title(title, fontsize=16)
        ax.set_axis_off()
        
        return fig
    
    def create_interactive_map(self,
                              gdfs: Dict[str, gpd.GeoDataFrame],
                              center: List[float] = None,
                              zoom: int = 10,
                              tiles: str = "OpenStreetMap") -> folium.Map:
        """
        Crea mapa interactivo con Folium.
        
        Args:
            gdfs: {'layer_name': gdf, ...}
            center: [lat, lon]
            zoom: Nivel de zoom inicial
            tiles: 'OpenStreetMap', 'CartoDB positron', 'Stamen Terrain'
            
        Returns:
            Mapa Folium
        """
        if center is None:
            # Calcular centro automáticamente
            all_geoms = []
            for gdf in gdfs.values():
                all_geoms.extend(gdf.geometry.tolist())
            bounds = gpd.GeoSeries(all_geoms).total_bounds
            center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]
        
        m = folium.Map(location=center, zoom_start=zoom, tiles=tiles)
        
        # Agregar capas
        for name, gdf in gdfs.items():
            folium.GeoJson(
                gdf,
                name=name,
                tooltip=folium.GeoJsonTooltip(fields=gdf.columns.tolist())
            ).add_to(m)
        
        folium.LayerControl().add_to(m)
        
        return m
    
    def create_choropleth_map(self,
                             gdf: gpd.GeoDataFrame,
                             value_column: str,
                             key_column: str = 'id',
                             legend_name: str = "") -> folium.Map:
        """
        Crea mapa coroplético (coloreado por valor).
        """
        pass
    
    def create_heatmap(self,
                      points_gdf: gpd.GeoDataFrame,
                      value_column: str = None) -> folium.Map:
        """
        Crea mapa de calor de puntos.
        """
        pass
    
    def add_markers(self,
                   map_obj: folium.Map,
                   points_gdf: gpd.GeoDataFrame,
                   popup_columns: List[str] = None) -> folium.Map:
        """
        Agrega marcadores a mapa existente.
        """
        pass
    
    def export_map(self,
                  map_obj: folium.Map,
                  output_path: str,
                  format: str = "html"):
        """
        Exporta mapa a archivo.
        
        Args:
            format: 'html', 'png' (requiere selenium)
        """
        if format == "html":
            map_obj.save(output_path)
        elif format == "png":
            # Requiere selenium y geckodriver
            import selenium
            # Implementar screenshot
        pass
```

**Dependencias**:
- matplotlib
- folium
- mapclassify (para clasificación de datos)

---

### 6. metrics_calculator.py

**Propósito**: Cálculo de métricas territoriales.

**Funcionalidades requeridas**:
```python
import geopandas as gpd
import numpy as np
from typing import Dict, Any

class MetricsCalculator:
    """
    Calcula métricas territoriales y de forma.
    """
    
    def shape_metrics(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Calcula métricas de forma de polígonos.
        
        Retorna:
        - area
        - perimeter
        - compactness (4π*area/perimeter²)
        - elongation
        - convexity
        """
        metrics = gdf.copy()
        metrics['area'] = gdf.geometry.area
        metrics['perimeter'] = gdf.geometry.length
        metrics['compactness'] = (4 * np.pi * metrics['area']) / (metrics['perimeter'] ** 2)
        
        return metrics
    
    def density_metrics(self,
                       gdf: gpd.GeoDataFrame,
                       value_column: str) -> gpd.GeoDataFrame:
        """
        Calcula densidad (valor/área).
        
        Ejemplos:
        - Densidad poblacional
        - Densidad de servicios
        - Densidad de vías
        """
        result = gdf.copy()
        result['area_km2'] = gdf.geometry.area / 1e6
        result['density'] = gdf[value_column] / result['area_km2']
        return result
    
    def connectivity_metrics(self,
                            network_gdf: gpd.GeoDataFrame,
                            nodes_gdf: gpd.GeoDataFrame = None) -> Dict[str, Any]:
        """
        Métricas de conectividad de redes (viales, etc.).
        
        Returns:
        - Número de nodos
        - Número de arcos
        - Densidad de red
        - Conectividad promedio
        """
        pass
    
    def fragmentation_index(self,
                           land_use_gdf: gpd.GeoDataFrame,
                           patch_column: str) -> float:
        """
        Calcula índice de fragmentación del paisaje.
        """
        pass
    
    def coverage_metrics(self,
                        coverage_gdf: gpd.GeoDataFrame,
                        study_area: Polygon) -> Dict[str, float]:
        """
        Métricas de cobertura espacial.
        
        Returns:
        - Área total cubierta
        - % de cobertura
        - Gaps (áreas no cubiertas)
        """
        pass
```

---

## 📝 Instrucciones de Implementación

### Paso 1: Instalación
```bash
pip install geopandas shapely matplotlib folium scipy numpy \
            scikit-learn rasterio mapclassify
```

### Paso 2: Configuración
```python
# modules/geo_analytics/config.py
from pydantic import BaseModel

class GeoAnalyticsConfig(BaseModel):
    default_crs: str = "EPSG:4326"
    buffer_resolution: int = 16
    map_tiles: str = "OpenStreetMap"
    output_format: str = "geojson"
```

### Paso 3: Pipeline Integrado
```python
# modules/geo_analytics/pipeline.py
class GeoAnalyticsPipeline:
    """Pipeline integrado de análisis geoespacial."""
    
    def __init__(self, config):
        self.spatial = SpatialAnalyzer()
        self.proximity = ProximityAnalyzer()
        self.risk = RiskAssessment()
        self.accessibility = AccessibilityCalculator()
        self.mapper = MapGenerator()
        self.metrics = MetricsCalculator()
    
    def analyze(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa solicitud de análisis geoespacial.
        
        request = {
            'type': 'proximity',
            'params': {...},
            'output': 'map'
        }
        """
        pass
```

---

## ✅ Criterios de Aceptación

- ✅ Análisis espaciales precisos y eficientes
- ✅ Generación de mapas estáticos e interactivos
- ✅ Evaluación de riesgos multi-amenaza
- ✅ Cálculo de métricas de accesibilidad
- ✅ Performance adecuado (< 5s para análisis comunes)
- ✅ Documentación completa

---

## 🚀 Ejemplo de Uso

```python
from modules.geo_analytics import GeoAnalyticsPipeline

pipeline = GeoAnalyticsPipeline(config)

# Análisis de proximidad
result = pipeline.proximity.service_area_analysis(
    facilities_gdf=hospitales,
    service_radius=5000,
    population_gdf=poblacion
)

# Generar mapa
mapa = pipeline.mapper.create_interactive_map(
    {'Hospitales': hospitales, 'Áreas de Servicio': result['service_areas']}
)
mapa.save('acceso_hospitales.html')
```

---

**¿Listo?** Copia este prompt en Cursor y genera el módulo completo de geo-analytics.
