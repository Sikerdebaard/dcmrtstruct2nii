from setuptools import setup, find_packages
import sys

minpyver = (3, 8)
if sys.version_info < minpyver:
    sys.exit(f'Sorry, Python < {".".join(minpyver)} is not supported')

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='dcmrtstruct2nii',
    version='5',
    description='Convert DICOM RT-Struct to nii',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Thomas Phil',
    author_email='thomas@tphil.nl',
    url='https://github.com/Sikerdebaard/dcmrtstruct2nii',
    python_requires=">=3.6",
    packages=find_packages(),  # same as name
    install_requires=[
        'numpy>=1.15.4',
        'pydicom>=1.2.1',
        'scikit-image>=0.17.1',
        'scipy>=1.2.0',
        'SimpleITK>=1.2.0',
        'cleo>=2.0.0',
        'termcolor>=2.2.0',
    ],
    entry_points={
        'console_scripts': [
            'dcmrtstruct2nii=dcmrtstruct2nii.cli.dcmrtstruct2nii:run',
        ],
    },
)
