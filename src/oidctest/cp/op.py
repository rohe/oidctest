import cherrypy
from cherrypy import url


class WebFinger(object):
    @cherrypy.expose
    def index(self):
        _path = url(qs=cherrypy.request.query_string)
        return ''


class ProviderInfo(object):
    @cherrypy.expose
    def index(self):
        pass


class Authorization(object):
    @cherrypy.expose
    def index(self):
        pass


class Token(object):
    @cherrypy.expose
    def index(self):
        pass


class UserInfo(object):
    @cherrypy.expose
    def index(self):
        pass


if __name__ == '__main__':

    cherrypy.tree.mount(WebFinger(), '/.wellknown/webfinger')
    cherrypy.tree.mount(ProviderInfo(), '/.wellknown/openid')
    cherrypy.tree.mount(Authorization(), '/authorization')
    cherrypy.tree.mount(Token(), '/token')
    cherrypy.tree.mount(UserInfo(), '/userinfo')

    cherrypy.engine.start()
    cherrypy.engine.block()

