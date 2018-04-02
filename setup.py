import setuptools

setuptools.setup(
    name="nbnovnc",
    version='0.0.2',
    url="https://github.com/ryanlovett/nbnovnc",
    author="Ryan Lovett",
    author_email="rylo@berkeley.edu",
    description="Jupyter extension to proxy a VNC session via noVNC",
    packages=setuptools.find_packages(),
	keywords=['Jupyter'],
	classifiers=['Framework :: Jupyter'],
    install_requires=[
        'notebook',
        'nbserverproxy >= 0.7'
    ],
    package_data={'nbnovnc': ['static/*']},
)
