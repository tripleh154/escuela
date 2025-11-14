import os
import pyodbc
from flask import Flask, jsonify, request

app = Flask(__name__)

# --- Variables de Entorno Requeridas ---
# Render leerá estas variables que configures en el Dashboard
SERVER = os.getenv('DB_SERVER')
DATABASE = os.getenv('DB_DATABASE')
USERNAME = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')

# --- Cadena de Conexión ---
# Utilizamos el controlador ODBC para SQL Server
DRIVER = '{ODBC Driver 17 for SQL Server}'

def get_db_connection():
    """Establece y retorna una conexión a Azure SQL Database."""
    if not all([SERVER, DATABASE, USERNAME, PASSWORD]):
        # Esto ayudará a diagnosticar si faltan variables de entorno
        raise ValueError("Faltan variables de entorno de la base de datos (DB_SERVER, DB_DATABASE, DB_USER, DB_PASSWORD)")

    connection_string = (
        f'DRIVER={DRIVER};'
        f'SERVER=tcp:{SERVER},1433;'
        f'DATABASE={DATABASE};'
        f'UID={USERNAME};'
        f'PWD={PASSWORD};'
        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    )
    
    # Intenta establecer la conexión
    return pyodbc.connect(connection_string)

@app.route('/')
def home():
    """Ruta de salud simple para verificar que la API está viva."""
    return jsonify({"message": "API de Alumnos en Render está funcionando."}), 200

@app.route('/alumnos', methods=['GET'])
def listar_alumnos():
    """Obtiene y lista todos los alumnos de la tabla."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ejecuta la consulta
        cursor.execute("SELECT id, nombre, apellido_paterno, apellido_materno FROM Alumnos")
        
        # Obtiene los resultados y los nombres de las columnas
        column_names = [column[0] for column in cursor.description]
        alumnos = [dict(zip(column_names, row)) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify(alumnos), 200

    except pyodbc.Error as ex:
        # Captura errores específicos de la base de datos
        return jsonify({"error": f"Error de base de datos: {ex}"}), 500
    except ValueError as ex:
        # Captura el error de variables de entorno
        return jsonify({"error": str(ex)}), 500
    except Exception as ex:
        # Captura cualquier otro error
        return jsonify({"error": f"Error inesperado: {ex}"}), 500

if __name__ == '__main__':
    # Nota: Render usará un servidor WSGI (como Gunicorn) para ejecutar la app, 
    # pero este bloque es útil para pruebas locales.
    # El puerto 10000 es el que Render usa por defecto, pero Gunicorn lo manejará.
    app.run(host='0.0.0.0', port=10000)