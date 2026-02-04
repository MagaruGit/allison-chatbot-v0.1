# Prompt para Módulo Frontend/UI Layer

## 📋 Contexto del Proyecto
Estás desarrollando el **Módulo Frontend** para un sistema de copiloto con IA para infraestructura y planeación territorial. Este módulo proporciona interfaces de usuario intuitivas para chat, visualización de mapas, dashboards analíticos y exportación de datos.

## 🎯 Objetivo del Módulo
Crear interfaces de usuario que:
1. Proporcionen chat conversacional fluido
2. Visualicen mapas interactivos con capas múltiples
3. Muestren dashboards con métricas y estadísticas
4. Permitan exportar reportes y datos
5. Sean responsivas y accesibles
6. Integren todos los módulos backend

## 📁 Estructura de Archivos a Generar

```
modules/frontend/
├── __init__.py
├── config.py                   # Configuración UI
├── main_app.py                 # App principal Streamlit
├── chat_interface.py           # Interface de chat
├── map_viewer.py               # Visor de mapas
├── dashboard.py                # Dashboards analíticos
├── export_handler.py           # Exportación de datos
├── session_manager.py          # Gestión de sesiones
└── components/
    ├── __init__.py
    ├── sidebar.py              # Barra lateral
    ├── header.py               # Header institucional
    ├── footer.py               # Footer
    ├── message_box.py          # Componente de mensaje
    └── map_controls.py         # Controles de mapa
```

## 🔧 Especificaciones Técnicas

### 1. main_app.py

**Propósito**: Aplicación principal que integra todos los componentes.

**Funcionalidades requeridas**:
```python
import streamlit as st
from modules.frontend.chat_interface import ChatInterface
from modules.frontend.map_viewer import MapViewer
from modules.frontend.dashboard import Dashboard
from modules.frontend.components import Header, Sidebar, Footer

def main():
    """
    Aplicación principal del copiloto.
    """
    # Configuración de página
    st.set_page_config(
        page_title="Allison - Copiloto IA Territorial",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inicializar estado de sesión
    init_session_state()
    
    # Header institucional
    Header.render()
    
    # Sidebar con navegación
    page = Sidebar.render()
    
    # Routing de páginas
    if page == "Chat":
        ChatInterface().render()
    elif page == "Mapas":
        MapViewer().render()
    elif page == "Dashboards":
        Dashboard().render()
    elif page == "Exportar":
        ExportHandler().render()
    
    # Footer
    Footer.render()

def init_session_state():
    """Inicializa variables de estado de sesión."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'selected_layers' not in st.session_state:
        st.session_state.selected_layers = []
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None

if __name__ == "__main__":
    main()
```

---

### 2. chat_interface.py

**Propósito**: Interface de chat conversacional.

