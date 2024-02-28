[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4037864.svg)](https://doi.org/10.5281/zenodo.4037864)
![unit tests](https://github.com/Sikerdebaard/dcmrtstruct2nii/workflows/Unit%20Tests/badge.svg)

# dcmrtstruct2nii

## Overview
`dcmrtstruct2nii` is a tool designed to convert DICOM RT-Struct files into NIfTI masks (.nii format). This conversion is a crucial step in scientific medical imaging workflows, particularly in radiology research. Our tool takes a straightforward, slice-by-slice approach to rasterize RT-Structs into masks, ensuring compatibility within the bounds of the original DICOM slices.

### Key Features:
- **Slice-by-Slice Rasterization**: Ensures each slice is accurately processed, maintaining the integrity of the original DICOM data.
- **Easy-to-Use CLI**: Simplifies the conversion process with straightforward command-line instructions.
- **Python API Support**: Offers flexibility for integration into custom Python scripts or applications.

## Installation

```bash
pip install dcmrtstruct2nii
```

## Usage

### CLI Tool

#### Installation and Help
```bash
# Install the tool via pip
pip install dcmrtstruct2nii

# Display help information
dcmrtstruct2nii --help
```

#### Listing Structures
```bash
# List all structures within a DICOM RT Struct file
dcmrtstruct2nii ls -r /path/to/rtstruct/file
```

#### Conversion
```bash
# Convert DICOM RT Structs to NIfTI masks
dcmrtstruct2nii convert -r /path/to/rtstruct/file.dcm -d /path/to/original/extracted/dicom -o /output/path
```

### Python API

#### Basic Example
```python
from dcmrtstruct2nii import dcmrtstruct2nii, list_rt_structs

# List RT Structures
print(list_rt_structs('/path/to/dicom/rtstruct/file.dcm'))

# Convert RT Struct to NIfTI mask
dcmrtstruct2nii('/path/to/dicom/rtstruct/file.dcm', '/path/to/original/extracted/dicom/files', '/output/path')
```

## Limitations

- **Interpolation**: Currently, the tool does not support interpolation between slices. We welcome contributions and suggestions for implementing this feature.

## Input File Format

- Ensure that DICOM and RT-Struct files are unzipped and available in a directory. This is necessary for the tool to read and process the input files correctly.

## License and Academic Use

`dcmrtstruct2nii` is provided under the [MIT License](https://github.com/Sikerdebaard/dcmrtstruct2nii/blob/master/LICENSE), supporting both open-source and academic use.

For academic purposes, please reference the tool using the citation provided below:

```bibtex
@software{dcmrtstruct2nii_2023,
  author       = {Thomas Phil and Thomas Albrecht and Skylar Gay and Mathis Ersted Rasmussen},
  title        = {{Sikerdebaard/dcmrtstruct2nii: dcmrtstruct2nii v5}},
  month        = sep,
  year         = 2023,
  publisher    = {Zenodo},
  version      = {v5},
  doi          = {10.5281/zenodo.4037864},
  url          = {https://doi.org/10.5281/zenodo.4037864}
}
```

## Contributing

We welcome contributions to `dcmrtstruct2nii`, including feature enhancements, bug fixes, and documentation improvements. Please feel free to submit issues and pull requests on our [GitHub repository](https://github.com/Sikerdebaard/dcmrtstruct2nii).
