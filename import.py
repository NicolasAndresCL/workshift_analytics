import sqlite3
import os

DB_NAME = "workshift.db"

def migrar_bd(db_name):
    if not os.path.exists(db_name):
        print("No existe la base de datos.")
        return

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Crear tabla nueva con esquema limpio
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Registro_nuevo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Fecha TEXT,
            Proyecto TEXT,
            Tarea TEXT,
            Duracion TEXT
        )
    """)

    # Revisar columnas de la tabla vieja
    cursor.execute("PRAGMA table_info(Registro)")
    columnas = [col[1] for col in cursor.fetchall()]
    print("Columnas detectadas en Registro:", columnas)

    # Copiar datos según columnas disponibles
    if all(c in columnas for c in ["Fecha","Proyecto","Tarea","Duracion"]):
        cursor.execute("""
            INSERT INTO Registro_nuevo (Fecha, Proyecto, Tarea, Duracion)
            SELECT Fecha, Proyecto, Tarea, Duracion
            FROM Registro
        """)
    else:
        print("La tabla antigua no tiene las columnas esperadas.")

    # Contar filas antes y después
    cursor.execute("SELECT COUNT(*) FROM Registro")
    filas_viejas = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Registro_nuevo")
    filas_nuevas = cursor.fetchone()[0]
    print(f"Filas antes: {filas_viejas}, después: {filas_nuevas}")

    # Eliminar tabla antigua y renombrar
    cursor.execute("DROP TABLE Registro")
    cursor.execute("ALTER TABLE Registro_nuevo RENAME TO Registro")

    conn.commit()
    conn.close()
    print("Migración completada correctamente.")

if __name__ == "__main__":
    migrar_bd(DB_NAME)