**Funcionalidades requeridas**:
```python
import streamlit as st
from typing import List, Dict
from modules.rag import RAGPipeline
from modules.sql_agent import SQLAgentPipeline
from modules.frontend.components.message_box import MessageBox

class ChatInterface:
    """
    Interface de chat conversacional con IA.
    """
    
    def __init__(self):
        self.rag_pipeline = RAGPipeline(config)
        self.sql_agent = SQLAgentPipeline(config)
    
    def render(self):
        """Renderiza interface de chat."""
        st.title("💬 Chat con Allison")
        st.markdown("Pregunta sobre infraestructura, normativa o análisis territorial")
        
        # Contenedor de mensajes
        self._render_messages()
        
        # Input de usuario
        self._render_input()
        
        # Sidebar con opciones
        self._render_chat_options()
    
    def _render_messages(self):
        """Renderiza historial de mensajes."""
        messages_container = st.container()
        
        with messages_container:
            for msg in st.session_state.messages:
                MessageBox.render(
                    content=msg['content'],
                    role=msg['role'],
                    sources=msg.get('sources', []),
                    timestamp=msg.get('timestamp')
                )
    
    def _render_input(self):
        """Renderiza input de usuario."""
        # Input con sugerencias
        suggestions = self._get_suggestions()
        
        # Mostrar sugerencias
        if suggestions:
            st.markdown("**💡 Sugerencias:**")
            cols = st.columns(len(suggestions))
            for i, suggestion in enumerate(suggestions):
                with cols[i]:
                    if st.button(suggestion, key=f"sug_{i}"):
                        self._process_query(suggestion)
        
        # Input principal
        user_input = st.chat_input("Escribe tu pregunta...")
        
        if user_input:
            self._process_query(user_input)
    
    def _process_query(self, query: str):
        """
        Procesa consulta del usuario.
        """
        # Agregar mensaje de usuario
        st.session_state.messages.append({
            'role': 'user',
            'content': query,
            'timestamp': datetime.now()
        })
        
        # Detectar tipo de consulta
        query_type = self._detect_query_type(query)
        
        # Procesar según tipo
        with st.spinner('Pensando...'):
            if query_type == 'sql':
                response = self.sql_agent.query(query)
            else:
                response = self.rag_pipeline.query(query)
        
        # Agregar respuesta
        st.session_state.messages.append({
            'role': 'assistant',
            'content': response['answer'],
            'sources': response.get('sources', []),
            'timestamp': datetime.now()
        })
        
        # Rerun para mostrar nueva respuesta
        st.rerun()
    
    def _detect_query_type(self, query: str) -> str:
        """
        Detecta tipo de consulta (RAG, SQL, GEO).
        """
        sql_keywords = ['total', 'cuántos', 'lista', 'cantidad']
        geo_keywords = ['mapa', 'cerca', 'distancia', 'área']
        
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in sql_keywords):
            return 'sql'
        elif any(kw in query_lower for kw in geo_keywords):
            return 'geo'
        else:
            return 'rag'
    
    def _get_suggestions(self) -> List[str]:
        """Genera sugerencias contextuales."""
        if len(st.session_state.messages) == 0:
            return [
                "¿Qué dice el POT sobre zonas rurales?",
                "Total de vías por municipio",
                "Mostrar mapa de riesgos"
            ]
        return []
    
    def _render_chat_options(self):
        """Renderiza opciones en sidebar."""
        with st.sidebar:
            st.subheader("⚙️ Opciones de Chat")
            
            # Limpiar historial
            if st.button("🗑️ Limpiar Chat"):
                st.session_state.messages = []
                st.rerun()
            
            # Exportar conversación
            if st.button("📥 Exportar Conversación"):
                self._export_conversation()
            
            # Configuraciones
            st.subheader("🔧 Configuración")
            temperature = st.slider("Creatividad", 0.0, 1.0, 0.3)
            max_tokens = st.slider("Longitud respuesta", 100, 2000, 500)
```

---

### 3. map_viewer.py

**Propósito**: Visor de mapas interactivo.

