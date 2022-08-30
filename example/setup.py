#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

module_name = "example_module"

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [ ]

test_requirements = [ ]

setup(
    author="Nastaran Tebyanian",
    author_email='nastaran.tebyanian@gmail.com',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    description="This project uses spatial robust decision making for green infrastructure planning.",
    entry_points={
        'console_scripts': [
            '{}={}.initialize:cli_entrypoint'.format(module_name, module_name),
        ],
    },
    #install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme,
    include_package_data=True,
    keywords=module_name,
    name=module_name,
    packages=find_packages(include=[module_name, '{}.*'.format(module_name)]),
    version='0.1.0',
    zip_safe=False,
)
