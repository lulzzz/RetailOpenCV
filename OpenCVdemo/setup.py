from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'Tools',
  ext_modules = cythonize("cython_tools.pyx"),
)