**Funcionalidades requeridas**:
```python
import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
from modules.geo_analytics import MapGenerator

class MapViewer:
    """
    Visor de mapas interactivo con múltiples capas.
    """
    
    def __init__(self):
        self.map_generator = MapGenerator()
    
    def render(self):
        """Renderiza visor de mapas."""
        st.title("🗺️ Visualización de Mapas")
        
        # Layout en columnas
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Mapa principal
            self._render_map()
        
        with col2:
            # Panel de control
            self._render_controls()
    
    def _render_map(self):
        """Renderiza mapa principal."""
        # Cargar capas seleccionadas
        layers = self._load_selected_layers()
        
        # Crear mapa
        if layers:
            m = self.map_generator.create_interactive_map(
                gdfs=layers,
                tiles=st.session_state.get('map_tiles', 'OpenStreetMap')
            )
        else:
            # Mapa vacío centrado en Antioquia
            m = folium.Map(
                location=[6.2476, -75.5658],  # Medellín
                zoom_start=8,
                tiles='OpenStreetMap'
            )
        
        # Renderizar con Streamlit
        map_data = st_folium(m, width=900, height=600)
        
        # Manejar clicks en mapa
        if map_data and map_data.get('last_object_clicked'):
            self._handle_map_click(map_data['last_object_clicked'])
    
    def _render_controls(self):
        """Renderiza controles de mapa."""
        st.subheader("🎛️ Controles")
        
        # Selector de capas
        st.subheader("📁 Capas")
        available_layers = self._get_available_layers()
        
        selected = st.multiselect(
            "Seleccionar capas",
            options=list(available_layers.keys()),
            default=st.session_state.get('selected_layers', [])
        )
        st.session_state.selected_layers = selected
        
        # Estilo de mapa base
        st.subheader("🎨 Estilo")
        tiles = st.selectbox(
            "Mapa base",
            ['OpenStreetMap', 'CartoDB positron', 'CartoDB dark_matter', 
             'Stamen Terrain', 'Stamen Toner']
        )
        st.session_state.map_tiles = tiles
        
        # Herramientas de análisis
        st.subheader("🔍 Análisis")
        
        if st.button("📏 Medir distancia"):
            st.info("Haz click en dos puntos del mapa")
        
        if st.button("📐 Calcular área"):
            st.info("Dibuja un polígono en el mapa")
        
        if st.button("🎯 Buffer"):
            distance = st.number_input("Distancia (m)", value=1000)
            # Implementar buffer
        
        # Exportar mapa
        st.subheader("💾 Exportar")
        if st.button("📥 Descargar Mapa"):
            self._export_map()
    
    def _load_selected_layers(self) -> Dict[str, gpd.GeoDataFrame]:
        """Carga capas seleccionadas desde base de datos."""
        layers = {}
        for layer_name in st.session_state.selected_layers:
            gdf = self._load_layer_from_db(layer_name)
            if gdf is not None:
                layers[layer_name] = gdf
        return layers
    
    def _get_available_layers(self) -> Dict[str, str]:
        """Obtiene capas disponibles."""
        # Consultar catálogo de capas
        return {
            'Municipios': 'municipios',
            'Vías': 'vias',
            'Ríos': 'rios',
            'Zonas de Riesgo': 'zonas_riesgo',
            'Infraestructura': 'infraestructura'
        }
    
    def _handle_map_click(self, click_data: Dict):
        """Maneja clicks en features del mapa."""
        st.info(f"Clicked: {click_data}")
        # Mostrar información del feature clickeado
    
    def _export_map(self):
        """Exporta mapa actual."""
        # Implementar exportación
        pass
```

---

### 4. dashboard.py

**Propósito**: Dashboards analíticos con métricas y visualizaciones.

