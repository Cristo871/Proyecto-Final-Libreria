from Librerias import *
import Librerias
from funciones_compartidas import maximizar_ventana
from BDS import bd_libros, tabla_comentarios, tabla_ventas, tabla_usuarios, tabla_carrito
from ventana_administrador import registro, ventana_admin
from Ventana_librero import ventana_librero
from ventana_usuario import ventana_usuario

# Paleta de colores
COLOR_FONDO = "#F4EFE6"        # crema/pergamino
COLOR_TARJETA = "#FFFDF8"      # blanco hueso para la tarjeta del formulario
COLOR_SOMBRA = "#DCCFB4"       # color de la "sombra" detras de la tarjeta
COLOR_BORDE = "#D8C9A8"        # borde tipo madera clara
COLOR_TEXTO = "#3E2B1F"        # marron oscuro, mas calido que negro puro
COLOR_TEXTO_SUAVE = "#8A7864"  # marron grisaceo para textos secundarios
COLOR_VERDE = "#216300"        # verde principal
COLOR_VERDE_HOVER = "#184A00"
COLOR_MARRON = "#7C5A3A"       # marron madera para el boton secundario
COLOR_MARRON_HOVER = "#5F4429"


def InicioDeSesion(cajanombre, cajacontraseña):
    usuarioI = cajanombre.get()
    contraseñaI = cajacontraseña.get()
    try:
        conexion = sqlite3.connect("RegistroDeUsuarios.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT USUARIO, PASSWORD, ROL FROM UsuariosBD WHERE USUARIO = ?",(usuarioI,))
        resultado = cursor.fetchone()
        conexion.close()

        if resultado:
            usuarioReal = resultado[0]
            contraseñaReal = resultado[1]  
            contraseña_encriptada = hashlib.sha256(contraseñaI.encode()).hexdigest()
            Rol = resultado[2]  
            
            if usuarioI == usuarioReal and contraseña_encriptada == contraseñaReal:
                messagebox.showinfo("Acceso Concedido", f"¡Bienvenido {usuarioI}!")
                Librerias.screen.withdraw()
                
                # Ejecuta la ventana independiente correspondiente al rol
                if Rol == "Administrador":
                    ventana_admin()
                elif Rol == "Librero":
                    ventana_librero()
                elif Rol == "usuario":
                    ventana_usuario(usuarioI)
            else:
                messagebox.showwarning("¡ACCESO DENEGADO!", "Usuario o Contraseña incorrecta")
        else:
            messagebox.showwarning("¡ERROR!", "Ocurrio un error inesperado al iniciar sesion")
            
    except Exception as e:
        messagebox.showwarning("¡ERROR!", f"Ocurrio un error en la busqueda de informacion del usuario: {e}")

# Ventana Principal
screen = ctk.CTk()
Librerias.screen = screen  # guardamos la referencia global para que las demas ventanas (admin, librero, usuario, registro) puedan usarla como ventana "padre"
screen.title("LIBRERIA CAL")
screen.configure(fg_color=COLOR_FONDO)
screen.resizable(True, True)

# Maximizamos con after() para evitar error de windows
screen.after(200, lambda: maximizar_ventana(screen))

bd_libros()
tabla_comentarios()
tabla_ventas()
tabla_usuarios()
tabla_carrito()

# frame contenedor que ocupa toda la pantalla
frame_contenedor = ctk.CTkFrame(screen, fg_color=COLOR_FONDO)
frame_contenedor.pack(fill=BOTH, expand=True)

# Contenedor de tamaño fijo donde se superponen las etiquetas
contenedor_tarjeta = ctk.CTkFrame(frame_contenedor, fg_color="transparent", width=420, height=560)
contenedor_tarjeta.place(relx=0.5, rely=0.5, anchor="center")

sombra_tarjeta = ctk.CTkFrame(contenedor_tarjeta, fg_color=COLOR_SOMBRA, corner_radius=22, width=380, height=520)
sombra_tarjeta.place(relx=0.5, rely=0.5, anchor="center")

frame_iniciodesesion = ctk.CTkFrame(
    contenedor_tarjeta,
    fg_color=COLOR_TARJETA,
    corner_radius=22,
    border_width=1,
    border_color=COLOR_BORDE,
    width=380,
    height=520,
)
frame_iniciodesesion.place(relx=0.5, rely=0.5, anchor="center")
frame_iniciodesesion.grid_columnconfigure(1, weight=1)

contraseña = StringVar()

etiquetatitulo = ctk.CTkLabel(
    frame_iniciodesesion,
    text="📚 LIBRERIA CAL",
    font=ctk.CTkFont(family="Georgia", size=28, weight="bold"),
    text_color=COLOR_VERDE,
)
etiquetatitulo.grid(row=0, column=1, padx=10, pady=(30, 2), sticky="snew")

etiquetanombre = ctk.CTkLabel(
    frame_iniciodesesion,
    text="👤 Nombre de usuario",
    font=ctk.CTkFont(family="Arial", size=13),
    text_color=COLOR_TEXTO,
    anchor="w",
)
etiquetanombre.grid(row=2, column=1,padx=25,pady=(0, 4),sticky="snew")

cajanombre = ctk.CTkEntry(
    frame_iniciodesesion,
    font=ctk.CTkFont(family="Arial", size=13),
    height=40,
    corner_radius=8,
    border_color=COLOR_BORDE,
    fg_color="white",
    text_color=COLOR_TEXTO
)
cajanombre.grid(row=3,column=1,padx=25,pady=(0, 16),sticky="snew")

etiquetacontraseña = ctk.CTkLabel(
    frame_iniciodesesion,
    text="🔒 Contraseña",
    font=ctk.CTkFont(family="Arial", size=13),
    text_color=COLOR_TEXTO,
    anchor="w",
)
etiquetacontraseña.grid(row=4, column=1,padx=25,pady=(0, 4),sticky="snew")

cajacontraseña = ctk.CTkEntry(
    frame_iniciodesesion,
    show="*",
    textvariable=contraseña,
    font=ctk.CTkFont(family="Arial", size=13),
    height=40,
    corner_radius=8,
    border_color=COLOR_BORDE,
    fg_color="white",
    text_color=COLOR_TEXTO,
)
cajacontraseña.grid(row=5, column=1, pady=(0, 26), padx=25, sticky="snew")

botoninicio = ctk.CTkButton(
    frame_iniciodesesion,
    text="INICIAR SESIÓN",
    command=lambda: InicioDeSesion(cajanombre, cajacontraseña),
    font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
    height=44,
    corner_radius=8,
    fg_color=COLOR_VERDE,
    hover_color=COLOR_VERDE_HOVER,
    text_color="white",
)
botoninicio.grid(row=6, column=1,pady=(0, 10),padx=25,sticky="snew")

pregunta = ctk.CTkLabel(
    frame_iniciodesesion,
    text="¿No tienes cuenta?",
    font=ctk.CTkFont(family="Arial", size=11),
    text_color=COLOR_TEXTO_SUAVE,
)
pregunta.grid(row=7, column=1, pady=(4, 4))

botonregistro = ctk.CTkButton(
    frame_iniciodesesion,
    text="REGISTRARSE",
    command=registro,
    font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
    height=44,
    corner_radius=8,
    fg_color="transparent",
    hover_color=COLOR_BORDE,
    border_width=1.5,
    border_color=COLOR_MARRON,
    text_color=COLOR_MARRON,
)
botonregistro.grid(row=8, column=1, pady=(0, 30),padx=25, sticky="snew")

screen.mainloop()