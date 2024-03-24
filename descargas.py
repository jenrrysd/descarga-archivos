from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
import subprocess
from urllib.parse import unquote, urlparse, parse_qs

PORT = 9099

class CustomHttpRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        """Sobrescribe el método do_GET para manejar descargas."""
        # Parsear la URL y los parámetros de consulta
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)

        # Chequear si es una solicitud de descarga
        if 'download' in query:
            self.path = parsed_path.path
            self.send_response(200)
            self.send_header('Content-type', 'application/octet-stream')
            self.send_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(self.path))
            self.end_headers()
            try:
                with open(os.path.join('.', self.path), 'rb') as file:
                    self.wfile.write(file.read())
                return
            except Exception as e:
                self.send_error(404, "File not found")
                return

        # Si no es una solicitud de descarga, continuar con el comportamiento normal
        super().do_GET()

    def list_directory(self, path):
        """Genera un listado del directorio solicitado."""
        try:
            listing = os.listdir(path)
        except OSError:
            self.send_error(404, "No tiene permisos para listar el directorio")
            return None
        listing.sort(key=lambda a: a.lower())
        r = []
        try:
            displaypath = unquote(self.path)
            r.append('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
            r.append("<html>\n<title>Lista de Archivos %s</title>\n" % displaypath)
            r.append("<body>\n<h2>Lista de Archivos %s</h2>\n" % displaypath)
            r.append("<body>\n<h3>Ruta compartida: {}</h3>\n".format(self.ruta))
            r.append("<hr>\n<ul>\n")
            for name in listing:
                fullname = os.path.join(path, name)
                displayname = linkname = name
                if os.path.isdir(fullname):
                    displayname = name + "/"
                    linkname = name + "/"
                elif os.path.islink(fullname):
                    displayname = name + "@"
                # Agregar el parámetro de consulta 'download' para indicar una solicitud de descarga
                r.append('<li><a href="%s">%s</a>' % (linkname, displayname))
                if not os.path.isdir(fullname) and not os.path.islink(fullname):
                    r.append(' (<a href="%s?download=1">Descargar</a>)' % linkname)
                r.append('</li>\n')
            r.append("</ul>\n<hr>\n</body>\n</html>\n")
            encoded = ''.join(r).encode('utf-8', 'surrogateescape')
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
            return None
        except:
            self.send_error(404, "Error al crear la lista del directorio.")
            return None

def run(server_class=HTTPServer, handler_class=CustomHttpRequestHandler, port=PORT):
    # Obtener la dirección IP local automáticamente
    ip_local = subprocess.check_output("hostname -I | cut -f1 -d' '", shell=True).decode('utf-8').strip()
    # Pedir al usuario que ingrese la ruta
    ruta = input('Ingresa la ruta donde se mostrarán los archivos: ').strip()
    os.chdir(ruta)
    handler_class.ruta = ruta
    print(f"Los archivos se están mostrando en la ruta: {ruta}")
    print(f"Exponiendo HTTPD con la IP y puerto: {ip_local}:{port}")
    
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    run()
