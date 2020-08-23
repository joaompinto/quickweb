import cherrypy


class RootServer:
    @cherrypy.expose
    def index(self, **keywords):
        return "it works!"


if __name__ == "__main__":
    server_config = {
        "server.socket_host": "0.0.0.0",
        "server.socket_port": 8443,
        "server.ssl_certificate": "cert.pem",
        "server.ssl_private_key": "privkey.pem",
    }

    cherrypy.config.update(server_config)
    cherrypy.quickstart(RootServer())
