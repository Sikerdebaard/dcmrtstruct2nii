from setuptools import setup, find_packages

setup(
    name='dcmrtstruct2nii',
    version='1.0',
    description='Convert DICOM RT-Struct to nii',
    author='Thomas Phil',
    author_email='thomas@tphil.nl',
    packages=find_packages(),  #same as name
    install_requires=[], #external packages as dependencies
    scripts=[
        'bin/dcmrtstruct2nii'
    ]
)
