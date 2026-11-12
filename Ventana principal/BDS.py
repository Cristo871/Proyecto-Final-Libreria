#Todo lo relacionado a la base de datos SQLite del proyecto
#las tablas libros, ventas, comentarios y usuarios y el guardado de los
#reportes/comentarios que mandan los usuarios.
from Librerias import *

# Creacion de las BD
def tabla_comentarios():
    try:
        conexion = sqlite3.connect("VentaLibros.db")
        cursor = conexion.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS COMENTARIOS (
        IDC INTEGER PRIMARY KEY AUTOINCREMENT,
        USUARIO TEXT NOT NULL,
        COMENTARIO TEXT NOT NULL,
        FECHA TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conexion.commit()
        conexion.close()
    except:
        messagebox.showinfo("ERROR", "Error con la base de datos de ventas")

def tabla_ventas():
    try:
        conexion = sqlite3.connect("VentaLibros.db")
        cursor = conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS VENTAS (
                IDV INTEGER PRIMARY KEY AUTOINCREMENT,
                USUARIO TEXT NOT NULL,
                LIBRO_ID INTEGER NOT NULL,
                TITULO TEXT NOT NULL,
                CANTIDAD INTEGER NOT NULL DEFAULT 1,
                PRECIO_UNITARIO REAL NOT NULL,
                TOTAL REAL NOT NULL,
                PASILLO INTEGER NOT NULL DEFAULT 1,
                FECHA TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (LIBRO_ID) REFERENCES LibrosBD(ID)
            )
        """)

        try:
            cursor.execute("ALTER TABLE VENTAS ADD COLUMN PASILLO INTEGER NOT NULL DEFAULT 1")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE VENTAS DROP COLUMN DIRECCION_ENVIO")
        except sqlite3.OperationalError:
            pass
        conexion.commit()
        conexion.close()
    except:
        messagebox.showinfo("ERROR", "Error con la base de datos de ventas")

#BD del carrito
def tabla_carrito():
    try:
        conexion = sqlite3.connect("VentaLibros.db")
        cursor = conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CARRITO (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USUARIO TEXT NOT NULL,
                LIBRO_ID INTEGER NOT NULL,
                TITULO TEXT NOT NULL,
                PRECIO_UNITARIO REAL NOT NULL,
                CANTIDAD INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (LIBRO_ID) REFERENCES LibrosBD(ID)
            )
        """)
        conexion.commit()
        conexion.close()
    except:
        messagebox.showinfo("ERROR", "Error con la base de datos del carrito")

#bd de los usuarios
def tabla_usuarios():
    try:
        conexion = sqlite3.connect("RegistroDeUsuarios.db")
        cursor = conexion.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS UsuariosBD (USUARIO TEXT PRIMARY KEY, PASSWORD TEXT, ROL TEXT DEFAULT 'usuario')")

        #si no hay un administrador crea uno predeterminado
        cursor.execute("SELECT COUNT(*) FROM UsuariosBD WHERE ROL = 'Administrador'")
        hay_admin = cursor.fetchone()[0]
        if hay_admin == 0:
            contraseña_default = hashlib.sha256("123".encode()).hexdigest()
            cursor.execute("INSERT OR IGNORE INTO UsuariosBD VALUES (?, ?, ?)", ("Cristo", contraseña_default, "Administrador"))

        conexion.commit()
        conexion.close()
    except:
        messagebox.showinfo("ERROR", "Error con la base de datos de usuarios")

def bd_libros():
    try:
        conexion = sqlite3.connect("VentaLibros.db")
        cursor = conexion.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS LibrosBD (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                TITULO TEXT NOT NULL,
                AUTOR TEXT,
                IMAGEN BLOB,
                CATEGORIA TEXT DEFAULT '',
                PRECIO REAL DEFAULT 0.0,
                STOCK INTEGER DEFAULT 0
            )
        """)

        try:
            cursor.execute("ALTER TABLE LibrosBD ADD COLUMN SINOPSIS TEXT DEFAULT 'Sin sinopsis disponible.'")
        except sqlite3.OperationalError:
            pass
        conexion.commit()
        conexion.close()
    except:
        messagebox.showinfo("ERROR","Error con la base de datos")


#funcion para guardar el reporte/comentario
def Save_report(usuario, comentario):
    try:
        conexion = sqlite3.connect("VentaLibros.db")
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO COMENTARIOS (USUARIO, COMENTARIO) 
            VALUES (?, ?)
        """, (usuario, comentario))
        conexion.commit()
        conexion.close()
        return True
    except:
        messagebox.showerror("ERROR","Se a producido un error al enviar el comentario")
        return False