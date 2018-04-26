# nbnovnc

**nbnovnc** provides Jupyter server and notebook extensions to proxy a notebook-side VNC session using noVNC, enabling users to run non-web applications within their Jupyter notebook server. This is mostly useful for hosted Jupyter environments such as JupyterHub or Binder.

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/ryanlovett/nbnovnc/5a64d9e)

![Screenshot](screenshot.png)

## Installation

### Install Dependencies
The extension requires [nbserverproxy](https://github.com/jupyterhub/nbserverproxy) and currently uses an opinionated VNC environment comprised of TightVNC server, noVNC, supervisord, and websockify 0.8.0 for python2.

On Debian/Ubuntu:
```
apt install tightvncserver novnc websockify supervisor xinit
```


### Install nbnovnc 
Install the library:
```
pip install nbnovnc
```

Either install the extensions for the user:
```
jupyter serverextension enable  --py nbnovnc
jupyter nbextension     install --py nbnovnc
jupyter nbextension     enable  --py nbnovnc
```

Or install the extensions for all users on the system:
```
jupyter serverextension enable  --py --sys-prefix nbnovnc
jupyter nbextension     install --py --sys-prefix nbnovnc
jupyter nbextension     enable  --py --sys-prefix nbnovnc
```

### Configuration

The following traitlets are available:

- NBNoVNC.geometry: The desktop geometry, e.g. 1024x768.
- NBNoVNC.depth: The color depth, e.g. 24.
- NBNoVNC.novnc_directory: The path to noVNC's web assets.
- NBNoVNC.vnc_command: The command to launch the VNC server. Contains replacement fields for display, depth, and geometry, e.g. `xinit -- /usr/bin/Xtightvnc :{display} -geometry {geometry} -depth {depth}`

You may configure the desktop environment by altering ~/.xinitrc.
