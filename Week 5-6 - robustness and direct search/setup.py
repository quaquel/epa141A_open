from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(
	name = "LakeProblem",
    ext_modules = cythonize(["intertemporal.pyx","dps.pyx"]),
    include_dirs=[numpy.get_include()]
)