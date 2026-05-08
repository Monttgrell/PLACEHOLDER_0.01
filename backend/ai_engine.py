import os
import requests
import json

# Explicación: Importamos las librerías necesarias.
# 'os' (Operating System) nos permite leer configuraciones ocultas de nuestro computador.
# 'requests' es la librería más famosa de Python para conectarnos a internet (como llamar a una API).
# 'json' nos ayuda a procesar datos estructurados.

def obtener_respuesta_deepseek(prompt: str) -> str:
    """
    Función auxiliar para comunicarnos con la API de DeepSeek.
    """
    # Explicación: Las claves (Contraseñas) de API NUNCA deben escribirse directamente en el código
    # porque si alguien roba el archivo, robará tu cuenta. 'os.getenv' busca la clave de forma segura en tu sistema.
    # El segundo texto ("TU_CLAVE_AQUI") es un valor de respaldo por si no la encuentra.
    api_key = os.getenv("DEEPSEEK_API_KEY", "TU_CLAVE_AQUI")
    
    # Esta es la "dirección web" a donde enviaremos nuestra carta (petición).
    url = "https://api.deepseek.com/chat/completions" 
    
    # Explicación: Los 'headers' (cabeceras) son como el exterior del sobre de una carta.
    # Aquí ponemos nuestra credencial de acceso (Bearer token) e indicamos que enviaremos datos tipo JSON.
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Explicación: El 'payload' (carga útil) es el contenido real de la carta.
    # Configuramos qué modelo usar, cómo debe comportarse el "sistema" y el mensaje del usuario.
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system", 
                "content": "Eres un asistente médico experto en estándares interoperables HL7 FHIR y en comunicación empática con pacientes."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        # Explicación: La 'temperatura' controla la creatividad de la IA.
        # 0.0 es como un robot estricto (perfecto para programación/datos). 1.0 es muy creativo.
        # Usamos 0.2 para que sea preciso pero no totalmente rígido.
        "temperature": 0.2 
    }
    
    try:
        # Explicación: Hacemos una petición 'POST' (enviar información) a la URL con nuestras cabeceras y datos.
        respuesta = requests.post(url, headers=headers, json=payload)
        
        # Explicación: 'raise_for_status()' es un guardián. Si DeepSeek nos responde con un error 
        # (por ejemplo, nos quedamos sin saldo o la clave es incorrecta), esto detendrá el programa y nos avisará.
        respuesta.raise_for_status() 
        
        # Explicación: Convertimos la respuesta de texto de internet a un diccionario de Python.
        datos = respuesta.json()
        
        # Explicación: Buceamos en el diccionario para extraer solamente el texto útil que generó la IA.
        return datos["choices"][0]["message"]["content"]
        
    except Exception as e:
        # Explicación: El bloque 'except' atrapa cualquier choque o error que ocurra arriba (ej. se cortó el internet)
        # y en lugar de destruir la aplicación, nos devuelve un mensaje de error amigable.
        return f"Error al conectar con el cerebro IA: {str(e)}"

def estructurar_como_fhir(texto_examen: str) -> str:
    """
    Componente: LEGACY GATEWAY
    Propósito: Toma un texto médico desordenado (ej. de un PDF) y le pide a la IA
    que lo estructure bajo el estándar internacional HL7 FHIR.
    """
    # Explicación: Este es nuestro "Prompt" (Instrucción maestra) usando "f-strings"
    # para insertar nuestra variable 'texto_examen' dentro del texto fácilmente.
    instruccion = f"""
    Toma el siguiente texto médico desestructurado extraído de un examen y conviértelo 
    a un formato JSON válido siguiendo el estándar HL7 FHIR (por ejemplo, como un recurso 'Observation').
    Devuelve ÚNICAMENTE el JSON puro, sin ningún texto o explicación adicional.
    
    Texto del examen:
    {texto_examen}
    """
    
    print("🧠 Procesando documento en Legacy Gateway...")
    return obtener_respuesta_deepseek(instruccion)

def traducir_a_lenguaje_paciente(texto_medico_tecnico: str) -> str:
    """
    Componente: TRADUCTOR SEMÁNTICO
    Propósito: Toma jerga médica compleja y la explica de forma amable y sencilla.
    """
    instruccion = f"""
    Actúa como un médico familiar muy empático. Traduce el siguiente diagnóstico 
    o resultado técnico a un lenguaje sencillo, cálido y esperanzador, 
    fácil de entender para un paciente sin conocimientos médicos.
    
    Texto técnico:
    {texto_medico_tecnico}
    """
    
    print("🗣️ Traductor Semántico trabajando...")
    return obtener_respuesta_deepseek(instruccion)

def generar_proyecciones(historial_completo: str) -> str:
    """
    Componente: GEMELO DIGITAL PREDICTIVO
    Propósito: Toma todo el historial del paciente y proyecta posibles
    complicaciones o sugerencias de prevención basadas en los datos consolidados.
    """
    instruccion = f"""
    Actúa como un sistema avanzado de inteligencia artificial médica. 
    Analiza el siguiente historial clínico completo de un paciente y genera un reporte estructurado que incluya:
    1. Resumen de salud actual.
    2. Proyecciones preventivas (ej. evolución de glucosa, peso, o riesgos latentes).
    3. Alertas de contraindicaciones o interacciones si las hay.
    
    El reporte debe estar redactado en un lenguaje empático pero profesional, dirigido al paciente.
    
    Historial Clínico:
    {historial_completo}
    """
    
    print("🔮 Generando proyecciones preventivas del Gemelo Digital...")
    return obtener_respuesta_deepseek(instruccion)
