# CHANGELOG

- v0.1.1
  - updated release workflows, no functional difference to 0.1.0
- v0.1.0
  - replace pdm with uv
  - updated all github actions to newer versions
  - automate the PyPI release process
  - allow more annotations to be rotated (with 2.8)
  - updated documentation
  - a small/cosmetic fix around the centered line output
- v0.1.0b5
  - updated dependencies
  - added installation instructions to README
  - test against 3.9, 3.10, 3.11 and (new) 3.12
  - added tests for the mapper
  - allow to run with --stdout and zip files, files will be concatenated
    and separated by long Lines
  - use recommended module resource load method
  - add XRv and XRv9k definitions to mapper (#4)
- v0.1.0b4
  - fix slot calculation
  - added a section about manual node configuration changes to the README
  - more diagnostic output at debug log level
- v0.1.0b3
  - fix longest prefix node type mapping
  - update package meta data
  - added a note regarding configurations when changing node types
- v0.1.0b2
  - fix slot calculation for nodes with interface gaps
  - increase IOL / IOL-2 maximum interfaces from 16 to 32
  - shorten prefix for IOL-L2 mapping from i86bi_linux_l2-ipbasek8 to
    i86bi_linux_l2 to allow for a broader match
- v0.1.0b1 minor cosmetic changes
- v0.1.0b0 initial release
