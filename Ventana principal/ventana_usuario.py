#Ventana usuario cuenta con los botones inicio donde salen los libros en general, libros donde salen los ultimos
#libros que se subieron, categorias/generos para una busqueda mas enfocada, carrito donde se guardan
#o se quitan los libros y el reporte de errores
from Librerias import *
import Librerias
from funciones_compartidas import maximizar_ventana, limpiar_pantalla, cerrar_sesion
from BDS import Save_report
import random          # se usa para asignar el pasillo de retiro de la compra
from datetime import datetime  # se usa para la fecha/hora que aparece en el ticket

# Misma paleta de colores que usan la mayoria de ventanas
COLOR_FONDO = "#F4EFE6"
COLOR_TARJETA = "#FFFDF8"
COLOR_BORDE = "#D8C9A8"
COLOR_TEXTO = "#3E2B1F"
COLOR_TEXTO_SUAVE = "#8A7864"
COLOR_VERDE = "#216300"
COLOR_VERDE_HOVER = "#184A00"
COLOR_VERDE_OSCURO = "#153F00"   # verde mas oscuro, para la tarjeta que agrupa el menu
COLOR_MARRON = "#123D02"       # verde bosque oscuro para botones secundarios (antes era marron)
COLOR_MARRON_HOVER = "#0A2601"
COLOR_PORTADA_FONDO = "white"      # marco donde va la portada del libro (antes marron, ahora blanco)
COLOR_PLACEHOLDER = "#8A7864"      # texto sobre el marco blanco cuando no hay portada (SIN FOTO, ERROR)
COLOR_ERROR = "#8B3A3A"            # terracota calido para errores y el boton de reportes
COLOR_DISPONIBLE = "#216300"
COLOR_AGOTADO = "#8B3A3A"

# Cantidad fija de portadas por fila en las cuadriculas de libros
# 5 columnas x (160+30)px de ancho por portada = 950px

LIBROS_POR_FILA = 5

def agregar_al_carrito(usuario, id_libro, titulo, precio_unitario, cantidad):
    #Guarda el libro en la tabla CARRITO si ese usuario ya tenia ese
    #mismo libro en el carrito se le suma la unidad
    try:
        conexion = sqlite3.connect("VentaLibros.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT ID, CANTIDAD FROM CARRITO WHERE USUARIO = ? AND LIBRO_ID = ?", (usuario, id_libro))
        fila_existente = cursor.fetchone()
        if fila_existente:
            id_carrito, cantidad_actual = fila_existente
            cursor.execute("UPDATE CARRITO SET CANTIDAD = ? WHERE ID = ?", (cantidad_actual + cantidad, id_carrito))
        else:
            cursor.execute("INSERT INTO CARRITO (USUARIO, LIBRO_ID, TITULO, PRECIO_UNITARIO, CANTIDAD) VALUES (?, ?, ?, ?, ?)", (usuario, id_libro, titulo, precio_unitario, cantidad))
        conexion.commit()
        conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo agregar al carrito: {e}")

def quitar_del_carrito(id_carrito):
    #Borra el libro añadido del carrito
    try:
        conexion = sqlite3.connect("VentaLibros.db")
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM CARRITO WHERE ID = ?", (id_carrito,))
        conexion.commit()
        conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar el carrito: {e}")

