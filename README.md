# dcmrtstruct2nii
DICOM RT-Struct to nii-mask

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
