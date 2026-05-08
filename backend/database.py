import sqlite3

# Explicación: Importamos la librería sqlite3 que viene incluida en Python.
# Nos permite conectarnos y manejar una base de datos SQLite (un archivo local).

def conectar_base_datos():
    """
    Establece y devuelve una conexión a la base de datos local SQLite.
    """
    # Explicación: La función connect() abre el archivo de la base de datos.
    # Si el archivo 'repositorio_soberano.db' no existe, SQLite lo creará automáticamente.
    conexion = sqlite3.connect("repositorio_soberano.db")
    
    # Explicación: Devolvemos la conexión para que otras partes de nuestro programa 
    # (como el archivo main.py) puedan usarla.
    return conexion

def inicializar_base_datos():
    """
    Crea las tablas necesarias para nuestro repositorio soberano si es que aún no existen.
    """
    # Explicación: Usamos nuestra función para obtener la conexión a la base de datos.
    conexion = conectar_base_datos()
    
    # Explicación: Un "cursor" es como un asistente o puntero que nos permite 
    # ejecutar comandos SQL (el lenguaje de las bases de datos) dentro de nuestra conexión.
    cursor = conexion.cursor()
    
    # Explicación: Ejecutamos un comando SQL para crear una tabla llamada 'paciente'.
    # Usamos comillas triples (''' ''') en Python para poder escribir textos que ocupan varias líneas.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paciente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            rut TEXT UNIQUE NOT NULL,
            fecha_nacimiento TEXT
        )
    ''')
    
    # Explicación: Creamos otra tabla para el 'historial_clinico', donde guardaremos los datos médicos.
    # Usamos FOREIGN KEY (llave foránea) para relacionar cada registro clínico con un paciente específico.
    # El campo 'contenido_fhir' guardará la información en formato texto estructurado (JSON).
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial_clinico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            tipo_recurso TEXT, 
            contenido_fhir TEXT, 
            fecha_registro TEXT,
            FOREIGN KEY(paciente_id) REFERENCES paciente(id)
        )
    ''')
    
    # Explicación: 'commit' significa "confirmar". Usamos esto para guardar los cambios 
    # permanentemente en el archivo de la base de datos.
    conexion.commit()
    
    # Explicación: Siempre es una excelente práctica cerrar la conexión cuando terminamos de usarla,
    # así liberamos memoria y evitamos que el archivo quede bloqueado.
    conexion.close()

# Explicación: Esta condición comprueba si estamos ejecutando este archivo directamente.
# Si es así (por ejemplo, al escribir 'python database.py' en la consola), se ejecuta la función de abajo.
if __name__ == "__main__":
    inicializar_base_datos()
    print("¡Éxito! Base de datos 'repositorio_soberano.db' inicializada correctamente.")
