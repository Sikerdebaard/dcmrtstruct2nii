from setuptools import setup, find_packages
import sys

if sys.version_info < (3, 6):
    sys.exit('Sorry, Python < 3.6 is not supported')

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='dcmrtstruct2nii',
    version='1.0.14',
    description='Convert DICOM RT-Struct to nii',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Thomas Phil',
    author_email='thomas@tphil.nl',
    url='https://github.com/Sikerdebaard/dcmrtstruct2nii',
    python_requires=">=3.6",
    packages=find_packages(),  #same as name
    install_requires=[
        'numpy==1.15.4',
        'pydicom==1.2.1',
        'scikit-image==0.14.1',
        'scipy==1.2.0',
        'SimpleITK==1.2.0',
        'cleo==0.7.2'
    ], #external packages as dependencies
    #scripts=[
    #    'bin/dcmrtstruct2nii'
    #]
    entry_points={
        'console_scripts': [
            'dcmrtstruct2nii=dcmrtstruct2nii.cli.dcmrtstruct2nii:run',
        ],
    },
)
