from setuptools import setup

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
    python_requires='>=3',
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Multimedia :: Sound/Audio',
    ],
    zip_safe=True,
)
