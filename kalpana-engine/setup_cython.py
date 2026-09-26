import sys
import os
from setuptools import setup, Extension
from Cython.Build import cythonize

extra_compile_args = ["-O3"]
if sys.platform == "win32":
    extra_compile_args.append("/O2")

extensions = [
    Extension(
        name="core",
        sources=["core.py"],
        extra_compile_args=extra_compile_args,
    )
]

setup(
    name="kalpana_core_native",
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': "3",
            'always_allow_keywords': True,
            'c_string_type': 'str',
            'c_string_encoding': 'utf-8',
        },
        annotate=False
    ),
)
