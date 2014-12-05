from setuptools import setup

# "import" __version__
for line in open("jack.py"):
    if line.startswith("__version__"):
        exec(line)
        break

setup(
    name="JACK-Client",
    version=__version__,
    py_modules=["jack"],
    install_requires=['cffi'],
    author="Matthias Geier",
    author_email="Matthias.Geier@gmail.com",
    description="JACK Audio Connection Kit (JACK) Client for Python",
    long_description=open("README.rst").read(),
    license="MIT",
    keywords="JACK audio low-latency multi-channel".split(),
    url="http://jackclient-python.rtfd.org/",
    platforms="any",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Sound/Audio",
    ],
)
