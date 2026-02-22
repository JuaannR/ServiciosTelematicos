# coding=utf-8
#!/usr/bin/env python3

import socket
import selectors    #https://docs.python.org/3/library/selectors.html
import select
import types        # Para definir el tipo de datos data
import argparse     # Leer parametros de ejecución
import os           # Obtener ruta y extension
from datetime import datetime, timedelta # Fechas de los mensajes HTTP
import time         # Timeout conexión
import sys          # sys.exit
import re           # Analizador sintáctico
import logging      # Para imprimir logs
from email.utils import formatdate



BUFSIZE = 8192 # Tamaño máximo del buffer que se puede utilizar
TIMEOUT_CONNECTION = 10+5+3+1+5 # Timout para la conexión persistente
MAX_ACCESOS = 10

Solicitud_HTTP = r"^(GET|POST) (/[^ ]*) (HTTP)(/)(1\.1)$"
Error = r"Error [0-9]+ ."

# Extensiones admitidas (extension, name in HTTP)
filetypes = {"gif":"image/gif", "jpg":"image/jpg", "jpeg":"image/jpeg", "png":"image/png", "htm":"text/htm", 
             "html":"text/html", "css":"text/css", "js":"text/js"}

# Configuración de logging
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s.%(msecs)03d] [%(levelname)-7s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()

# Crear un handler que escriba en un archivo
file_handler = logging.FileHandler("servidor.log", mode='w')  # "a" para append, "w" para sobrescribir

# Configurar el formato para este handler
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] [%(levelname)-7s] %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

# Añadir el handler al logger
logger.addHandler(file_handler)


#Envia datos a través del socket cliente (cs)
#Retorna el número de bytes enviados
def enviar_mensaje(cs, data):
    return cs.send(data)
    pass

#Recibe datos a través del socket cliente (cs)
# Se leen los datos y se convierten a string

def recibir_mensaje(cs):
    data = cs.recv(BUFSIZE)
    return data.decode()
    pass

# Cerrar conexión activa
def cerrar_conexion(cs):
    cs.close()
    pass


def process_cookies(headers,  cs):
    """ Esta función procesa la cookie cookie_counter
        1. Se analizan las cabeceras en headers para buscar la cabecera Cookie
        2. Una vez encontrada una cabecera Cookie se comprueba si el valor es cookie_counter
        3. Si no se encuentra cookie_counter , se devuelve 1
        4. Si se encuentra y tiene el valor MAX_ACCESSOS se devuelve MAX_ACCESOS
        5. Si se encuentra y tiene un valor 1 <= x < MAX_ACCESOS se incrementa en 1 y se devuelve el valor
    """
    pass

#CONSTANTE GLOBAL PARA INDICAR EL NOMBRE DEL SERVIDOR
SERVER_NAME = "web.nombreorganizacionXXYY.org"
EMAILS_VALIDOS = ["domingo@um.es", "juan@um.es"]

