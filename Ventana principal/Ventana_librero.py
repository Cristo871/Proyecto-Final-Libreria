#Pantallas del rol "Librero": su ventana con menu lateral, la gestion del
#inventario (listar, buscar, editar y eliminar libros), el formulario
#para anadir un libro nuevo y el panel de comentarios/reportes recibidos
from Librerias import *
import Librerias
from funciones_compartidas import maximizar_ventana, limpiar_pantalla, cerrar_sesion

# Paleta de colores
COLOR_FONDO = "#F4EFE6"
COLOR_TARJETA = "#FFFDF8"
COLOR_SOMBRA = "#DCCFB4"
COLOR_BORDE = "#D8C9A8"
COLOR_TEXTO = "#3E2B1F"
COLOR_TEXTO_SUAVE = "#8A7864"
COLOR_VERDE = "#216300"
COLOR_VERDE_HOVER = "#184A00"
COLOR_MARRON = "#123D02"        # verde bosque oscuro para botones secundarios (mismo tono que usa el admin)
COLOR_MARRON_HOVER = "#0A2601"
COLOR_ERROR = "#8B3A3A"         # terracota calido para eliminar/cerrar sesion
COLOR_ERROR_HOVER = "#6E2C2C"
COLOR_FILA_PAR = COLOR_TARJETA
COLOR_FILA_IMPAR = "#EFE6D3"    # crema un poco mas oscuro, rayado tipo cebra de las tablas

def estilizar_tabla_ttk_librero():
    #Mismo estilo que usa la ventana admin para las ttk.Treeview
    #encabezado verde con texto blanco, filas mas altas
    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure("Treeview", background=COLOR_TARJETA, fieldbackground=COLOR_TARJETA, foreground=COLOR_TEXTO, rowheight=32, font=("Arial", 10), borderwidth=0)
    estilo.configure("Treeview.Heading", background=COLOR_VERDE, foreground="white", font=("Arial", 10, "bold"), borderwidth=0, relief="flat")
    estilo.map("Treeview.Heading", background=[("active", COLOR_VERDE_HOVER)])
    estilo.map("Treeview", background=[("selected", COLOR_BORDE)], foreground=[("selected", COLOR_TEXTO)])

