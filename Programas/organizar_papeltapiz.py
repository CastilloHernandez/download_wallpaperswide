from PIL import Image
import os
import shutil

# Ruta al directorio que contiene tus imágenes de fondo de pantalla
directorio_imagenes = "/media/emmanuel/T7/Imagenes/Papel tapiz"

# Obtén la lista de archivos en el directorio
archivos = os.listdir(directorio_imagenes)

# Itera a través de los archivos
for archivo in archivos:
    ruta_archivo = os.path.join(directorio_imagenes, archivo)
    
    # Verifica si el archivo es una imagen
    if os.path.isfile(ruta_archivo) and archivo.lower().endswith((".png", ".jpg", ".jpeg")):
        try:
            # Abre la imagen y obtén su tamaño
            imagen = Image.open(ruta_archivo)
            ancho, alto = imagen.size
            
            # Crea el directorio correspondiente al tamaño si no existe
            directorio_destino = os.path.join(directorio_imagenes, f"{ancho}x{alto}")
            os.makedirs(directorio_destino, exist_ok=True)
            
            # Mueve la imagen al directorio correspondiente
            shutil.move(ruta_archivo, os.path.join(directorio_destino, archivo))
            print(f"La imagen '{archivo}' se movió a '{directorio_destino}'")
        
        except Exception as e:
            print(f"Error al procesar '{archivo}': {str(e)}")

print("Proceso completado")
