from setuptools import setup, find_packages
import unittest

def test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests')
    return test_suite

setup(
    name='pynetstring',
    version='0.5',
    py_modules=['pynetstring'],
    packages=['tests'],
    license='MIT',
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Topic :: Software Development',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3'],
    description='A module for encoding and decoding netstrings.',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    install_requires=[],
    python_requires=">=3",
    test_suite='setup.test_suite',
    url='https://github.com/rj79/pynetstring',
    author='Robert Johansson',
    author_email='robertrockar@live.com'
)
