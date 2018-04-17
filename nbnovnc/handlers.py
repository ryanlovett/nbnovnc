import configparser
import socket
import tempfile

from notebook.utils import url_path_join as ujoin

from traitlets import Unicode, Integer
from traitlets.config.configurable import Configurable

from nbserverproxy.handlers import AddSlashHandler, SuperviseAndProxyHandler

class NBNoVNC(Configurable):
    desktop_session = Unicode(u"openbox --startup .config/openbox/autostart",
        help="Command to start desktop session.", config=True)
    websocket_wait = Integer(3,
        help="Wait in seconds before connecting to websocket.", config=True)
    geometry = Unicode(u"1024x768", help="Desktop geometry.", config=True)
    depth = Integer(24, help="Desktop display depth.", config=True)

class SupervisorHandler(SuperviseAndProxyHandler):
    '''Manage a novnc instance along with websockify and a VNC server.'''

    name = 'supervisord'
    
    def initialize(self, state):
        super().initialize(state)
        self.c = NBNoVNC(config=self.config)
        # This is racy because we don't immediately start the VNC server.
        self.vnc_port = self.random_empty_port()

    def random_empty_port(self):
        '''Allocate a random empty port for use by the VNC server.'''
        sock = socket.socket()
        sock.bind(('', 0))
        port = sock.getsockname()[1]
        sock.close()
        return port

    @property
    def display(self):
        return self.vnc_port-5900

    def write_conf(self):
        config = configparser.ConfigParser()
        config['supervisord'] = {}
        config['program:xtightvnc'] = {
            'command': "Xtightvnc :{} -geometry {} -depth {}".format(
                self.display, self.c.geometry, self.c.depth
            ),
            'priority': 10,
        }
        config['program:websockify'] = {
            'command': "websockify --web /usr/share/novnc/ {port} localhost:{vnc_port}".format(port=self.port, vnc_port=self.vnc_port),
            'priority': 20,
        }
        config['program:desktop'] = {
            'command': self.c.desktop_session,
            'priority': 30,
            'environment': 'DISPLAY=":{}"'.format(self.display)
        }
        f = tempfile.NamedTemporaryFile(mode='w', delete=False)
        config.write(f)
        f.close()
        return f.name

    def get_env(self):
        return { 'DISPLAY': ':' + str(self.display) }

    def get_cmd(self):
        filename = self.write_conf()
        return [ "supervisord", "-c", filename, "--nodaemon" ]

def setup_handlers(web_app):
    web_app.add_handlers('.*', [
        (ujoin(web_app.settings['base_url'], 'novnc/(.*)'), SupervisorHandler, dict(state={})),
        (ujoin(web_app.settings['base_url'], 'novnc'), AddSlashHandler)
    ])

# vim: set et ts=4 sw=4:
