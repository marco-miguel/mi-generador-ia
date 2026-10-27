import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
import re

# --- CONFIGURACIÓN Y CARGA DE API ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    st.error("⚠️ No se encontró GEMINI_API_KEY en el archivo .env")

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Generador IA", page_icon="🤖", layout="wide")

# --- CSS PERSONALIZADO (NEO CYBERPUNK) ---
st.markdown("""
<style>
    .stApp { 
        background-color: #0d0f12; 
        background-image: linear-gradient(#1a1a1a 1px, transparent 1px), linear-gradient(90deg, #1a1a1a 1px, transparent 1px);
        background-size: 40px 40px; color: #e0e0e0; font-family: 'Courier New', Courier, monospace; 
    }
    h1 { color: #00ffff; text-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 40px #00ffff; text-align: center; font-size: 3.5rem !important; margin-bottom: 0px; letter-spacing: 2px; }
    .subtitulo { text-align: center; color: #ff00ff; font-size: 1.2rem; text-shadow: 0 0 5px #ff00ff; margin-top: -10px; margin-bottom: 20px; letter-spacing: 1px; }
    h2, h3 { color: #ff00ff; text-shadow: 0 0 5px #ff00ff; }
    
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea textarea { 
        background-color: #1a1a1a !important; color: #00ffff !important; border: 1px solid #ff00ff !important; border-radius: 5px; box-shadow: 0 0 5px #ff00ff inset; font-family: 'Courier New', Courier, monospace; 
    }
    
    .stButton>button { 
        background: linear-gradient(90deg, #ff00ff, #00ffff); color: #000000; font-weight: bold; border: none; border-radius: 5px; padding: 10px 24px; font-size: 1.2rem; box-shadow: 0 0 10px #ff00ff, 0 0 20px #00ffff; transition: all 0.3s ease; width: 100%; text-transform: uppercase; 
    }
    .stButton>button:hover { box-shadow: 0 0 20px #ff00ff, 0 0 40px #00ffff; transform: scale(1.02); }
    
    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; background-color: #0d0f12; border-bottom: 2px solid #ff00ff; padding-bottom: 10px; }
    .stTabs [data-baseweb="tab"] { color: #e0e0e0; background-color: #1a1a1a; border: 1px solid #333; border-radius: 5px; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { color: #00ffff !important; border: 1px solid #00ffff !important; box-shadow: 0 0 10px #00ffff; }
    
    /* Estilo normal para el bloque de código */
    .stCodeBlock { 
        background-color: #111 !important; 
        border-left: 5px solid #00ffff; 
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.1); 
        margin-bottom: 10px;
        transition: all 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNCIÓN PARA MOSTRAR BLOQUES CON BOTÓN DE COPIA Y COLOR ---
def mostrar_bloque(texto, key_base):
    # Si el texto está vacío, no mostramos nada
    if not texto.strip():
        return
        
    # Creamos una columna para el texto y otra para el botón
    col1, col2 = st.columns([8.5, 1.5])
    
    with col1:
        # Verificamos si este bloque ya fue copiado en la sesión
        if st.session_state.get(f"copiado_{key_base}", False):
            # Si ya se copió, aplicamos un estilo verde brillante
            st.markdown(f"""
            <div style="background-color: #0a2a1a; border-left: 5px solid #00ff00; padding: 10px; border-radius: 5px; color: #00ff00; font-family: 'Courier New', monospace; font-size: 14px; white-space: pre-wrap;">
            {texto}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Si no se ha copiado, mostramos el bloque normal
            st.code(texto, language="text")
            
    with col2:
        # Este es el botón que marca el bloque como copiado
        if not st.session_state.get(f"copiado_{key_base}", False):
            if st.button("📋 Marcar Copiado", key=f"btn_{key_base}"):
                st.session_state[f"copiado_{key_base}"] = True
                st.toast("¡Bloque marcado! Ahora usa Ctrl+C o el botón de copiar del recuadro.")
                st.rerun()
        else:
            st.success("✅")

# --- INTERFAZ ---
st.markdown("<h1>GENERADOR IA</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo'>[ PRODUCTOR DE CONTENIDO ]</p>", unsafe_allow_html=True)
st.write("---")

modo_app = st.radio("► SELECCIONA EL MÓDULO:", ["Generador de Video Completo", "Generador de Ideas por Nicho"], horizontal=True)
st.write("---")

# ==========================================
# MÓDULO 1: GENERADOR DE VIDEO COMPLETO
# ==========================================
if modo_app == "Generador de Video Completo":
    col1, col2 = st.columns(2)
    with col1:
        titulo = st.text_input("► INGRESA EL TÍTULO O IDEA:", "Cómo ahorrar dinero en 2026")
        modo_video = st.selectbox("► TIPO DE VIDEO (MODO):", [
            "Lista de consejos", "Historia personal", "Explicación rápida", 
            "Tutorial paso a paso", "Storytelling (Narrativa)", "Top 5 / Ranking",
            "Mitos vs Realidad", "Análisis / Opinión"
        ])
    with col2:
        tono = st.selectbox("► TONO:", [
            "Informativo", "Divertido / Humor", "Serio / Formal", 
            "Inspirador / Motivacional", "Polémico / Controversial",
            "Misterioso / Suspenso", "Casual / Amigable"
        ])
        duracion = st.selectbox("► DURACIÓN:", [
            "15 segundos (Súper rápido)", "30 segundos (Corto)", 
            "60 segundos (Reel estándar)", "90 segundos (Profundo)", 
            "3 minutos (YouTube)", "5 a 10 minutos (Video largo)"
        ])
    
    instrucciones_extra = st.text_input("► INSTRUCCIONES EXTRA PARA LA IA (Opcional):", 
                                        placeholder="Ej: Usa ejemplos de la vida real, lenguaje callejero, menciona estadísticas...")

    if st.button("⚡ INICIAR GENERACIÓN DE PROTOCOLO"):
        if not GEMINI_API_KEY:
            st.error("Falta la API Key.")
        else:
            # Reseteamos los estados de copiado en cada nueva generación
            for key in list(st.session_state.keys()):
                if key.startswith("copiado_"):
                    del st.session_state[key]
                    
            with st.spinner("Calculando escenas y diseñando planos cinematográficos..."):
                prompt = f"""
                Eres un experto director de cine y creador de contenido. Devuelve un documento con estas 5 secciones exactas. 
                NO mezcles las secciones.
                
                INSTRUCCIONES ESPECÍFICAS: {instrucciones_extra if instrucciones_extra else "Ninguna."}

                **1. GUION EN VOZ EN OFF**
                (Texto continuo, gancho inicial. Tono: {tono}. Duración: {duracion}).

                **2. DESGLOSE POR ESCENAS**
                Escribe cada escena en una línea nueva con el formato: "Escena X: [Voz] | [Visual]".

                **3. PROMPTS PARA IMÁGENES (IA)**
                REGLA DE ORO: El video tendrá una imagen CADA 4 SEGUNDOS. 
                Calcula cuántas imágenes se necesitan para la duración de "{duracion}" y genera EXACTAMENTE esa cantidad de prompts.
                Cada prompt debe ser extremadamente detallado (sujeto, acción, entorno, iluminación cinematográfica, tipo de lente).
                Escribe CADA PROMPT en inglés en una línea nueva. Usa exactamente este formato por línea:
                "Prompt X (Escena Y): [Descripción super detallada en inglés], vertical format 9:16, cinematic lighting, 35mm lens, TikTok style".

                **4. IDEAS Y SUGERENCIAS EXTRA**
                (3 títulos alternativos, 2 ideas de audio).

                **5. DESCRIPCIÓN Y HASHTAGS**
                (Una descripción atractiva para el video y 5 hashtags virales relevantes).

                Título: {titulo} | Modo: {modo_video}
                """
                try:
                    interaction = client.interactions.create(model="gemini-3.8-flash", input=prompt)
                    resultado = interaction.output_text
                    
                    secciones = {}
                    m_g = re.search(r'\*\*1\. GUION EN VOZ EN OFF\*\*(.*?)(?=\*\*2\.|$)', resultado, re.DOTALL)
                    m_e = re.search(r'\*\*2\. DESGLOSE POR ESCENAS\*\*(.*?)(?=\*\*3\.|$)', resultado, re.DOTALL)
                    m_p = re.search(r'\*\*3\. PROMPTS PARA IMÁGENES.*?\*\*(.*?)(?=\*\*4\.|$)', resultado, re.DOTALL)
                    m_x = re.search(r'\*\*4\. IDEAS Y SUGERENCIAS EXTRA\*\*(.*?)(?=\*\*5\.|$)', resultado, re.DOTALL)
                    m_d = re.search(r'\*\*5\. DESCRIPCIÓN Y HASHTAGS\*\*(.*?)$', resultado, re.DOTALL)
                    
                    if m_g: secciones["guion"] = m_g.group(1).strip()
                    if m_e: secciones["escenas"] = m_e.group(1).strip()
                    if m_p: secciones["prompts"] = m_p.group(1).strip()
                    if m_x: secciones["extras"] = m_x.group(1).strip()
                    if m_d: secciones["descripcion"] = m_d.group(1).strip()

                    st.success("✅ Protocolo generado. Los bloques cambiarán a verde al marcarlos como copiados.")
                    
                    tabs = st.tabs(["📜 GUION", "🎬 ESCENAS", "🖼️ PROMPTS IMÁGENES", "💡 EXTRAS", "🏷️ DESCRIPCIÓN"])
                    
                    with tabs[0]: 
                        mostrar_bloque(secciones.get("guion",""), "guion")
                    
                    with tabs[1]:
                        texto_escenas = secciones.get("escenas","")
                        bloques_escenas = re.split(r'(?=\*?\s*Escena\s*\d+)', texto_escenas)
                        for idx, bloque in enumerate(bloques_escenas):
                            if bloque.strip():
                                mostrar_bloque(bloque.strip(), f"escena_{idx}")
                                
                    with tabs[2]: 
                        texto_prompts = secciones.get("prompts","")
                        bloques_prompts = re.split(r'(?=\*?\s*Prompt\s*\d+)', texto_prompts)
                        for idx, bloque in enumerate(bloques_prompts):
                            if bloque.strip():
                                mostrar_bloque(bloque.strip(), f"prompt_{idx}")
                                
                    with tabs[3]: 
                        mostrar_bloque(secciones.get("extras",""), "extras")
                    
                    with tabs[4]: 
                        mostrar_bloque(secciones.get("descripcion",""), "descripcion")
                        
                    st.write("---")
                    st.download_button(
                        label="📥 Descargar Todo el Proyecto (.txt)",
                        data=resultado,
                        file_name=f"proyecto_{titulo.replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"Error: {e}")

# ==========================================
# MÓDULO 2: GENERADOR DE IDEAS POR NICHO
# ==========================================
elif modo_app == "Generador de Ideas por Nicho":
    # (Este módulo se queda igual, pero podrías aplicarle la misma función mostrar_bloque si quisieras)
    col1, col2 = st.columns(2)
    with col1:
        nicho = st.text_input("► INGRESA TU NICHO:", "Finanzas personales para jóvenes")
    with col2:
        cantidad = st.slider("► CANTIDAD DE IDEAS:", min_value=3, max_value=10, value=5)

    if st.button("🧠 GENERAR LLUVIA DE IDEAS"):
        if not GEMINI_API_KEY:
            st.error("Falta la API Key.")
        else:
            with st.spinner("Buscando ideas en el ciberespacio..."):
                prompt_ideas = f"""
                Actúa como estratega de contenido. Para el nicho "{nicho}", dame {cantidad} ideas de videos virales.
                Para cada una, dame solo:
                1. Un Título llamativo.
                2. Una frase de Gancho (Hook) para los primeros 3 segundos.
                Sé breve y directo. Formatea como una lista numerada.
                """
                try:
                    interaction = client.interactions.create(model="gemini-3.1-flash-lite", input=prompt_ideas)
                    ideas = interaction.output_text
                    st.success(f"✅ {cantidad} ideas generadas.")
                    mostrar_bloque(ideas, "ideas")
                except Exception as e:
                    st.error(f"Error: {e}")
