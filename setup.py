from setuptools import setup, find_packages

setup(
    name='netstring_bin',
    version='0.1.dev1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='A module for encoding and decoding netstrings',
    long_description=open('README.txt').read(),
    install_requires=[],
    url='https://github.com/rj79/netstring',
    author='Robert Johansson',
    author_email='robertrockar@live.com'
)
