from setuptools import setup
from Cython.Build import cythonize

setup(
    name='FA2 Utils',
    ext_modules=cythonize("fa2util.pyx"),
    zip_safe=False
)