def gestion_libros(frame_pantallas, busqueda=""):
    limpiar_pantalla(frame_pantallas)
    
    frame_top = ctk.CTkFrame(frame_pantallas, fg_color=COLOR_FONDO, corner_radius=0)
    frame_top.pack(fill=X, padx=25, pady=15)
    
    ctk.CTkLabel(frame_top, text="GESTIÓN LIBROS", font=ctk.CTkFont(family="Times New Roman", size=16, weight="bold"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO).pack(side=LEFT)
    
    # Botón para añadir un libro directamente desde este panel
    btn_agregar = ctk.CTkButton(frame_top, text="+ Añadir Libro", fg_color=COLOR_VERDE, hover_color=COLOR_VERDE_HOVER, text_color="white", font=ctk.CTkFont(family="Arial", size=11, weight="bold"), command=lambda: ventana_añadir_libro(frame_pantallas), corner_radius=8)
    btn_agregar.pack(side=RIGHT)

    # Buscador por titulo o autor
    frame_busqueda = ctk.CTkFrame(frame_pantallas, fg_color=COLOR_FONDO, corner_radius=0)
    frame_busqueda.pack(fill=X, padx=25, pady=(0, 10))

    caja_busqueda = ctk.CTkEntry(frame_busqueda, font=ctk.CTkFont(family="Arial", size=11), width=320, height=34, corner_radius=8, border_color=COLOR_BORDE, fg_color="white", text_color=COLOR_TEXTO, placeholder_text="Buscar por título o autor...")
    caja_busqueda.pack(side=LEFT, padx=(0, 10))
    caja_busqueda.insert(0, busqueda)

    def ejecutar_busqueda(event=None):
        gestion_libros(frame_pantallas, caja_busqueda.get().strip())
    # Boton de busqueda
    ctk.CTkButton(frame_busqueda, text="🔍 Buscar", fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text_color="white", font=ctk.CTkFont(family="Arial", size=11, weight="bold"), command=ejecutar_busqueda, height=34, corner_radius=8).pack(side=LEFT)
    caja_busqueda.bind("<Return>", ejecutar_busqueda)
    if busqueda:
        ctk.CTkButton(frame_busqueda, text="Limpiar", fg_color=COLOR_TEXTO_SUAVE, hover_color=COLOR_TEXTO, text_color="white", font=ctk.CTkFont(family="Arial", size=11, weight="bold"), command=lambda: gestion_libros(frame_pantallas, ""), height=34, corner_radius=8).pack(side=LEFT, padx=(5, 0))

    # Frame del scroll de gestion del librero
    container = ctk.CTkFrame(frame_pantallas, fg_color=COLOR_FONDO, corner_radius=0)
    container.pack(fill=BOTH, expand=True, padx=25, pady=(0, 15))
    
    canvas = tk.Canvas(container, bg=COLOR_FONDO, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient=VERTICAL, command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=COLOR_FONDO)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    # el ancho base del lienzo
    ventana_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(ventana_id, width=e.width))
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)

    #Permite scrollear con la rueda del mouse desde cualquier parte de la pantalla
    def _scroll_gestion(evento):
        canvas.yview_scroll(int(-1 * (evento.delta / 120)), "units")
    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _scroll_gestion))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    try:
        conexion = sqlite3.connect("VentaLibros.db")
        cursor = conexion.cursor()
        if busqueda:
            Bus = '%' + busqueda + '%'
            cursor.execute("""SELECT ID, TITULO, AUTOR, CATEGORIA, PRECIO, STOCK, IMAGEN FROM LibrosBD WHERE TITULO LIKE ? OR AUTOR LIKE ? ORDER BY ID DESC""", (Bus, Bus))
        else:
            cursor.execute("SELECT ID, TITULO, AUTOR, CATEGORIA, PRECIO, STOCK, IMAGEN FROM LibrosBD ORDER BY ID DESC")
        libros = cursor.fetchall() #fetchall trae todas las filas que encontro en la ultima consulta y guarda los datos en la variable libros
        conexion.close()

        if not libros:
            texto_vacio = f"No hay libros que coincidan con '{busqueda}'." if busqueda else "El inventario está vacío."
            tk.Label(scrollable_frame, text=texto_vacio, font=("Arial", 11, "italic"), bg=COLOR_FONDO, fg=COLOR_TEXTO_SUAVE).pack(pady=40)
            return

        for indice_libro, libro in enumerate(libros):
            id_db, titulo_db, autor_db, cat_db, precio_db, stock_db, blob_db = libro
            
            #Fila principal 
            color_fila = COLOR_FILA_PAR if indice_libro % 2 == 0 else COLOR_FILA_IMPAR
            fila_frame = tk.Frame(scrollable_frame, bg=color_fila, highlightbackground=COLOR_BORDE, highlightthickness=1)
            fila_frame.pack(fill=X, pady=6, ipady=4, padx=5)
            
            # Configuramos pesos específicos en las columnas de la fila para que no se descuadre
            fila_frame.columnconfigure(0, weight=0, minsize=PORTADA_LISTA[0] + 20)
            fila_frame.columnconfigure(1, weight=1, minsize=280) # La info del texto se expande 
            fila_frame.columnconfigure(2, weight=0, minsize=120)
            fila_frame.columnconfigure(3, weight=0, minsize=110)
            
            # la portada tiene tamaño fijo para que sea consistente
            # Al tocar la portada se abre directamente la ventana de modificar el libro
            marco_foto = tk.Frame(fila_frame, width=PORTADA_LISTA[0], height=PORTADA_LISTA[1], bg=COLOR_VERDE, cursor="hand2")
            marco_foto.pack_propagate(False)
            marco_foto.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
            marco_foto.bind("<Button-1>", lambda e, id_l=id_db: ventana_edicion(id_l, frame_pantallas)) #e =  evento #si toca la pantalla se mandara directamente a la funcion ventana_édicion
            lbl_foto = tk.Label(marco_foto, bg=COLOR_VERDE, cursor="hand2")
            lbl_foto.pack(expand=True, fill=BOTH)
            lbl_foto.bind("<Button-1>", lambda e, id_l=id_db: ventana_edicion(id_l, frame_pantallas))
            #tamaño de las imagenes/portadas
            if blob_db:
                try:
                    imagen = io.BytesIO(blob_db) #convierte las imagenes de bytes a codigo binario para que la maquina pueda leerlo
                    img_pil = Image.open(imagen).resize(PORTADA_LISTA) #tamaño fijo desde el inicio
                    img_tk = ImageTk.PhotoImage(img_pil)
                    lbl_foto.config(image=img_tk)
                    lista_imagenes_tk.append(img_tk) #abre la variable de imagenes
                except:
                    lbl_foto.config(text="Err\nImg", fg="white", font=("Arial", 8))
            else:
                lbl_foto.config(text="Sin\nFoto", fg="white", font=("Arial", 8))
                
            # frames de Textos
            info_frame = tk.Frame(fila_frame, bg=color_fila)
            info_frame.grid(row=0, column=1, padx=10, sticky="ew")
            
            # longitud del string (texto) para evitar roturas visuales
            titulo_corto = titulo_db if len(titulo_db) <= 32 else titulo_db[:29] + "..."
            autor_corto = autor_db if len(autor_db) <= 38 else autor_db[:35] + "..."
            genero_corto = cat_db if len(cat_db) <= 45 else cat_db[:42] + "..."
            
            tk.Label(info_frame, text=titulo_corto, font=("Arial", 11, "bold"), bg=color_fila, fg=COLOR_TEXTO, anchor="w").pack(fill=X, pady=(2, 0))
            tk.Label(info_frame, text=f"Autor: {autor_corto}", font=("Arial", 9), bg=color_fila, fg=COLOR_TEXTO_SUAVE, anchor="w").pack(fill=X)
            tk.Label(info_frame, text=f"Géneros: {genero_corto}", font=("Arial", 8, "italic"), bg=color_fila, fg=COLOR_TEXTO_SUAVE, anchor="w").pack(fill=X)
            
            #frames del precio y stock
            datos_frame = tk.Frame(fila_frame, bg=color_fila)
            datos_frame.grid(row=0, column=2, padx=5, sticky="ns")
            
            tk.Label(datos_frame, text=f"Precio: ${precio_db:.2f}", font=("Arial", 10, "bold"), bg=color_fila, fg=COLOR_VERDE, anchor="w").pack(fill=X, pady=(12, 0))
            
            color_stock = COLOR_ERROR if stock_db <= 3 else COLOR_TEXTO
            tk.Label(datos_frame, text=f"Stock: {stock_db} u.", font=("Arial", 9, "bold"), bg=color_fila, fg=color_stock, anchor="w").pack(fill=X)

            # frame de editar y eliminar
            acciones_frame = tk.Frame(fila_frame, bg=color_fila)
            acciones_frame.grid(row=0, column=3, padx=10, sticky="e")
            
            # Botón Editar 
            btn_editar = ctk.CTkButton(acciones_frame, text="✏️ Editar", font=ctk.CTkFont(family="Arial", size=10, weight="bold"), fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text_color="white", width=90, height=26, corner_radius=6, command=lambda id_l=id_db: ventana_edicion(id_l, frame_pantallas))
            btn_editar.pack(side=TOP, pady=3)
            
            # Botón Eliminar 
            btn_eliminar = ctk.CTkButton(acciones_frame, text="🗑️ Borrar", font=ctk.CTkFont(family="Arial", size=10, weight="bold"), fg_color=COLOR_ERROR, hover_color=COLOR_ERROR_HOVER, text_color="white", width=90, height=26, corner_radius=6, command=lambda id_l=id_db, t=titulo_db: confirmar_eliminacion(id_l, t, frame_pantallas))
            btn_eliminar.pack(side=TOP, pady=3)
            
    except:
        messagebox.showerror("Error", "No se pudieron cargar los libros")

