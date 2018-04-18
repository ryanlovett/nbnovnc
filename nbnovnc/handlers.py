import configparser
import os
import socket
import tempfile

from notebook.utils import url_path_join as ujoin

from traitlets import Unicode, Integer
from traitlets.config.configurable import Configurable

from nbserverproxy.handlers import AddSlashHandler, SuperviseAndProxyHandler

class SupervisorHandler(SuperviseAndProxyHandler):
    '''Supervise supervisord.'''

    name = 'supervisord'

    def supervisor_config(self):
        config = configparser.ConfigParser()
        config['supervisord'] = {}
        return config

    def write_conf(self):
        config = self.supervisor_config()
        f = tempfile.NamedTemporaryFile(mode='w', delete=False)
        config.write(f)
        f.close()
        return f.name

    def get_cmd(self):
        filename = self.write_conf()
        return [ "supervisord", "-c", filename, "--nodaemon" ]

class NBNoVNC(Configurable):
    desktop_session = Unicode(u"openbox --startup /etc/X11/xinit/xinitrc",
        help="Command to start desktop session.", config=True)
    geometry = Unicode(u"1024x768", help="Desktop geometry.", config=True)
    depth = Integer(24, help="Desktop display depth.", config=True)
    novnc_directory = Unicode(u"/usr/share/novnc",
        help="Path to noVNC web assets.", config=True)

class NoVNCHandler(SupervisorHandler):
    '''Supervise novnc, websockify, and a VNC server.'''
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

    def get_env(self):
        return { 'DISPLAY': ':' + str(self.display) }

    def supervisor_config(self):
        config = super().supervisor_config()
        config['program:xtightvnc'] = {
            'command': "Xtightvnc :{} -geometry {} -depth {}".format(
                self.display, self.c.geometry, self.c.depth
            ),
            'priority': 10,
        }
        config['program:websockify'] = {
            'command': "websockify --web {} {} localhost:{}".format(
                self.c.novnc_directory,
                self.port,
                self.vnc_port
            ),
            'priority': 20,
        }
        config['program:desktop'] = {
            'command': self.c.desktop_session,
            'priority': 30,
            'environment': 'DISPLAY=":{}"'.format(self.display)
        }
        return config

    async def get(self, path):
        '''
        When clients visit novnc/, actually get novnc/vnc_auto.html
        or novnc/vnc_lite.html from our proxied service instead.
        '''
        if len(path) == 0:
            for f in ['vnc_auto.html', 'vnc_lite.html']:
                if os.path.exists(os.path.join(self.c.novnc_directory, f)):
                    path = f
                    break
        return await super().get(path)

def setup_handlers(web_app):
    web_app.add_handlers('.*', [
        (ujoin(web_app.settings['base_url'], 'novnc/(.*)'), NoVNCHandler,
            dict(state={})),
        (ujoin(web_app.settings['base_url'], 'novnc'), AddSlashHandler)
    ])

# vim: set et ts=4 sw=4:
