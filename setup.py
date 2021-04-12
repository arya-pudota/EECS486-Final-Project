"""
politiquiz python package configuration.

"""

from setuptools import setup

setup(
    name='reducer',
    version='0.1.0',
    packages=['reducer'],
    include_package_data=True,
    install_requires=[
        'bs4',
        'Flask',
        'html5validator',
        'pylint',
        'requests',
        'spacy',
    ],
    python_requires='>=3.6',
)
