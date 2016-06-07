__author__ = 'arkilic'
import setuptools
import versioneer
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
    name='amostra',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    license="BSD 3-Clause",
    url="https://github.com/NSLS-II/amostra.git",
    packages=['amostra', 'amostra.client', 'amostra.schemas',
              'amostra.server']
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Development Status :: 3 - Alpha",
        'Programming Language :: Python :: 3',
    ],
)
