import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

__version__ = 'unknown'

# "import" __version__
for line in open('src/jack.py'):
    if line.startswith('__version__'):
        exec(line)
        break

setup(
    name='JACK-Client',
    version=__version__,
    package_dir={'': 'src'},
    py_modules=['jack'],
    setup_requires=['CFFI>=1.0'],
    install_requires=['CFFI>=1.0'],
    extras_require={'NumPy': ['NumPy']},
    cffi_modules=['jack_build.py:ffibuilder'],
    author='Matthias Geier',
    author_email='Matthias.Geier@gmail.com',
    description='JACK Audio Connection Kit (JACK) Client for Python',
    long_description=open('README.rst').read(),
    license='MIT',
    keywords='JACK audio low-latency multi-channel'.split(),
    url='http://jackclient-python.readthedocs.io/',
    platforms='any',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Sound/Audio',
    ],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    zip_safe=True,
)
