#ventana del rol Administrador: su ventana con menu lateral, el
#historial de ventas, el listado de usuarios registrados y la gestion de
#roles crear usuarios y cambiar su rol.
from Librerias import *
import Librerias
from funciones_compartidas import maximizar_ventana, limpiar_pantalla, cerrar_sesion
from Ventana_librero import comentarios

# Misma paleta de colores que usan la mayoria de ventanas
COLOR_FONDO = "#F4EFE6"
COLOR_TARJETA = "#FFFDF8"
COLOR_SOMBRA = "#DCCFB4"
COLOR_BORDE = "#D8C9A8"
COLOR_TEXTO = "#3E2B1F"
COLOR_TEXTO_SUAVE = "#8A7864"
COLOR_VERDE = "#216300"
COLOR_VERDE_HOVER = "#184A00"
COLOR_VERDE_OSCURO = "#153F00"   # verde mas oscuro, para la tarjeta que agrupa el menu
COLOR_MARRON = "#123D02"         # verde bosque oscuro para botones secundarios (antes era marron)
COLOR_MARRON_HOVER = "#0A2601"
COLOR_ERROR = "#8B3A3A"          # terracota calido para el boton de cerrar sesion
COLOR_ERROR_HOVER = "#6E2C2C"
COLOR_FILA_PAR = COLOR_TARJETA
COLOR_FILA_IMPAR = "#EFE6D3"     # crema un poco mas oscuro, para el rayado tipo cebra de las tablas

def estilizar_tabla_ttk():
    #encabezado verde con texto blanco, filas mas altas Se llama una vez al abrir la
    #ventana del administrador.
    estilo = ttk.Style()
    estilo.theme_use("clam")  # el tema por defecto de Windows no deja personalizar colores
    estilo.configure("Treeview", background=COLOR_TARJETA, fieldbackground=COLOR_TARJETA, foreground=COLOR_TEXTO, rowheight=32, font=("Arial", 10), borderwidth=0)
    estilo.configure("Treeview.Heading", background=COLOR_VERDE, foreground="white", font=("Arial", 10, "bold"), borderwidth=0, relief="flat")
    estilo.map("Treeview.Heading", background=[("active", COLOR_VERDE_HOVER)])
    estilo.map("Treeview", background=[("selected", COLOR_BORDE)], foreground=[("selected", COLOR_TEXTO)])