#def para el registro de los comentarios del administrador
def comentarios(frame_pantallas):
    limpiar_pantalla(frame_pantallas)

    ctk.CTkLabel(frame_pantallas, text="COMENTARIOS", font=ctk.CTkFont(family="Times New Roman", size=16, weight="bold"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO).pack(anchor="w", padx=30, pady=15)

    #tarjeta con borde para la tabla
    tarjeta_tabla = ctk.CTkFrame(frame_pantallas, fg_color=COLOR_TARJETA, corner_radius=14, border_width=1, border_color=COLOR_BORDE)
    tarjeta_tabla.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))

    #frame para la tabla y su barra de desplazamiento
    frame_tabla = tk.Frame(tarjeta_tabla, bg=COLOR_TARJETA)
    frame_tabla.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)
    
    # Configurar las columnas de la tabla visual
    columnas = ("id", "usuario", "comentario", "fecha")


    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

    # Definir los nombres de las columnas
    tabla.heading("id", text="ID")
    tabla.heading("usuario", text="Usuario")
    tabla.heading("comentario", text="Comentarios")
    tabla.heading("fecha", text="Fecha y Hora")
    
    # Ajustar el ancho y alineación de las columnas
    tabla.column("id", width=50, anchor="center")
    tabla.column("usuario", width=120, anchor="w")
    tabla.column("comentario", width=350, anchor="w")
    tabla.column("fecha", width=150, anchor="center")

    # Filas alternadas
    tabla.tag_configure("par", background=COLOR_FILA_PAR)
    tabla.tag_configure("impar", background=COLOR_FILA_IMPAR)
    
    # barra de desplazamiento (Scrollbar)
    scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=tabla.yview)
    tabla.configure(yscrollcommand=scrollbar.set)
    
    tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    #Abir la bd
    try:
        conexion = sqlite3.connect("VentaLibros.db")
        cursor = conexion.cursor()
        
        # Traemos los comentarios ordenados del más reciente al más antiguo
        cursor.execute("SELECT IDC, USUARIO, COMENTARIO, FECHA FROM COMENTARIOS ORDER BY IDC DESC")
        registros = cursor.fetchall()
        conexion.close()
        
        # Insertar los datos dentro de la tabla
        for indice, fila in enumerate(registros):
            etiqueta_fila = "par" if indice % 2 == 0 else "impar"
            tabla.insert("", tk.END, values=fila, tags=(etiqueta_fila,))
            
        if not registros:
            ctk.CTkLabel(frame_pantallas, text="No hay reportes de usuarios todavía.", font=ctk.CTkFont(family="Arial", size=11, slant="italic"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO_SUAVE).pack(pady=20)
            
    except:
        messagebox.showerror("Error","Ah ocurrido un error, No se pudieron cargar los comentarios")

#eliminacion del libro
def confirmar_eliminacion(id_libro, titulo, frame_pantallas):
    respuesta = messagebox.askyesno("Confirmar eliminación", f"¿Estás seguro de que deseas eliminar permanentemente el libro:\n'{titulo}'?")
    if respuesta:
        try:
            conexion = sqlite3.connect("VentaLibros.db")
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM LibrosBD WHERE ID = ?", (id_libro,))
            conexion.commit()
            conexion.close()
            messagebox.showinfo("Éxito", "Libro eliminado correctamente.")
            gestion_libros(frame_pantallas) # Refresca el frame al termina la eliminacion para que se refleje el cambio
        except:
            messagebox.showerror("Error", "No se pudo eliminar el registro")


# ventana para la editar/modificar un libro
def ventana_edicion(id_libro, frame_pantallas):
    # Crear la ventana flotante para la edición del libro
    edicion = ctk.CTkToplevel()
    edicion.title("MODIFICAR LIBRO")
    edicion.configure(fg_color=COLOR_FONDO)
    # Se usa after para evitar que se minimice
    edicion.after(200, lambda: maximizar_ventana(edicion))
    edicion.grab_set() # Da prioridad absoluta a esta ventana

    # Contenedor con scroll para que el formulario
    contenedor_scroll = ctk.CTkFrame(edicion, fg_color=COLOR_FONDO, corner_radius=0)
    contenedor_scroll.pack(fill=BOTH, expand=True)
    canvas_edicion = tk.Canvas(contenedor_scroll, bg=COLOR_FONDO, highlightthickness=0)
    scrollbar_edicion = ttk.Scrollbar(contenedor_scroll, orient=VERTICAL, command=canvas_edicion.yview)
    canvas_edicion.configure(yscrollcommand=scrollbar_edicion.set)
    canvas_edicion.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar_edicion.pack(side=RIGHT, fill=Y)

    # Permite scrollear con la rueda del mouse desde cualquier parte de la ventana
    def _scroll_edicion(evento):
        canvas_edicion.yview_scroll(int(-1 * (evento.delta / 120)), "units")
    canvas_edicion.bind("<Enter>", lambda e: canvas_edicion.bind_all("<MouseWheel>", _scroll_edicion))
    canvas_edicion.bind("<Leave>", lambda e: canvas_edicion.unbind_all("<MouseWheel>"))

    # Frame que siempre ocupa el ancho completo del canvas (mismo patrón que gestion_libros)
    frame_centrador_edicion = tk.Frame(canvas_edicion, bg=COLOR_FONDO)
    id_centrador_edicion = canvas_edicion.create_window((0, 0), window=frame_centrador_edicion, anchor="nw")
    canvas_edicion.bind("<Configure>", lambda e: canvas_edicion.itemconfig(id_centrador_edicion, width=e.width))
    frame_centrador_edicion.bind("<Configure>", lambda e: canvas_edicion.configure(scrollregion=canvas_edicion.bbox("all")))

    # Columnas "espaciadoras" a los lados para que la tarjeta blanca quede centrada
    frame_centrador_edicion.grid_columnconfigure(0, weight=1)
    frame_centrador_edicion.grid_columnconfigure(1, weight=0)
    frame_centrador_edicion.grid_columnconfigure(2, weight=1)

    # Tarjeta centrada donde esta el formulario
    contenido = ctk.CTkFrame(frame_centrador_edicion, fg_color=COLOR_TARJETA, corner_radius=18, border_width=1, border_color=COLOR_BORDE)
    contenido.grid(row=0, column=1, pady=25)
    contenido_interno = tk.Frame(contenido, bg=COLOR_TARJETA, padx=50, pady=30)
    contenido_interno.pack()
    contenido = contenido_interno  # a partir de aqui "contenido" sigue siendo el frame donde se colocan los campos, igual que antes

    img_blob_seleccionada = [b""] 
    referencia_preview = [None]
    lista_generos_disponibles = ["Fantasía", "Ciencia Ficción", "Terror", "Romance", "Drama", "Misterio", "Acción", "Aventura", "Suspenso", "Comedia"]
    generos_checkbuttons = {}

    # Cargar datos actuales desde la Base de Datos
    try:
        conexion = sqlite3.connect("VentaLibros.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT TITULO, AUTOR, CATEGORIA, PRECIO, STOCK, IMAGEN, SINOPSIS FROM LibrosBD WHERE ID = ?", (id_libro,))
        libro = cursor.fetchone()
        conexion.close()
    except:
        messagebox.showerror("Error", "No se pudieron cargar los datos")
        edicion.destroy()
        return

    if not libro:
        messagebox.showerror("Error", "Libro no encontrado.")
        edicion.destroy()
        return

    titulo_act, autor_act, cat_act, precio_act, stock_act, blob_act, sinopsis_act = libro
    img_blob_seleccionada[0] = blob_act if blob_act else b""

    # seleccion de la imagen
    def seleccionar_imagen():
        ruta_imagen = filedialog.askopenfilename(
            title="Seleccionar Portada del Libro",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif")] #formatos de archivos que puede cargar
        )
        if ruta_imagen:
            try:
                with open(ruta_imagen, 'rb') as archivo:
                    img_blob_seleccionada[0] = archivo.read()
                
                # Forzamos el tamaño estándar de portada
                img_pil = Image.open(ruta_imagen).resize(PORTADA_MODAL)
                img_tk = ImageTk.PhotoImage(img_pil)
                
                label_preview.config(image=img_tk, text="")
                referencia_preview[0] = img_tk 
                lista_imagenes_tk.append(img_tk)
                label_imagen_estado.config(text="Nueva imagen cargada correctamente", fg=COLOR_VERDE)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")

    def guardar_cambios():
        titulo = caja_titulo.get().strip()
        autor = caja_autor.get().strip()
        sinopsis = caja_sinopsis.get("1.0", tk.END).strip()
        if sinopsis == "":
            sinopsis = "Sin sinopsis disponible."
        blob_data = img_blob_seleccionada[0]

        generos_seleccionados = []
        for g, var in generos_checkbuttons.items():
            if var.get():
                generos_seleccionados.append(g)
        texto_categorias = ", ".join(generos_seleccionados) if generos_seleccionados else "General"

        try:
            precio = float(caja_precio.get() if caja_precio.get() else 0)
            stock = int(caja_stock.get() if caja_stock.get() else 0)
        except ValueError:
            messagebox.showwarning("Error de datos", "Se ha introducido un número erróneo.")
            return

        if titulo == "":
            messagebox.showwarning("Campos Incompletos", "El título del libro es obligatorio.")
            return

        try:
            conexion = sqlite3.connect("VentaLibros.db")
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE LibrosBD 
                SET TITULO=?, AUTOR=?, IMAGEN=?, CATEGORIA=?, PRECIO=?, STOCK=?, SINOPSIS=?
                WHERE ID=?
            """, (titulo, autor, blob_data, texto_categorias, precio, stock, sinopsis, id_libro))
            conexion.commit()
            conexion.close()

            messagebox.showinfo("Éxito", "Los cambios han sido guardados correctamente.")
            edicion.destroy()
            gestion_libros(frame_pantallas)  # Refresca el inventario en tiempo real
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al guardar: {e}")

    # interfaz de la ventana edicion/modificar/editar
    tk.Label(contenido, text=f"Modificando Libro ID: {id_libro}", font=("Arial", 16, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO).pack(pady=(0, 15))

    tk.Label(contenido, text="Título del Libro:", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 10)).pack(anchor="w", padx=30)
    caja_titulo = tk.Entry(contenido, width=75, font=("Arial", 11))
    caja_titulo.pack(pady=(2, 8), padx=30, fill=X, ipady=4)
    caja_titulo.insert(0, titulo_act)

    tk.Label(contenido, text="Autor:", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 10)).pack(anchor="w", padx=30)
    caja_autor = tk.Entry(contenido, width=75, font=("Arial", 11))
    caja_autor.pack(pady=(2, 8), padx=30, fill=X, ipady=4)
    caja_autor.insert(0, autor_act)

    tk.Label(contenido, text="Seleccione los Géneros aplicables:", font=("Arial", 10, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO).pack(anchor="w", padx=30, pady=(5, 2))
    frame_generos = tk.Frame(contenido, bg=COLOR_TARJETA)
    frame_generos.pack(anchor="w", padx=30, fill=X, pady=(0, 8))

    categorias_actuales = [c.strip() for c in cat_act.split(",")]
    # posiciona automaticamente la lista de generos que se guardaron
    for index, genero in enumerate(lista_generos_disponibles): 
        var_booleana = tk.BooleanVar()
        if genero in categorias_actuales:
            var_booleana.set(True)
        generos_checkbuttons[genero] = var_booleana
        casilla = tk.Checkbutton(frame_generos, text=genero, variable=var_booleana, font=("Arial", 9), bg=COLOR_TARJETA, fg=COLOR_TEXTO, activebackground=COLOR_TARJETA, selectcolor=COLOR_FONDO) #la casilla de la palomita para seleccionar el genero
        casilla.grid(row=index // 3, column=index % 3, sticky="w", padx=5, pady=2)

    tk.Label(contenido, text="Sinopsis del Libro:", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 10)).pack(anchor="w", padx=30, pady=(5, 0))
    caja_sinopsis = tk.Text(contenido, width=75, height=6, font=("Arial", 10))
    caja_sinopsis.pack(pady=(2, 8), padx=30, fill=X)
    caja_sinopsis.insert("1.0", sinopsis_act if sinopsis_act else "Sin sinopsis disponible.")

    # Precio y Stock en la misma fila
    frame_precio_stock = tk.Frame(contenido, bg=COLOR_TARJETA)
    frame_precio_stock.pack(fill=X, padx=30, pady=(0, 8))
    frame_precio_stock.columnconfigure(0, weight=1)
    frame_precio_stock.columnconfigure(1, weight=1)

    frame_col_precio = tk.Frame(frame_precio_stock, bg=COLOR_TARJETA)
    frame_col_precio.grid(row=0, column=0, sticky="ew", padx=(0, 8))
    tk.Label(frame_col_precio, text="Precio ($):", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 10)).pack(anchor="w")
    caja_precio = tk.Entry(frame_col_precio, font=("Arial", 11))
    caja_precio.pack(fill=X, ipady=4)
    caja_precio.insert(0, str(precio_act))

    frame_col_stock = tk.Frame(frame_precio_stock, bg=COLOR_TARJETA)
    frame_col_stock.grid(row=0, column=1, sticky="ew", padx=(8, 0))
    tk.Label(frame_col_stock, text="Unidades disponibles (Stock):", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 10)).pack(anchor="w")
    caja_stock = tk.Entry(frame_col_stock, font=("Arial", 11))
    caja_stock.pack(fill=X, ipady=4)
    caja_stock.insert(0, str(stock_act))

    # Portada e imagen
    tk.Label(contenido, text="Portada del libro:", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 10)).pack(anchor="w", padx=30, pady=(5, 4))
    frame_portada_edicion = tk.Frame(contenido, bg=COLOR_TARJETA)
    frame_portada_edicion.pack(padx=30, fill=X, pady=(0, 10))

    # marco del libro de la ventana que se muestra en la ventana editar
    marco_preview = tk.Frame(frame_portada_edicion, width=PORTADA_MODAL[0], height=PORTADA_MODAL[1], bg=COLOR_BORDE, bd=1, relief="sunken")
    marco_preview.pack_propagate(False)
    marco_preview.pack(side=LEFT, padx=(0, 20))

    label_preview = tk.Label(marco_preview, bg=COLOR_BORDE)
    label_preview.pack(expand=True, fill=tk.BOTH)

    frame_botones_imagen = tk.Frame(frame_portada_edicion, bg=COLOR_TARJETA)
    frame_botones_imagen.pack(side=LEFT, fill=X, expand=True, anchor="n")

    boton_foto = ctk.CTkButton(frame_botones_imagen, text="📁 Cambiar Imagen...", command=seleccionar_imagen, fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text_color="white", font=ctk.CTkFont(family="Arial", size=11, weight="bold"), corner_radius=8)
    boton_foto.pack(fill=X, ipady=2)

    label_imagen_estado = tk.Label(frame_botones_imagen, text="Imagen actual del sistema", fg=COLOR_TEXTO_SUAVE, font=("Arial", 9, "italic"), bg=COLOR_TARJETA)
    label_imagen_estado.pack(anchor="w", pady=(8, 0))

    if blob_act:
        try:
            imagen = io.BytesIO(blob_act)
            img_pil = Image.open(imagen).resize(PORTADA_MODAL)
            img_tk = ImageTk.PhotoImage(img_pil)
            label_preview.config(image=img_tk)
            referencia_preview[0] = img_tk
            lista_imagenes_tk.append(img_tk)
        except:
            label_preview.config(text="Error\nImagen", fg=COLOR_ERROR)
    else:
        label_preview.config(text="Sin\nImagen", fg=COLOR_TEXTO_SUAVE)

    # Botones en fila: Guardar y Cancelar
    frame_botones_finales = tk.Frame(contenido, bg=COLOR_TARJETA)
    frame_botones_finales.pack(fill=X, padx=30, pady=(10, 5))
    frame_botones_finales.columnconfigure(0, weight=2)
    frame_botones_finales.columnconfigure(1, weight=1)

    boton_guardar = ctk.CTkButton(frame_botones_finales, text="✔ GUARDAR CAMBIOS", command=guardar_cambios, fg_color=COLOR_VERDE, hover_color=COLOR_VERDE_HOVER, text_color="white", font=ctk.CTkFont(family="Arial", size=12, weight="bold"), height=40, corner_radius=8)
    boton_guardar.grid(row=0, column=0, sticky="ew", padx=(0, 8))

    boton_cancelar = ctk.CTkButton(frame_botones_finales, text="Cancelar", command=edicion.destroy, fg_color=COLOR_TEXTO_SUAVE, hover_color=COLOR_TEXTO, text_color="white", font=ctk.CTkFont(family="Arial", size=12, weight="bold"), height=40, corner_radius=8)
    boton_cancelar.grid(row=0, column=1, sticky="ew")

#Ventana para agregar mas libros
def ventana_añadir_libro(frame_pantallas=None):
    nueva_ventana = ctk.CTkToplevel()
    nueva_ventana.title("AÑADIR NUEVO LIBRO")
    nueva_ventana.configure(fg_color=COLOR_FONDO)

    nueva_ventana.after(200, lambda: maximizar_ventana(nueva_ventana))

    # Contenedor con scroll para que el formulario
    contenedor_scroll2 = ctk.CTkFrame(nueva_ventana, fg_color=COLOR_FONDO, corner_radius=0)
    contenedor_scroll2.pack(fill=BOTH, expand=True)
    canvas_nueva = tk.Canvas(contenedor_scroll2, bg=COLOR_FONDO, highlightthickness=0)
    scrollbar_nueva = ttk.Scrollbar(contenedor_scroll2, orient=VERTICAL, command=canvas_nueva.yview)
    canvas_nueva.configure(yscrollcommand=scrollbar_nueva.set)
    canvas_nueva.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar_nueva.pack(side=RIGHT, fill=Y)

    # Permite scrollear con la rueda del mouse desde cualquier parte de la ventana
    def _scroll_nueva(evento):
        canvas_nueva.yview_scroll(int(-1 * (evento.delta / 120)), "units")
    canvas_nueva.bind("<Enter>", lambda e: canvas_nueva.bind_all("<MouseWheel>", _scroll_nueva))
    canvas_nueva.bind("<Leave>", lambda e: canvas_nueva.unbind_all("<MouseWheel>"))

    # Frame que siempre ocupa el ancho completo del canvas 
    frame_centrador_nueva = tk.Frame(canvas_nueva, bg=COLOR_FONDO)
    id_centrador_nueva = canvas_nueva.create_window((0, 0), window=frame_centrador_nueva, anchor="nw")
    canvas_nueva.bind("<Configure>", lambda e: canvas_nueva.itemconfig(id_centrador_nueva, width=e.width))
    frame_centrador_nueva.bind("<Configure>", lambda e: canvas_nueva.configure(scrollregion=canvas_nueva.bbox("all")))

    # Columnas "espaciadoras" a los lados para que la tarjeta blanca quede centrada de verdad
    frame_centrador_nueva.grid_columnconfigure(0, weight=1)
    frame_centrador_nueva.grid_columnconfigure(1, weight=0)
    frame_centrador_nueva.grid_columnconfigure(2, weight=1)

    # Tarjeta centrada donde vive el formulario, con el mismo estilo de tarjeta/borde que el resto del programa
    contenido2 = ctk.CTkFrame(frame_centrador_nueva, fg_color=COLOR_TARJETA, corner_radius=18, border_width=1, border_color=COLOR_BORDE)
    contenido2.grid(row=0, column=1, pady=25)
    contenido2_interno = tk.Frame(contenido2, bg=COLOR_TARJETA, padx=50, pady=30)
    contenido2_interno.pack()
    contenido2 = contenido2_interno  # contenido2 es el frame donde se colocan los campos

    #variable para guardar los bytes de imagen seleccionada
    img_blob_seleccionada = [b""] 
    referencia_preview = [None] 

    lista_generos_disponibles = ["Fantasía", "Ciencia Ficción", "Terror", "Romance", "Drama", "Misterio", "Acción", "Aventura", "Suspenso", "Comedia"]
    generos = {}

    def seleccionar_imagen():
        ruta_imagen = filedialog.askopenfilename(
            title="Seleccionar Portada del Libro",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if ruta_imagen:
            try:
                #Abrir la ruta de la imagen y cerrarlo
                with open(ruta_imagen, 'rb') as archivo:
                    img_blob_seleccionada[0] = archivo.read()
                img_pil = Image.open(ruta_imagen)
                #tamaño estándar de las imagenes
                img_pil.thumbnail(PORTADA_MODAL) 
                img_tk = ImageTk.PhotoImage(img_pil)
                #etiqueta/label para mostrar una imagen
                label_preview.config(image=img_tk, text="")
                referencia_preview[0] = img_tk 
                label_imagen_no_selecionada.config(text="se a cargado la imagen correctamente", fg=COLOR_VERDE)
            except:
                messagebox.showerror("Error","No se pudo cargar la imagen")

    def guardar_libro():
        titulo = caja_titulo.get()
        autor = caja_autor.get()
        blob_data = img_blob_seleccionada[0]
        
        sinopsis = caja_sinopsis.get("1.0", tk.END).strip()
        if sinopsis == "":
            sinopsis = "Sin sinopsis disponible." # Texto por defecto si se deja vacío

        generos_seleccionados = []
        #marcador de generos (palomita)
        for genero, var in generos.items():
            if var.get(): 
                generos_seleccionados.append(genero)
        
        texto_categorias = ", ".join(generos_seleccionados) if generos_seleccionados else "General"
        
        try:
            #obtencion de datos
            precio = float(caja_precio.get() if caja_precio.get() else 0)
            stock = int(caja_stock.get() if caja_stock.get() else 0)
        except ValueError:
            messagebox.showwarning("Error de datos", "Se a introducido un numero erroneo.")
            return
        
        if titulo == "":
            messagebox.showwarning("Campos Incompletos", "El título del libro es obligatorio.")
            return
            
        try:
            conexion = sqlite3.connect("VentaLibros.db")
            cursor = conexion.cursor()
            #insertas nuevas tuplas (libros) en la bd
            cursor.execute("""
                INSERT INTO LibrosBD (TITULO, AUTOR, IMAGEN, CATEGORIA, PRECIO, STOCK, Sinopsis) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (titulo, autor, blob_data, texto_categorias, precio, stock, sinopsis))
            conexion.commit()
            conexion.close()
            
            messagebox.showinfo("Éxito", f"El libro '{titulo}' ha sido guardado con los géneros: {texto_categorias}")
            nueva_ventana.destroy()
            if frame_pantallas is not None:
                gestion_libros(frame_pantallas)  # reinicia el frame para que se reflejen los cambios
        except:
            messagebox.showerror("Error", f"A ocurrido un error no se guardaron los cambios")

    tk.Label(contenido2, text="Formulario de Registro de Libros", font=("Arial", 16, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO).pack(pady=(0, 15))

    tk.Label(contenido2, text="Título del Libro:", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 10)).pack(anchor="w", padx=30)
    caja_titulo = tk.Entry(contenido2, width=75, font=("Arial", 11))
    caja_titulo.pack(pady=(2, 8), padx=30, fill=X, ipady=4)

    tk.Label(contenido2, text="Autor:", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 10)).pack(anchor="w", padx=30)
    caja_autor = tk.Entry(contenido2, width=75, font=("Arial", 11))
    caja_autor.pack(pady=(2, 8), padx=30, fill=X, ipady=4)

    tk.Label(contenido2, text="Seleccione los Géneros aplicables:", font=("Arial", 10, "bold"), bg=COLOR_TARJETA, fg=COLOR_TEXTO).pack(anchor="w", padx=30, pady=(5, 2))

    frame_guardarlibro = tk.Frame(contenido2, bg=COLOR_TARJETA)
    frame_guardarlibro.pack(anchor="w", padx=30, fill=X, pady=(0, 8))
    #acomoda automaticamente los generos
    for index, genero in enumerate(lista_generos_disponibles):
        var_booleana = tk.BooleanVar()
        generos[genero] = var_booleana
        #casilla de seleccion (palomita) de los generos
        casilla = tk.Checkbutton(frame_guardarlibro, text=genero, variable=var_booleana, font=("Arial", 9), bg=COLOR_TARJETA, fg=COLOR_TEXTO, activebackground=COLOR_TARJETA, selectcolor=COLOR_FONDO)
        casilla.grid(row=index // 3, column=index % 3, sticky="w", padx=5, pady=2)

    #caja de la sinopsis
    tk.Label(contenido2, text="Sinopsis del Libro:", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 10)).pack(anchor="w", padx=30, pady=(5, 0))
    caja_sinopsis = tk.Text(contenido2, width=75, height=6, font=("Arial", 10))
    caja_sinopsis.pack(pady=(2, 8), padx=30, fill=X)

    # Precio y Stock en la misma fila
    frame_precio_stock2 = tk.Frame(contenido2, bg=COLOR_TARJETA)
    frame_precio_stock2.pack(fill=X, padx=30, pady=(0, 8))
    frame_precio_stock2.columnconfigure(0, weight=1)
    frame_precio_stock2.columnconfigure(1, weight=1)

    frame_col_precio2 = tk.Frame(frame_precio_stock2, bg=COLOR_TARJETA)
    frame_col_precio2.grid(row=0, column=0, sticky="ew", padx=(0, 8))
    tk.Label(frame_col_precio2, text="Precio ($):", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 10)).pack(anchor="w")
    caja_precio = tk.Entry(frame_col_precio2, font=("Arial", 11))
    caja_precio.pack(fill=X, ipady=4)

    frame_col_stock2 = tk.Frame(frame_precio_stock2, bg=COLOR_TARJETA)
    frame_col_stock2.grid(row=0, column=1, sticky="ew", padx=(8, 0))
    tk.Label(frame_col_stock2, text="Unidades disponibles (Stock):", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 10)).pack(anchor="w")
    caja_stock = tk.Entry(frame_col_stock2, font=("Arial", 11))
    caja_stock.pack(fill=X, ipady=4)

    # Portada e imagen
    tk.Label(contenido2, text="Portada del libro:", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 10)).pack(anchor="w", padx=30, pady=(5, 4))
    frame_portada_nueva = tk.Frame(contenido2, bg=COLOR_TARJETA)
    frame_portada_nueva.pack(padx=30, fill=X, pady=(0, 10))

    marco_preview = tk.Frame(frame_portada_nueva, width=PORTADA_MODAL[0], height=PORTADA_MODAL[1], bg=COLOR_BORDE, bd=1, relief="sunken")
    marco_preview.pack_propagate(False)
    marco_preview.pack(side=LEFT, padx=(0, 20))

    label_preview = tk.Label(marco_preview, text="Vista\nPrevia", bg=COLOR_BORDE, fg=COLOR_TEXTO_SUAVE)
    label_preview.pack(expand=True, fill=tk.BOTH)

    frame_botones_imagen2 = tk.Frame(frame_portada_nueva, bg=COLOR_TARJETA)
    frame_botones_imagen2.pack(side=LEFT, fill=X, expand=True, anchor="n")

    boton_foto = ctk.CTkButton(frame_botones_imagen2, text="📁 Seleccionar Imagen...", command=seleccionar_imagen, fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text_color="white", font=ctk.CTkFont(family="Arial", size=11, weight="bold"), corner_radius=8)
    boton_foto.pack(fill=X, ipady=2)

    label_imagen_no_selecionada = tk.Label(frame_botones_imagen2, text="Sin imagen seleccionada", fg=COLOR_ERROR, font=("Arial", 9, "italic"), bg=COLOR_TARJETA)
    label_imagen_no_selecionada.pack(anchor="w", pady=(8, 0))

    # Botones finales en fila: Guardar y Cancelar, igual que en modificar
    frame_botones_finales2 = tk.Frame(contenido2, bg=COLOR_TARJETA)
    frame_botones_finales2.pack(fill=X, padx=30, pady=(10, 5))
    frame_botones_finales2.columnconfigure(0, weight=2)
    frame_botones_finales2.columnconfigure(1, weight=1)

    boton_guardar = ctk.CTkButton(frame_botones_finales2, text="✔ GUARDAR LIBRO", command=guardar_libro, fg_color=COLOR_VERDE, hover_color=COLOR_VERDE_HOVER, text_color="white", font=ctk.CTkFont(family="Arial", size=12, weight="bold"), height=40, corner_radius=8)
    boton_guardar.grid(row=0, column=0, sticky="ew", padx=(0, 8))

    boton_cancelar2 = ctk.CTkButton(frame_botones_finales2, text="Cancelar", command=nueva_ventana.destroy, fg_color=COLOR_TEXTO_SUAVE, hover_color=COLOR_TEXTO, text_color="white", font=ctk.CTkFont(family="Arial", size=12, weight="bold"), height=40, corner_radius=8)
    boton_cancelar2.grid(row=0, column=1, sticky="ew")


