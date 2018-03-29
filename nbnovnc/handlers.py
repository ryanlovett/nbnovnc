import tempfile

from notebook.utils import url_path_join as ujoin

from nbserverproxy.handlers import AddSlashHandler, SuperviseAndProxyHandler

class NoVNCHandler(SuperviseAndProxyHandler):
    '''Manage a novnc instance along with websockify, x11vnc, and Xvfb.'''

    name = 'circusd'

    conf_tmpl = """
[circus]

[watcher:Xvfb]
cmd = Xvfb :0 -screen 0 1024x768x24
numprocesses = 1
priority = 4

[watcher:x11vnc]
cmd = x11vnc -loop
numprocesses = 1
priority = 3
hooks.after_start = nbnovnc.circus.sleep

[watcher:websockify]
cmd = websockify --web /usr/share/novnc/ {port} localhost:5900
numprocesses = 1
priority = 2

[watcher:windowmanager]
cmd = openbox-session
numprocesses = 1
priority = 1

[env:windowmanager]
DISPLAY = :0
"""

    def write_conf(self, port):
        '''Create a configuration file and return its name.'''
        conf = self.conf_tmpl.format(port=port)
        f = tempfile.NamedTemporaryFile(mode='w', delete=False)
        f.write(conf)
        f.close()
        return f.name

    def get_env(self):
        return { 'DISPLAY': ':0' }

    def get_cmd(self):
        filename = self.write_conf(self.port)
        self.log.info("nvnovnc: circusd ini file: {}".format(filename))
        self.log.info("nvnovnc:\n--\n{}".format(open(filename).read()))

        # shiny command.
        return [ 'circusd', filename ]

def setup_handlers(web_app):
    web_app.add_handlers('.*', [
        (ujoin(web_app.settings['base_url'], 'novnc/(.*)'), NoVNCHandler, dict(state={})),
        (ujoin(web_app.settings['base_url'], 'novnc'), AddSlashHandler)
    ])

# vim: set et ts=4 sw=4:
