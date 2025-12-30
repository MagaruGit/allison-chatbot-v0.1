import streamlit as st
import streamlit.components.v1 as components
import os
import time
import random

# Debug: Verificar inicio de la aplicación
print("🚀 Iniciando aplicación Allison...")

try:
    from rag import get_qa_chain, create_vector_db, buscar_capa_gis, buscar_datos_vias
    print("✅ Módulo rag importado correctamente")
except Exception as e:
    print(f"❌ Error importando rag: {e}")
    st.error(f"Error al cargar módulos: {e}")


# Inicializar historial de chat al principio para controlar la UI
if "messages" not in st.session_state:
    st.session_state.messages = []

# Estado para controlar la generación de respuesta
if "stop_generation" not in st.session_state:
    st.session_state.stop_generation = False
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

# Configuración de página con identidad institucional
st.set_page_config(
    page_title="Allison - Gobernación de Antioquia",
    page_icon="assets/logo_allison.svg",
    layout="centered"
)

# --- HEADER PERSONALIZADO CON LOGO GOBERNACIÓN ---
import base64
if os.path.exists("assets/logo_gobernacion.png"):
    with open("assets/logo_gobernacion.png", "rb") as f:
        header_logo_data = base64.b64encode(f.read()).decode("utf-8")
    
    st.markdown(f"""
        <style>
            header[data-testid="stHeader"] {{
                background-color: #FFFFFF;
                background-image: url("data:image/png;base64,{header_logo_data}");
                background-repeat: no-repeat;
                background-position: 20px center; /* Alineado a la izquierda con margen */
                background-size: auto 80%; /* Ajustar altura del logo */
                border-bottom: 2px solid rgb(3, 110, 58); /* Línea verde sutil abajo */
            }}
            /* Mover los items del header (como el botón de deploy) a la derecha si estorban */
            header[data-testid="stHeader"] > div:first-child {{
                background: transparent;
            }}
        </style>
    """, unsafe_allow_html=True)
else:
    # Fallback: Barra verde simple
    st.markdown("""
        <style>
            header[data-testid="stHeader"] {
                background-color: rgb(3, 110, 58);
            }
        </style>
    """, unsafe_allow_html=True)

# --- Ocultar footer y badges/avatares de Streamlit/GitHub (global y móvil) ---
hide_streamlit_footer = """
<style>
/* ===== SELECTORES ESPECÍFICOS QUE FUNCIONARON A OTROS USUARIOS ===== */
.css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
.styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
.viewerBadge_text__1JaDK, .css-14xtw13, .e8zbici0,
.css-1dp5vir, .e1ewe7hr1, .css-1adrfps,
.css-z5fcl4, .e1ewe7hr0 {
    display: none !important;
    visibility: hidden !important;
}

/* ===== OCULTAR ELEMENTOS GLOBALMENTE ===== */
#MainMenu {visibility: hidden !important; display: none !important;}
#GithubIcon {visibility: hidden !important; display: none !important;}
footer {visibility: hidden !important; display: none !important; height: 0 !important;}

/* Ocultar links a GitHub */
a[href*="github"] {
    display: none !important;
    visibility: hidden !important;
}

/* ===== OCULTAR HEADER COMPLETO EN MÓVIL ===== */
@media (max-width: 768px) {
    header {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    [data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    [data-testid="stToolbar"] {
        display: none !important;
    }

    [data-testid="stDecoration"] {
        display: none !important;
    }

    [data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    /* Ocultar cualquier imagen de avatar */
    img[src*="avatars"],
    img[src*="github"],
    img[alt*="avatar"],
    img[alt*="Avatar"] {
        display: none !important;
    }
    
    /* Ocultar badges y elementos flotantes */
    .viewerBadge_container__r5I1v,
    .viewerBadge_link__qRIco,
    .styles_viewerBadge__CvC9N,
    div[class*="viewerBadge"],
    div[class*="StatusWidget"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
    }
}

/* ===== OCULTAR TODOS LOS ELEMENTOS DE STREAMLIT CLOUD ===== */
.viewerBadge_container__r5I1v,
.viewerBadge_link__qRIco,
.styles_viewerBadge__CvC9N,
div[class*="viewerBadge"],
a[href*="streamlit.io/cloud"],
a[href*="streamlit.io"][target="_blank"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="manage-app-button"],
[data-testid="stToolbar"],
.stDeployButton,
button[kind="header"],
img[src*="avatars.githubusercontent.com"],
img[src*="github"],
div[class*="StatusWidget"],
header[data-testid="stHeader"] button,
header[data-testid="stHeader"] a[target="_blank"],
header[data-testid="stHeader"] img,
.stToolbar,
div[style*="position: fixed"][style*="bottom"][style*="right"],
div[style*="position: fixed"][style*="top"][style*="right"] img {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    width: 0 !important;
    height: 0 !important;
    max-width: 0 !important;
    max-height: 0 !important;
    overflow: hidden !important;
}

/* Forzar ocultar el toolbar del header */
header[data-testid="stHeader"] > div:last-child {
    display: none !important;
}
</style>
"""
st.markdown(hide_streamlit_footer, unsafe_allow_html=True)

# --- JAVASCRIPT SIMPLIFICADO PARA OCULTAR BRANDING ---
# Solo ocultamos elementos específicos de Streamlit Cloud, sin eliminar nada crítico
components.html("""
<script>
(function() {
    // Solo ocultar badges de Streamlit Cloud, sin eliminar elementos del DOM
    var style = window.parent.document.createElement('style');
    style.textContent = `
        [class*="viewerBadge"],
        [class*="StatusWidget"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="manage-app-button"],
        .stDeployButton,
        a[href*="streamlit.io/cloud"] {
            display: none !important;
            visibility: hidden !important;
        }
    `;
    window.parent.document.head.appendChild(style);
})();
</script>
""", height=0, width=0)