def ventana_librero():
    estilizar_tabla_ttk_librero()
    screen3 = ctk.CTkToplevel(Librerias.screen)
    screen3.title("LIBRERIA CAL - LIBRERO")
    screen3.configure(fg_color=COLOR_FONDO)
    # after para evitar que se minimize la ventana
    screen3.after(200, lambda: maximizar_ventana(screen3))
    screen3.protocol("WM_DELETE_WINDOW", Librerias.screen.destroy)

    # Marco lateral izquierdo para el menú
    frame_lateral = ctk.CTkFrame(screen3, fg_color=COLOR_VERDE, width=230, corner_radius=16)
    frame_lateral.pack(side=LEFT, fill=Y, pady=10, padx=10)
    frame_lateral.pack_propagate(False)
    frame_lateral.columnconfigure(0, weight=1)

    Labeltitulo = ctk.CTkLabel(frame_lateral, text="📚 LIBRERIA CAL", fg_color="transparent", text_color="white", font=ctk.CTkFont(family="Arial", size=14, weight="bold"))
    Labeltitulo.grid(row=0, column=0, pady=(20, 20), padx=10, sticky="nsew")

    # Marco derecho principal donde se mostrará todos los libros
    frame_pantallas = ctk.CTkFrame(screen3, fg_color=COLOR_FONDO, corner_radius=0)
    frame_pantallas.pack(side=RIGHT, fill=BOTH, expand=True, padx=(0, 10), pady=10) 

    # botones del menu lateral
    Boton_gestion_libros = ctk.CTkButton(frame_lateral, anchor="w", text_color="white", fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text="📦  Gestión de libros", command=lambda: gestion_libros(frame_pantallas), font=ctk.CTkFont(family="Arial", size=12, weight="bold"), corner_radius=10)
    Boton_gestion_libros.grid(row=1, column=0, pady=(10, 6), padx=10, sticky="snew", ipady=10)

    Boton_comentarios = ctk.CTkButton(frame_lateral, anchor="w", text_color="white", fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text="💬  Comentarios", command=lambda: comentarios(frame_pantallas), font=ctk.CTkFont(family="Arial", size=12, weight="bold"), corner_radius=10)
    Boton_comentarios.grid(row=2, column=0, pady=(6, 10), padx=10, sticky="snew", ipady=10)

    # Boton de cerrar sesion, separado del resto al fondo de la barra lateral
    frame_lateral.grid_rowconfigure(3, weight=1)
    Boton_cerrar_sesion = ctk.CTkButton(frame_lateral, anchor="w", text_color="white", fg_color=COLOR_ERROR, hover_color=COLOR_ERROR_HOVER, text="🚪  Cerrar sesión", command=lambda: cerrar_sesion(screen3), font=ctk.CTkFont(family="Arial", size=12, weight="bold"), corner_radius=10)
    Boton_cerrar_sesion.grid(row=3, column=0, pady=(0, 10), padx=14, sticky="sew")

    gestion_libros(frame_pantallas)