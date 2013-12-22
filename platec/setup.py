from distutils.core import setup, Extension
import numpy as np 

extra_compile_args = "-std=c99"

module1 = Extension('platec',                    
                    sources = ['platecmodule.c',
                        'platecapi.cpp',
                        'plate.cpp',
                        'lithosphere.cpp',
                        'sqrdmd.c'],
                    extra_compile_args=[extra_compile_args],
                    )

setup (name = 'Platec',
       version = '1.0',
       description = 'platec',
       ext_modules = [module1])