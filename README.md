[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4037864.svg)](https://doi.org/10.5281/zenodo.4037864)
![unit tests](https://github.com/Sikerdebaard/dcmrtstruct2nii/workflows/Unit%20Tests/badge.svg)
  

# dcmrtstruct2nii
DICOM RT-Struct to nii-mask. This is a naïve approach to rasterizing rt-struct to masks in nii format. If there's holes in your RT-Struct then this approach will most likely not work. The RT-Struct needs to be within the bounds of the slices of the original DICOM. Rasterization is done on a slice-by-slice basis, interpolation between slices is currently unsupported.

# Interpolation
Interpolation of the mask between slices is currently unsupported. Send us an algorithm or a pull requests and we'll happly add it.

# Input file format
The DICOM and RT-Struct inputs need to be unzipped in a directory. Currently this is the only way to read the input files.

# CLI Tool
```
# install using pip and show tool help
pip install dcmrtstruct2nii
dcmrtstruct2nii --help

# list structures in DICOM RT Struct
dcmrtstruct2nii list -r /path/to/rtstruct/file

# convert help output
dcmrtstruct2nii convert --help

# convert DICOM RT Structs to .nii.gz masks
dcmrtstruct2nii convert -r /path/to/rtstruct/file.dcm -d /path/to/original/extracted/dicom -o /output/path
```

# Python API
```
# install using pip and show tool help
pip install dcmrtstruct2nii
```

```
# lets test it
from dcmrtstruct2nii import dcmrtstruct2nii, list_rt_structs

print(list_rt_structs('/path/to/dicom/rtstruct/file.dcm'))

dcmrtstruct2nii('/path/to/dicom/rtstruct/file.dcm', '/path/to/original/extracted/dicom/files', '/output/path')
```

# License and academic use

The program is licensed [Apache license 2.0](https://github.com/Sikerdebaard/dcmrtstruct2nii/blob/master/LICENSE).

For academic use, use a presistent copy from [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4037864.svg)](https://doi.org/10.5281/zenodo.4037864). 

Please cite:

```Thomas Phil, Thomas Albrecht, Skylar Gay, & Mathis Ersted Rasmussen. (2023). Sikerdebaard/dcmrtstruct2nii: dcmrtstruct2nii v3 (Version v3). Zenodo. https://doi.org/10.5281/zenodo.4037864```
