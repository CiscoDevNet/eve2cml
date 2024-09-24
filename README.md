# eve2cml

[![PyPI version](https://badge.fury.io/py/eve2cml.svg)](https://pypi.org/project/eve2cml/) [![Coverage Status](https://coveralls.io/repos/github/CiscoDevNet/eve2cml/badge.svg?branch=main)](https://coveralls.io/github/CiscoDevNet/eve2cml?branch=main) [![GH workflow](https://github.com/CiscoDevNet/eve2cml/actions/workflows/python-package.yml/badge.svg)](https://github.com/CiscoDevNet/eve2cml/actions/workflows/python-package.yml)

![image showing a topology conversion](https://raw.githubusercontent.com/CiscoDevNet/eve2cml/main/assets/header.png)

Convert EVE-NG topology files either in ZIP format or in plain-text XML (.unl) to CML2 YAML format.

> [!CAUTION]
>
> This is considered "beta" as in "it works for me but might have bugs or things don't work as you expect them to work."  So, use with care and at your own risk.

## Online conversion

The easiest way to convert files into CML format is to use the online converter provided [here](https://www.marcuscom.com/eve2cml/).  Simply upload your UNL or ZIP files and the tool will convert them for you, using the eve2cml package in the background.

## Installation

eve2cml requires Python 3, it has been tested with 3.9, 3.10, 3.11 and 3.12.  You can either

- use [pipx](https://github.com/pypa/pipx) to install it in an isolated environment:

    ```plain
    $ pipx install eve2cml
      installed package eve2cml 0.1.0b4, installed using Python 3.10.12
      These apps are now globally available
        - eve2cml
        done! ✨ 🌟 ✨

    $ eve2cml --version
    eve2cml 0.1.0b4

    $
    ```

- pip-install it from PyPI by running `pip install eve2cml`. This will install the package into your current Python environment.  It is suggested to use a virtual or local environment instead of the system / global environment.

## Development

eve2cml uses [UV](https://docs.astral.sh/uv/) to manage Python related things like dependencies, virtual environments and Python installations.  At a minimum, Git and UV must be installed as prerequisites.  After UV is installed, it can install Python for you (`uv python install...` and you can run `make sync` and a virtual environment will be created, all dependencies will be installed and a dev-version of eve2cml will be available.  Changes should be pushed into a new branch to a forked copy of the repository and result, eventually, in a pull request.

There's a couple of make targets available which help with developing eve2cml:

- `make covo`, shows code coverage, opens in a browser window
- `make test`, runs all available tests
- `make format`, formats the code with ruff
- `make build`, builds distribution packages in `dist`
- `make clean`, cleans up created files (also `mrproper`, which deletes the .venv)

## Mapping node types

There's some default node type mappings which can be dumped into a file using the `--dump` flag.

The mapper defines three elements:

- `interface_lists`: A map with a list of interface names for each mapped CML node definitions. The key is the CML node definition ID

- `unknown_type`: Which node definition ID should be inserted into the topology if the EVE node type is not defined in the mapper (a string like "desktop")

- `map`: Maps EVE node types into CML node and image definitions.  The map key is an EVE node type where the format is "eve-node-type:eve-node-template:eve-node-image" (separated by colons).  An example is `qemu:linux`.  When the image part is missing then the CML default image for the mapped node type is used.  The value for each key is of the form:

  - `image_def`: the CML image definition ID for this node definition ID (can safely be null/undefined)
  - `node_def`: the mapped CML node definition ID
  - `override`: a boolean. It determines whether values like CPU or memory should be taken from the EVE definition.  If `true` then the EVE values will not be used, the default values from CML for this particular node type will then be used instead

  There's a specific "corner case" where the type is identical to the template (e.g. "iol:iol" or "docker:docker").  In this particular case, mapper keys are searched for partial matches where the map key matches the beginning of the provided EVE image.  For example, "iol:iol:i86bi_linux_l2:" matches all IOL images that start with `i86bi_linux_l2` and maps them (by default) into `ioll2-xe`.

After modification / adding more or different node type mappings to the exported map YAML, use the file via the `--mapper modified_map.yaml` flag.

Disclaimer:  There's certainly things out there which do not properly translate.  If you encounter anything then raise an issue in the issue tracker and I'll look into it.

> [!NOTE]
> It is possible to change node types when importing.  For example, you might want to change IOSv-L2 instances to IOLL2-XE instances by providing a custom import map.  However, this does **NOT** change the device configuration of the imported nodes.  So, if the configuration uses `GigabitEthernet0/4` in the original IOSv-L2 configuration then it is your responsibility to change this to `Ethernet1/0` for the configuration of the imported IOLL2-XE device.  This can be easily done via a sed script or using a text editor and global search and replace.  But this might be more involved depending on the original/target device type.  See the [Change configurations](#change-configurations) section below for an example.

## Usage

```plain
$ eve2cml -h
usage: eve2cml [-h] [-V] [--level {debug,info,warning,error,critical}] [--stdout] [--nocolor] [--dump] [--mapper MAPPER] [-t] [--all] file_or_zip [file_or_zip ...]

Convert UNL/XML topologies to CML2 topologies

positional arguments:
  file_or_zip           Path to either a UNL or ZIP with UNL file

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  --level {debug,info,warning,error,critical}
                        specify the log level, default is warning
  --stdout              do not store in files, print to stdout
  --nocolor             no color log output
  --dump                Dump the mapper as YAML
  --mapper MAPPER       custom mapper YAML file
  -t, --text            text output
  --all                 print all objects in text mode

Example: eve2cml exportedlabs.zip

$
```

## Change configurations

With a custom mapper file, node types can be modified while importing.  For example, adding map entries like the following

```yaml
  qemu:vios:
    image_def: null
    node_def: iol-xe
    override: false
  qemu:viosl2:
    image_def: null
    node_def: ioll2-xe
    override: false
```

to the mapper will change all IOSv instances to IOL-XE instances and all IOSv-L2 instances to IOLL2-XE instances.  However, the day zero configuration files of those nodes will not be modified to match the now different interface names.  In this particular case, where most of the configuration between IOSv and IOL-XE is identical *except for the interface names*, a simple sed script can do the trick.  Here's how this can be done:

1. create a sed script file with this content, filename `ios2iol-config`:

   ```plain
   s#GigabitEthernet0/0#Ethernet0/0#
   s#GigabitEthernet0/1#Ethernet0/1#
   s#GigabitEthernet0/2#Ethernet0/2#
   s#GigabitEthernet0/3#Ethernet0/3#
   s#GigabitEthernet0/4#Ethernet1/0#
   s#GigabitEthernet0/5#Ethernet1/1#
   s#GigabitEthernet0/6#Ethernet1/2#
   s#GigabitEthernet0/7#Ethernet1/3#
   s#GigabitEthernet0/8#Ethernet2/0#
   s#GigabitEthernet0/9#Ethernet2/1#
   s#GigabitEthernet0/10#Ethernet2/2#
   s#GigabitEthernet0/11#Ethernet2/3#
   s#GigabitEthernet0/12#Ethernet3/0#
   s#GigabitEthernet0/13#Ethernet3/1#
   s#GigabitEthernet0/14#Ethernet3/2#
   s#GigabitEthernet0/15#Ethernet3/3#
   ```

2. dump the default / built-in mapper into a file (`--dump` option)
3. modify the mapper to include the changes outlined above
4. convert the topology with the modified map file (`--mapper` option)
5. run `sed -f ios2iol-config lab.yaml >lab_with_configs_changed.yaml`

This will change all occurrences within the CML lab file from IOSv notation to IOL notation.

## Contributing

If you have a more complete map file with additional or more specific node type mappings or if you have improved the code, fixed a bug or a typo or added a new feature then I more than welcome you to raise a pull request!

## Issues

If you encounter any issues with the converter then please open a issue in the [GitHub issue tracker](https://github.com/CiscoDevNet/eve2cml/issues).

### IOL interfaces

There's a known issue with the maximum number of interfaces defined in the shipping node definitions for IOL and IOL-L2.  As for the released version of CML 2.7.0, the maximum number of interfaces is 16.  If you have topologies which use more interfaces (`Ethernet4/0` and up) then you need to add the additional interfaces to the node definition in CML (Tools -> Node and image definitions -> IOL / IOL-L2).  In the interface section, add the required interfaces and name them properly.  Don't forget to click "Update" at the bottom when done.

This is fixed in the 2.7.1 release, once available.

The converter has now 32 interfaces defined in the mapper (`Ethernet0/0` to `Ethernet7/3`).

### Known issues

There's a few things which are known to cause issues.  Some of them might be addressable by code changes in the converter and/or changes on the CML side of things.  And some might just not be possible at all.

- Text objects in EVE can have a background color.  The converter adds additional rectangles behind the text object in CML.  It "guesses" the size of these rectangles.  Those guesses are inaccurate.
- Font (names) might not translate well.  I think there's a general issue with serif vs. sans-serif mapping.
- Images (PNGs) as part of a topology are ignored as there's no representation for them in CML.
- More complex text boxes in EVE do not translate well into the more simple text annotation of CML.  For color, size and font name, the first occurrence is used for the entire text object.  Things like bullet lists etc. are completely ignored.
- EVE multi-point networks are represented by unmanaged switches in CML.  They have max 32 ports.  That might not be enough.
- Workbooks ("tasks") are not stored anywhere.  Unclear at the moment, if and how to handle them.

Also check the [TODO](/TODO.md) file for additional things that will likely be added in subsequent releases.
