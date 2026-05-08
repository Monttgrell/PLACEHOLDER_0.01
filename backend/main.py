from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import datetime

# Explicación: Importamos nuestros módulos.
from . import database, models, ai_engine

app = FastAPI(title="Motor Central PLACEHOLDER", description="Backend del Repositorio Soberano")

class DocumentoBruto(BaseModel):
    texto: str

class TextoMedico(BaseModel):
    texto_tecnico: str

@app.on_event("startup")
def iniciar_aplicacion():
    database.inicializar_base_datos()
    print("🚀 Servidor iniciado. Base de datos SQLite lista.")

@app.get("/")
def ruta_principal():
    return {"mensaje": "¡Bienvenido al motor central de PLACEHOLDER!"}

@app.post("/nuevo_paciente")
def registrar_paciente(paciente: models.Paciente):
    conexion = database.conectar_base_datos()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "INSERT INTO paciente (nombre, rut, fecha_nacimiento) VALUES (?, ?, ?)",
            (paciente.nombre, paciente.rut, paciente.fecha_nacimiento)
        )
        conexion.commit() 
        nuevo_id = cursor.lastrowid 
        return {"mensaje": "Paciente registrado exitosamente", "paciente_id": nuevo_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al registrar: {e}")
    finally:
        conexion.close()

@app.get("/pacientes")
def listar_pacientes():
    """
    Ruta para listar todos los pacientes registrados en nuestra base de datos.
    """
    conexion = database.conectar_base_datos()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, rut, fecha_nacimiento FROM paciente")
    pacientes = []
    # Explicación: Iteramos sobre las filas devueltas por SQL y armamos diccionarios.
    for fila in cursor.fetchall():
        pacientes.append({
            "id": fila[0],
            "nombre": fila[1],
            "rut": fila[2],
            "fecha_nacimiento": fila[3]
        })
    conexion.close()
    return pacientes

@app.get("/historial/{paciente_id}")
def obtener_historial_paciente(paciente_id: int):
    """
    Recupera todo el historial clínico (repositorio soberano) de un paciente.
    """
    conexion = database.conectar_base_datos()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, paciente_id, tipo_recurso, contenido_fhir, fecha_registro FROM historial_clinico WHERE paciente_id = ?",
        (paciente_id,)
    )
    historial = []
    for fila in cursor.fetchall():
        historial.append({
            "id": fila[0],
            "paciente_id": fila[1],
            "tipo_recurso": fila[2],
            "contenido_fhir": fila[3],
            "fecha_registro": fila[4]
        })
    conexion.close()
    return historial

@app.post("/procesar_documento/{paciente_id}")
def procesar_documento_medico(paciente_id: int, documento: DocumentoBruto):
    fhir_json = ai_engine.estructurar_como_fhir(documento.texto)
    conexion = database.conectar_base_datos()
    cursor = conexion.cursor()
    fecha_hoy = datetime.date.today().isoformat()
    cursor.execute(
        "INSERT INTO historial_clinico (paciente_id, tipo_recurso, contenido_fhir, fecha_registro) VALUES (?, ?, ?, ?)",
        (paciente_id, "Observation", fhir_json, fecha_hoy)
    )
    conexion.commit()
    conexion.close()
    return {"mensaje": "Documento procesado y encriptado en estándar FHIR", "fhir": fhir_json}

@app.get("/proyecciones/{paciente_id}")
def proyecciones_gemelo_digital(paciente_id: int):
    """
    Toma TODO el historial del paciente y le pide a DeepSeek que genere 
    proyecciones preventivas y alertas de contraindicaciones.
    """
    historial = obtener_historial_paciente(paciente_id)
    if not historial:
        return {"proyeccion": "Aún no hay suficientes datos clínicos para generar un análisis del gemelo digital."}
    
    # Explicación: Convertimos la lista de historial a un texto largo para que la IA lo lea.
    historial_texto = str(historial)
    
    # Llamamos a nuestro nuevo motor de proyecciones
    analisis = ai_engine.generar_proyecciones(historial_texto)
    return {"proyeccion": analisis}

@app.post("/traducir_diagnostico")
def traducir_lenguaje_medico(diagnostico: TextoMedico):
    traduccion = ai_engine.traducir_a_lenguaje_paciente(diagnostico.texto_tecnico)
    return {"traduccion_amigable": traduccion}

@app.delete("/eliminar_paciente/{paciente_id}")
def borrar_perfil(paciente_id: int):
    """
    Implementación del Derecho al Olvido (Soberanía Digital).
    Borra de forma permanente los datos del usuario.
    """
    conexion = database.conectar_base_datos()
    cursor = conexion.cursor()
    
    try:
        # Explicación: Integridad Referencial.
        # En SQLite, no deberíamos borrar un "Paciente" si aún tiene "Registros Clínicos" asociados.
        # Quedarían datos huérfanos sin dueño. Por eso, PRIMERO borramos su historial.
        cursor.execute("DELETE FROM historial_clinico WHERE paciente_id = ?", (paciente_id,))
        
        # Explicación: Una vez que su historial está limpio, borramos al paciente.
        cursor.execute("DELETE FROM paciente WHERE id = ?", (paciente_id,))
        
        conexion.commit()
        return {"mensaje": "Perfil y datos eliminados permanentemente."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al eliminar el perfil: {e}")
    finally:
        conexion.close()

import json

@app.post("/registrar_signos/{paciente_id}")
def guardar_signos(paciente_id: int, signos: models.SignosVitales):
    """
    Recibe el ingreso manual de signos vitales y los guarda estructurados.
    """
    # Explicación: Creamos un diccionario simple estructurado (emulando FHIR)
    # y lo convertimos a formato de texto (JSON) para guardarlo en la base de datos.
    estructura_fhir = {
        "resourceType": "Observation",
        "category": "Vital Signs",
        "effectiveDateTime": f"{signos.fecha}T{signos.hora}",
        "components": [
            {"type": "Weight", "value": signos.peso, "unit": "kg"},
            {"type": "Height", "value": signos.altura, "unit": "m"},
            {"type": "HeartRate", "value": signos.ritmo_cardiaco, "unit": "bpm"}
        ]
    }
    
    # json.dumps convierte el diccionario de Python en texto.
    contenido_fhir_texto = json.dumps(estructura_fhir)
    
    conexion = database.conectar_base_datos()
    cursor = conexion.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO historial_clinico (paciente_id, tipo_recurso, contenido_fhir, fecha_registro) VALUES (?, ?, ?, ?)",
            (paciente_id, "Observation (Vitales)", contenido_fhir_texto, signos.fecha)
        )
        conexion.commit()
        return {"mensaje": "Signos vitales guardados exitosamente en el repositorio."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al guardar signos: {e}")
    finally:
        conexion.close()
