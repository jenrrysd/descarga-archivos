import http.server
import socketserver
import os
import subprocess

PORT = 8090

def obtener_ip_servidor():
    try:
        ip = subprocess.check_output("ip route | awk '{print $9}' | head -1", shell=True).decode().strip()
        return ip
    except Exception as e:
        print(f"No se pudo determinar la dirección IP del servidor debido a: {e}")
        return '127.0.0.1'

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Asegúrate de llamar a end_headers antes de agregar tus propias cabeceras
        super().end_headers()



    def list_directory(self, path):
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(http.server.HTTPStatus.NOT_FOUND, "No se pudo listar el directorio")
            return None
        list.sort(key=lambda a: a.lower())
        r = []
        try:
            displaypath = os.path.relpath(path, self.directory)
            r.append('<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8">\n<title>Compartido %s</title>\n</head>'
                     % displaypath)
            r.append(f'<body>\n<h2>Directorio compartido: {ruta} </h2>')
            r.append('<ul>')
            for name in list:
                fullname = os.path.join(path, name)
                displayname = linkname = name
                # Append `/` for directories or `@` for symbolic links
                if os.path.isdir(fullname):
                    displayname = name + "/"
                    linkname = name + "/"
                if os.path.islink(fullname):
                    displayname = name + "@"
                    # Note: a link to a directory displays with @ and links with /
                r.append('<li><a href="%s">%s</a>' % (linkname, displayname))
                if not os.path.isdir(fullname):
                    r.append(' <a href="%s" download>[Descargar]</a>' % (linkname))
                r.append('</li>')
            r.append('</ul>\n<hr>\n</body>\n</html>\n')
            encoded = '\n'.join(r).encode('utf-8', 'surrogateescape')
            f = http.server.io.BytesIO()
            f.write(encoded)
            f.seek(0)
            self.send_response(http.server.HTTPStatus.OK)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            return f
        except:
            self.send_error(http.server.HTTPStatus.NOT_FOUND, "Error al listar el directorio")
            return None

# Solicitar la ruta al usuario
ruta = input("Por favor, ingresa la ruta de la carpeta a compartir: ")
if not os.path.isdir(ruta):
    print("La ruta especificada no existe o no es una carpeta.")
    exit(1)

os.chdir(ruta)  # Cambiar al directorio especificado

ip_servidor = obtener_ip_servidor()
print(f"----------------------------------------------------")
print(f"Ingresar a la dirección: http://{ip_servidor}:{PORT}")    

handler = CustomHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), handler)

print(f"----------------------------------------------------")
print(f"-----------EL SERVIDOR ESTA CORRIENDO---------------")
httpd.serve_forever()
