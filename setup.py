import setuptools

setuptools.setup(
    name="nbnovnc",
    version='0.0.1',
    url="https://github.com/ryanlovett/nbnovnc",
    author="Ryan Lovett",
    description="Jupyter extension to proxy a VNC session via noVNC",
    packages=setuptools.find_packages(),
	keywords=['Jupyter'],
	classifiers=['Framework :: Jupyter'],
    install_requires=[
        'notebook',
        'nbserverproxy >= 0.5.1'
    ],
    package_data={'nbnovnc': ['static/*']},
)
