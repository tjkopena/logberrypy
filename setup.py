from setuptools import setup

setup(
    name             = 'logberry',
    version          = '0.2.0',
    description      = 'Structured logging library',
    packages         = ['logberry'],
    python_requires  = '>=3.6',
    author           = 'Joseph Kopena',
    author_email     = 'tjkopena@gmail.com',
    install_requires = ["janus"],
)
