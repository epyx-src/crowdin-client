# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

with open('README.rst') as readme:
    long_description = readme.read()

with open('requirements.txt') as reqs:
    install_requires = [
        line for line in reqs.read().split('\n') if (line and not
                                                     line.startswith('--'))
    ]

setup(
    name='crowdin-client',
    version=__import__('crowdin').__version__,
    author='epyx SA',
    author_email='dev@epyx.ch',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/epyx-src/crowdin-client',
    license='MIT',
    description='Command-line client for the crowdin.net API',
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Software Development :: Localization',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],
    zip_safe=False,
    install_requires=install_requires,
    scripts=[
        'scripts/crowdin',
    ],
)
