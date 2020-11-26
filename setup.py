import os
import io
import runpy
from setuptools import setup


current = os.path.realpath(os.path.dirname(__file__))

with io.open(os.path.join(current, 'README.md'), encoding="utf-8") as f:
    long_description = f.read()

with open(os.path.join(current, 'requirements.txt')) as f:
    requires = f.read().splitlines()

__version__ = "1.0.0"

setup(
    name='webex-cortex',
    description="Cortex Responder for WebexTeams",
    license="MIT License",
    url="https://github.com/KalleDK/webex-cortex",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=__version__,
    author="Kalle M. Aagaard",
    author_email="webex-cortex@k-moeller.dk",
    maintainer="Kalle M. Aagaard",
    maintainer_email='webex-cortex@k-moeller.dk',
    packages=["webexcortex"],
    platforms=["Linux"],
    keywords=['wrapper'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=requires,
    entry_points={'console_scripts': [
        'webexcortex = webexcortex.__main__:init']},
)