# --- BOTONES EN EL HEADER (Visualización) ---
st.markdown("""
    <style>
        .header-buttons-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 3.75rem; /* Altura estándar del header de Streamlit */
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 2rem;
            z-index: 999999;
            pointer-events: none; /* Permitir clicks en el header subyacente */
        }   
        
        .header-btn-group {
            display: flex;
            gap: 1rem;
            pointer-events: auto; /* Habilitar clicks en los botones */
        }
        
        .header-btn {
            background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid rgb(3, 110, 58);
            color: rgb(3, 110, 58);
            padding: 0.4rem 1.2rem;
            border-radius: 20px;
            font-family: 'Expressway', 'Overpass', sans-serif;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        .header-btn:hover {
            background-color: rgb(3, 110, 58);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(3, 110, 58, 0.2);
        }
    </style>
    
    <div class="header-buttons-container">
        <div class="header-btn-group" style="margin-left: auto;">
            <button class="header-btn">Contacto</button>
            <button class="header-btn">Ayuda</button>
        </div>
    </div>
""", unsafe_allow_html=True)

# Estilos CSS personalizados (Fondo blanco y detalles institucionales)
st.markdown("""
    <style>
        /* FUENTES */
        /* Importamos Overpass como fallback cercano a Expressway si no está instalada localmente */
        @import url('https://fonts.googleapis.com/css2?family=Overpass:wght@300;400;700&display=swap');
        
        /* AUMENTAR TAMAÑO BASE (ZOOM) */
        html {
            font-size: 20px; /* Aumentamos la base de 16px a 20px */
        }

        /* Aplicar Expressway a todo el cuerpo, con fallbacks */
        html, body, [class*="css"]  {
            font-family: 'Expressway', 'Overpass', 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }

        /* Fondo con gradiente sutil para dar profundidad */
        .stApp {
            background: linear-gradient(180deg, #FFFFFF 0%, #F2F2F2 100%);
            color: rgb(48, 47, 49);
        }
        
        /* CONTENEDOR PRINCIPAL MÁS ANCHO */
        .block-container {
            max-width: 900px; /* Más ancho para que quepa más texto */
            padding-top: 2rem;
            padding-bottom: 150px; /* Espacio suficiente para el input fijo */
        }
        
        /* Ajuste para que el scroll automático respete el espacio del input */
        #scroll-to-spinner, #scroll-to-end {
            scroll-margin-bottom: 150px;
        }
        
        /* Forzar color negro en textos para asegurar contraste */
        p, .stMarkdown {
            color: rgb(48, 47, 49) !important;
            font-size: 1.1rem; /* Texto un poco más grande */
            line-height: 1.6;
        }

        /* Ocultar menú de hamburguesa y footer de Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden; display: none !important;}
        
        /* ELIMINAR ESTILOS POR DEFECTO DE LAS BURBUJAS DE CHAT */
        .stChatMessage {
            background-color: transparent !important;
            border: none !important;
            align-items: center !important; /* Centrar verticalmente avatar y mensaje */
        }

        /* Ajuste fino para el avatar */
        .stChatMessage .stAvatar {
            margin-top: 0 !important;
        }
        
        /* Personalizar colores de Streamlit (Barras y botones) */
        /* header[data-testid="stHeader"] se maneja dinámicamente abajo */
        
        .stButton>button {
            background-color: rgb(3, 110, 58);
            color: white;
            font-weight: bold;
            border-radius: 8px;
            font-size: 1.1rem; /* Botones más grandes */
            padding: 0.5rem 1rem;
        }
        /* Color de la barra lateral */
        section[data-testid="stSidebar"] {
            background-color: #f8f9fa;
            border-right: 1px solid #e0e0e0;
        }
        
    /* Ocultar el footer de Streamlit ("Made with Streamlit") */
    footer, .stFooter {
        visibility: hidden !important;
        height: 0px !important;
        display: none !important;
        background-color: transparent !important;
        opacity: 0 !important;
    }
    
    /* Asegurar que el fondo general sea blanco para evitar bordes negros */
    .stApp, body, html {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
    }
    
    /* Eliminar cualquier fondo oscuro en el root */
    :root {
        --background-color: #FFFFFF !important;
    }
    
    /* Ocultar el menú de hamburguesa y el botón de deploy si se desea una vista más limpia */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Asegurar espacio al final para que el input fijo no tape el contenido */
    [data-testid="stMain"] .block-container {
        padding-bottom: 120px !important;
    }
    
    /* --- NUEVO ESTILO PARA INPUT FLOTANTE (st.chat_input) --- */
    
    /* Ocultar el contenedor inferior original de Streamlit (causante de líneas y bordes) */
    /* IMPORTANTE: No ocultar stBottom si usamos st.chat_input, ya que vive ahí. 
       Pero como lo movemos con position: fixed, no importa. 
       Sin embargo, stBottom tiene un background blanco que puede tapar cosas. 
       Lo hacemos transparente. */
    [data-testid="stBottom"] {
        background-color: #FFFFFF !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* FORZAR FONDO BLANCO EN TODOS LOS CONTENEDORES INFERIORES */
    [data-testid="stBottom"] > div,
    [data-testid="stBottom"] > div > div,
    [data-testid="stBottomBlockContainer"],
    .stChatFloatingInputContainer,
    [data-testid="stAppViewBlockContainer"],
    [class*="bottom"],
    [class*="Bottom"] {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
    }
    
    /* Asegurar que el input de chat sea visible y reseteado */
    [data-testid="stChatInput"] {
        display: block !important;
        background-color: transparent !important;
    }

    /* Estilo del texto dentro del input (Color y reset) */
    [data-testid="stChatInput"] textarea {
        color: #000000 !important;
        background-color: transparent !important;
        border: none !important;
        caret-color: #000000;
    }

    /* ELIMINAR SOMBREADO DE AUTOCOMPLETADO (CHROME/EDGE) */
    [data-testid="stChatInput"] textarea:-webkit-autofill,
    [data-testid="stChatInput"] textarea:-webkit-autofill:hover, 
    [data-testid="stChatInput"] textarea:-webkit-autofill:focus, 
    [data-testid="stChatInput"] textarea:-webkit-autofill:active {
        -webkit-box-shadow: 0 0 0 30px white inset !important;
        -webkit-text-fill-color: #000000 !important;
        transition: background-color 5000s ease-in-out 0s;
    }

    /* MEJORAR CALIDAD Y ESTILO DE LOS AVATARES */
    [data-testid="stChatMessageAvatar"] {
        background-color: #FFFFFF !important; /* Fondo blanco para resaltar el logo */
        border: 1px solid #e0e0e0; /* Borde sutil */
        padding: 4px !important; /* Espacio interno para que el logo respire */
        width: 45px !important;
        height: 45px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    [data-testid="stChatMessageAvatar"] img {
        object-fit: contain !important; /* Asegura que el logo se vea completo y nítido */
        width: 100% !important;
        height: 100% !important;
    }
    
    /* ANIMACIÓN TEXTO GOBERNACIÓN (Letra por letra) */
    @keyframes letter-blink {
        0% { color: rgb(48, 47, 49); text-shadow: none; }
        15% { color: rgb(3, 110, 58); text-shadow: 0 0 5px rgba(3, 110, 58, 0.3); } /* Punto máximo más lento */
        30% { color: rgb(48, 47, 49); text-shadow: none; } /* Fin del parpadeo */
        100% { color: rgb(48, 47, 49); text-shadow: none; } /* Pausa larga */
    }
    .gob-letter {
        animation: letter-blink 10s infinite; /* Ciclo de 10 segundos */
        display: inline-block;
    }
    
    /* ANIMACIÓN TÍTULO ALLISON (Brillo blanco cada 15s) */
    @keyframes shine-title {
        0% { background-position: -200%; }
        20% { background-position: 200%; } /* Pasa lento (3s aprox) */
        100% { background-position: 200%; } /* Espera larga (12s) */
    }
    .allison-title {
        background: linear-gradient(110deg, #000000 35%, #666666 45%, #FFFFFF 50%, #666666 55%, #000000 65%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine-title 15s linear infinite;
    }
    
    /* Asegurar que el placeholder sea visible, más claro y pequeño */
    [data-testid="stChatInput"] textarea::placeholder {
        color: #AAAAAA !important; /* Gris más claro */
        font-size: 0.9rem !important; /* Texto más pequeño */
        opacity: 1 !important;
    }
    
    /* Efecto de foco */
    [data-testid="stChatInput"] > div:focus-within {
        box-shadow: none !important;
        border-color: rgb(3, 110, 58) !important;
    }
    
    /* Estilo del botón de enviar (flecha) */
    [data-testid="stChatInput"] button {
        color: rgb(3, 110, 58) !important;
        border: none !important;
        background: transparent !important;
        align-self: center !important; /* Centrar verticalmente */
        margin-top: auto !important;
        margin-bottom: auto !important;
    }
    [data-testid="stChatInput"] button:hover {
        color: #000000 !important;
        background: transparent !important;
    }
        
        /* Centrar imagen usando CSS Flexbox en lugar de columnas de Streamlit para precisión */
        .logo-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding-bottom: 0px; /* Reducido al mínimo */
            padding-top: 60px; /* Reducido a la mitad para subir todo */
        }
        .logo-container img {
            max-width: 300px;
            height: auto;
            filter: drop-shadow(0 10px 15px rgba(0,0,0,0.15)); /* Sombra flotante */
            transition: transform 0.3s ease;
        }
        .logo-container img:hover {
            transform: scale(1.05); /* Efecto sutil al pasar el mouse */
        }

        /* --- RESPONSIVE DESIGN (MÓVIL) --- */
        @media only screen and (max-width: 600px) {
            /* Ajuste general de fuentes */
            html {
                font-size: 14px !important;
            }
            
            /* Header: Logo más pequeño y botones ajustados */
            header[data-testid="stHeader"] {
                background-size: auto 50% !important;
                background-position: 10px center !important;
            }
            .header-buttons-container {
                padding: 0 0.5rem !important;
            }
            .header-btn {
                padding: 0.25rem 0.6rem !important;
                font-size: 0.75rem !important;
                margin-top: 5px !important;
            }
            
            /* Logo Principal y Título */
            .logo-container {
                padding-top: 10px !important;
            }
            .logo-container img {
                max-width: 140px !important;
            }
            .allison-title {
                font-size: 3.5em !important;
                margin-top: -5px !important;
            }
            
            /* Textos de bienvenida */
            #typewriter-1 {
                font-size: 1rem !important;
                line-height: 1.3 !important;
                min-height: 3em !important; /* Espacio para 2 líneas */
            }
            #typewriter-2 {
                font-size: 0.9rem !important;
            }
            
            /* Input de chat en móvil - Solo ajustar ancho, la posición la maneja cada estado */
            [data-testid="stChatInput"] {
                width: 92% !important;
                max-width: 100% !important;
            }
            
            /* Ajustar padding del contenedor principal */
            .block-container {
                padding-top: 1rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
            
            /* Ocultar logo de Streamlit y botón de GitHub en móvil */
            .viewerBadge_container__r5I1v,
            .viewerBadge_link__qRIco,
            [data-testid="stDecoration"],
            .stDeployButton,
            [data-testid="manage-app-button"],
            a[href*="streamlit.io"],
            a[href*="github.com"],
            iframe[title="streamlit"],
            .styles_viewerBadge__CvC9N,
            /* Botones flotantes de Streamlit Cloud */
            div[class*="viewerBadge"],
            div[class*="StatusWidget"],
            button[kind="header"],
            [data-testid="stStatusWidget"],
            .stActionButton,
            /* Forzar ocultar todo en la esquina inferior derecha */
            div[style*="position: fixed"][style*="bottom"],
            div[style*="position: fixed"][style*="right"] {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                pointer-events: none !important;
                width: 0 !important;
                height: 0 !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DINÁMICA PARA LA BARRA DE INPUT (CENTRO vs ABAJO) ---
welcome_placeholder = st.empty()

if len(st.session_state.messages) == 0:
    # --- MENSAJE DE BIENVENIDA ALEATORIO (Encima del input) ---
    greetings = [
        "¡Hola! Estoy lista para ayudarte con tus consultas.",
        "¿En qué puedo serte útil el día de hoy?",
        "Cuéntame, ¿qué necesitas saber sobre la Secretaría?",
        "Estoy a tu disposición. ¿Por dónde empezamos?",
        "¡Bienvenido! ¿Cómo puedo hacer tu día más fácil?",
        "¿Tienes alguna pregunta en mente? Soy todo oídos.",
        "Aquí estoy para resolver tus dudas de infraestructura.",
        "¡Un gusto saludarte! ¿En qué te puedo colaborar?",
        "¿Buscas algún documento o información específica?",
        "Estoy aquí para apoyarte, pregúntame lo que quieras."
    ]
    selected_greeting = random.choice(greetings)
    
    with welcome_placeholder.container():
        # CSS para el contenedor del mensaje de bienvenida
        # Posicionado justo arriba del input, no con position fixed absoluto
        st.markdown("""
        <style>
            #welcome-message {
                position: fixed;
                bottom: 26%;
                left: 50%;
                transform: translateX(-50%);
                width: 80%;
                text-align: center;
                font-size: 1.3rem;
                color: rgb(48, 47, 49);
                font-weight: bold;
                z-index: 9998;
                font-family: 'Expressway', 'Overpass', sans-serif;
            }
            #welcome-message span {
                opacity: 0;
                display: inline-block;
            }
            
            /* Ajuste para móviles */
            @media only screen and (max-width: 600px) {
                #welcome-message {
                    bottom: 25% !important;
                    font-size: 1rem !important;
                    width: 90% !important;
                }
            }
        </style>
        """, unsafe_allow_html=True)

        # Contenedor vacío para el texto animado
        st.markdown("""
        <div id="welcome-message"></div>
        """, unsafe_allow_html=True)
        
        # JavaScript para animar letra por letra y luego desaparecer en reversa
        components.html(f"""
        <script>
            async function animateWelcome() {{
                const text = "{selected_greeting}";
                const container = window.parent.document.getElementById('welcome-message');
                if (!container) return;
                
                container.innerHTML = '';
                const spans = [];
                
                // Crear spans para cada carácter
                for (let i = 0; i < text.length; i++) {{
                    const span = document.createElement('span');
                    span.textContent = text[i] === ' ' ? '\\u00A0' : text[i];
                    span.style.opacity = '0';
                    span.style.display = 'inline-block';
                    container.appendChild(span);
                    spans.push(span);
                }}
                
                // Animación de aparición letra por letra
                for (let i = 0; i < spans.length; i++) {{
                    spans[i].style.transition = 'opacity 0.05s ease-in';
                    spans[i].style.opacity = '1';
                    await new Promise(r => setTimeout(r, 40));
                }}
                
                // Esperar 5 segundos
                await new Promise(r => setTimeout(r, 5000));
                
                // Animación de desaparición letra por letra (en reversa)
                for (let i = spans.length - 1; i >= 0; i--) {{
                    spans[i].style.transition = 'opacity 0.05s ease-out';
                    spans[i].style.opacity = '0';
                    await new Promise(r => setTimeout(r, 40));
                }}
            }}
            
            // Escuchar el evento disparado por la animación de subtítulos
            window.parent.document.addEventListener('startWelcomeAnimation', function() {{
                animateWelcome();
            }});
        </script>
        """, height=0, width=0)

    # ESTADO INICIAL: CENTRADO (Estilo ChatGPT)
    st.markdown("""
    <style>
        /* Animación de entrada inicial */
        @keyframes floatIn {
            0% {
                opacity: 0;
                transform: translate(-50%, -30%);
            }
            100% {
                opacity: 1;
                transform: translate(-50%, -50%);
            }
        }
        
        [data-testid="stChatInput"] {
            position: fixed;
            top: 78%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 70%; /* Aumentado para ser más visible */
            max-width: 800px; /* Aumentado el ancho máximo */
            z-index: 9999;
            padding: 0 !important;
            animation: floatIn 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }
        
        /* Ajuste móvil para el input inicial */
        @media only screen and (max-width: 600px) {
            [data-testid="stChatInput"] {
                top: 82% !important; /* Bajar más el input en móvil para dar espacio al mensaje */
                width: 90% !important;
            }
        }
        
        [data-testid="stChatInput"] > div {
            background-color: #FFFFFF !important;
            border: 2px solid rgb(3, 110, 58) !important;
            border-radius: 15px !important; /* Más cuadrado con esquinas suavizadas */
            padding: 2px 10px !important; /* Reducido para hacerla más delgada */
            box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
            display: flex !important;
            align-items: center !important; /* Centrado vertical crítico */
            justify-content: center !important;
        }
        /* Asegurar que no haya fondos oscuros internos */
        [data-testid="stChatInput"] [data-baseweb="base-input"],
        [data-testid="stChatInput"] [data-baseweb="textarea"] {
            background-color: transparent !important;
            align-items: center !important;
        }
        [data-testid="stChatInput"] textarea {
            font-size: 1.1rem !important;
            padding-top: 6px !important; 
            padding-bottom: 6px !important;
            min-height: auto !important;
            height: auto !important;
            line-height: 1.2 !important;
            align-self: center !important; /* Asegurar que el textarea se centre */
        }
        /* Centrar explícitamente el botón de enviar */
        [data-testid="stChatInputSubmitButton"] {
            align-self: center !important;
            margin-top: 0 !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            height: auto !important;
            display: flex !important;
            align-items: center !important;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    # ESTADO CHAT ACTIVO: ABAJO (STANDARD)
    st.markdown("""
    <style>
        /* Animación de deslizamiento hacia abajo */
        @keyframes slideDown {
            0% {
                opacity: 0.8;
                transform: translateY(-100px) scale(1.05);
            }
            50% {
                transform: translateY(10px) scale(0.98);
            }
            100% {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }
        
        [data-testid="stChatInput"] {
            position: fixed;
            bottom: 10px;
            left: 0;
            right: 0;
            margin-left: auto;
            margin-right: auto;
            width: 90%;
            max-width: 700px;
            z-index: 9999;
            padding: 0 !important;
            animation: slideDown 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }
        [data-testid="stChatInput"] > div {
            background-color: #FFFFFF !important;
            border: 2px solid rgb(3, 110, 58) !important;
            border-radius: 15px !important;
            padding: 5px 10px !important;
            box-shadow: none !important;
            display: flex !important;
            align-items: center !important;
        }
        /* Asegurar que no haya fondos oscuros internos */
        [data-testid="stChatInput"] [data-baseweb="base-input"],
        [data-testid="stChatInput"] [data-baseweb="textarea"] {
            background-color: transparent !important;
        }
        [data-testid="stChatInput"] textarea {
            font-size: 1.1rem !important;
        }
        
        /* Ajuste móvil para el input en modo chat activo */
        @media only screen and (max-width: 600px) {
            [data-testid="stChatInput"] {
                bottom: 100px !important; /* Subido para no solaparse con botones de micrófono/enviar */
                width: 92% !important;
                max-width: 100% !important;
                left: 50% !important;
                right: auto !important;
                transform: translateX(-50%) !important;
                margin: 0 !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO INSTITUCIONAL ---
# Logo de Allison centrado perfectamente con CSS
if os.path.exists("assets/logo_allison.svg"):
    # Leemos la imagen en base64 para incrustarla directamente en HTML y centrarla con CSS
    import base64
    with open("assets/logo_allison.svg", "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    
    st.markdown(
        f"""
        <div class="logo-container">
            <img src="data:image/svg+xml;base64,{data}" alt="Logo Allison">
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("Logo Allison no encontrado en assets/")

# --- TÍTULO Y DESCRIPCIÓN ---
# Fuente Didot aplicada al título, con margen superior reducido para acercarlo al logo
st.markdown("<h1 class='allison-title' style='text-align: center; font-family: Didot, serif; font-size: 6em; margin-top: -20px; margin-bottom: -10px;'>Allison</h1>", unsafe_allow_html=True)

# Lógica para animar el subtítulo solo una vez por sesión
if "subtitle_animated" not in st.session_state:
    st.session_state.subtitle_animated = False

if not st.session_state.subtitle_animated:
    # Versión para animar (contenedores vacíos + script JS)
    st.markdown("""
    <div style='text-align: center; color: rgb(48, 47, 49); margin-top: 0px;'>
        <div id="typewriter-1" style='font-weight: bold; font-size: 1.2em; min-height: 1.5em; margin-bottom: -5px;'></div>
        <div id="typewriter-2" style='font-style: italic; font-size: 1.1em; min-height: 1.5em;'></div>
        <br>
    </div>
    """, unsafe_allow_html=True)
    
    components.html("""
    <script>
        async function typeWriter(text, elementId, speed, useSpans) {
            var element = window.parent.document.getElementById(elementId);
            if (!element) return;
            element.innerHTML = "";
            for (var i = 0; i < text.length; i++) {
                if (useSpans) {
                    var span = document.createElement("span");
                    var char = text.charAt(i);
                    span.innerHTML = (char === " ") ? "&nbsp;" : char;
                    span.className = "gob-letter";
                    span.style.animationDelay = (i * 0.1) + "s";
                    element.appendChild(span);
                } else {
                    element.innerHTML += text.charAt(i);
                }
                await new Promise(r => setTimeout(r, speed));
            }
        }
        
        async function start() {
            // Esperar un poco para asegurar que el DOM esté listo
            await new Promise(r => setTimeout(r, 100));
            
            // 1. Animar "Asistente Virtual..."
            await typeWriter("Asistente Virtual de la Secretaría de Infraestructura Física", "typewriter-1", 35, false);
            
            // 2. Esperar 1 segundo y animar "Gobernación de Antioquia"
            await new Promise(r => setTimeout(r, 1000));
            await typeWriter("Gobernación de Antioquia", "typewriter-2", 35, true);
            
            // 3. Esperar 1 segundo y disparar evento para el mensaje de bienvenida
            await new Promise(r => setTimeout(r, 1000));
            window.parent.document.dispatchEvent(new CustomEvent('startWelcomeAnimation'));
        }
        start();
    </script>
    """, height=0, width=0)
    
    # Marcar como animado para que no se repita en cada interacción
    st.session_state.subtitle_animated = True
else:
    # Versión estática (para después de la primera carga)
    # Generamos el HTML con spans para cada letra con delay escalonado
    gob_text = "Gobernación de Antioquia"
    gob_html = "".join([f'<span class="gob-letter" style="animation-delay: {i*0.1}s">{char if char != " " else "&nbsp;"}</span>' for i, char in enumerate(gob_text)])
    
    st.markdown(f"""
    <div style='text-align: center; color: rgb(48, 47, 49); margin-top: 0px;'>
        <b style='font-size: 1.2em; display: block; margin-bottom: 5px;'>Asistente Virtual de la Secretaría de Infraestructura Física</b>
        <i style='font-size: 1.1em;'>{gob_html}</i><br><br>
    </div>
    """, unsafe_allow_html=True)

# Sidebar para gestión de documentos
with st.sidebar:
    st.header("Gestión de Documentos")
    uploaded_files = st.file_uploader("Subir documentos (TXT, PDF)", accept_multiple_files=True, type=['txt', 'pdf'])
    
    if uploaded_files:
        if not os.path.exists("data"):
            os.makedirs("data")
        
        for uploaded_file in uploaded_files:
            with open(os.path.join("data", uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success(f"Se subieron {len(uploaded_files)} archivos.")
    
    if st.button("Re-indexar Base de Datos"):
        with st.spinner("Creando base de datos vectorial..."):
            create_vector_db()
        st.success("Base de datos actualizada!")

# Definir avatares
# Prioridad: SVG > JPG > Default
if os.path.exists("assets/user_avatar.svg"):
    USER_AVATAR = "assets/user_avatar.svg"
elif os.path.exists("assets/user_avatar.jpg"):
    USER_AVATAR = "assets/user_avatar.jpg"
else:
    USER_AVATAR = "👤"

BOT_AVATAR = "assets/logo_allison.svg" if os.path.exists("assets/logo_allison.svg") else "🤖"

# Mostrar mensajes del chat con estilos personalizados
for message in st.session_state.messages:
    role = message["role"]
    avatar = USER_AVATAR if role == "user" else BOT_AVATAR
    
    with st.chat_message(role, avatar=avatar):
        if role == "user":
            # Estilo Usuario: Fondo blanco, borde sutil, alineado (visualmente)
            st.markdown(f"""
                <div style='background-color: #FFFFFF; 
                            color: #000000; 
                            padding: 15px; 
                            border-radius: 15px; 
                            border: 1px solid #e0e0e0; 
                            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                            margin-bottom: 10px;'>
                    {message["content"]}
                </div>
            """, unsafe_allow_html=True)
        else:
            # Estilo Allison: Fondo verde institucional, texto blanco
            st.markdown(f"""
                <div style='background-color: rgb(3, 110, 58); 
                            color: #FFFFFF; 
                            font-family: "Expressway", sans-serif;
                            padding: 15px; 
                            border-radius: 15px; 
                            border: 1px solid rgb(3, 110, 58);
                            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                            margin-bottom: 10px;'>
                    {message["content"]}
                </div>
            """, unsafe_allow_html=True)

# Input del usuario personalizado con st.chat_input (Incluye botón de enviar)
prompt = st.chat_input("")

if prompt:
    # Limpiar mensaje de bienvenida inmediatamente
    welcome_placeholder.empty()

    # FORZAR CAMBIO DE ESTILO A "ABAJO" INMEDIATAMENTE
    st.markdown("""
    <style>
        [data-testid="stChatInput"] {
            position: fixed;
            bottom: 10px;
            top: auto !important; /* Anular top */
            left: 0;
            right: 0;
            margin-left: auto;
            margin-right: auto;
            width: 90%;
            max-width: 700px;
            z-index: 9999;
            padding: 0 !important;
            transform: none !important; /* Quitar centrado */
        }
        [data-testid="stChatInput"] > div {
            background-color: #FFFFFF !important;
            border: 2px solid rgb(3, 110, 58) !important;
            border-radius: 15px !important;
            padding: 5px 10px !important;
            box-shadow: none !important;
            display: flex !important;
            align-items: center !important;
        }
        /* Asegurar que no haya fondos oscuros internos */
        [data-testid="stChatInput"] [data-baseweb="base-input"],
        [data-testid="stChatInput"] [data-baseweb="textarea"] {
            background-color: transparent !important;
        }
        [data-testid="stChatInput"] textarea {
            font-size: 1.1rem !important;
        }
        
        /* Ajuste móvil después de enviar mensaje */
        @media only screen and (max-width: 600px) {
            [data-testid="stChatInput"] {
                bottom: 15px !important;
                width: 92% !important;
                max-width: 100% !important;
                left: 50% !important;
                right: auto !important;
                transform: translateX(-50%) !important;
                margin: 0 !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    # Limpiar el prompt procesado para evitar re-ejecuciones
    st.session_state.user_prompt = ""
    
    # Guardar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(f"""
            <div style='background-color: #FFFFFF; 
                        color: #000000; 
                        padding: 15px; 
                        border-radius: 15px; 
                        border: 1px solid #e0e0e0; 
                        box-shadow: 0 4px 10px rgba(0,0,0,0.1);'>
                {prompt}
            </div>
        """, unsafe_allow_html=True)
        
    # Scroll para mostrar que se envió el mensaje
    # Eliminamos el scroll agresivo anterior que causaba saltos
    
    # Generar respuesta
    with st.chat_message("assistant", avatar=BOT_AVATAR):
        # Placeholder animado para "Escribiendo..."
        status_placeholder = st.empty()
        status_placeholder.markdown("""
            <style>
                @keyframes dots {
                    0% { content: ""; }
                    25% { content: "."; }
                    50% { content: ".."; }
                    75% { content: "..."; }
                    100% { content: ""; }
                }
                .typing-dots::after {
                    content: "";
                    animation: dots 1.5s infinite steps(1);
                    display: inline-block;
                    width: 1.5em;
                    text-align: left;
                }
            </style>
            <div style='color: #666666; font-style: italic; padding: 10px; font-size: 1rem;'>
                Allison está escribiendo<span class="typing-dots"></span>
            </div>
        """, unsafe_allow_html=True)

        qa_chain = get_qa_chain()
        
        if qa_chain:
            try:
                # Buscar información de capas GIS y datos de vías antes de invocar la cadena
                info_capas = buscar_capa_gis(prompt)
                info_vias = buscar_datos_vias(prompt)
                
                # Si encontramos capas o datos, las añadimos al prompt invisiblemente para que el modelo las use
                prompt_con_contexto = prompt
                if info_capas:
                    prompt_con_contexto += f"\n\n{info_capas}"
                if info_vias:
                    prompt_con_contexto += f"\n\n{info_vias}"
                
                response = qa_chain.invoke({"query": prompt_con_contexto})
                result = response["result"]
            except Exception as e:
                result = f"Lo siento, ocurrió un error al procesar tu solicitud: {e}"
        else:
            result = "No se pudo inicializar el chatbot. Por favor, verifica la configuración."
            
        # Limpiar el mensaje de estado antes de mostrar la respuesta
        status_placeholder.empty()
        
        # Script de Auto-Scroll Robusto (Sin saltos)
        # Usa scrollTop directo en el contenedor principal para evitar conflictos
        components.html(
            """
            <script>
                function setupAutoScroll() {
                    const observer = new MutationObserver(() => {
                        const main = window.parent.document.querySelector('.main');
                        if (main) {
                            main.scrollTop = main.scrollHeight;
                        }
                    });
                    
                    // Observar cambios en todo el cuerpo para capturar el streaming
                    observer.observe(window.parent.document.body, { 
                        childList: true, 
                        subtree: true, 
                        characterData: true 
                    });
                }
                setupAutoScroll();
            </script>
            """,
            height=0,
            width=0
        )
        
        # Simular efecto de escritura (Streaming) con aceleración exponencial
        message_placeholder = st.empty()
        full_response = ""
        
        # Marcar que estamos generando
        st.session_state.is_generating = True
        
        # Configuración de velocidad dinámica
        curr_delay = 0.04  # Empieza con velocidad moderada
        min_delay = 0.01   # Velocidad máxima limitada (10ms) para que sea legible
        acceleration = 0.98 # Aceleración muy suave (reduce el delay solo un 2% por carácter)

        # Estilo global para el mensaje del bot
        st.markdown("""
            <style>
                .bot-message-content, .bot-message-content * {
                    color: #FFFFFF !important;
                }
            </style>
        """, unsafe_allow_html=True)

        # Iteramos sobre el texto para simular la escritura carácter por carácter
        for i, char in enumerate(result):
            full_response += char
            # Actualizamos el contenedor con el texto acumulado + cursor parpadeante
            message_placeholder.markdown(f"""<div class="bot-message-content" style='background-color: rgb(3, 110, 58); color: #FFFFFF; font-family: "Expressway", sans-serif; padding: 15px; border-radius: 15px; border: 1px solid rgb(3, 110, 58); box-shadow: 0 4px 10px rgba(0,0,0,0.05);'>{full_response}▌</div>""", unsafe_allow_html=True)
            
            time.sleep(curr_delay)
            # Acelerar exponencialmente hasta el límite
            curr_delay = max(min_delay, curr_delay * acceleration)
        
        # Marcar que terminamos de generar
        st.session_state.is_generating = False
        
        # Mostrar respuesta final limpia (sin cursor)
        message_placeholder.markdown(f"""<div class="bot-message-content" style='background-color: rgb(3, 110, 58); color: #FFFFFF; font-family: "Expressway", sans-serif; padding: 15px; border-radius: 15px; border: 1px solid rgb(3, 110, 58); box-shadow: 0 4px 10px rgba(0,0,0,0.05);'>{full_response}</div>""", unsafe_allow_html=True)
        
        # Guardar en historial
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- INYECTAR BOTONES DE MICRÓFONO Y ENVIAR (SOLO MÓVIL) ---
# Los botones se inyectan directamente en el documento padre vía JavaScript
components.html("""
<script>
(function() {
    // Función para cerrar el teclado
    function closeKeyboard() {
        var textareas = window.parent.document.querySelectorAll('textarea');
        textareas.forEach(function(ta) {
            ta.blur();
        });
        if (window.parent.document.activeElement) {
            window.parent.document.activeElement.blur();
        }
    }
    
    // Función para agregar listener al botón de Streamlit
    function attachSubmitListener() {
        var submitBtn = window.parent.document.querySelector('[data-testid="stChatInputSubmitButton"]');
        if (submitBtn && !submitBtn.hasAttribute('data-allison-listener')) {
            submitBtn.setAttribute('data-allison-listener', 'true');
            submitBtn.addEventListener('click', function() {
                setTimeout(closeKeyboard, 50);
            });
        }
    }
    
    // Observador para detectar cuando Streamlit recrea el botón de enviar
    var observer = new MutationObserver(function() {
        attachSubmitListener();
    });
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
    
    // Agregar listener inicial
    attachSubmitListener();
    
    // Verificar si ya existe el contenedor para no duplicarlo
    if (window.parent.document.getElementById('allison-action-buttons')) {
        return;
    }
    
    // Crear estilos en el documento padre
    var style = window.parent.document.createElement('style');
    style.textContent = `
        #allison-action-buttons {
            position: fixed;
            bottom: 15px;
            left: 50%;
            transform: translateX(-50%);
            display: none;
            flex-direction: row;
            justify-content: center;
            align-items: center;
            gap: 20px;
            z-index: 999999;
        }
        
        .allison-action-btn {
            width: 50px;
            height: 50px;
            background-color: rgb(3, 110, 58);
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            cursor: pointer;
            transition: transform 0.2s, background-color 0.2s;
            border: 2px solid white;
        }
        
        .allison-action-btn:active {
            transform: scale(0.95);
            background-color: rgb(2, 80, 42);
        }
        
        .allison-action-btn.listening {
            background-color: #cc0000 !important;
            animation: mic-pulse 1.5s infinite;
        }
        
        @keyframes mic-pulse {
            0% { box-shadow: 0 0 0 0 rgba(204, 0, 0, 0.7); }
            70% { box-shadow: 0 0 0 15px rgba(204, 0, 0, 0); }
            100% { box-shadow: 0 0 0 0 rgba(204, 0, 0, 0); }
        }
        
        .allison-action-btn svg {
            width: 24px;
            height: 24px;
            fill: white;
        }
        
        /* Mostrar solo en móvil */
        @media only screen and (max-width: 768px) {
            #allison-action-buttons {
                display: flex !important;
            }
            
            /* Ajustar posición del input para dejar espacio a los botones */
            [data-testid="stChatInput"] {
                bottom: 100px !important;
            }
        }
    `;
    window.parent.document.head.appendChild(style);
    
    // Crear contenedor de botones
    var container = window.parent.document.createElement('div');
    container.id = 'allison-action-buttons';
    
    // Crear botón de micrófono
    var micBtn = window.parent.document.createElement('div');
    micBtn.className = 'allison-action-btn';
    micBtn.id = 'mic-btn-allison';
    micBtn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>';
    
    // Crear botón de enviar
    var sendBtn = window.parent.document.createElement('div');
    sendBtn.className = 'allison-action-btn';
    sendBtn.id = 'send-btn-allison';
    sendBtn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>';
    
    // Variables para reconocimiento de voz
    var recognition = null;
    var isListening = false;
    
    // Evento click del micrófono
    micBtn.onclick = function() {
        if (isListening) {
            stopDictation();
        } else {
            startDictation();
        }
    };
    
    // Evento click del botón enviar
    sendBtn.onclick = function() {
        // Cerrar el teclado
        closeKeyboard();
        
        // Buscar el botón de enviar de Streamlit y hacer click
        var submitBtn = window.parent.document.querySelector('[data-testid="stChatInputSubmitButton"]');
        if (submitBtn) {
            submitBtn.click();
        }
        
        // Asegurar que el foco se quite después del click
        setTimeout(closeKeyboard, 100);
    };
    
    function startDictation() {
        var SpeechRecognition = window.parent.webkitSpeechRecognition || window.parent.SpeechRecognition;
        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = "es-ES";
            
            recognition.onstart = function() {
                isListening = true;
                micBtn.classList.add('listening');
            };
            
            recognition.onerror = function(e) {
                console.error(e);
                stopDictation();
            };
            
            recognition.onend = function() {
                stopDictation();
            };
            
            recognition.onresult = function(e) {
                var transcript = e.results[0][0].transcript;
                insertText(transcript);
                stopDictation();
            };
            
            recognition.start();
        } else {
            alert("Tu navegador no soporta reconocimiento de voz. Usa Chrome en Android.");
        }
    }
    
    function stopDictation() {
        isListening = false;
        micBtn.classList.remove('listening');
        if (recognition) {
            try { recognition.stop(); } catch(e) {}
        }
    }
    
    function insertText(text) {
        var textareas = window.parent.document.querySelectorAll('textarea');
        for (var i = 0; i < textareas.length; i++) {
            var ta = textareas[i];
            if (ta.placeholder === '' || ta.getAttribute('data-testid') === 'stChatInputTextArea') {
                var nativeSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype, "value").set;
                nativeSetter.call(ta, text);
                ta.dispatchEvent(new Event('input', { bubbles: true }));
                ta.focus();
                break;
            }
        }
    }
    
    // Agregar botones al contenedor
    container.appendChild(micBtn);
    container.appendChild(sendBtn);
    
    // Agregar contenedor al body del padre
    window.parent.document.body.appendChild(container);
})();
</script>
""", height=0, width=0)
