from setuptools import setup
setup(name='amostra',
      version='0.0.1',
      author='Brookhaven National Laboratory',
      py_modules=['amostra'],
      description='Reference implementation of SampleManager',
      url='http://github.com/tacaswell/amostra',
      requires=['six', 'json', 'jsonschema']
      )
