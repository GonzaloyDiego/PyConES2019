from interfaz import *
from PIL import Image
from stegano import lsb
import sys, os, codecs, binascii, Metadatos

# Leemos el contenido binario de un fichero y lo convertimos en UTF-8.
def procesarFichero(self, file_name):
    fich = open(file_name, "rb")
    hexadecimal = fich.read()
    fich.close()

    byte = codecs.encode(hexadecimal, "hex")

    return byte.decode("utf-8")

# A partir de un contenido, lo convertimos en hexadecimal y lo escribimos en un fichero.
def escribirFichero(self, file_name, content):
    error = False

    try:
        byte = content.encode("utf-8")
        hexadecimal = codecs.decode(byte, "hex")

        fich = open(file_name, "wb")
        fich.write(hexadecimal)
        fich.close()
    
    except binascii.Error:
        error = True
        self.listWidget.addItem("¡ERROR! El contenido extraído de las imágenes está dañado.")

# A partir de un contenido binario, lo convertimos en UTF-8.
def procesarContenido(self, content):
    byte = codecs.encode(content, "hex")
    
    return byte.decode("utf-8")

def obtener_firma(self, img_name, metadatos):
    if metadatos:
        firma = Metadatos.obtener_firma_img(self, img_name)          # Extrae la firma de la primera imagen empleando Metadatos.
    else:
        firma = lsb.reveal(img_name).split("#####")[0]               # Extrae la firma de la primera imagen empleando LSB.

    return firma

# A partir de un contenido, lo convertirmos en hexadecimal y lo devolvemos (solo para la firma).
def procesarFirma(self, firma):
    try:
        byte = firma.encode("utf-8")
        hexadecimal = codecs.decode(byte, 'hex')
        return hexadecimal
    
    except binascii.Error:
        self.listWidget.addItem("¡ERROR! No se ha podido procesar la firma.")

# Genera tantas imágenes como fragmentos tenga el fichero y en cada una de ellas almacena el contenido correspondiente.
def ocultar_en_imgs(self, fromdir, firma, extension, usar_metadatos):
    todir = fromdir[:fromdir.rfind('_')] + '_images/'   # De la ruta del directorio, nos quedamos con el nombre y le añadimos el sufijo '_images'

    # Creamos un directorio (si no existe).
    if not os.path.exists(todir):
        os.mkdir(todir)

    else:
        for fname in os.listdir(todir):
            # Si el directorio existe y tiene contenido, dejamos el directorio y eliminamos el contenido del directorio.
            os.remove(os.path.join(todir, fname))

    parts = os.listdir(fromdir)     # Generamos una lista con los fragmentos que hay en el directorio.
    parts.sort()

    firma = procesarContenido(self, firma)

    for index, part in enumerate(parts):
        content = procesarFichero(self, fromdir + part)

        part_name = part[:part.rfind('.')]

        if usar_metadatos:
            img = Image.open(self.lineEdit_3.text())
            img.save(todir + part_name + '.' + img.format.lower())
            newImage = Image.open(todir + part_name + '.' + img.format.lower())

            if 'part_001' in newImage.filename:
                Metadatos.ocultar_informacion(self, newImage.filename, 'firma', firma)
                Metadatos.ocultar_informacion(self, newImage.filename, 'extension', extension)

            Metadatos.ocultar_informacion(self, newImage.filename, 'contenido', content)
        
        else:
            img = Image.open(self.lineEdit_3.text())

            if img.format == 'JPEG':
                img.save(todir + part_name + '.png')
                newImage = Image.open(todir + part_name + '.png')
            else:
                img.save(todir + part_name + '.' + img.format.lower())
                newImage = Image.open(todir + part_name + '.' + img.format.lower())

            if 'part_001' in newImage.filename:
                secret = lsb.hide(newImage.filename, firma + "#####" + extension + "#####" + content)
                secret.save(newImage.filename)
                
            else:
                secret = lsb.hide(newImage.filename, content)
                secret.save(newImage.filename)

        os.remove(fromdir + part)
    
    os.rmdir(fromdir)

    return todir

# A partir de un directorio, obtenemos el contenido almacenado en cada una de las imágenes.
def recuperar_de_imgs(self, fromdir, usar_metadatos):
    todir = fromdir + '_parts'
    extension = ""
    content = ""

    # Creamos un directorio (si no existe).
    if not os.path.exists(todir):
        os.mkdir(todir)
    else:
        for fname in os.listdir(todir):
            # Si el directorio existe y tiene contenido, dejamos el directorio y eliminamos el contenido del directorio.
            os.remove(os.path.join(todir, fname))

    images = os.listdir(fromdir)
    images.sort()

    self.listWidget.addItem("Extrayendo información de las imágenes en el directorio {}...".format(fromdir))

    for index, image in enumerate(images):
        if usar_metadatos:
            if 'part_001' in image:
                extension = Metadatos.recuperar_informacion(self, fromdir + '/' + image, 'extension')
            
            content = Metadatos.recuperar_informacion(self, fromdir + '/' + image, 'contenido')

        else:
            if 'part_001' in image:
                try:
                    extension = lsb.reveal(fromdir + '/' + image).split("#####")[1]
                    content = lsb.reveal(fromdir + '/' + image).split("#####")[2]
                
                except IndexError:
                    self.listWidget.addItem("¡ERROR! No se ha podido obtener el tipo de archivo.")
            else:
                content = lsb.reveal(fromdir + '/' + image).split("#####")[0]

        nombre_fich = image[:image.rfind('.')] + '.enc'
        filename = os.path.join(todir, nombre_fich)
        escribirFichero(self, filename, content)    # Una vez que hemos extraído todo el contenido de las imágenes, lo escribimos en el fichero de destino.

    return (todir, extension)

def eliminarFragmentos(dir):
    fragmentos = os.listdir(dir)

    for fragment in fragmentos:
        os.remove(dir + '/' + fragment)

    os.rmdir(dir)