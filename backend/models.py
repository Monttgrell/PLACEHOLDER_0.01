from pydantic import BaseModel
from typing import Optional

# Explicación: Pydantic valida que los datos tengan el formato correcto.

class Paciente(BaseModel):
    """
    Molde para CREAR a un Paciente.
    """
    nombre: str  
    rut: str
    fecha_nacimiento: str

class PacienteRespuesta(Paciente):
    """
    Molde para DEVOLVER a un Paciente desde la base de datos al Frontend.
    Hereda de Paciente, pero le añade el ID único.
    """
    id: int
    
class RegistroClinico(BaseModel):
    """
    Molde para CREAR un registro en el historial clínico.
    """
    paciente_id: int  
    tipo_recurso: str 
    contenido_fhir: Optional[str] = None
    fecha_registro: str

class HistorialRespuesta(RegistroClinico):
    """
    Molde para DEVOLVER un registro clínico al Frontend.
    """
    id: int

class SignosVitales(BaseModel):
    """
    Molde para recibir el ingreso manual de signos vitales.
    """
    peso: float
    altura: float
    ritmo_cardiaco: int
    fecha: str
    hora: str