def registro():
    screen2 = ctk.CTkToplevel(Librerias.screen)
    screen2.title("REGISTRO")
    screen2.configure(fg_color=COLOR_FONDO)
    screen2.resizable(True, True)
    # maximizar con after() para evitar el error de minimizado.
    screen2.after(200, lambda: maximizar_ventana(screen2))

    frame_contenedor2 = ctk.CTkFrame(screen2, fg_color=COLOR_FONDO, corner_radius=0)
    frame_contenedor2.pack(fill=BOTH, expand=True)

    # Contenedor de tamaño fijo para superponer la "sombra" y la tarjeta
    contenedor_tarjeta2 = ctk.CTkFrame(frame_contenedor2, fg_color="transparent", corner_radius=0, width=420, height=440)
    contenedor_tarjeta2.place(relx=0.5, rely=0.5, anchor="center")

    sombra_tarjeta2 = ctk.CTkFrame(contenedor_tarjeta2, fg_color=COLOR_SOMBRA, corner_radius=22, width=380, height=400)
    sombra_tarjeta2.place(relx=0.5, rely=0.5, anchor="center")

    frame_registro = ctk.CTkFrame(
        contenedor_tarjeta2,
        fg_color=COLOR_TARJETA,
        corner_radius=22,
        border_width=1,
        border_color=COLOR_BORDE,
        width=380,
        height=400,
    )
    frame_registro.place(relx=0.5, rely=0.5, anchor="center")
    frame_registro.grid_columnconfigure(1, weight=1)
    
    def registrar():
        usuario = caja_nombre2.get()
        contraseña = caja_contraseña2.get()
        if usuario == "" or contraseña == "":
            messagebox.showwarning("¡ERROR!", "Por favor, llene todos los campos.")
            return
        try:
            conexion = sqlite3.connect("RegistroDeUsuarios.db")
            cursor = conexion.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS UsuariosBD (USUARIO TEXT PRIMARY KEY, PASSWORD TEXT, ROL TEXT DEFAULT 'usuario')")
            contraseña_encriptada = hashlib.sha256(contraseña.encode()).hexdigest()
            cursor.execute("INSERT INTO UsuariosBD VALUES (?,?,?)",(usuario, contraseña_encriptada,"usuario"))
            conexion.commit()
            messagebox.showinfo("Registro exitoso","Usuario Registrado con exito")
            screen2.destroy()
        except:
            messagebox.showinfo("Error","Los datos introducidos ya estan en uso ingrese otros   ")

    ctk.CTkLabel(
        frame_registro, text="📖 CREAR CUENTA",
        font=ctk.CTkFont(family="Georgia", size=24, weight="bold"),
        text_color=COLOR_VERDE,
    ).grid(row=0, column=1, padx=10, pady=(30, 25), sticky="snew")

    Label_nombre2 = ctk.CTkLabel(frame_registro, text="👤 Nombre de usuario", font=ctk.CTkFont(family="Arial", size=13), text_color=COLOR_TEXTO, anchor="w")
    Label_nombre2.grid(row=1,column=1,pady=(0, 4),padx=25,sticky="ew")

    caja_nombre2 = ctk.CTkEntry(frame_registro, font=ctk.CTkFont(family="Arial", size=13), height=40, corner_radius=8, border_color=COLOR_BORDE, fg_color="white", text_color=COLOR_TEXTO)
    caja_nombre2.grid(row=2,column=1,pady=(0, 16),padx=25,sticky="ew")

    Label_contraseña2 = ctk.CTkLabel(frame_registro, text="🔒 Contraseña", font=ctk.CTkFont(family="Arial", size=13), text_color=COLOR_TEXTO, anchor="w")
    Label_contraseña2.grid(row=3,column=1,pady=(0, 4),padx=25,sticky="ew")

    caja_contraseña2 = ctk.CTkEntry(frame_registro, show="*", font=ctk.CTkFont(family="Arial", size=13), height=40, corner_radius=8, border_color=COLOR_BORDE, fg_color="white", text_color=COLOR_TEXTO)
    caja_contraseña2.grid(row=4,column=1,pady=(0, 26),padx=25,sticky="ew")

    boton_registro2 = ctk.CTkButton(
        frame_registro, text="Registrar usuario", command=registrar,
        font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
        height=44, corner_radius=8, fg_color=COLOR_VERDE, hover_color=COLOR_VERDE_HOVER, text_color="white",
    )
    boton_registro2.grid(row=5,column=1,pady=(0, 30),padx=25,sticky="ew")


