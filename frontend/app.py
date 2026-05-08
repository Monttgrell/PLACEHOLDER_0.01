import streamlit as st
import requests
import easyocr
import numpy as np
from PIL import Image
import datetime
import time

# Configuración inicial de la página
st.set_page_config(page_title="PLACEHOLDER Gemelo Digital", page_icon="🧬", layout="wide")

# Explicación: Inicializamos la variable de estado (memoria) para saber si el usuario ya verificó su identidad.
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

@st.cache_resource
def cargar_lector_ocr():
    return easyocr.Reader(['es']) 

lector_ocr = cargar_lector_ocr()

st.title("🧬 PLACEHOLDER: Infraestructura de Salud Soberana")
st.markdown("*Empoderando al ciudadano mediante un Gemelo Digital y control total de sus datos.*")

# ==========================================
# BARRA LATERAL: GESTIÓN DE IDENTIDAD
# ==========================================
st.sidebar.header("👤 Gestión de Identidad")

with st.sidebar.expander("Crear Nuevo Perfil"):
    with st.form("form_nuevo_paciente"):
        nombre = st.text_input("Nombre Completo")
        rut = st.text_input("RUT")
        hoy = datetime.date.today()
        fecha_minima = hoy - datetime.timedelta(days=36500)
        fecha_defecto = hoy - datetime.timedelta(days=365*30)
        
        fecha_nac = st.date_input(
            "Fecha de Nacimiento",
            min_value=fecha_minima,
            max_value=hoy,
            value=fecha_defecto
        )
        submit_btn = st.form_submit_button("Registrar Paciente")
        
        if submit_btn and nombre and rut:
            try:
                res = requests.post("http://localhost:8000/nuevo_paciente", json={
                    "nombre": nombre,
                    "rut": rut,
                    "fecha_nacimiento": str(fecha_nac)
                })
                if res.status_code == 200:
                    st.success("¡Perfil creado con éxito! Actualiza la lista.")
                else:
                    st.error("Error al crear perfil.")
            except Exception as e:
                st.error("Error de conexión al servidor FastAPI.")

pacientes_lista = []
try:
    res = requests.get("http://localhost:8000/pacientes")
    if res.status_code == 200:
        pacientes_lista = res.json()
except:
    st.sidebar.error("🚨 Servidor FastAPI apagado. Por favor, inícialo.")

st.sidebar.markdown("### Selecciona tu Paciente Activo:")
opciones = {p['id']: f"{p['nombre']} ({p['rut']})" for p in pacientes_lista}

# Explicación: Si el usuario cambia de paciente, debemos bloquear la pantalla nuevamente.
# Esto asegura que nadie pueda ver los datos de otra persona sin escanearse.
def al_cambiar_paciente():
    st.session_state.autenticado = False

paciente_activo_id = st.sidebar.selectbox(
    "Paciente", 
    options=list(opciones.keys()), 
    format_func=lambda x: opciones[x],
    on_change=al_cambiar_paciente
)

if paciente_activo_id:
    if st.sidebar.button("🗑️ Eliminar mi Perfil y Datos", type="primary"):
        try:
            res = requests.delete(f"http://localhost:8000/eliminar_paciente/{paciente_activo_id}")
            if res.status_code == 200:
                st.sidebar.success("Perfil eliminado exitosamente.")
                st.session_state.autenticado = False
                st.rerun()
            else:
                st.sidebar.error("Error al intentar eliminar el perfil.")
        except:
            st.sidebar.error("Error de conexión con el servidor.")

if not paciente_activo_id:
    st.warning("⚠️ Por favor, crea un nuevo perfil en la barra lateral izquierda para comenzar.")
    st.stop()

# ==========================================
# PANTALLA DE BLOQUEO BIOMÉTRICA (LOCK SCREEN)
# ==========================================
if not st.session_state.autenticado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>🔐 Acceso Restringido</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Se requiere validación biométrica para acceder al Repositorio Soberano.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🧬 Iniciar Escaneo de Identidad", use_container_width=True, type="primary"):
            # Explicación: st.spinner detiene visualmente la app mientras time.sleep simula
            # el tiempo que tomaría un escaneo facial o dactilar real.
            with st.spinner("Escaneando patrones biométricos y verificando llaves en la blockchain..."):
                time.sleep(3)
            
            st.success("✅ Identidad Verificada. Acceso Concedido.")
            st.session_state.autenticado = True
            time.sleep(1) # Pequeña pausa para que el usuario lea el mensaje de éxito
            st.rerun()

