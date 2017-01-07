# -*- coding: utf-8 -*
from setuptools.command.install import install
from setuptools import find_packages
from setuptools import setup
import subprocess
import codecs
import sys
import os

def read(*parts):
    # intentionally *not* adding an encoding option to open
    # see here: https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), *parts), 'r').read()

setup(name="hitchvm",
    version=read('VERSION').replace('\n', ''),
    description="Set up virtual machines on spec.",
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries',
        'Operating System :: Unix',
        'Environment :: Console',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='hitch testing framework bdd tdd declarative tests testing jinja2 yaml',
    author='Colm O\'Connor',
    author_email='colm.oconnor.github@gmail.com',
    url='https://github.com/hitchtest/hitchvm',
    license='AGPL',
    install_requires=[
        'commandlib>=0.2.5', 'jinja2', 'path.py',
    ],
    packages=find_packages(exclude=["docs", "tests"]),
    package_data={},
    zip_safe=False,
    include_package_data=True,
)