#muestra el historial completo de ventas registradas en la BD
def ventas_admin(frame_pantallas):
    limpiar_pantalla(frame_pantallas)
    ctk.CTkLabel(frame_pantallas, text="VENTAS REGISTRADAS", font=ctk.CTkFont(family="Times New Roman", size=16, weight="bold"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO).pack(anchor="w", padx=30, pady=15)

    tarjeta_tabla_ventas = ctk.CTkFrame(frame_pantallas, fg_color=COLOR_TARJETA, corner_radius=14, border_width=1, border_color=COLOR_BORDE)
    tarjeta_tabla_ventas.pack(fill=BOTH, expand=True, padx=30, pady=(0, 20))

    frame_tabla_ventas = tk.Frame(tarjeta_tabla_ventas, bg=COLOR_TARJETA)
    frame_tabla_ventas.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

    columnas_ventas = ("id", "usuario", "libro", "cantidad", "precio", "total", "pasillo", "fecha")
    tabla_v = ttk.Treeview(frame_tabla_ventas, columns=columnas_ventas, show="headings")

    tabla_v.heading("id", text="ID")
    tabla_v.heading("usuario", text="Usuario")
    tabla_v.heading("libro", text="Libro")
    tabla_v.heading("cantidad", text="Cantidad")
    tabla_v.heading("precio", text="Precio Unit.")
    tabla_v.heading("total", text="Total")
    tabla_v.heading("pasillo", text="Pasillo de retiro")
    tabla_v.heading("fecha", text="Fecha")

    tabla_v.column("id", width=50, anchor="center")
    tabla_v.column("usuario", width=100, anchor="w")
    tabla_v.column("libro", width=180, anchor="w")
    tabla_v.column("cantidad", width=70, anchor="center")
    tabla_v.column("precio", width=90, anchor="e")
    tabla_v.column("total", width=90, anchor="e")
    tabla_v.column("pasillo", width=120, anchor="center")
    tabla_v.column("fecha", width=140, anchor="center")

    tabla_v.tag_configure("par", background=COLOR_FILA_PAR)
    tabla_v.tag_configure("impar", background=COLOR_FILA_IMPAR)

    scrollbar_v = ttk.Scrollbar(frame_tabla_ventas, orient=tk.VERTICAL, command=tabla_v.yview)
    tabla_v.configure(yscrollcommand=scrollbar_v.set)

    tabla_v.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)

    try:
        conexion = sqlite3.connect("VentaLibros.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT IDV, USUARIO, TITULO, CANTIDAD, PRECIO_UNITARIO, TOTAL, PASILLO, FECHA FROM VENTAS ORDER BY IDV DESC")
        registros_ventas = cursor.fetchall()
        conexion.close()

        for indice, fila in enumerate(registros_ventas):
            id_v, usuario_v, titulo_v, cantidad_v, precio_v, total_v, pasillo_v, fecha_v = fila
            etiqueta_fila = "par" if indice % 2 == 0 else "impar"
            tabla_v.insert("", tk.END, values=(id_v, usuario_v, titulo_v, cantidad_v, f"${precio_v:.2f}", f"${total_v:.2f}", f"Pasillo {pasillo_v}", fecha_v), tags=(etiqueta_fila,))

        if not registros_ventas:
            ctk.CTkLabel(frame_pantallas, text="No se han registrado ventas todavía.", font=ctk.CTkFont(family="Arial", size=11, slant="italic"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO_SUAVE).pack(pady=20)
    except:
        messagebox.showerror("Error", "Ha ocurrido un error, No se pudieron cargar las ventas")

#muestra el total ganado por mes y por libro, en 2 frames lado a lado
def ventas_por_mes(frame_pantallas):
    limpiar_pantalla(frame_pantallas)
    ctk.CTkLabel(frame_pantallas, text="VENTAS POR MES", font=ctk.CTkFont(family="Times New Roman", size=16, weight="bold"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO).pack(anchor="w", padx=30, pady=15)

    # Traduce el numero de mes ("01", "02"...) que devuelve strftime a un nombre legible
    nombres_mes = {
        "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
        "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
        "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre",
    }

    # Contenedor con los 2 frames lado a lado: izquierda el total por mes,
    # derecha el total por libro. Ambas columnas se reparten el mismo ancho.
    frame_resumenes = ctk.CTkFrame(frame_pantallas, fg_color=COLOR_FONDO, corner_radius=0)
    frame_resumenes.pack(fill=BOTH, expand=True, padx=30, pady=(0, 20))
    frame_resumenes.columnconfigure(0, weight=1)
    frame_resumenes.columnconfigure(1, weight=1)
    frame_resumenes.rowconfigure(1, weight=1)

    #Frame izquierdo: total ganado por mes
    ctk.CTkLabel(frame_resumenes, text="📆 Total por Mes", font=ctk.CTkFont(family="Arial", size=13, weight="bold"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO).grid(row=0, column=0, sticky="w", pady=(0, 8), padx=(0, 10))

    tarjeta_tabla_mes = ctk.CTkFrame(frame_resumenes, fg_color=COLOR_TARJETA, corner_radius=14, border_width=1, border_color=COLOR_BORDE)
    tarjeta_tabla_mes.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

    frame_tabla_mes = tk.Frame(tarjeta_tabla_mes, bg=COLOR_TARJETA)
    frame_tabla_mes.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

    columnas_mes = ("mes", "cantidad", "total")
    tabla_m = ttk.Treeview(frame_tabla_mes, columns=columnas_mes, show="headings")

    tabla_m.heading("mes", text="Mes")
    tabla_m.heading("cantidad", text="Ventas")
    tabla_m.heading("total", text="Total Ganado")

    tabla_m.column("mes", width=130, anchor="w")
    tabla_m.column("cantidad", width=80, anchor="center")
    tabla_m.column("total", width=110, anchor="e")

    tabla_m.tag_configure("par", background=COLOR_FILA_PAR)
    tabla_m.tag_configure("impar", background=COLOR_FILA_IMPAR)

    scrollbar_m = ttk.Scrollbar(frame_tabla_mes, orient=tk.VERTICAL, command=tabla_m.yview)
    tabla_m.configure(yscrollcommand=scrollbar_m.set)

    tabla_m.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_m.pack(side=tk.RIGHT, fill=tk.Y)

    try:
        conexion = sqlite3.connect("VentaLibros.db")
        cursor = conexion.cursor()
        # strftime('%Y-%m', FECHA) agrupa todas las ventas de un mismo mes/año juntas,
        # y SUM(TOTAL) calcula lo ganado en ese grupo (lo que ya pagaron los clientes)
        cursor.execute("""
            SELECT strftime('%Y-%m', FECHA) AS periodo, COUNT(*) AS cantidad, SUM(TOTAL) AS total_mes
            FROM VENTAS
            GROUP BY periodo
            ORDER BY periodo DESC
        """)
        resumen_mensual = cursor.fetchall()
        conexion.close()

        total_general = 0
        for indice, fila in enumerate(resumen_mensual):
            periodo, cantidad_mes, total_mes = fila
            anio, mes_num = periodo.split("-")
            mes_legible = f"{nombres_mes.get(mes_num, mes_num)} {anio}"
            etiqueta_fila = "par" if indice % 2 == 0 else "impar"
            tabla_m.insert("", tk.END, values=(mes_legible, cantidad_mes, f"${total_mes:.2f}"), tags=(etiqueta_fila,))
            total_general += total_mes

        if not resumen_mensual:
            ctk.CTkLabel(frame_resumenes, text="No se han registrado ventas todavía.", font=ctk.CTkFont(family="Arial", size=11, slant="italic"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO_SUAVE).grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(8, 0))
        else:
            # Total acumulado de todos los meses juntos, debajo de su tabla
            ctk.CTkLabel(frame_resumenes, text=f"Total acumulado: ${total_general:.2f}", font=ctk.CTkFont(family="Arial", size=12, weight="bold"), fg_color=COLOR_FONDO, text_color=COLOR_VERDE).grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(8, 0))
    except:
        messagebox.showerror("Error", "Ha ocurrido un error, No se pudieron cargar las ventas por mes")

    #Frame derecho: total ganado por libro 
    ctk.CTkLabel(frame_resumenes, text="📚 Total por Libro", font=ctk.CTkFont(family="Arial", size=13, weight="bold"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO).grid(row=0, column=1, sticky="w", pady=(0, 8), padx=(10, 0))

    tarjeta_tabla_libros = ctk.CTkFrame(frame_resumenes, fg_color=COLOR_TARJETA, corner_radius=14, border_width=1, border_color=COLOR_BORDE)
    tarjeta_tabla_libros.grid(row=1, column=1, sticky="nsew", padx=(10, 0))

    frame_tabla_libros = tk.Frame(tarjeta_tabla_libros, bg=COLOR_TARJETA)
    frame_tabla_libros.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

    columnas_libros = ("libro", "unidades", "total")
    tabla_l = ttk.Treeview(frame_tabla_libros, columns=columnas_libros, show="headings")

    tabla_l.heading("libro", text="Libro")
    tabla_l.heading("unidades", text="Unidades")
    tabla_l.heading("total", text="Total Ganado")

    tabla_l.column("libro", width=180, anchor="w")
    tabla_l.column("unidades", width=80, anchor="center")
    tabla_l.column("total", width=110, anchor="e")

    tabla_l.tag_configure("par", background=COLOR_FILA_PAR)
    tabla_l.tag_configure("impar", background=COLOR_FILA_IMPAR)

    scrollbar_l = ttk.Scrollbar(frame_tabla_libros, orient=tk.VERTICAL, command=tabla_l.yview)
    tabla_l.configure(yscrollcommand=scrollbar_l.set)

    tabla_l.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_l.pack(side=tk.RIGHT, fill=tk.Y)

    try:
        conexion = sqlite3.connect("VentaLibros.db")
        cursor = conexion.cursor()
        # Se agrupa por TITULO porque es lo que ya se
        # guarda en cada venta y es lo que se le muestra al administrador;
        # SUM(CANTIDAD) suma todas las unidades vendidas de ese libro y
        # SUM(TOTAL) lo que se gano con el, sin importar en que mes fue.
        cursor.execute("""
            SELECT TITULO, SUM(CANTIDAD) AS unidades_totales, SUM(TOTAL) AS total_libro
            FROM VENTAS
            GROUP BY TITULO
            ORDER BY total_libro DESC
        """)
        resumen_libros = cursor.fetchall()
        conexion.close()

        for indice, fila in enumerate(resumen_libros):
            titulo_l, unidades_l, total_l = fila
            etiqueta_fila = "par" if indice % 2 == 0 else "impar"
            tabla_l.insert("", tk.END, values=(titulo_l, unidades_l, f"${total_l:.2f}"), tags=(etiqueta_fila,))

        if not resumen_libros:
            ctk.CTkLabel(frame_resumenes, text="Todavía no se ha vendido ningún libro.", font=ctk.CTkFont(family="Arial", size=11, slant="italic"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO_SUAVE).grid(row=2, column=1, sticky="w", padx=(10, 0), pady=(8, 0))
    except:
        messagebox.showerror("Error", "Ha ocurrido un error, No se pudieron cargar los libros vendidos")

#muestra el listado de usuarios registrados
def registros_admin(frame_pantallas):
    limpiar_pantalla(frame_pantallas)
    ctk.CTkLabel(frame_pantallas, text="USUARIOS REGISTRADOS", font=ctk.CTkFont(family="Times New Roman", size=16, weight="bold"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO).pack(anchor="w", padx=30, pady=15)

    tarjeta_tabla_reg = ctk.CTkFrame(frame_pantallas, fg_color=COLOR_TARJETA, corner_radius=14, border_width=1, border_color=COLOR_BORDE)
    tarjeta_tabla_reg.pack(fill=BOTH, expand=True, padx=30, pady=(0, 20))

    frame_tabla_reg = tk.Frame(tarjeta_tabla_reg, bg=COLOR_TARJETA)
    frame_tabla_reg.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

    columnas_reg = ("usuario", "rol")
    tabla_r = ttk.Treeview(frame_tabla_reg, columns=columnas_reg, show="headings")
    tabla_r.heading("usuario", text="Usuario")
    tabla_r.heading("rol", text="Rol")
    tabla_r.column("usuario", width=250, anchor="w")
    tabla_r.column("rol", width=180, anchor="center")

    tabla_r.tag_configure("par", background=COLOR_FILA_PAR)
    tabla_r.tag_configure("impar", background=COLOR_FILA_IMPAR)

    scrollbar_r = ttk.Scrollbar(frame_tabla_reg, orient=tk.VERTICAL, command=tabla_r.yview)
    tabla_r.configure(yscrollcommand=scrollbar_r.set)
    tabla_r.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_r.pack(side=tk.RIGHT, fill=tk.Y)

    try:
        conexion = sqlite3.connect("RegistroDeUsuarios.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT USUARIO, ROL FROM UsuariosBD ORDER BY USUARIO ASC")
        registros_usuarios = cursor.fetchall()
        conexion.close()

        for indice, fila in enumerate(registros_usuarios):
            usuario_r, rol_r = fila
            etiqueta_fila = "par" if indice % 2 == 0 else "impar"
            tabla_r.insert("", tk.END, values=(usuario_r, rol_r if rol_r else "usuario"), tags=(etiqueta_fila,))

        if not registros_usuarios:
            ctk.CTkLabel(frame_pantallas, text="No hay usuarios registrados todavía.", font=ctk.CTkFont(family="Arial", size=11, slant="italic"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO_SUAVE).pack(pady=20)
    except:
        messagebox.showerror("Error", "Ha ocurrido un error, No se pudieron cargar los usuarios")

#gestion de roles
#permite crear un usuario nuevo directamente eligiendo su rol y cambiar el rol de los usuarios ya existentes
def roles_admin(frame_pantallas):
    limpiar_pantalla(frame_pantallas)
    ctk.CTkLabel(frame_pantallas, text="GESTIÓN DE ROLES", font=ctk.CTkFont(family="Times New Roman", size=16, weight="bold"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO).pack(anchor="w", padx=30, pady=15)

    lista_roles_disponibles = ["Administrador", "Librero", "usuario"]

    #Seccion para añadir un usuario nuevo directamente desde el panel de administrador 
    frame_nuevo_usuario = ctk.CTkFrame(frame_pantallas, fg_color=COLOR_TARJETA, corner_radius=14, border_width=1, border_color=COLOR_BORDE)
    frame_nuevo_usuario.pack(fill=X, padx=30, pady=(0, 15))

    ctk.CTkLabel(frame_nuevo_usuario, text="Añadir Usuario Nuevo", font=ctk.CTkFont(family="Arial", size=12, weight="bold"), fg_color=COLOR_TARJETA, text_color=COLOR_TEXTO).grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(14, 10))

    ctk.CTkLabel(frame_nuevo_usuario, text="Usuario:", fg_color=COLOR_TARJETA, text_color=COLOR_TEXTO, font=ctk.CTkFont(family="Arial", size=10)).grid(row=1, column=0, padx=(15, 5), sticky="w")
    caja_usuario_nuevo = ctk.CTkEntry(frame_nuevo_usuario, font=ctk.CTkFont(family="Arial", size=10), width=180, height=32, corner_radius=8, border_color=COLOR_BORDE, fg_color="white", text_color=COLOR_TEXTO)
    caja_usuario_nuevo.grid(row=1, column=1, padx=(0, 15))

    ctk.CTkLabel(frame_nuevo_usuario, text="Contraseña:", fg_color=COLOR_TARJETA, text_color=COLOR_TEXTO, font=ctk.CTkFont(family="Arial", size=10)).grid(row=1, column=2, padx=(0, 5), sticky="w")
    caja_contraseña_nueva = ctk.CTkEntry(frame_nuevo_usuario, font=ctk.CTkFont(family="Arial", size=10), width=180, height=32, corner_radius=8, border_color=COLOR_BORDE, fg_color="white", text_color=COLOR_TEXTO, show="*")
    caja_contraseña_nueva.grid(row=1, column=3, padx=(0, 15))

    ctk.CTkLabel(frame_nuevo_usuario, text="Rol:", fg_color=COLOR_TARJETA, text_color=COLOR_TEXTO, font=ctk.CTkFont(family="Arial", size=10)).grid(row=2, column=0, padx=(15, 5), pady=(8, 14), sticky="w")
    combo_rol_nuevo = ctk.CTkComboBox(frame_nuevo_usuario, values=lista_roles_disponibles, width=180, fg_color="white", border_color=COLOR_BORDE, button_color="white", button_hover_color=COLOR_BORDE, dropdown_fg_color="white", text_color=COLOR_TEXTO)
    combo_rol_nuevo.set("usuario")
    combo_rol_nuevo.grid(row=2, column=1, pady=(8, 14), sticky="w")

    def crear_usuario():
        usuario_nuevo = caja_usuario_nuevo.get().strip()
        contraseña_nueva = caja_contraseña_nueva.get()
        rol_nuevo = combo_rol_nuevo.get()

        if usuario_nuevo == "" or contraseña_nueva == "":
            messagebox.showwarning("Campos incompletos", "Por favor llene el usuario y la contraseña.")
            return

        try:
            conexion = sqlite3.connect("RegistroDeUsuarios.db")
            cursor = conexion.cursor()
            contraseña_encriptada = hashlib.sha256(contraseña_nueva.encode()).hexdigest()
            cursor.execute("INSERT INTO UsuariosBD VALUES (?,?,?)", (usuario_nuevo, contraseña_encriptada, rol_nuevo))
            conexion.commit()
            conexion.close()
            messagebox.showinfo("Éxito", f"Usuario '{usuario_nuevo}' creado con el rol '{rol_nuevo}'.")
            roles_admin(frame_pantallas)  #refresca el panel para reflejar el nuevo usuario en la lista
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ese nombre de usuario ya existe.")
        except:
            messagebox.showerror("Error", "No se pudo crear el usuario.")

    ctk.CTkButton(frame_nuevo_usuario, text="+ Crear Usuario", fg_color=COLOR_VERDE, hover_color=COLOR_VERDE_HOVER, text_color="white", font=ctk.CTkFont(family="Arial", size=10, weight="bold"), corner_radius=8, command=crear_usuario).grid(row=2, column=3, pady=(8, 14), padx=(0, 15), sticky="ew")

    #Seccion con la lista de usuarios existentes donde se puede modificar el rol de cada uno
    ctk.CTkLabel(frame_pantallas, text="Usuarios Registrados", font=ctk.CTkFont(family="Arial", size=12, weight="bold"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO).pack(anchor="w", padx=30, pady=(5, 5))

    container_roles = ctk.CTkFrame(frame_pantallas, fg_color=COLOR_FONDO, corner_radius=0)
    container_roles.pack(fill=BOTH, expand=True, padx=30, pady=(0, 15))

    canvas_roles = tk.Canvas(container_roles, bg=COLOR_FONDO, highlightthickness=0)
    scrollbar_roles = ttk.Scrollbar(container_roles, orient=VERTICAL, command=canvas_roles.yview)
    scrollable_roles = tk.Frame(canvas_roles, bg=COLOR_FONDO)

    scrollable_roles.bind("<Configure>", lambda e: canvas_roles.configure(scrollregion=canvas_roles.bbox("all")))
    ventana_roles_id = canvas_roles.create_window((0, 0), window=scrollable_roles, anchor="nw")
    canvas_roles.bind("<Configure>", lambda e: canvas_roles.itemconfig(ventana_roles_id, width=e.width))
    canvas_roles.configure(yscrollcommand=scrollbar_roles.set)

    canvas_roles.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar_roles.pack(side=RIGHT, fill=Y)

    try:
        conexion = sqlite3.connect("RegistroDeUsuarios.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT USUARIO, ROL FROM UsuariosBD ORDER BY USUARIO ASC")
        usuarios_existentes = cursor.fetchall()
        conexion.close()

        if not usuarios_existentes:
            ctk.CTkLabel(scrollable_roles, text="No hay usuarios registrados todavía.", font=ctk.CTkFont(family="Arial", size=11, slant="italic"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO_SUAVE).pack(pady=20)

        for usuario_e, rol_e in usuarios_existentes:
            fila_usuario = ctk.CTkFrame(scrollable_roles, fg_color=COLOR_TARJETA, corner_radius=10, border_width=1, border_color=COLOR_BORDE)
            fila_usuario.pack(fill=X, pady=4, padx=5)

            ctk.CTkLabel(fila_usuario, text=usuario_e, font=ctk.CTkFont(family="Arial", size=10, weight="bold"), fg_color=COLOR_TARJETA, text_color=COLOR_TEXTO, width=180, anchor="w").pack(side=LEFT, padx=(15, 5), pady=10)

            combo_rol_actual = ctk.CTkComboBox(fila_usuario, values=lista_roles_disponibles, width=150, fg_color="white", border_color=COLOR_BORDE, button_color="white", button_hover_color=COLOR_BORDE, dropdown_fg_color="white", text_color=COLOR_TEXTO)
            combo_rol_actual.set(rol_e if rol_e else "usuario")
            combo_rol_actual.pack(side=LEFT, padx=5, pady=10)

            def guardar_rol(usuario_u=usuario_e, combo=combo_rol_actual):
                nuevo_rol = combo.get()
                try:
                    conexion = sqlite3.connect("RegistroDeUsuarios.db")
                    cursor = conexion.cursor()
                    cursor.execute("UPDATE UsuariosBD SET ROL = ? WHERE USUARIO = ?", (nuevo_rol, usuario_u))
                    conexion.commit()
                    conexion.close()
                    messagebox.showinfo("Éxito", f"El rol de '{usuario_u}' ha sido actualizado a '{nuevo_rol}'.")
                except:
                    messagebox.showerror("Error", "No se pudo actualizar el rol.")

            ctk.CTkButton(fila_usuario, text="Guardar Rol", fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text_color="white", font=ctk.CTkFont(family="Arial", size=9, weight="bold"), corner_radius=8, command=guardar_rol).pack(side=LEFT, padx=10, pady=10)
    except:
        messagebox.showerror("Error", "No se pudieron cargar los usuarios")

def ventana_admin():
    screen3 = ctk.CTkToplevel(Librerias.screen)
    screen3.title("LIBRERIA CAL - ADMINISTRADOR")
    screen3.configure(fg_color=COLOR_FONDO)
    screen3.after(200, lambda: maximizar_ventana(screen3))
    screen3.protocol("WM_DELETE_WINDOW", Librerias.screen.destroy) #si se destruye la top level tambien se destruye la ventana principal

    estilizar_tabla_ttk()

    frame_lateral = ctk.CTkFrame(screen3, fg_color=COLOR_VERDE, width=250, corner_radius=0)
    frame_lateral.pack(side=LEFT, fill=Y, pady=10, padx=10)
    frame_lateral.pack_propagate(False)
    frame_lateral.columnconfigure(0, weight=1)

    Label_titulo = ctk.CTkLabel(frame_lateral, text="📚 LIBRERIA CAL", fg_color=COLOR_VERDE_HOVER, text_color="white", font=ctk.CTkFont(family="Georgia", size=15, weight="bold"), corner_radius=10)
    Label_titulo.grid(row=0, column=0, pady=(14, 4), padx=14, sticky="nsew", ipady=12)

    etiqueta_saludo = ctk.CTkLabel(frame_lateral, text="👋 Panel de Administrador", fg_color=COLOR_VERDE, text_color="#DCEBD0", font=ctk.CTkFont(family="Arial", size=11, slant="italic"))
    etiqueta_saludo.grid(row=1, column=0, pady=(0, 14), padx=16, sticky="w")

    # Linea separadora sutil entre el encabezado y el menu de navegacion
    separador_menu = ctk.CTkFrame(frame_lateral, fg_color="#3A7A1B", height=1, corner_radius=0)
    separador_menu.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 14))

    # Tarjeta que agrupa los botones del menu, para que no queden
    # flotando sueltos directo sobre el verde de fondo.
    tarjeta_menu = ctk.CTkFrame(frame_lateral, fg_color=COLOR_VERDE_OSCURO, corner_radius=14)
    tarjeta_menu.grid(row=3, column=0, sticky="new", padx=14)
    tarjeta_menu.columnconfigure(0, weight=1)

    frame_pantallas = ctk.CTkFrame(screen3, fg_color=COLOR_FONDO, corner_radius=0)
    frame_pantallas.pack(side=RIGHT, fill=BOTH, expand=True) 

    Boton_gestion_libros = ctk.CTkButton(tarjeta_menu, anchor="w", text_color="white", fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text="💰  Ventas", command=lambda: ventas_admin(frame_pantallas), font=ctk.CTkFont(family="Arial", size=12, weight="bold"), corner_radius=10)
    Boton_gestion_libros.grid(row=0, column=0, pady=(10, 6), padx=10, sticky="snew", ipady=10)

    #reporte con el total ganado por mes y por libro
    Boton_ventas_mes = ctk.CTkButton(tarjeta_menu, anchor="w", text_color="white", fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text="📆  Ventas por Mes", command=lambda: ventas_por_mes(frame_pantallas), font=ctk.CTkFont(family="Arial", size=12, weight="bold"), corner_radius=10)
    Boton_ventas_mes.grid(row=1, column=0, pady=6, padx=10, sticky="snew", ipady=10)

    Boton_roles = ctk.CTkButton(tarjeta_menu, anchor="w", text_color="white", fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text="🛡️  Roles", command=lambda: roles_admin(frame_pantallas), font=ctk.CTkFont(family="Arial", size=12, weight="bold"), corner_radius=10)
    Boton_roles.grid(row=2, column=0, pady=6, padx=10, sticky="snew", ipady=10)

    Boton_Registros = ctk.CTkButton(tarjeta_menu, anchor="w", text_color="white", fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text="📋  Registros", command=lambda: registros_admin(frame_pantallas), font=ctk.CTkFont(family="Arial", size=12, weight="bold"), corner_radius=10)
    Boton_Registros.grid(row=3, column=0, pady=6, padx=10, sticky="snew", ipady=10)

    Boton_comentarios = ctk.CTkButton(tarjeta_menu, anchor="w", text_color="white", fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text="💬  Comentarios", command=lambda: comentarios(frame_pantallas), font=ctk.CTkFont(family="Arial", size=12, weight="bold"), corner_radius=10)
    Boton_comentarios.grid(row=4, column=0, pady=(6, 10), padx=10, sticky="snew", ipady=10)

    # Boton de cerrar sesion, separado del resto y empujado al fondo de la barra lateral
    frame_lateral.grid_rowconfigure(5, weight=1)
    Boton_cerrar_sesion = ctk.CTkButton(frame_lateral, anchor="w", text_color="white", fg_color=COLOR_ERROR, hover_color=COLOR_ERROR_HOVER, text="🚪  Cerrar sesión", command=lambda: cerrar_sesion(screen3), font=ctk.CTkFont(family="Arial", size=12, weight="bold"), corner_radius=10)
    Boton_cerrar_sesion.grid(row=5, column=0, pady=(20, 10), padx=14, sticky="sew")

    # Al entrar a la ventana del administrador, arranca mostrando el resumen de Ventas por Mes
    ventas_por_mes(frame_pantallas)