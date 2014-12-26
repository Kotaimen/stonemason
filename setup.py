#!/usr/bin/env python


import re
import codecs
import os

from setuptools import setup, find_packages


where_am_i = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(where_am_i, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


long_description = read('README.md')

install_requires = [
    'six>=1.8.0',
    'Flask>=0.9',
    'python-memcached>=1.53',
]

tests_require = [
    'nose',
    'coverage',
    'virtualenv>=1.10',
    'mock',
]

find_excludes = [
    'res',
    'tests',
]

py_modules = []

package_data = {}

setup(
    name='stonemason',
    version=find_version('stonemason', '__init__.py'),
    description='Map tile service toolkit.',
    long_description=long_description,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='map tile mapnik gdal tms',
    author='The Stonemasons',
    author_email='kotaimen.c@gmail.com, gliese.q@gmail.com',
    url='http://github.com/kotaimen/stonemason',
    license='MIT',
    py_modules=py_modules,
    packages=find_packages(exclude=find_excludes),
    package_data=package_data,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='tests',
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    }
)
