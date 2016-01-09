from setuptools import setup

setup(name='samplez',
      version='0.0.1',
      author='Brookhaven National Laboratory',
      py_modules=['samplez'],
      description='Reference implementation of SampleManager',
      url='http://github.com/tacaswell/samplez',
      requires=['six', 'json', 'jsonschema']
      )
