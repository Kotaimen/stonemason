import re
import codecs
import os
import sys

from setuptools import setup, find_packages

from distutils.extension import Extension
from distutils.command.sdist import sdist as sdist_
from distutils.command.clean import clean as clean_
from distutils import log


# Can't use six here
IS_PY3 = sys.version_info.major == 3

# Check Cython availability
try:
    from Cython.Distutils import build_ext
except ImportError:
    HAS_CYTHON = False
else:
    HAS_CYTHON = True


#
# Find package version
#
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

#
# Requirements
#
install_requires = [
    'six>=1.9.0',
    'Flask>=0.10',
    'Pillow>=2.3.0,<3.0.0',
    'boto>=2.35.0',
    'Click>=4.0',
    'gunicorn>=19.0.0',
    'pylibmc>=1.5.0',
    'numpy>=1.6',
    'scipy>=0.9',
    'scikit-image'
]

if IS_PY3:
    pass
else:
    install_requires.append('futures>=3.0.0')

tests_require = [
    'nose>=1.3.0',
    'coverage>=3.7.0',
    'moto>=0.4.0',
]

py_modules = []


#
# Cython extension modules
#

ext_modules = []

cython_modules = [
    ('stonemason.pyramid.hilbert',
     ['stonemason/pyramid/hilbert.pyx', ]),
]

entry_points = '''
[console_scripts]
stonemason=stonemason.__main__:cli
stonemason%d=stonemason.__main__:cli
''' % sys.version_info.major
#
# Custom commands
#

cmdclass = {}

if HAS_CYTHON:

    # Build cython file when doing build_ext command
    for module, sources in cython_modules:
        ext_modules.append(Extension(module, sources))

    cmdclass['build_ext'] = build_ext

    class sdist(sdist_):
        """ Build c source from Cython source for sdist """

        def run(self):
            from Cython.Build import cythonize

            for ext in self.distribution.ext_modules:
                sources = list(s for s in ext.sources if s.endswith('.pyx'))
                cythonize(sources)

            sdist_.run(self)

    cmdclass['sdist'] = sdist

    class clean(clean_):
        """ Removes all Cython generated C files """

        def run(self):
            clean_.run(self)
            for ext in self.distribution.ext_modules:
                sources = list(s for s in ext.sources if s.endswith('.pyx'))
                for source in sources:
                    try:
                        log.info("removing '%s'" % source[:-3] + 'c')
                        os.unlink(source[:-3] + 'c')
                        log.info("removing '%s'" % source[:-3] + 'so')
                        os.unlink(source[:-3] + 'so')
                    except OSError:
                        pass

    cmdclass['clean'] = clean

else:
    # No Cython, assuming build using sdist, just build .so from c
    for module, sources in cython_modules:
        c_sources = list(source[:-3] + 'c' for source in sources)
        ext_modules.append(Extension(module, c_sources))

package_data = {
    'stonemason.mason.theme':
        [
            'samples/manifest.mason',
            'samples/sample_world/*.mason',
            'samples/sample_world/ne_50m_*',
            'samples/sample_world/*.xml',
            'samples/sample_world/readme.md',
        ],
    'stonemason.pyramid': ['hilbert.c'],
    'stonemason.service.tileserver.maps': ['templates/*'],
    'stonemason.service.tileserver.admin': ['templates/*'],

}

#
# Setup
#

setup(
    name='stonemason',
    version=find_version('stonemason', '__init__.py'),
    description='Map tile service toolkit.',
    long_description=long_description,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Multimedia :: Graphics',
        'Programming Language :: Cython',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='map tile mapnik gdal tms',
    author='K&R',
    author_email='kotaimen.c@gmail.com, gliese.q@gmail.com',
    url='http://github.com/kotaimen/stonemason',
    license='MIT',

    py_modules=py_modules,
    ext_modules=ext_modules,
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    package_data=package_data,
    entry_points=entry_points,

    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='tests',
    zip_safe=False,
    cmdclass=cmdclass,

    extras_require={
        'testing': tests_require,
    }

)