# ==========================================
# DASHBOARD PRINCIPAL (Solo visible si está autenticado)
# ==========================================
if st.session_state.autenticado:
    tab1, tab2, tab3, tab4 = st.tabs(["Carga de Documentos", "Signos Vitales", "Historial", "Análisis"])
    
    # --- PESTAÑA 1: Carga de Documentos ---
    with tab1:
        st.header("Extracción Automática de Documentos Médicos")
        st.markdown("Sube una foto de tu examen (receta, laboratorio, etc.). Nuestra IA extraerá el texto y lo convertirá a un estándar médico universal (FHIR).")
        
        imagen_subida = st.file_uploader("Sube una imagen (PNG, JPG)", type=["png", "jpg", "jpeg"])
        
        if imagen_subida is not None:
            st.image(imagen_subida, caption="Documento subido a tu dispositivo", width=400)
            
            if st.button("Analizar Documento con IA", type="primary"):
                with st.spinner("1️⃣ Leyendo la imagen (esto puede tardar unos segundos)..."):
                    imagen_pil = Image.open(imagen_subida)
                    imagen_np = np.array(imagen_pil)
                    resultados_ocr = lector_ocr.readtext(imagen_np)
                    texto_extraido = " ".join([resultado[1] for resultado in resultados_ocr])
                    
                st.info(f"**Texto extraído (Pre-visualización):** {texto_extraido[:300]}...")
                
                with st.spinner("2️⃣ Estructurando datos en estándar FHIR y guardando en tu repositorio..."):
                    try:
                        res = requests.post(
                            f"http://localhost:8000/procesar_documento/{paciente_activo_id}",
                            json={"texto": texto_extraido}
                        )
                        if res.status_code == 200:
                            st.success("✅ ¡Éxito! Documento encriptado y guardado.")
                            with st.expander("Ver JSON FHIR generado por DeepSeek"):
                                st.json(res.json()["fhir"])
                        else:
                            st.error("Error al guardar en el servidor.")
                    except:
                        st.error("🚨 Error de red con FastAPI.")
    
    # --- PESTAÑA 2: SIGNOS VITALES ---
    with tab2:
        st.header("❤️ Ingreso Manual de Signos Vitales")
        st.markdown("Registra tus constantes vitales directamente en tu Repositorio Soberano.")
        
        with st.form("form_signos"):
            col1, col2 = st.columns(2)
            with col1:
                peso = st.number_input("Peso (kg)", min_value=1.0, max_value=300.0, value=70.0, step=0.1)
                altura = st.number_input("Altura (m)", min_value=0.5, max_value=3.0, value=1.70, step=0.01)
                ritmo = st.number_input("Ritmo Cardíaco (LPM/bpm)", min_value=30, max_value=250, value=70, step=1)
            
            with col2:
                fecha_medicion = st.date_input("Fecha de medición", value=datetime.date.today())
                hora_medicion = st.time_input("Hora de medición", value=datetime.datetime.now().time())
            
            btn_signos = st.form_submit_button("Guardar Registro", type="primary")
            
            if btn_signos:
                try:
                    res = requests.post(f"http://localhost:8000/registrar_signos/{paciente_activo_id}", json={
                        "peso": peso,
                        "altura": altura,
                        "ritmo_cardiaco": ritmo,
                        "fecha": str(fecha_medicion),
                        "hora": str(hora_medicion)
                    })
                    if res.status_code == 200:
                        st.success("¡Constantes vitales guardadas exitosamente en tu repositorio!")
                    else:
                        st.error("Error al guardar registro.")
                except Exception as e:
                    st.error("Error de conexión con el backend.")
    
    # --- PESTAÑA 3: HISTORIAL ---
    with tab3:
        st.header("Tu Historial Clínico Soberano")
        st.markdown("Visualiza todos los datos médicos estructurados que has acumulado con el tiempo.")
        
        if st.button("🔄 Cargar Historial"):
            with st.spinner("Cargando tu repositorio..."):
                try:
                    res = requests.get(f"http://localhost:8000/historial/{paciente_activo_id}")
                    if res.status_code == 200:
                        historial = res.json()
                        if historial:
                            for registro in historial:
                                with st.expander(f"📅 {registro['fecha_registro']} - {registro['tipo_recurso']}"):
                                    st.write(f"**ID de Registro:** {registro['id']}")
                                    st.code(registro["contenido_fhir"], language="json")
                        else:
                            st.info("Aún no tienes registros en tu historial clínico.")
                except:
                    st.error("Error al conectar con el servidor.")
    
    # --- PESTAÑA 4: ANÁLISIS PREDICTIVO ---
    with tab4:
        st.header("🔮 Proyecciones del Gemelo Digital")
        st.markdown("La IA (DeepSeek) analizará absolutamente **todo** tu repositorio soberano para buscar patrones, proyectar tu salud futura y alertarte sobre contraindicaciones.")
        
        if st.button("Generar Análisis Completo", type="primary"):
            with st.spinner("Analizando tus datos vitales y proyectando escenarios de salud..."):
                try:
                    res = requests.get(f"http://localhost:8000/proyecciones/{paciente_activo_id}")
                    if res.status_code == 200:
                        datos = res.json()
                        st.success("Análisis completado exitosamente.")
                        st.markdown(datos["proyeccion"])
                    else:
                        st.error("Error al generar proyecciones.")
                except:
                    st.error("Error de conexión.")
