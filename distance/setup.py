from distutils.core import setup
from Cython.Build import cythonize
from distutils.core import Extension
import numpy as np


name = "dist_models"

sourcefiles = ["{}.pyx".format(name)]
headerfiles = ["/usr/local/lib/python3.7/site-packages/Cython/Includes", np.get_include()]

extensions = [
    Extension(
        name=name,
        sources=sourcefiles,
        include_dirs=headerfiles,
        language="c++"
    )
    ]


setup(
    ext_modules=cythonize(extensions)
)

print("Compile finished!")

