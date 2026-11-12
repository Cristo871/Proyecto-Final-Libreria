#Funciones de apoyo que son usadas por varios modulos maximizar ventana 
#limpiar pantalla, cierre de sesion

from Librerias import *
import Librerias
import os  # se usa en crear_panel_decorativo para ubicar las imagenes de fondo

def maximizar_ventana(ventana):
    #Maximiza una ventana (Tk o Toplevel) para que ocupe toda la pantalla disponible
    try:
        # Funciona en Windows y en algunas versiones de linux
        ventana.state("zoomed")
    except:
        messagebox.showerror("Error","Error al cargar las ventanas")

def limpiar_pantalla(frame_pantallas):
    for widget in frame_pantallas.winfo_children():
        widget.destroy()
    lista_imagenes_tk.clear()

def cerrar_sesion(ventana_actual):
    if messagebox.askyesno("Cerrar sesión", "¿Seguro que quieres cerrar sesión?"):
        ventana_actual.destroy()
        Librerias.screen.deiconify()
        maximizar_ventana(Librerias.screen)