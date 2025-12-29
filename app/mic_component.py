
# --- COMPONENTE DE MICRÓFONO FLOTANTE (SOLO MÓVIL) ---
# Inyectamos HTML/JS para crear un botón de micrófono que use Web Speech API
# y escriba directamente en el textarea de Streamlit.
components.html("""
<style>
    /* Estilo del botón flotante */
    #mic-btn {
        position: fixed;
        bottom: 80px; /* Encima del input si está abajo, o flotando si está arriba */
        right: 20px;
        width: 60px;
        height: 60px;
        background-color: rgb(3, 110, 58);
        border-radius: 50%;
        display: none; /* Oculto por defecto, se muestra solo en móvil */
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        cursor: pointer;
        z-index: 999999;
        transition: transform 0.2s, background-color 0.2s;
        border: 2px solid white;
    }
    
    #mic-btn:active {
        transform: scale(0.95);
        background-color: rgb(2, 80, 42);
    }
    
    #mic-btn.listening {
        background-color: #cc0000;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(204, 0, 0, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(204, 0, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(204, 0, 0, 0); }
    }
    
    /* Icono de micrófono (SVG simple) */
    #mic-icon {
        width: 30px;
        height: 30px;
        fill: white;
    }
    
    /* Mostrar solo en pantallas pequeñas (móvil) */
    @media only screen and (max-width: 768px) {
        #mic-btn {
            display: flex;
        }
    }
</style>

<div id="mic-btn" onclick="toggleDictation()">
    <svg id="mic-icon" viewBox="0 0 24 24">
        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
        <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
    </svg>
</div>

<script>
    var recognition;
    var isListening = false;
    
    function toggleDictation() {
        if (isListening) {
            stopDictation();
        } else {
            startDictation();
        }
    }

    function startDictation() {
        if (window.hasOwnProperty('webkitSpeechRecognition')) {
            recognition = new webkitSpeechRecognition();
            
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = "es-ES"; // Español
            
            recognition.onstart = function() {
                isListening = true;
                document.getElementById('mic-btn').classList.add('listening');
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
                insertTextToStreamlit(transcript);
                stopDictation();
            };
            
            recognition.start();
        } else {
            alert("Tu navegador no soporta reconocimiento de voz. Intenta usar Chrome en Android.");
        }
    }
    
    function stopDictation() {
        isListening = false;
        document.getElementById('mic-btn').classList.remove('listening');
        if (recognition) {
            recognition.stop();
        }
    }
    
    function insertTextToStreamlit(text) {
        // Buscar el textarea de Streamlit dentro del iframe padre
        var textareas = window.parent.document.getElementsByTagName('textarea');
        for (var i = 0; i < textareas.length; i++) {
            var ta = textareas[i];
            if (ta.getAttribute('data-testid') === 'stChatInputTextArea' || 
                ta.getAttribute('aria-label') === 'Chat input') {
                
                // Establecer el valor
                // React necesita que se dispare un evento de input real para actualizar su estado
                var nativeTextAreaValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                nativeTextAreaValueSetter.call(ta, text);
                
                var event = new Event('input', { bubbles: true});
                ta.dispatchEvent(event);
                
                // Opcional: Hacer foco
                ta.focus();
                break;
            }
        }
    }
</script>
""", height=0, width=0)
