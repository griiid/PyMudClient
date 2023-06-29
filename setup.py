import pathlib

from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent.resolve()

PACKAGE_NAME = 'pymudclient'
AUTHOR = 'griiid'
AUTHOR_EMAIL = 'gridwing@gmail.com'
URL = 'https://github.com/griiid/PyMudClient'
DOWNLOAD_URL = 'https://pypi.org/project/pymudclient/'

LICENSE = 'MIT'
VERSION = '0.1.2'
DESCRIPTION = 'A MUD client core written in Python'
LONG_DESCRIPTION = (HERE  / 'README.md').read_text(encoding='utf8')
LONG_DESC_TYPE = 'text/markdown'

requirements = (HERE / 'requirements.txt').read_text(encoding='utf8')
INSTALL_REQUIRES = [s.strip() for s in requirements.split('\n')]

dev_requirements = (HERE / 'dev_requirements.txt').read_text(encoding='utf8')
EXTRAS_REQUIRE = {'dev': [s.strip() for s in dev_requirements.split('\n')]}

CLASSIFIERS = [f'Programming Language :: Python :: 3.{v}' for v in range(7, 13)]
PYTHON_REQUIRES = '>=3.7'

params = dict(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    license=LICENSE,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    python_requires=PYTHON_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    packages=find_packages(),
    classifiers=CLASSIFIERS,
)

setup(**params)
