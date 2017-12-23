from setuptools import setup, find_packages

setup(
    name='pynetstring',
    version='0.1.dev1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Topic :: Software Development',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3'],
    description='A module for encoding and decoding netstrings.',
    include_package_data=True,
    long_description=open('README.rst').read(),
    install_requires=[],
    python_requires=">=3",
    url='https://github.com/rj79/pynetstring',
    author='Robert Johansson',
    author_email='robertrockar@live.com'
)
