from setuptools import setup
from Cython.Build import cythonize
from setuptools import setup, find_packages
import numpy

with open('README.rst') as f:
    long_description = ''.join(f.readlines())

setup(
    name='beeclust',
    license='MIT',
    version='0.2',
    description='Clusting algorithm based on behavior of bees.',
    long_description=long_description,
    author='Ladislav Martínek',
    author_email='martilad@fit.cvut.cz',
    keywords='Beeclust, clustering',
    url='https://github.com/martilad/beeclust',
    packages=find_packages(),
    ext_modules=cythonize('beeclust/fastbee.pyx', language_level=3),
    include_dirs=[numpy.get_include()],
    install_requires=[
        'NumPy',
        'Cython',
        'Sphinx',
        'pytest',
    ],
    setup_requires=[
        'Cython',
        'NumPy',
        'pytest-runner',
    ],
    tests_require=[
        'pytest'
    ],
    classifiers=[
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Natural Language :: English',
        'Topic :: Software Development',
        'Development Status :: 4 - Beta',
        ],
    zip_safe=False,
)