#Envia una respuesta HTTP de error correctamente formada
def enviar_error(cs, codigo, mensaje, descripcion):
    
    cuerpo = (
    "<!DOCTYPE html>\n"
    "<html lang=\"es\">\n"
    "<head>\n"
    "    <meta charset=\"UTF-8\">\n"
    "    <title>{} - {}</title>\n"
    "    <style>\n"
    "        body {{\n"
    "            font-family: Arial, sans-serif;\n"
    "            background-color: #f2f2f2;\n"
    "            text-align: center;\n"
    "            padding-top: 80px;\n"
    "        }}\n"
    "        h1 {{\n"
    "            font-size: 48px;\n"
    "            color: #333;\n"
    "        }}\n"
    "        p {{\n"
    "            font-size: 20px;\n"
    "            color: #666;\n"
    "        }}\n"
    "        a {{\n"
    "            color: #007BFF;\n"
    "            text-decoration: none;\n"
    "        }}\n"
    "        a:hover {{\n"
    "            text-decoration: underline;\n"
    "        }}\n"
    "    </style>\n"
    "</head>\n"
    "<body>\n"
    "    <h1>{} {}</h1>\n"                   
    "    <p>{}</p>\n"                        
    "    <p><a href=\"/\">Volver al inicio</a></p>\n"
    "</body>\n"
    "</html>\n"
    ).format(codigo, descripcion, codigo, mensaje, descripcion)
    logger.info("Cuerpo error recibido:\n" + cuerpo)
    cuerpo_bytes = cuerpo.encode()
    content_length = len(cuerpo_bytes)
    fecha = formatdate(timeval=None, localtime=False, usegmt=True)
    
    respuesta = (
        "HTTP/1.1 {} {}\r\n"
        "Server: {}\r\n"
        "Date: {}\r\n"
        "Content-Type: text/html\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(codigo, mensaje, SERVER_NAME, fecha, content_length)
    logger.info("Respuesta error:\n" + respuesta)
    cs.send(respuesta.encode())
    cs.send(cuerpo_bytes)

    """#Cuerpo HTML del error
    cuerpo = (
    "<html>\r\n"
    "<head><title>{} {}</title></head>\r\n"
    "<body>\r\n"
    "<h1>{} {}</h1>\r\n"
    "<p>{}</p>\r\n"
    "</body>\r\n"
     "</html>"
    ).format(codigo, mensaje, codigo, mensaje, descripcion)
    #logger.info("Cuerpo error recibido:\n" + cuerpo)
    cuerpo_bytes = cuerpo.encode()
    content_length = len(cuerpo_bytes)
    fecha = formatdate(timeval=None, localtime=False, usegmt=True)
    
    respuesta = (
        "HTTP/1.1 {} {}\r\n"
        "Server: {}\r\n"
        "Date: {}\r\n"
        "Content-Type: text/html\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(codigo, mensaje, SERVER_NAME, fecha, content_length)
    #logger.info("Respuesta error:\n" + respuesta)
    cs.send(respuesta.encode())
    cs.send(cuerpo_bytes)""" 
    
def construir_respuesta(codigo_de_estado, nombre_servidor, fecha, content_type, tam, timeout):
    respuesta = (
        "HTTP/1.1 {}\r\n"
        "Server: {}\r\n"
        "Date: {}\r\n"
        "Content-Type: {}\r\n"
        "Content-Length: {}\r\n"
        "Connection: keep-alive\r\n"
        "Keep-Alive: timeout={}\r\n"
        "\r\n"
    ).format(codigo_de_estado, nombre_servidor, fecha, content_type, tam, TIMEOUT_CONNECTION)
    return respuesta
def enviar_html(cs, email):
    cuerpo = (
    "<!DOCTYPE html>\n"
    "<html lang=\"es\">\n"
    "<head>\n"
    "    <meta charset=\"UTF-8\">\n"
    "    <title>Email válido</title>\n"
    "    <style>\n"
    "        body {{\n"
    "            font-family: Arial, sans-serif;\n"
    "            background-color: #e8ffe8;\n"
    "            text-align: center;\n"
    "            padding-top: 80px;\n"
    "        }}\n"
    "        h1 {{\n"
    "            font-size: 42px;\n"
    "            color: #2e7d32;\n"
    "        }}\n"
    "        p {{\n"
    "            font-size: 22px;\n"
    "            color: #444;\n"
    "        }}\n"
    "        a {{\n"
    "            color: #0066cc;\n"
    "            text-decoration: none;\n"
    "        }}\n"
    "        a:hover {{\n"
    "            text-decoration: underline;\n"
    "        }}\n"
    "    </style>\n"
    "</head>\n"
    "<body>\n"
    "    <h1>✔ Email válido</h1>\n"
    "    <p>El email <strong>{}</strong> está autorizado.</p>\n"
    "    <p><a href=\"/\">Volver al inicio</a></p>\n"
    "</body>\n"
    "</html>\n"
    ).format(email)
    #logger.info("Cuerpo error recibido:\n" + cuerpo)
    cuerpo_bytes = cuerpo.encode()
    content_length = len(cuerpo_bytes)
    fecha = formatdate(timeval=None, localtime=False, usegmt=True)
    
    respuesta = (
        "HTTP/1.1 {}\r\n"
        "Server: {}\r\n"
        "Date: {}\r\n"
        "Content-Type: text/html\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format("200 OK", SERVER_NAME, fecha, content_length)
    logger.info("Respuesta error:\n" + respuesta)
    cs.send(respuesta.encode())
    cs.send(cuerpo_bytes)

def process_web_request(cs, webroot):

    # "lista" con el socket que esta escucahndo
    rlist, _, _ = select.select([cs], [], [], TIMEOUT_CONNECTION)

    #Persistencia HTTP
    # mientras el cliente este conectado (no salta el timeout) el servidor procesa peticiones por ese socket
    while len(rlist) == 1:
        logger.info("Se establece conexión")
        # Solo nos interesa rlist para lectura
        
        # si el cliente envia mensaje sin datos (el navegador ha cerrado la conexión) se deja de procesar request
        datos = recibir_mensaje(cs)
        if not datos:
            logger.info("No se recibieron datos")
            break
        logger.info("Datos recibidos:\n" + datos)
        # Aquí iría el procesamiento de HTTP
        
        
        
        # Separar cabeceras del cuerpo
        cabezera, _, body = datos.partition("\r\n\r\n")  
        linea_cabezera = cabezera.split("\r\n")

        #Verificar que existe la cabecera host
        host_presente = any(line.startswith("Host:") for line in linea_cabezera)
        
        if not host_presente:
            logger.info("Error 400 Bad Request - Host requerido")
            enviar_error(cs, 400, "Bad Request", "Host requerido")
            break
            
 
        
        
        
        
        #Si no hay línea de solicitud -> Petición mal formada
        if len(linea_cabezera) == 0:
            logger.info("Error 400 Bad Request")
            enviar_error(cs, 400, "Bad Request", "Peticion mal formada")
            break
        
        #Analizar línea de solicitud
        #Se espera GET /ruta HTTP/1.1
        linea_solicitad = linea_cabezera[0]
        
        m = re.match(Solicitud_HTTP, linea_solicitad)
        
        #Si no se cumple el patrón -> Petición mal formada
        if not m:
            logger.info("Error 400 Bad Request")
            enviar_error(cs, 400, "Bad Request", "Peticion mal formada")
            break
        #logger.info("No falla la expresion regular")
        
        #Extraer partes de la linea
        metodo = m.group(1) #GET o POST
        ruta = m.group(2) # /index.html
        formato = m.group(3) #redundante
        ralla = m.group(4) #redundante
        version = m.group(5) # 1.1
        
        # Validar método -> Solo se permite GET #### SE PERMITE POST TAMBIEN
        if metodo != "GET" and metodo != "POST":
            logger.info("Error 405 Method Not Allowed")
            enviar_error(cs, 405, "Method Not Allowed", "Metodo no permitido")
            break

        #Validar versión HTTP -> Solo se permite HTTP/1.1
        if version != "1.1":
            logger.info("Error 505 HTTP Version Not Supported")
            enviar_error(cs, 505, "HTTP Version Not Supported", "Version HTTP no soportada")
            break
        
        if ruta == "/":
            ruta = "/index.html"
            # Construir ruta absoluta del fichero
            ruta_completa = os.path.join(webroot, ruta.lstrip("/"))
        else :
            ruta_completa = os.path.join(webroot, ruta.lstrip("/"))
            email = ruta_completa.split("?")[-1]
            email = ruta_completa.split("=")[-1]
            email = email.replace("%40", "@")
            
        

        # Verficar que el fichero existe
        """if not os.path.isfile(ruta_completa):
            logger.info("Error 404 Not Found")
            enviar_error(cs, 404, "Not Found", "El recurso solicitado no existe")
            break"""
        
        if os.path.isfile(ruta_completa):
        
            #Si el fichero existe, enviamos 200 OK
            tam = os.path.getsize(ruta_completa)
            
            #Obtener extensión
            ext = ruta_completa.split(".")[-1]  #se queda con lo ultimo -> hola.png -> png
            content_type = filetypes[ext]
            #content_type = filetypes.get(ext, "application/octet-stream")
            
            # Fecha HTTP correcta
            fecha = formatdate(timeval=None, localtime=False, usegmt=True)

            # Construir respuesta 200 OK
            respuesta = construir_respuesta("200 OK", SERVER_NAME, fecha, content_type, tam, TIMEOUT_CONNECTION)
            
            # Enviar cabeceras
            cs.send(respuesta.encode())
            logger.info("Respuesta enviada: \r\n" + respuesta)

            # Enviar fichero en bloques
            with open(ruta_completa, "rb") as f:
                tamano = os.path.getsize(ruta_completa)
                inicio = 0
                while tamano > BUFSIZE:
                    #logger.info("Hacesmos")
                    f.seek(inicio)
                    bloque = f.read(BUFSIZE)
                    inicio+=BUFSIZE
                    tamano-=BUFSIZE
                    cs.send(bloque)
                f.seek(inicio)
                envio = f.read(tamano)
                cs.send(envio)
        elif email in EMAILS_VALIDOS:
            logger.info("Email valido: " + email)
            enviar_html(cs, email)
        else:
            # Verficar que el fichero existe
            logger.info("Error 404 Not Found")
            enviar_error(cs, 404, "Not Found", "El recurso solicitado no existe")
            break
            
        

        rlist, _, _ = select.select([cs], [], [], TIMEOUT_CONNECTION)
    
     
    if not rlist:
        logger.info("Se alcanzó el TIMEOUT sin respuestas")
            
    logger.info("Se cierra conexión")

    
    """ Procesamiento principal de los mensajes recibidos.
        Típicamente se seguirá un procedimiento similar al siguiente (aunque el alumno puede modificarlo si lo desea)

        * Bucle para esperar hasta que lleguen datos en la red a través del socket cs con select()

            * Se comprueba si hay que cerrar la conexión por exceder TIMEOUT_CONNECTION segundos
              sin recibir ningún mensaje o hay datos. Se utiliza select.select

            * Si no es por timeout y hay datos en el socket cs.
                * Leer los datos con recv.
                * Analizar que la línea de solicitud y comprobar está bien formateada según HTTP 1.1
                    * Devuelve una lista con los atributos de las cabeceras.
                    * Comprobar si la versión de HTTP es 1.1
                    * Comprobar si es un método GET o POST. Si no devolver un error Error 405 "Method Not Allowed".
                    * Leer URL y eliminar parámetros si los hubiera
                    * Comprobar si el recurso solicitado es /, En ese caso el recurso es index.html
                    * Construir la ruta absoluta del recurso (webroot + recurso solicitado)
                    * Comprobar que el recurso (fichero) existe, si no devolver Error 404 "Not found"
                    * Analizar las cabeceras. Imprimir cada cabecera y su valor. Si la cabecera es Cookie comprobar
                      el valor de cookie_counter para ver si ha llegado a MAX_ACCESOS.
                      Si se ha llegado a MAX_ACCESOS devolver un Error "403 Forbidden"
                    * Obtener el tamaño del recurso en bytes.
                    * Extraer extensión para obtener el tipo de archivo. Necesario para la cabecera Content-Type
                    * Preparar respuesta con código 200. Construir una respuesta que incluya: la línea de respuesta y
                      las cabeceras Date, Server, Connection, Set-Cookie (para la cookie cookie_counter),
                      Content-Length y Content-Type.
                    * Leer y enviar el contenido del fichero a retornar en el cuerpo de la respuesta.
                    * Se abre el fichero en modo lectura y modo binario
                        * Se lee el fichero en bloques de BUFSIZE bytes (8KB)
                        * Cuando ya no hay más información para leer, se corta el bucle

            * Si es por timeout, se cierra el socket tras el período de persistencia.
                * NOTA: Si hay algún error, enviar una respuesta de error con una pequeña página HTML que informe del error.
    """


def main():
    """ Función principal del servidor
    """

    try:

        # Argument parser para obtener la ip y puerto de los parámetros de ejecución del programa. IP por defecto 0.0.0.0
        parser = argparse.ArgumentParser()
        parser.add_argument("-p", "--port", help="Puerto del servidor", type=int, required=True)
        parser.add_argument("-ip", "--host", help="Dirección IP del servidor o localhost", required=True)
        parser.add_argument("-wb", "--webroot", help="Directorio base desde donde se sirven los ficheros (p.ej. /home/user/mi_web)")
        parser.add_argument('--verbose', '-v', action='store_true', help='Incluir mensajes de depuración en la salida')
        args = parser.parse_args()


        if args.verbose:
            logger.setLevel(logging.DEBUG)

        logger.info('Enabling server in address {} and port {}.'.format(args.host, args.port))

        logger.info("Serving files from {}".format(args.webroot))

        socket_server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0) # Crear socket TCP
        socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permitir reusar la misma dirección
        socket_server.bind((args.host, args.port)) # Vincular el socket a una IP y puerto elegidos
        socket_server.listen() # Escuchar conexiones entrantes

        while True:
            conn, _ = socket_server.accept() # Aceptamos la conexión entrante
            pid = os.fork() # Crear un proceso hijo
            if pid == 0: # Proceso hijo
                cerrar_conexion(socket_server) # Cerrar el socket del padre
                process_web_request(conn, args.webroot) # Procesar la petición del cliente en el socket especifico
                cerrar_conexion(conn) # Cerrar la conexión con el cliente / se cierra el socket especifico del cliente
                sys.exit(0)
            else: # Proceso padre
                cerrar_conexion(conn) # Cerrar el socket especifico del hijo y sigo escuchando por socket_server

        '''
        while True:
            conn, _ = socket_server.accept()
            process_web_request(conn, args.webroot)
            cerrar_conexion(conn)
            CODIGO DE PRUEBA PARA WINDOS, PORQUE EL FORK PETA :)
        '''
        
        """ Funcionalidad a realizar
        * Crea un socket TCP (SOCK_STREAM)
        * Permite reusar la misma dirección previamente vinculada a otro proceso. Debe ir antes de sock.bind
        * Vinculamos el socket a una IP y puerto elegidos

        * Escucha conexiones entrantes

        * Bucle infinito para mantener el servidor activo indefinidamente
            - Aceptamos la conexión

            - Creamos un proceso hijo

            - Si es el proceso hijo se cierra el socket del padre y procesar la petición con process_web_request()

            - Si es el proceso padre cerrar el socket que gestiona el hijo.
        """
    except KeyboardInterrupt:
        cerrar_conexion(socket_server)
        sys.exit(0)

if __name__== "__main__":
    main()