**Funcionalidades requeridas**:
```python
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class Dashboard:
    """
    Dashboards analíticos y de métricas.
    """
    
    def render(self):
        """Renderiza dashboard principal."""
        st.title("📊 Dashboards Analíticos")
        
        # Tabs para diferentes dashboards
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Resumen General",
            "🛣️ Infraestructura Vial",
            "⚠️ Riesgos",
            "🏥 Accesibilidad"
        ])
        
        with tab1:
            self._render_general_summary()
        
        with tab2:
            self._render_road_infrastructure()
        
        with tab3:
            self._render_risk_dashboard()
        
        with tab4:
            self._render_accessibility_dashboard()
    
    def _render_general_summary(self):
        """Dashboard de resumen general."""
        st.subheader("Resumen del Departamento de Antioquia")
        
        # KPIs en cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Municipios", "125", delta="+0")
        
        with col2:
            st.metric("Población", "6.5M", delta="+2.3%")
        
        with col3:
            st.metric("Área (km²)", "63,612", delta="+0")
        
        with col4:
            st.metric("Vías (km)", "15,234", delta="+145 km")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de población por subregión
            data = self._get_population_by_subregion()
            fig = px.bar(
                data,
                x='subregion',
                y='poblacion',
                title='Población por Subregión'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gráfico de infraestructura
            data = self._get_infrastructure_stats()
            fig = px.pie(
                data,
                values='count',
                names='type',
                title='Distribución de Infraestructura'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_road_infrastructure(self):
        """Dashboard de infraestructura vial."""
        st.subheader("Infraestructura Vial")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            subregion = st.selectbox(
                "Subregión",
                ["Todas", "Valle de Aburrá", "Urabá", "Oriente"]
            )
        
        with col2:
            road_type = st.selectbox(
                "Tipo de vía",
                ["Todas", "Primaria", "Secundaria", "Terciaria"]
            )
        
        with col3:
            condition = st.selectbox(
                "Estado",
                ["Todos", "Bueno", "Regular", "Malo"]
            )
        
        # Tabla de vías
        data = self._get_roads_data(subregion, road_type, condition)
        st.dataframe(data, use_container_width=True)
        
        # Gráfico de estado de vías
        fig = px.histogram(
            data,
            x='estado',
            color='tipo',
            title='Estado de Vías por Tipo'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_risk_dashboard(self):
        """Dashboard de riesgos."""
        st.subheader("Análisis de Riesgos Territoriales")
        
        # Selector de tipo de riesgo
        risk_type = st.selectbox(
            "Tipo de Riesgo",
            ["Deslizamiento", "Inundación", "Sísmico", "Multi-amenaza"]
        )
        
        # Mapa de calor de riesgos
        risk_data = self._get_risk_data(risk_type)
        
        fig = px.density_mapbox(
            risk_data,
            lat='lat',
            lon='lon',
            z='risk_score',
            radius=10,
            center=dict(lat=6.25, lon=-75.56),
            zoom=8,
            mapbox_style="open-street-map",
            title=f"Mapa de Riesgo: {risk_type}"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Población en riesgo
        st.metric("Población en Alto Riesgo", "245,000", delta="-12%")
    
    def _render_accessibility_dashboard(self):
        """Dashboard de accesibilidad a servicios."""
        st.subheader("Accesibilidad a Servicios")
        
        # Selector de servicio
        service_type = st.selectbox(
            "Tipo de Servicio",
            ["Salud", "Educación", "Transporte", "Recreación"]
        )
        
        # Métricas de accesibilidad
        acc_data = self._get_accessibility_metrics(service_type)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Cobertura", f"{acc_data['coverage']}%")
        
        with col2:
            st.metric("Tiempo Promedio", f"{acc_data['avg_time']} min")
        
        with col3:
            st.metric("Población sin Acceso", f"{acc_data['no_access']}")
        
        # Gráfico de accesibilidad por municipio
        fig = px.bar(
            acc_data['by_municipality'],
            x='municipio',
            y='accesibilidad',
            title=f'Accesibilidad a {service_type} por Municipio'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Métodos auxiliares para cargar datos
    def _get_population_by_subregion(self) -> pd.DataFrame:
        # Implementar consulta a BD
        pass
    
    def _get_infrastructure_stats(self) -> pd.DataFrame:
        pass
    
    def _get_roads_data(self, subregion, road_type, condition) -> pd.DataFrame:
        pass
    
    def _get_risk_data(self, risk_type) -> pd.DataFrame:
        pass
    
    def _get_accessibility_metrics(self, service_type) -> Dict:
        pass
```

---

### 5. export_handler.py

**Propósito**: Exportación de datos y reportes.

