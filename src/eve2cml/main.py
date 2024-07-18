import argparse
import io
import logging
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import List

import yaml

from ._version import __version__
from .eve import Lab, Network, Node, Objects, Topology
from .log import initialize_logging
from .mapper import Eve2CMLmapper

_LOGGER = logging.getLogger(__name__)


def parse_xml(xml_content: str, filename: str, mapper: Eve2CMLmapper):
    lab = ET.fromstring(xml_content)
    lab_name = lab.attrib.get("name", "")
    lab_version = lab.attrib.get("version", "")
    script_timeout = int(lab.attrib.get("scripttimeout", 0))
    countdown = int(lab.attrib.get("countdown", 0))
    lock = int(lab.attrib.get("lock", 0))
    sat = int(lab.attrib.get("sat", 0))

    desc = lab.find(".//description")
    task = lab.find(".//body")

    description = ""
    if desc is not None and desc.text:
        description += f"## Description: \n\n{desc.text}\n\n"
    if task is not None and task.text:
        description += f"## Task: \n\n{task.text}\n\n"
    description += f"Imported from {filename} via `eve2cml` converter"

    parsed_lab = Lab(
        name=lab_name,
        version=lab_version,
        scripttimeout=script_timeout,
        countdown=countdown,
        lock=bool(lock),
        sat=sat,
        description=description,
        topology=Topology(nodes=Node.parse(lab), networks=Network.parse(lab)),
        objects=Objects.parse(lab, ".//objects", filename),
        filename=filename,
        mapper=mapper,
    )

    return parsed_lab


def convert_file(content: str, filename: str, mapper: Eve2CMLmapper) -> Lab:
    _LOGGER.info("Parse XML file %s", filename)
    lab = parse_xml(content, filename, mapper)
    _LOGGER.info("Done with file %s", filename)
    return lab


def convert_files(file_or_zip: str, mapper: Eve2CMLmapper) -> List[Lab]:
    lab: List[Lab] = []
    if zipfile.is_zipfile(file_or_zip):
        with zipfile.ZipFile(file_or_zip, "r") as zip_file:
            for file_info in zip_file.infolist():
                dirname = str(Path(file_info.filename).parent)
                if dirname.startswith("__MACOSX"):
                    continue
                filename = Path(file_info.filename).name
                if filename.endswith(".unl"):
                    try:
                        content = zip_file.read(file_info.filename)
                        dir = f"{dirname}--{filename}" if dirname != "." else filename
                        lab.append(convert_file(content.decode("utf-8"), dir, mapper))
                    except KeyError:
                        print(f"File {filename} not found in the ZIP archive.")
    else:
        try:
            with open(file_or_zip, encoding="utf-8") as xml_file:
                txt_content = xml_file.read()
                lab.append(convert_file(txt_content, file_or_zip, mapper))
        except FileNotFoundError as exc:
            _LOGGER.critical("%s", exc)
            sys.exit(1)
    return lab


def dump_as_text(out: io.TextIOWrapper, lab: Lab, dump_all: bool):
    out.write(">>> Nodes <<<\n")
    for node in lab.topology.nodes:
        out.write(f"{node}\n")
        num_ifaces = len(node.interfaces) - 1
        for idx, interface in enumerate(node.interfaces):
            bullet = "|--" if idx < num_ifaces else "\\__"
            out.write(f"  {bullet} {interface}\n")
        out.write("\n")

    out.write(">>> Networks <<<\n")
    for network in lab.topology.networks:
        out.write(f"{network}")
    out.write("\n")

    out.write(">>> Text objects <<<\n")
    for text_object in lab.objects.textobjects:
        out.write(f"{text_object}")
    out.write("\n")

    if not dump_all:
        return

    out.write(">>> Tasks <<<\n")
    for task in lab.objects.tasks:
        out.write(f"{task}")
    out.write("\n")

    out.write(">>> Configs <<<\n")
    for config in lab.objects.configs:
        out.write(f"{config}")
    out.write("\n")

    out.write(">>> Config sets <<<\n")
    for configset in lab.objects.configsets:
        out.write(f"Config Set ID: {configset.id}\n")
        out.write(f"Config Set Name: {configset.name}\n")
        out.write("Contained Configs:\n")
        for config in configset.configs:
            out.write(f"{config}\n")
        out.write("\n")


