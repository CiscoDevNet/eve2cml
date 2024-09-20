# TODOs

### Configuration sets

- need to provide a command line flag to specify which config set, if present, should be included in the resulting CML YAML file
- alternatively, if config sets are present, write multiple files, one for each config set

## Annotations

- add "dashed" property for squares and circles
- add transparency conversion

## Done

### Handle pnet0, pnet1,

- pnet0: This is typically used as the management interface. It connects EVE-NG to the host machine's management network, allowing access to the EVE-NG web interface and manage virtual network devices.
- pnet1, pnet2, etc.: These are additional physical network interfaces that can be configured within EVE-NG. They allow connecting virtual network devices to separate physical networks or VLANs. They need to be mapped to bridgeN using ext conns.  Insert an intermediate UMS if the number of connected ports is greater than 1.

### General file handling

- allow for files to be present in ZIP format
- unpack content in ZIP file and convert each file in the ZIP

### Device mapper

- take the device mapping from package data as YAML and import it at program start instead of including it in code
- allow to export this data to provide a starting point / sample to customize
- allow to import this data at program start to allow for custom mappings
