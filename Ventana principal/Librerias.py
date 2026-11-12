from tkinter import *
import tkinter as tk
import sqlite3
from tkinter import messagebox
#libreria para abrir los archivos de windows
from tkinter import filedialog  
from tkinter import ttk  
#libreria para modificar y adaptar las imagenes de la ventana
from PIL import Image, ImageTk
#libreri para la transformacion de la imagen de bytes a numeros binarios
import io
#Libreria para encriptar la contraseña
import hashlib
#decoracion
import customtkinter as ctk

# Variable global para mantener las imágenes
lista_imagenes_tk = []

# Tamaño de las portadas
PORTADA_LISTA = (90, 120)       # Miniaturas en listas de inventario (admin y librero)
PORTADA_CUADRICULA = (160, 215) # Miniaturas en cuadrícula (categorías y catálogo del usuario)
PORTADA_MODAL = (130, 175)      # Vista previa en formularios de añadir/editar libro
PORTADA_DETALLE = (150, 205)    # Portada grande en la ficha de detalles/compra del usuario

screen = None