def centered_line_with_stars(name="", cols=80) -> str:
    if len(name) == 0:
        return "*" * cols
    num_asterisks = cols - len(name) - 2
    asterisks_each_side = num_asterisks // 2
    asterisks_left = "*" * asterisks_each_side
    asterisks_right = asterisks_left
    if num_asterisks % 2 != 0:
        asterisks_right += "*"
    return f"{asterisks_left} {name} {asterisks_right}"


def main():
    parser = argparse.ArgumentParser(
        description="Convert UNL/XML topologies to CML2 topologies"
    )
    parser.epilog = f"Example: {parser.prog} exportedlabs.zip"
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "--level",
        default="warning",
        choices=["debug", "info", "warning", "error", "critical"],
        help="specify the log level, default is warning",
    )
    parser.add_argument(
        "--stdout", action="store_true", help="do not store in files, print to stdout"
    )
    parser.add_argument("--nocolor", action="store_true", help="no color log output")
    parser.add_argument("--dump", action="store_true", help="Dump the mapper as YAML")
    parser.add_argument("--mapper", help="custom mapper YAML file")
    parser.add_argument("-t", "--text", action="store_true", help="text output")
    parser.add_argument(
        "--all", action="store_true", help="print all objects in text mode"
    )
    parser.add_argument(
        "file_or_zip", nargs="+", help="Path to either a UNL or  ZIP with UNL file"
    )
    args = parser.parse_args()

    initialize_logging(args.level, args.nocolor)

    if args.dump:
        _LOGGER.warning("dumping the mapper into %s", args.file_or_zip)
        filename = sys.stdout.fileno() if args.stdout else args.file_or_zip[0]
        with open(filename, "w") as fh:
            Eve2CMLmapper().load().dump(fh)
        return

    if args.all and not args.text:
        _LOGGER.warn("--all is only relevant with text output, ignoring")

    mapper = Eve2CMLmapper().load(args.mapper)
    labs: List[Lab] = []
    for arg in args.file_or_zip:
        labs.extend(convert_files(arg, mapper))

    # YAML is the default
    if not args.text:

        def yaml_multiline_string_pipe(dumper, data):
            text_list = [line.rstrip() for line in data.splitlines()]
            fixed_data = "\n".join(text_list)
            if len(text_list) > 1:
                return dumper.represent_scalar(
                    "tag:yaml.org,2002:str", fixed_data, style="|"
                )
            return dumper.represent_scalar("tag:yaml.org,2002:str", fixed_data)

        yaml.add_representer(str, yaml_multiline_string_pipe)

        if args.stdout:
            for lab in labs:
                print(
                    centered_line_with_stars(
                        str(Path(lab.filename).with_suffix(".yaml"))
                    )
                )
                sys.stdout.write(yaml.dump(lab.as_cml_dict(), sort_keys=False))
                print(centered_line_with_stars())
            return

        for lab in labs:
            cml_filename = Path(lab.filename).with_suffix(".yaml")
            with open(cml_filename, "w", encoding="utf-8") as cml_file:
                cml_file.write(yaml.dump(lab.as_cml_dict(), sort_keys=False))
        return

    # this is simply text output
    for lab in labs:
        txt_filename = (
            sys.stdout.fileno()
            if args.stdout
            else str(Path(lab.filename).with_suffix(".txt"))
        )
        with open(txt_filename, "w", encoding="utf-8") as out:
            dump_as_text(out, lab, args.all)
    return
