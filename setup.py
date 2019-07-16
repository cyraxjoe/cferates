import setuptools
from setuptools.config import read_configuration

config = read_configuration("setup.cfg")
setup_params = {}
setup_params = dict(setup_params, **config['metadata'])
setup_params = dict(setup_params, **config['options'])
setuptools.setup(**setup_params)
