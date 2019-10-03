from interfaz import *
import sys, os, codecs

from PIL import Image
from libxmp import XMPFiles, consts, XMPError, XMPMeta

# Oculta la información pasada por parámetro en los metadatos de una imagen.
def ocultar_informacion(self, img_name, tag, content):
    xmpfile = XMPFiles(file_path=img_name, open_forupdate=True)

    tipo = Image.open(img_name).format      # Obtenemos el tipo de la imagen.
        
    if tipo == 'JPEG':                      # Si la imagen es JPEG, almacenamos el contenido en los campos consts.XMP_NS_JPEG
        xmp = xmpfile.get_xmp()
        xmp.set_property(consts.XMP_NS_JPEG, tag, content)
        
    else:                                   # Si la imagen es PNG
        if xmpfile.get_xmp() is None:       # Comprobamos si tiene campos XMP, sino, creamos uno vacío.
            xmp = XMPMeta()
        else:                               # Si tiene campos XMP, los cogemos.
            xmp = xmpfile.get_xmp()
        
        xmp.set_property(consts.XMP_NS_PNG, tag, content)   # Almacenamos el contenido en los campos consts.XMP_NS_PNG
        
    xmpfile.put_xmp(xmp)
    xmpfile.close_file()

# Recupera la información almacenada en los metadatos de la imagen pasada por parámetro.
def recuperar_informacion(self, img_name, tag):
    xmpfile = XMPFiles(file_path=img_name)
    xmp = xmpfile.get_xmp()

    tipo = Image.open(img_name).format      # Obtenemos el tipo de la imagen.

    if tipo == 'JPEG':                      # Si la imagen es JPEG, obtenemos el contenido almacenado en los campos consts.XMP_NS_JPEG
        info = xmp.get_property(consts.XMP_NS_JPEG, tag)

    else:                                   # Si la imagen es PNG, obtenemos el contenido almacenado en los campos consts.XMP_NS_PNG
        info = xmp.get_property(consts.XMP_NS_PNG, tag)

    xmpfile.close_file()

    return info

# Extraemos la firma del archivo de la primera imagen.
def obtener_firma_img(self, img_name):
    return recuperar_informacion(self, img_name, 'firma')

# Obtenemos el tipo de un archivo a partir del contenido hexadecimal de este.
def get_tipo(self, file_name):
    tipo = ""

    fich = open(file_name, "rb")
    content = fich.read()

    bytes = codecs.encode(content, 'hex')
    churro = bytes.decode('utf-8').upper()

    tipos = [ 
            ('D0CF11E0A1B11AE1', '576F72642E446F63756D656E742E', '.doc'),
            ('504B030414', '776F7264', '.docx'),
            ('504B030414', '70726573656E746174696F6E', '.pptx'),
            ('504B030414', '776F726B736865657473', '.xlsx'),
            ('25504446', '.pdf'),
            ('2525454F46', '.pdf'),
            ('66747970', '.mp4'),
            ('474946383961', '.gif'),
            ('474946383761', '.gif'),
            ('FFD8FFE800104A46494600', 'FFD9', '.jpg'),
            ('FFD8FFE100104A46494600', 'FFD9', '.jpg'),
            ('FFD8FFE000104A46494600', 'FFD9', '.jpg'),
            ('FFD8FFE300104A46494600', 'FFD9', '.jpeg'),
            ('FFD8FFE200104A46494600', 'FFD9', '.jpeg'),
            ('89504E47', '.png'),
            ]

    i = 0
    cont = 0

    encontrado = False

    while i < len(tipos) and encontrado == False:

        if len(tipos[i]) == 2 and '494433' in churro[:6]:   # Este caso es solo para ficheros .mp3
            encontrado = True
            tipo = '.mp3'

        elif len(tipos[i]) == 2 and 'FFD9' in churro[len(churro)-4:]:
            encontrado = True
            tipo = '.jpg'

        elif len(tipos[i]) == 2 and tipos[i][0] in churro:
            encontrado = True
            tipo = tipos[i][1]

        elif len(tipos[i]) == 3 and tipos[i][0] in churro and tipos[i][1] in churro:
            encontrado = True
            tipo = tipos[i][2]

        i += 1

    if encontrado == False:
        self.listWidget.addItem("Fich no soportado")
        return

    return tipo

self.get_tipo(self, 'Resumen_Examen_IR.pdf')