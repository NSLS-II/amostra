__author__ = 'arkilic'
import setuptools
import versioneer
import os


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'requirements.txt')) as requirements_file:
    # Parse requirements.txt, ignoring any commented-out lines.
    requirements = [line for line in requirements_file.read().splitlines()
                    if not line.startswith('#')]

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
    name='amostra',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    license="BSD 3-Clause",
    url="https://github.com/NSLS-II/amostra.git",
    packages=setuptools.find_packages(),
    install_package_data = True,
    install_requires=requirements,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Development Status :: 3 - Alpha",
        'Programming Language :: Python :: 3',
    ],
)