**Funcionalidades requeridas**:
```python
import streamlit as st
from io import BytesIO
import pandas as pd
import geopandas as gpd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class ExportHandler:
    """
    Maneja exportación de datos y reportes.
    """
    
    def render(self):
        """Renderiza interface de exportación."""
        st.title("📥 Exportar Datos")
        
        # Selector de tipo de exportación
        export_type = st.selectbox(
            "¿Qué deseas exportar?",
            ["Conversación de Chat", "Datos de Mapa", "Dashboard", "Reporte Completo"]
        )
        
        if export_type == "Conversación de Chat":
            self._export_conversation()
        elif export_type == "Datos de Mapa":
            self._export_map_data()
        elif export_type == "Dashboard":
            self._export_dashboard()
        elif export_type == "Reporte Completo":
            self._export_full_report()
    
    def _export_conversation(self):
        """Exporta conversación de chat."""
        st.subheader("💬 Exportar Conversación")
        
        format = st.radio("Formato", ["PDF", "TXT", "JSON"])
        
        if st.button("Generar"):
            if format == "PDF":
                pdf = self._generate_conversation_pdf()
                st.download_button(
                    label="📥 Descargar PDF",
                    data=pdf,
                    file_name="conversacion.pdf",
                    mime="application/pdf"
                )
            elif format == "TXT":
                txt = self._generate_conversation_txt()
                st.download_button(
                    label="📥 Descargar TXT",
                    data=txt,
                    file_name="conversacion.txt",
                    mime="text/plain"
                )
            elif format == "JSON":
                json_data = self._generate_conversation_json()
                st.download_button(
                    label="📥 Descargar JSON",
                    data=json_data,
                    file_name="conversacion.json",
                    mime="application/json"
                )
    
    def _export_map_data(self):
        """Exporta datos de capas de mapa."""
        st.subheader("🗺️ Exportar Datos de Mapa")
        
        layers = st.multiselect(
            "Seleccionar capas",
            ["Municipios", "Vías", "Ríos", "Zonas de Riesgo"]
        )
        
        format = st.radio("Formato", ["GeoJSON", "Shapefile", "CSV"])
        
        if st.button("Generar") and layers:
            for layer in layers:
                data = self._get_layer_data(layer)
                
                if format == "GeoJSON":
                    geojson = data.to_json()
                    st.download_button(
                        f"📥 Descargar {layer} (GeoJSON)",
                        geojson,
                        f"{layer}.geojson"
                    )
                elif format == "Shapefile":
                    # Generar Shapefile
                    pass
                elif format == "CSV":
                    csv = data.to_csv()
                    st.download_button(
                        f"📥 Descargar {layer} (CSV)",
                        csv,
                        f"{layer}.csv"
                    )
    
    def _export_full_report(self):
        """Genera reporte completo PDF."""
        st.subheader("📄 Reporte Completo")
        
        # Opciones de reporte
        include_maps = st.checkbox("Incluir mapas", value=True)
        include_stats = st.checkbox("Incluir estadísticas", value=True)
        include_chat = st.checkbox("Incluir conversaciones", value=False)
        
        if st.button("Generar Reporte"):
            with st.spinner("Generando reporte..."):
                pdf = self._generate_full_pdf_report(
                    include_maps, include_stats, include_chat
                )
                st.download_button(
                    "📥 Descargar Reporte",
                    pdf,
                    "reporte_allison.pdf",
                    mime="application/pdf"
                )
    
    def _generate_conversation_pdf(self) -> bytes:
        """Genera PDF de conversación."""
        # Implementar con reportlab
        pass
    
    def _generate_full_pdf_report(self, maps, stats, chat) -> bytes:
        """Genera reporte PDF completo."""
        pass
```

---

## 📝 Instrucciones de Implementación

### Paso 1: Instalación
```bash
pip install streamlit streamlit-folium plotly pandas \
            reportlab pillow
```

### Paso 2: Temas y Estilos
```python
# .streamlit/config.toml
[theme]
primaryColor = "#036E3A"  # Verde Gobernación
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### Paso 3: Custom CSS
```python
# modules/frontend/styles.py
def load_custom_css():
    st.markdown("""
    <style>
    .stApp {
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .user-message {
        background-color: #E3F2FD;
    }
    
    .assistant-message {
        background-color: #F5F5F5;
    }
    </style>
    """, unsafe_allow_html=True)
```

---

## ✅ Criterios de Aceptación

- ✅ Chat fluido y responsivo
- ✅ Mapas interactivos con múltiples capas
- ✅ Dashboards informativos y visuales
- ✅ Exportación en múltiples formatos
- ✅ UI accesible y responsive
- ✅ Performance < 2s para cargas

---

**¿Listo?** Copia este prompt en Cursor para generar el módulo frontend completo.
