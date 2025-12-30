import setuptools
from ntpath import dirname
import os

with open('README.md', 'r') as f:
    longDescription = f.read()

def isRPI():
    path = '/sys/firmware/devicetree/base/model'
    if os.path.exists(path):
        with open(path, 'r') as m:
            if 'raspberry pi' in m.read().lower():
                return True
    return False

def getDeps():
    deps=['Flask', 'schedule', 'flask-expects-json', 'requests', 'matplotlib', 'hid', 'pyudev', 'dacite']
    if isRPI():
        #rpi specific
        deps.extend(['rpi-lgpio', 'rpi-rf', 'RPLCD', 'waitress', 'smbus2', 'pimoroni-bme280'])
    return deps

# single sourcing version number to __init__.py
def getVersion(pkgDir):
    currentPath = dirname(__file__)
    initPath = f"{currentPath}/{pkgDir}/__init__.py"

    with open(initPath) as f:
        for line in f.readlines():
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]

        else:
            raise RuntimeError("Unable to find version string.")

setuptools.setup(
    name="smart-home-server",
    version=getVersion("smart_home_server"),
    author="Joshua McPherson",
    author_email="joshuamcpherson5@gmail.com",
    description="A server for home automation",
    long_description = longDescription,
    long_description_content_type = 'text/markdown',
    url="https://github.com/PrinceOfPuppers/smart-home-server",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=getDeps(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
    ],
    python_requires='>=3.6',
    scripts=["bin/smart-home-server"],
    entry_points={
        'console_scripts': ['smart-home-server = smart_home_server:main'],
    },
)


