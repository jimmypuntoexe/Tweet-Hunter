from distutils.core import setup
from setuptools import find_packages

requires = [
    'six>=1.10.0',
]

if __name__ == "__main__":
    setup(
        name="Hunter",
        version="1.0.1",
        packages=find_packages(),
        author='Jimmi',
        install_requires=requires,
        description='The API to fetch data from different sources',
        include_package_data=True,
    )