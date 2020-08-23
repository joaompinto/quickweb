import cherrypy

#  https://docs.cherrypy.org/en/latest/advanced.html#id14


# set the priority according to your needs if you are hooking something
# else on the 'before_finalize' hook point.
@cherrypy.tools.register("before_finalize", priority=60)
def secureheaders():
    headers = cherrypy.response.headers
    headers["X-Frame-Options"] = "DENY"
    headers["X-XSS-Protection"] = "1; mode=block"
    headers["Content-Security-Policy"] = "default-src 'self';"