def procesar_compra(id_libro, titulo_libro, precio_unitario, cantidad, usuario, ventana_padre, accion_cerrar=None):
    #Registra la venta en la base de datos, descuenta el stock y muestra
    #el ticket. La usan tanto la ficha de compra individual como el carrito,
    #Devuelve True si la compra
    #se realizo, False si no sin stock o error.
    try:
        conexion = sqlite3.connect("VentaLibros.db")
        cursor = conexion.cursor()

        # Revalidamos el stock justo antes de confirmar
        cursor.execute("SELECT STOCK FROM LibrosBD WHERE ID = ?", (id_libro,))
        fila_stock = cursor.fetchone()
        stock_actual = fila_stock[0] if fila_stock else 0

        if stock_actual < cantidad:
            conexion.close()
            messagebox.showwarning("Sin existencias suficientes", f"Solo quedan {stock_actual} unidad(es) disponibles de '{titulo_libro}'.")
            return False

        total_compra = precio_unitario * cantidad
        # Punto de venta con retiro en sucur se asigna un pasillo al azar donde el cliente pasa
        # a recoger los libros (se muestra despues en el ticket).
        pasillo_asignado = random.randint(1, 8)

        cursor.execute("""
            INSERT INTO VENTAS (USUARIO, LIBRO_ID, TITULO, CANTIDAD, PRECIO_UNITARIO, TOTAL, PASILLO)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (usuario, id_libro, titulo_libro, cantidad, precio_unitario, total_compra, pasillo_asignado))
        numero_ticket = cursor.lastrowid

        cursor.execute("UPDATE LibrosBD SET STOCK = STOCK - ? WHERE ID = ?", (cantidad, id_libro))

        conexion.commit()
        conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo registrar la compra: {e}")
        return False

    mostrar_ticket_compra(usuario, titulo_libro, cantidad, precio_unitario, total_compra, pasillo_asignado, numero_ticket, ventana_padre, accion_cerrar)
    return True


def busqueda_libros(frame_pantallas, query_sql, params=(), usuario="usuario", on_click=None):
    # on_click(id_libro) define qué pasa al tocar una portada.
    # Por defecto abre la ficha de compra
    if on_click is None:
        on_click = lambda id_libro: mostrar_detalles_libro(id_libro, usuario)

    limpiar_pantalla(frame_pantallas)
    frame_busqueda = ctk.CTkFrame(frame_pantallas, fg_color=COLOR_FONDO, corner_radius=0)
    frame_busqueda.pack(anchor="w", padx=30, pady=(20, 0), fill=X)
    caja_busqueda = ctk.CTkEntry(frame_busqueda, font=ctk.CTkFont(family="Arial", size=11), width=320, height=32, corner_radius=8, border_color=COLOR_BORDE, fg_color="white", text_color=COLOR_TEXTO)
    caja_busqueda.pack(side=LEFT, padx=(0, 10)) 

    def ejecutar_busqueda(event=None):
        txt = caja_busqueda.get()
        busqueda_libros(frame_pantallas, "SELECT ID, TITULO, IMAGEN FROM LibrosBD WHERE TITULO LIKE ?", ('%' + txt + '%',), usuario, on_click)

    ctk.CTkButton(frame_busqueda, text="Buscar", fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text_color="white", corner_radius=8, height=32, command=ejecutar_busqueda).pack(side=LEFT)
    caja_busqueda.bind("<Return>", ejecutar_busqueda)

    framelibros_contenedor = ctk.CTkFrame(frame_pantallas, fg_color=COLOR_FONDO, corner_radius=0)
    framelibros_contenedor.pack(fill=BOTH, expand=True, padx=30, pady=10)

    # Contenedor con scroll para que la cuadricula de libros no se corte si
    # hay mas filas de las que entran en la pantalla (mismo patron que ya
    # usa mostrar_detalles_libro): un Canvas con Scrollbar, y adentro un
    # frame normal (framelibros) donde se sigue armando la cuadricula igual
    # que antes.
    canvas_libros = tk.Canvas(framelibros_contenedor, bg=COLOR_FONDO, highlightthickness=0)
    scrollbar_libros = ttk.Scrollbar(framelibros_contenedor, orient=VERTICAL, command=canvas_libros.yview)
    canvas_libros.configure(yscrollcommand=scrollbar_libros.set)
    canvas_libros.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar_libros.pack(side=RIGHT, fill=Y)

    framelibros = tk.Frame(canvas_libros, bg=COLOR_FONDO)
    id_framelibros = canvas_libros.create_window((0, 0), window=framelibros, anchor="nw")
    canvas_libros.bind("<Configure>", lambda e: canvas_libros.itemconfig(id_framelibros, width=e.width))
    framelibros.bind("<Configure>", lambda e: canvas_libros.configure(scrollregion=canvas_libros.bbox("all")))

    # Permite scrollear con la rueda del mouse mientras el cursor esta
    # sobre la cuadricula (se activa/desactiva al entrar/salir para no
    # interferir con el scroll de otras pantallas)
    def _scroll_libros(evento):
        canvas_libros.yview_scroll(int(-1 * (evento.delta / 120)), "units")
    canvas_libros.bind("<Enter>", lambda e: canvas_libros.bind_all("<MouseWheel>", _scroll_libros))
    canvas_libros.bind("<Leave>", lambda e: canvas_libros.unbind_all("<MouseWheel>"))

    try:
        conexion = sqlite3.connect("VentaLibros.db")
        cursor = conexion.cursor()
        cursor.execute(query_sql, params)
        libros = cursor.fetchall()
        conexion.close()
    
        if not libros:
            ctk.CTkLabel(framelibros, text="No hay libros para mostrar en esta sección.", fg_color=COLOR_FONDO, text_color=COLOR_TEXTO_SUAVE, font=ctk.CTkFont(family="Arial", size=11)).pack(pady=20)
            return
        #Reacomoda automaticamente los marcos de los libros donde van las portadas de los libros
        # Cantidad fija de columnas
        libros_por_fila = LIBROS_POR_FILA
        for indice, libro in enumerate(libros):
            id_db, titulo_db, blob_db = libro[0], libro[1], libro[2]
            fila_actual = (indice // libros_por_fila) * 2
            columna_actual = indice % libros_por_fila
        
            marco = ctk.CTkFrame(framelibros, fg_color=COLOR_PORTADA_FONDO, width=PORTADA_CUADRICULA[0], height=PORTADA_CUADRICULA[1], corner_radius=0, border_width=1, border_color=COLOR_BORDE, cursor="hand2")
            marco.pack_propagate(False)
            marco.grid(row=fila_actual, column=columna_actual, pady=(10, 2), padx=15)
            #"<Button-1>" sirve para que puedas hacer click con el click izquierdo si se quiere con la rueda centra o derecho solo se cambia en vez de 1 a 2 hasta 3
            marco.bind("<Button-1>", lambda e, id_l=id_db: on_click(id_l))
        
            label_foto = ctk.CTkLabel(marco, text="", fg_color=COLOR_PORTADA_FONDO, cursor="hand2")
            label_foto.pack(expand=True, fill=tk.BOTH)
            label_foto.bind("<Button-1>", lambda e, id_l=id_db: on_click(id_l))
        
            if blob_db:
                try:
                    imagen = io.BytesIO(blob_db)
                    img_pil = Image.open(imagen).resize(PORTADA_CUADRICULA)
                    img_tk = ImageTk.PhotoImage(img_pil)
                    label_foto.configure(image=img_tk)
                    lista_imagenes_tk.append(img_tk)
                except:
                    label_foto.configure(text="ERROR\nPORTADA", text_color=COLOR_PLACEHOLDER)
            else:
                label_foto.configure(text=f"PORTADA\n{titulo_db[:6]}...", text_color=COLOR_PLACEHOLDER)
        
            titulo_label = ctk.CTkLabel(framelibros, text=titulo_db, fg_color=COLOR_FONDO, text_color=COLOR_TEXTO, font=ctk.CTkFont(family="Arial", size=9, weight="bold"), justify=LEFT, wraplength=110, cursor="hand2")
            titulo_label.grid(row=fila_actual + 1, column=columna_actual, sticky="nw", padx=15, pady=(0, 10))
            titulo_label.bind("<Button-1>", lambda e, id_l=id_db: on_click(id_l))
        
    except:
        messagebox.showerror("Error", "Error al cargar libros")

def mostrar_ticket_compra(usuario, titulo_libro, cantidad, precio_unitario, total_compra, pasillo, numero_ticket, ventana_padre, accion_cerrar=None):
    #recibo de una compra el ticket le indica al cliente en qué pasillo se encuentra el libro
    ticket = ctk.CTkToplevel(ventana_padre)
    ticket.title("Ticket de compra")
    ticket.configure(fg_color=COLOR_FONDO)
    ticket.geometry("360x540")
    ticket.resizable(False, False)

    tarjeta_ticket = ctk.CTkFrame(ticket, fg_color=COLOR_TARJETA, corner_radius=14, border_width=1, border_color=COLOR_BORDE)
    tarjeta_ticket.pack(fill=BOTH, expand=True, padx=16, pady=16)

    ctk.CTkLabel(tarjeta_ticket, text="🧾 LIBRERIA WEB", font=ctk.CTkFont(family="Georgia", size=17, weight="bold"), text_color=COLOR_VERDE, fg_color=COLOR_TARJETA).pack(pady=(20, 0))
    ctk.CTkLabel(tarjeta_ticket, text="Ticket de compra", font=ctk.CTkFont(family="Arial", size=11, slant="italic"), text_color=COLOR_TEXTO_SUAVE, fg_color=COLOR_TARJETA).pack(pady=(0, 14))

    def linea_separadora():
        ctk.CTkFrame(tarjeta_ticket, fg_color=COLOR_BORDE, height=1, corner_radius=0).pack(fill=X, padx=18, pady=8)

    linea_separadora()

    fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
    for etiqueta, valor in (("N° Ticket", f"{numero_ticket}"), ("Fecha", fecha_hora), ("Cliente", usuario)):
        fila_dato = ctk.CTkFrame(tarjeta_ticket, fg_color=COLOR_TARJETA, corner_radius=0)
        fila_dato.pack(fill=X, padx=18)
        ctk.CTkLabel(fila_dato, text=etiqueta, font=ctk.CTkFont(family="Arial", size=10), text_color=COLOR_TEXTO_SUAVE, fg_color=COLOR_TARJETA).pack(side=LEFT)
        ctk.CTkLabel(fila_dato, text=valor, font=ctk.CTkFont(family="Arial", size=10, weight="bold"), text_color=COLOR_TEXTO, fg_color=COLOR_TARJETA).pack(side=RIGHT)

    linea_separadora()

    ctk.CTkLabel(tarjeta_ticket, text=titulo_libro, font=ctk.CTkFont(family="Arial", size=12, weight="bold"), text_color=COLOR_TEXTO, fg_color=COLOR_TARJETA, wraplength=290, justify=LEFT).pack(anchor="w", padx=18)
    fila_cantidad_precio = ctk.CTkFrame(tarjeta_ticket, fg_color=COLOR_TARJETA, corner_radius=0)
    fila_cantidad_precio.pack(fill=X, padx=18, pady=(2, 0))
    ctk.CTkLabel(fila_cantidad_precio, text=f"{cantidad} x ${precio_unitario:.2f}", font=ctk.CTkFont(family="Arial", size=10), text_color=COLOR_TEXTO_SUAVE, fg_color=COLOR_TARJETA).pack(side=LEFT)
    ctk.CTkLabel(fila_cantidad_precio, text=f"${total_compra:.2f}", font=ctk.CTkFont(family="Arial", size=10, weight="bold"), text_color=COLOR_TEXTO, fg_color=COLOR_TARJETA).pack(side=RIGHT)

    linea_separadora()

    fila_total = ctk.CTkFrame(tarjeta_ticket, fg_color=COLOR_TARJETA, corner_radius=0)
    fila_total.pack(fill=X, padx=18)
    ctk.CTkLabel(fila_total, text="TOTAL", font=ctk.CTkFont(family="Arial", size=13, weight="bold"), text_color=COLOR_TEXTO, fg_color=COLOR_TARJETA).pack(side=LEFT)
    ctk.CTkLabel(fila_total, text=f"${total_compra:.2f}", font=ctk.CTkFont(family="Arial", size=16, weight="bold"), text_color=COLOR_VERDE, fg_color=COLOR_TARJETA).pack(side=RIGHT)

    linea_separadora()

    aviso_retiro = ctk.CTkFrame(tarjeta_ticket, fg_color=COLOR_FONDO, corner_radius=10)
    aviso_retiro.pack(fill=X, padx=18, pady=(6, 16))
    ctk.CTkLabel(aviso_retiro, text="📍 Pase a la sucursal a retirar su compra", font=ctk.CTkFont(family="Arial", size=10, weight="bold"), text_color=COLOR_TEXTO, fg_color=COLOR_FONDO, wraplength=260, justify=LEFT).pack(padx=10, pady=(10, 2))
    ctk.CTkLabel(aviso_retiro, text=f"Pasillo {pasillo}", font=ctk.CTkFont(family="Georgia", size=22, weight="bold"), text_color=COLOR_VERDE, fg_color=COLOR_FONDO).pack(pady=(0, 10))

    ctk.CTkLabel(tarjeta_ticket, text="¡Gracias por su compra!", font=ctk.CTkFont(family="Arial", size=10, slant="italic"), text_color=COLOR_TEXTO_SUAVE, fg_color=COLOR_TARJETA).pack(pady=(0, 10))


    def cerrar_todo():
        ticket.destroy()
        if accion_cerrar is not None:
            accion_cerrar()
        else:
            ventana_padre.destroy()

    ctk.CTkButton(tarjeta_ticket, text="Aceptar", command=cerrar_todo, fg_color=COLOR_VERDE, hover_color=COLOR_VERDE_HOVER, text_color="white", corner_radius=8, height=38).pack(pady=(0, 20), padx=18, fill=X)


def mostrar_detalles_libro(id_libro, usuario):
    try:
        conexion = sqlite3.connect("VentaLibros.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT TITULO, AUTOR, CATEGORIA, PRECIO, IMAGEN, SINOPSIS, STOCK FROM LibrosBD WHERE ID = ?", (id_libro,))
        informacion = cursor.fetchone()
        conexion.close()

        if not informacion:
            messagebox.showwarning("Aviso", "El libro seleccionado ya no está disponible.")
            return

        titulo_libro, autor_libro, generos_libro, precio_libro, blob_db, sinopsis_libro, stock_libro = informacion
        sinopsis_libro = sinopsis_libro or "Sin sinopsis disponible."
        stock_libro = stock_libro if stock_libro else 0
        hay_stock = stock_libro > 0

        detalles = ctk.CTkToplevel(Librerias.screen)
        detalles.title(f"Detalles: {titulo_libro}")
        detalles.configure(fg_color=COLOR_FONDO)

        detalles.after(200, lambda: maximizar_ventana(detalles))

        frame_detalles = tk.Frame(detalles, bg=COLOR_FONDO)
        frame_detalles.pack(fill=BOTH, expand=True)

        # la tarjeta de compra (columna 0) ocupa casi toda la pantalla y solo se le
        # resta una parte fija a la derecha (columna 1) para los libros sugeridos.
        frame_detalles.grid_columnconfigure(0, weight=1)
        frame_detalles.grid_columnconfigure(1, weight=0)

        # frame donde esta la ficha del libro
        contenido3 = ctk.CTkFrame(frame_detalles, fg_color=COLOR_TARJETA, corner_radius=18, border_width=1, border_color=COLOR_BORDE)
        contenido3.grid(row=0, column=0, pady=20, padx=(20, 10), sticky="nsew")

        # Panel de "tambien te puede interesar" un segundo frame con una lista descendente de otros libros en miniatura 
        panel_sugeridos = ctk.CTkFrame(frame_detalles, fg_color=COLOR_TARJETA, corner_radius=18, border_width=1, border_color=COLOR_BORDE, width=260)
        panel_sugeridos.grid(row=0, column=1, pady=20, padx=(10, 20), sticky="ns")

        ctk.CTkLabel(panel_sugeridos, text="También te puede interesar", font=ctk.CTkFont(family="Arial", size=12, weight="bold"), fg_color=COLOR_TARJETA, text_color=COLOR_TEXTO, wraplength=230, justify=LEFT).pack(anchor="w", padx=16, pady=(18, 10))

        try:
            conexion_sug = sqlite3.connect("VentaLibros.db")
            cursor_sug = conexion_sug.cursor()
            # Prioriza libros de la misma categoria
            cursor_sug.execute(
                "SELECT ID, TITULO, IMAGEN, PRECIO FROM LibrosBD WHERE ID != ? ORDER BY (CATEGORIA = ?) DESC, RANDOM() LIMIT 6",
                (id_libro, generos_libro),
            )
            libros_sugeridos = cursor_sug.fetchall()
            conexion_sug.close()
        except:
            libros_sugeridos = []

        PORTADA_MINI = (60, 80)
        for id_sug, titulo_sug, blob_sug, precio_sug in libros_sugeridos:
            fila_sugerido = ctk.CTkFrame(panel_sugeridos, fg_color=COLOR_TARJETA, corner_radius=0, cursor="hand2")
            fila_sugerido.pack(fill=X, padx=12, pady=6)

            marco_mini = ctk.CTkFrame(fila_sugerido, width=PORTADA_MINI[0], height=PORTADA_MINI[1], fg_color=COLOR_PORTADA_FONDO, corner_radius=0, border_width=1, border_color=COLOR_BORDE, cursor="hand2")
            marco_mini.pack_propagate(False)
            marco_mini.pack(side=LEFT, padx=(0, 8))
            lbl_mini = ctk.CTkLabel(marco_mini, text="", fg_color=COLOR_PORTADA_FONDO, cursor="hand2")
            lbl_mini.pack(expand=True, fill=BOTH)

            if blob_sug:
                try:
                    imagen_mini = io.BytesIO(blob_sug)
                    img_pil_mini = Image.open(imagen_mini).resize(PORTADA_MINI)
                    img_tk_mini = ImageTk.PhotoImage(img_pil_mini)
                    lbl_mini.configure(image=img_tk_mini)
                    lista_imagenes_tk.append(img_tk_mini)
                except:
                    lbl_mini.configure(text="?", text_color=COLOR_PLACEHOLDER)
            else:
                lbl_mini.configure(text="?", text_color=COLOR_PLACEHOLDER)

            frame_texto_mini = ctk.CTkFrame(fila_sugerido, fg_color=COLOR_TARJETA, corner_radius=0, cursor="hand2")
            frame_texto_mini.pack(side=LEFT, fill=X, expand=True)
            ctk.CTkLabel(frame_texto_mini, text=titulo_sug, font=ctk.CTkFont(family="Arial", size=10, weight="bold"), fg_color=COLOR_TARJETA, text_color=COLOR_TEXTO, wraplength=130, justify=LEFT, cursor="hand2").pack(anchor="w")
            ctk.CTkLabel(frame_texto_mini, text=f"${precio_sug:.2f}", font=ctk.CTkFont(family="Arial", size=10, weight="bold"), fg_color=COLOR_TARJETA, text_color=COLOR_VERDE, cursor="hand2").pack(anchor="w", pady=(2, 0))

            # Al tocar cualquier parte de la fila, cierra esta ficha y abre la
            # del libro sugerido.
            def abrir_sugerido(id_l=id_sug):
                detalles.destroy()
                mostrar_detalles_libro(id_l, usuario)

            for widget_click in (fila_sugerido, marco_mini, lbl_mini, frame_texto_mini, *frame_texto_mini.winfo_children()):
                widget_click.bind("<Button-1>", lambda e, funcion=abrir_sugerido: funcion())

        # portada y datos del libro
        frame_encabezado = ctk.CTkFrame(contenido3, fg_color=COLOR_TARJETA, corner_radius=0)
        frame_encabezado.pack(fill=X, padx=20, pady=(20, 5))

        marco_portada = ctk.CTkFrame(frame_encabezado, width=PORTADA_DETALLE[0], height=PORTADA_DETALLE[1], fg_color=COLOR_PORTADA_FONDO, corner_radius=0, border_width=1, border_color=COLOR_BORDE)
        marco_portada.pack_propagate(False)
        marco_portada.pack(side=LEFT, padx=(0, 15))
        lbl_portada = ctk.CTkLabel(marco_portada, text="", fg_color=COLOR_PORTADA_FONDO)
        lbl_portada.pack(expand=True, fill=BOTH)

        if blob_db:
            try:
                imagen = io.BytesIO(blob_db)
                img_pil = Image.open(imagen).resize(PORTADA_DETALLE)
                img_tk = ImageTk.PhotoImage(img_pil)
                lbl_portada.configure(image=img_tk)
                lista_imagenes_tk.append(img_tk)
            except:
                lbl_portada.configure(text="ERROR\nPORTADA", text_color=COLOR_PLACEHOLDER)
        else:
            lbl_portada.configure(text="SIN\nPORTADA", text_color=COLOR_PLACEHOLDER)

        frame_info = ctk.CTkFrame(frame_encabezado, fg_color=COLOR_TARJETA, corner_radius=0)
        frame_info.pack(side=LEFT, fill=BOTH, expand=True)

        ctk.CTkLabel(frame_info, text=titulo_libro, font=ctk.CTkFont(family="Arial", size=15, weight="bold"), fg_color=COLOR_TARJETA, text_color=COLOR_TEXTO, wraplength=500, justify=LEFT).pack(anchor="w")
        ctk.CTkLabel(frame_info, text=f"Autor: {autor_libro or 'Desconocido'}", font=ctk.CTkFont(family="Arial", size=11), fg_color=COLOR_TARJETA, text_color=COLOR_TEXTO).pack(anchor="w", pady=(6, 0))
        ctk.CTkLabel(frame_info, text=f"Géneros: {generos_libro or 'Sin categoría'}", font=ctk.CTkFont(family="Arial", size=11, slant="italic"), text_color=COLOR_TEXTO_SUAVE, fg_color=COLOR_TARJETA, wraplength=500, justify=LEFT).pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(frame_info, text=f"Precio: ${precio_libro:.2f}", font=ctk.CTkFont(family="Arial", size=15, weight="bold"), text_color=COLOR_VERDE, fg_color=COLOR_TARJETA).pack(anchor="w", pady=(8, 0))

        texto_stock = f"Disponibles: {stock_libro} unidad(es)" if hay_stock else "SIN EXISTENCIAS"
        color_stock = COLOR_DISPONIBLE if hay_stock else COLOR_AGOTADO
        ctk.CTkLabel(frame_info, text=texto_stock, font=ctk.CTkFont(family="Arial", size=10, weight="bold"), text_color=color_stock, fg_color=COLOR_TARJETA).pack(anchor="w", pady=(2, 0))

        # sinopsis
        ctk.CTkLabel(contenido3, text="Sinopsis", font=ctk.CTkFont(family="Arial", size=12, weight="bold"), fg_color=COLOR_TARJETA, text_color=COLOR_TEXTO).pack(
            anchor="w", padx=20, pady=(12, 2))
        texto_sinopsis = ctk.CTkTextbox(contenido3, height=110, font=ctk.CTkFont(family="Arial", size=10), wrap="word", fg_color="white", border_width=1, border_color=COLOR_BORDE, text_color=COLOR_TEXTO)
        texto_sinopsis.insert("1.0", sinopsis_libro)
        texto_sinopsis.configure(state="disabled")
        texto_sinopsis.pack(fill=X, padx=20)

        #cantidad de libros
        frame_cantidad = ctk.CTkFrame(contenido3, fg_color=COLOR_TARJETA, corner_radius=0)
        frame_cantidad.pack(fill=X, padx=20, pady=(0, 10))
        ctk.CTkLabel(frame_cantidad, text="Cantidad:", font=ctk.CTkFont(family="Arial", size=12), fg_color=COLOR_TARJETA, text_color=COLOR_TEXTO).pack(side=LEFT, padx=(0, 10))

        variable_cantidad = IntVar(value=1 if hay_stock else 0)
        spin_cantidad = tk.Spinbox(frame_cantidad, from_=1, to=max(stock_libro, 1), width=6, font=("Arial", 11), bg="white", fg=COLOR_TEXTO, relief="solid", bd=1, textvariable=variable_cantidad,state="normal" if hay_stock else "disabled")
        spin_cantidad.pack(side=LEFT, ipady=3)

        lbl_total = ctk.CTkLabel(frame_cantidad, text=f"Total: ${precio_libro * (1 if hay_stock else 0):.2f}", font=ctk.CTkFont(family="Arial", size=15, weight="bold"), text_color=COLOR_VERDE, fg_color=COLOR_TARJETA)
        lbl_total.pack(side=RIGHT)

        def actualizar_total(*args): 
            try:
                cantidad = int(variable_cantidad.get())
            except (ValueError, tk.TclError):
                cantidad = 0
            lbl_total.configure(text=f"Total: ${precio_libro * cantidad:.2f}")

        variable_cantidad.trace_add("write", actualizar_total)

        def realizar_compra():
            try:
                cantidad = int(variable_cantidad.get())
                if cantidad <= 0:
                    raise ValueError
            except (ValueError, tk.TclError):
                messagebox.showwarning("Cantidad inválida", "Ingrese una cantidad válida.")
                return
            procesar_compra(id_libro, titulo_libro, precio_libro, cantidad, usuario, detalles)

        def agregar_carrito_click():
            try:
                cantidad = int(variable_cantidad.get())
                if cantidad <= 0:
                    raise ValueError
            except (ValueError, tk.TclError):
                messagebox.showwarning("Cantidad inválida", "Ingrese una cantidad válida.")
                return
            agregar_al_carrito(usuario, id_libro, titulo_libro, precio_libro, cantidad)
            messagebox.showinfo("Carrito", f"'{titulo_libro}' se agregó al carrito ({cantidad} unidad(es)).")

        # Botones finales en fila: Comprar ahora, añadir al carrito y Cancelar
        frame_botones_compra = ctk.CTkFrame(contenido3, fg_color=COLOR_TARJETA, corner_radius=0)
        frame_botones_compra.pack(fill=X, padx=20, pady=(5, 15))
        frame_botones_compra.columnconfigure(0, weight=2)
        frame_botones_compra.columnconfigure(1, weight=2)
        frame_botones_compra.columnconfigure(2, weight=1)

        ##state= sirve para habilidar o desabilitar las opciones dependiendo de lo que se desee en este caso si hay stock no pasa nada pero si no hay se desabilita
        boton_comprar = ctk.CTkButton(frame_botones_compra, text="🛒 COMPRAR AHORA", command=realizar_compra, fg_color=COLOR_VERDE if hay_stock else "#B5A488", hover_color=COLOR_VERDE_HOVER, text_color="white",font=ctk.CTkFont(family="Arial", size=12, weight="bold"), height=42, corner_radius=8, state="normal" if hay_stock else "disabled")
        boton_comprar.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        boton_carrito = ctk.CTkButton(frame_botones_compra, text="🛒+ Carrito", command=agregar_carrito_click, fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text_color="white", font=ctk.CTkFont(family="Arial", size=12, weight="bold"), height=42, corner_radius=8, state="normal" if hay_stock else "disabled")
        boton_carrito.grid(row=0, column=1, sticky="ew", padx=(0, 8))

        boton_cerrar = ctk.CTkButton(frame_botones_compra, text="Cerrar", command=detalles.destroy, fg_color=COLOR_TEXTO_SUAVE, hover_color=COLOR_MARRON_HOVER, text_color="white", font=ctk.CTkFont(family="Arial", size=12, weight="bold"), height=42, corner_radius=8)
        boton_cerrar.grid(row=0, column=2, sticky="ew")
    except Exception as e:
        messagebox.showerror("Error", f"Ha ocurrido un error con el programa: {e}")

def inicio_usuario(frame_pantallas, usuario):
    busqueda_libros(frame_pantallas, "SELECT ID, TITULO, IMAGEN FROM LibrosBD ORDER BY ID ASC", params=(), usuario=usuario)
    ctk.CTkLabel(frame_pantallas, text="Inicio", font=ctk.CTkFont(family="Times New Roman", size=16, slant="italic", weight="bold"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO).pack(before=frame_pantallas.winfo_children()[0], anchor="w", padx=30, pady=(10,0))

def ir_a_libros(frame_pantallas, usuario="usuario"):
    busqueda_libros(frame_pantallas, "SELECT ID, TITULO, IMAGEN FROM LibrosBD ORDER BY ID DESC", params=(), usuario=usuario)
    ctk.CTkLabel(frame_pantallas, text="RECIENTES / ÚLTIMOS SUBIDOS", font=ctk.CTkFont(family="Times New Roman", size=16, slant="italic", weight="bold"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO).pack(before=frame_pantallas.winfo_children()[0], anchor="w", padx=30, pady=(10,0))

def ir_a_categorias(frame_pantallas, on_click=None, usuario="usuario"):
    # on_click(id_libro) define qué pasa al tocar una portada.
    # Por defecto abre la ficha de compra
    if on_click is None:
        on_click = lambda id_libro: mostrar_detalles_libro(id_libro, usuario)

    limpiar_pantalla(frame_pantallas)

    ctk.CTkLabel(frame_pantallas, text="CATEGORÍAS / GÉNEROS", font=ctk.CTkFont(family="Times New Roman", size=16, slant="italic", weight="bold"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO).pack(anchor="w", padx=30, pady=15)

    frame_filtro = ctk.CTkFrame(frame_pantallas, fg_color=COLOR_FONDO, corner_radius=0)
    frame_filtro.pack(anchor="w", padx=30, fill=X)

    ctk.CTkLabel(frame_filtro, text="Seleccione un Género:", fg_color=COLOR_FONDO, text_color=COLOR_TEXTO, font=ctk.CTkFont(family="Arial", size=10, weight="bold")).pack(side=LEFT, padx=(0,10))
    #seleccion de genero/categoria
    genero_filtro = ctk.CTkComboBox(frame_filtro, values=["Fantasía", "Ciencia Ficción", "Terror", "Romance", "Drama", "Misterio", "Acción", "Aventura", "Suspenso"], fg_color="white", border_color=COLOR_BORDE, button_color="white", button_hover_color=COLOR_BORDE, dropdown_fg_color="white", text_color=COLOR_TEXTO)
    genero_filtro.set("Fantasía")
    genero_filtro.pack(side=LEFT, padx=5)


    contenedor_scroll_categorias = ctk.CTkFrame(frame_pantallas, fg_color=COLOR_FONDO, corner_radius=0)
    contenedor_scroll_categorias.pack(fill=BOTH, expand=True, padx=30, pady=15)

    canvas_categorias = tk.Canvas(contenedor_scroll_categorias, bg=COLOR_FONDO, highlightthickness=0)
    scrollbar_categorias = ttk.Scrollbar(contenedor_scroll_categorias, orient=VERTICAL, command=canvas_categorias.yview)
    canvas_categorias.configure(yscrollcommand=scrollbar_categorias.set)
    canvas_categorias.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar_categorias.pack(side=RIGHT, fill=Y)

    frame_resultados_categorias = tk.Frame(canvas_categorias, bg=COLOR_FONDO)
    id_resultados_categorias = canvas_categorias.create_window((0, 0), window=frame_resultados_categorias, anchor="nw")
    canvas_categorias.bind("<Configure>", lambda e: canvas_categorias.itemconfig(id_resultados_categorias, width=e.width))
    frame_resultados_categorias.bind("<Configure>", lambda e: canvas_categorias.configure(scrollregion=canvas_categorias.bbox("all")))

    # Permite scrollear con la rueda del mouse mientras el cursor esta
    # sobre los resultados
    def _scroll_categorias(evento):
        canvas_categorias.yview_scroll(int(-1 * (evento.delta / 120)), "units")
    canvas_categorias.bind("<Enter>", lambda e: canvas_categorias.bind_all("<MouseWheel>", _scroll_categorias))
    canvas_categorias.bind("<Leave>", lambda e: canvas_categorias.unbind_all("<MouseWheel>"))

    def filtrar_por_categoria():
        for i in frame_resultados_categorias.winfo_children():
            i.destroy()
    
        try:
            #Obtencion de datos de la categoria que selecciono el usuario
            cat_elegida = genero_filtro.get()
            conexion = sqlite3.connect("VentaLibros.db")
            cursor = conexion.cursor()
            cursor.execute("SELECT ID, TITULO, IMAGEN FROM LibrosBD WHERE CATEGORIA LIKE ?", ('%' + cat_elegida + '%',))
            libros_cat = cursor.fetchall()
            conexion.close()
        
            if not libros_cat:
                ctk.CTkLabel(frame_resultados_categorias, text=f"No hay obras que pertenezcan al género '{cat_elegida}'.", fg_color=COLOR_FONDO, text_color=COLOR_TEXTO_SUAVE).pack(pady=10)
                return
            

            libros_por_fila = LIBROS_POR_FILA
            for indice, libro in enumerate(libros_cat):
                id_db, titulo_db, blob_db = libro[0], libro[1], libro[2]
                fila_actual = (indice // libros_por_fila) * 2
                columna_actual = indice % libros_por_fila
            
                marco = ctk.CTkFrame(frame_resultados_categorias, fg_color=COLOR_PORTADA_FONDO, width=PORTADA_CUADRICULA[0], height=PORTADA_CUADRICULA[1], corner_radius=0, border_width=1, border_color=COLOR_BORDE, cursor="hand2")
                marco.pack_propagate(False)
                marco.grid(row=fila_actual, column=columna_actual, pady=(10, 2), padx=15)
                marco.bind("<Button-1>", lambda e, id_l=id_db: on_click(id_l))
            
                label_foto = ctk.CTkLabel(marco, text="", fg_color=COLOR_PORTADA_FONDO, cursor="hand2")
                label_foto.pack(expand=True, fill=tk.BOTH)
                label_foto.bind("<Button-1>", lambda e, id_l=id_db: on_click(id_l))
            
                if blob_db:
                    try:
                        img = io.BytesIO(blob_db)
                        img_pil = Image.open(img).resize(PORTADA_CUADRICULA)
                        img_tk = ImageTk.PhotoImage(img_pil)
                        label_foto.configure(image=img_tk)
                        lista_imagenes_tk.append(img_tk)
                    except:
                        label_foto.configure(text="ERROR", text_color=COLOR_PLACEHOLDER)
                else:
                    label_foto.configure(text="SIN FOTO", text_color=COLOR_PLACEHOLDER)
                
                titulo_label = ctk.CTkLabel(frame_resultados_categorias, text=titulo_db, fg_color=COLOR_FONDO, text_color=COLOR_TEXTO, font=ctk.CTkFont(family="Arial", size=9, weight="bold"), justify=LEFT, wraplength=PORTADA_CUADRICULA[0], cursor="hand2")
                titulo_label.grid(row=fila_actual + 1, column=columna_actual, sticky="nw", padx=15, pady=(0, 10))
                titulo_label.bind("<Button-1>", lambda e, id_l=id_db: on_click(id_l))
        except:
            messagebox.showwarning("Error", "Se ha producido un error")

    ctk.CTkButton(frame_filtro, text="Filtrar", command=filtrar_por_categoria, fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text_color="white", corner_radius=8).pack(side=LEFT, padx=10)
    filtrar_por_categoria()

def ir_a_carrito(frame_pantallas, usuario):
    # guarda los libros que se añadieron al carrito
    limpiar_pantalla(frame_pantallas)
    ctk.CTkLabel(frame_pantallas, text="🛒 Tu Carrito", font=ctk.CTkFont(family="Times New Roman", size=16, weight="bold"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO).pack(anchor="w", padx=30, pady=15)

    try:
        conexion = sqlite3.connect("VentaLibros.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT ID, LIBRO_ID, TITULO, PRECIO_UNITARIO, CANTIDAD FROM CARRITO WHERE USUARIO = ?", (usuario,))
        items_carrito = cursor.fetchall()
        conexion.close()
    except Exception as e:
        items_carrito = []
        messagebox.showerror("Error", f"No se pudo cargar el carrito: {e}")

    if not items_carrito:
        ctk.CTkLabel(frame_pantallas, text="Tu carrito está vacío. Agregá libros desde su ficha de compra.", fg_color=COLOR_FONDO, text_color=COLOR_TEXTO_SUAVE, font=ctk.CTkFont(family="Arial", size=11)).pack(anchor="w", padx=30)
        return

    frame_lista_carrito = ctk.CTkFrame(frame_pantallas, fg_color=COLOR_FONDO, corner_radius=0)
    frame_lista_carrito.pack(fill=BOTH, expand=True, padx=30, pady=10)

    for id_carrito, id_libro, titulo, precio, cantidad in items_carrito:
        fila = ctk.CTkFrame(frame_lista_carrito, fg_color=COLOR_TARJETA, corner_radius=10, border_width=1, border_color=COLOR_BORDE)
        fila.pack(fill=X, pady=6)

        frame_texto_item = ctk.CTkFrame(fila, fg_color=COLOR_TARJETA, corner_radius=0)
        frame_texto_item.pack(side=LEFT, fill=X, expand=True, padx=15, pady=10)
        ctk.CTkLabel(frame_texto_item, text=titulo, font=ctk.CTkFont(family="Arial", size=12, weight="bold"), fg_color=COLOR_TARJETA, text_color=COLOR_TEXTO).pack(anchor="w")
        ctk.CTkLabel(frame_texto_item, text=f'{cantidad} x ${precio:.2f}  =  ${cantidad * precio:.2f}', font=ctk.CTkFont(family="Arial", size=10), fg_color=COLOR_TARJETA, text_color=COLOR_TEXTO_SUAVE).pack(anchor="w", pady=(2, 0))

        def comprar_item(id_carrito=id_carrito, id_libro=id_libro, titulo=titulo, precio=precio, cantidad=cantidad):
            # ticket de compra
            def refrescar_tras_ticket():
                quitar_del_carrito(id_carrito)
                ir_a_carrito(frame_pantallas, usuario)
            procesar_compra(id_libro, titulo, precio, cantidad, usuario, frame_pantallas.winfo_toplevel(), accion_cerrar=refrescar_tras_ticket)

        def quitar_item(id_carrito=id_carrito):
            quitar_del_carrito(id_carrito)
            ir_a_carrito(frame_pantallas, usuario)

        ctk.CTkButton(fila, text="Comprar", command=comprar_item, fg_color=COLOR_VERDE, hover_color=COLOR_VERDE_HOVER, text_color="white", corner_radius=8, width=90).pack(side=LEFT, padx=(0, 8), pady=10)
        ctk.CTkButton(fila, text="Quitar", command=quitar_item, fg_color=COLOR_ERROR, hover_color="#6E2C2C", text_color="white", corner_radius=8, width=90).pack(side=LEFT, padx=(0, 15), pady=10)

def ir_a_reportes(frame_pantallas, usuario):
    limpiar_pantalla(frame_pantallas)
    ctk.CTkLabel(frame_pantallas, text="REPORTE DE ERRORES", font=ctk.CTkFont(family="Times New Roman", size=16, weight="bold"), fg_color=COLOR_FONDO, text_color=COLOR_TEXTO).pack(anchor="w", padx=30, pady=15)
    ctk.CTkLabel(frame_pantallas, text="Describa el error técnico detectado en el sistema:", fg_color=COLOR_FONDO, text_color=COLOR_TEXTO, font=ctk.CTkFont(family="Arial", size=10)).pack(anchor="w", padx=30, pady=5)
    caja_reporte = ctk.CTkTextbox(frame_pantallas, width=600, height=140, font=ctk.CTkFont(family="Arial", size=10), fg_color="white", border_width=1, border_color=COLOR_BORDE, text_color=COLOR_TEXTO)
    caja_reporte.pack(anchor="w", padx=30, pady=5)

    def enviar_comentario():
        comentario = caja_reporte.get("1.0", END).strip()
        if comentario == "":
            messagebox.showwarning("Reporte Vacío", "Por favor escriba un comentario antes de enviar.")
            return

        if Save_report(usuario, comentario):
            messagebox.showinfo("Report","Se envio el reporte correctamente")
            caja_reporte.delete("1.0", END)

    ctk.CTkButton(frame_pantallas, text="Enviar Reporte a Soporte", command=enviar_comentario, fg_color=COLOR_ERROR, hover_color="#6E2C2C", text_color="white", font=ctk.CTkFont(family="Arial", size=10, weight="bold"), corner_radius=8, height=38).pack(anchor="w", padx=30, pady=15)

def ventana_usuario(usuario):
    screen3 = ctk.CTkToplevel(Librerias.screen)
    screen3.title("LIBRERIA CAL")
    screen3.configure(fg_color=COLOR_FONDO)
    # Maximizar con after() para evitar el minimizado que a veces pasa en Windows
    screen3.after(200, lambda: maximizar_ventana(screen3))
    screen3.protocol("WM_DELETE_WINDOW", Librerias.screen.destroy)

    frame_lateral = ctk.CTkFrame(screen3, fg_color=COLOR_VERDE, width=250, corner_radius=0)
    frame_lateral.pack(side=LEFT, fill=Y, pady=10, padx=10)
    frame_lateral.pack_propagate(False)
    frame_lateral.columnconfigure(0, weight=1)

    Labeltitulo = ctk.CTkLabel(frame_lateral, text="📚 LIBRERIA CAL", fg_color=COLOR_VERDE_HOVER, text_color="white", font=ctk.CTkFont(family="Georgia", size=15, weight="bold"), corner_radius=10)
    Labeltitulo.grid(row=0, column=0, pady=(14, 4), padx=14, sticky="nsew", ipady=12)

    # Saludo con el nombre del usuario que inicio sesion
    etiqueta_saludo = ctk.CTkLabel(frame_lateral, text=f"👋 Bienvenido, {usuario}", fg_color=COLOR_VERDE, text_color="#DCEBD0", font=ctk.CTkFont(family="Arial", size=11, slant="italic"))
    etiqueta_saludo.grid(row=1, column=0, pady=(0, 14), padx=16, sticky="w")

    # Linea separadora sutil entre el encabezado y el menu de navegacion
    separador_menu = ctk.CTkFrame(frame_lateral, fg_color="#3A7A1B", height=1, corner_radius=0)
    separador_menu.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 14))

    # Tarjeta que agrupa los 4 botones del menu,sueltos directo sobre el verde de fondo.
    tarjeta_menu = ctk.CTkFrame(frame_lateral, fg_color=COLOR_VERDE_OSCURO, corner_radius=14)
    tarjeta_menu.grid(row=3, column=0, sticky="new", padx=14)
    tarjeta_menu.columnconfigure(0, weight=1)

    frame_pantallas = ctk.CTkFrame(screen3, fg_color=COLOR_FONDO, corner_radius=0)
    frame_pantallas.pack(side=RIGHT, fill=BOTH, expand=True)

    botoninicio = ctk.CTkButton(tarjeta_menu, anchor="w", text_color="white", fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text="🏠  Inicio", command=lambda: inicio_usuario(frame_pantallas, usuario), font=ctk.CTkFont(family="Arial", size=12, weight="bold"), corner_radius=10)
    botoninicio.grid(row=0, column=0, pady=(10, 6), padx=10, sticky="snew", ipady=10)

    botonlibros = ctk.CTkButton(tarjeta_menu, anchor="w", text_color="white", fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text="📚  Libros", command=lambda: ir_a_libros(frame_pantallas, usuario), font=ctk.CTkFont(family="Arial", size=12, weight="bold"), corner_radius=10)
    botonlibros.grid(row=1, column=0, pady=6, padx=10, sticky="snew", ipady=10)

    botoncategorias = ctk.CTkButton(tarjeta_menu, anchor="w", fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text_color="white", text="🏷️ Categorias", command=lambda: ir_a_categorias(frame_pantallas, usuario=usuario), font=ctk.CTkFont(family="Arial", size=12, weight="bold"), corner_radius=10)
    botoncategorias.grid(row=2, column=0, pady=6, padx=10, sticky="snew", ipady=10)

    botoncarrito = ctk.CTkButton(tarjeta_menu, anchor="w", text_color="white", fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text="🛒  Carrito", command=lambda: ir_a_carrito(frame_pantallas, usuario), font=ctk.CTkFont(family="Arial", size=12, weight="bold"), corner_radius=10)
    botoncarrito.grid(row=3, column=0, pady=6, padx=10, sticky="snew", ipady=10)

    botonreportes = ctk.CTkButton(tarjeta_menu, anchor="w", text_color="white", fg_color=COLOR_MARRON, hover_color=COLOR_MARRON_HOVER, text="⚠️  Reporte de errores", command=lambda: ir_a_reportes(frame_pantallas, usuario), font=ctk.CTkFont(family="Arial", size=12, weight="bold"), corner_radius=10)
    botonreportes.grid(row=4, column=0, pady=(6, 10), padx=10, sticky="snew", ipady=10)

    # Boton de cerrar sesion, separado del resto del menu
    boton_cerrar_sesion = ctk.CTkButton(frame_lateral, anchor="w", text_color="white", fg_color=COLOR_ERROR, hover_color="#6E2C2C", text="🚪  Cerrar sesión", command=lambda: cerrar_sesion(screen3), font=ctk.CTkFont(family="Arial", size=12, weight="bold"), corner_radius=10)
    boton_cerrar_sesion.grid(row=4, column=0, pady=(20, 10), padx=14, sticky="sew")
    frame_lateral.grid_rowconfigure(4, weight=1)

    # Arranca mostrando la vista de inicio por defecto
    inicio_usuario(frame_pantallas, usuario)