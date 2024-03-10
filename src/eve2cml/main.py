import argparse
import json
import logging
import os
import sys
import xml.etree.ElementTree as ET
import zipfile
from typing import List

import yaml

from .eve import *
from .log import initialize_logging

_LOGGER = logging.getLogger(__name__)


def parse_xml(xml_content: str, filename: str):
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
    )

    return parsed_lab


def convert_file(content: str, filename: str) -> Lab:
    _LOGGER.info("Parse XML file %s", filename)
    lab = parse_xml(content, filename)
    _LOGGER.info("Done with file %s", filename)
    return lab


def convert_files(file_or_zip: str) -> List[Lab]:
    lab: List[Lab] = []
    if zipfile.is_zipfile(file_or_zip):
        with zipfile.ZipFile(file_or_zip, "r") as zip_file:
            for file_info in zip_file.infolist():
                dirname = os.path.dirname(file_info.filename)
                if dirname.startswith("__MACOSX"):
                    continue
                filename = os.path.basename(file_info.filename)
                if filename.endswith(".unl"):
                    try:
                        content = zip_file.read(file_info.filename)
                        dir = f"{dirname}--{filename}" if dirname else filename
                        lab.append(convert_file(content.decode("utf-8"), dir))
                    except KeyError:
                        print(f"File {filename} not found in the ZIP archive.")
    else:
        with open(file_or_zip, "r", encoding="utf-8") as xml_file:
            content = xml_file.read()
            lab.append(convert_file(content, file_or_zip))
    return lab


def dump_as_text(filename: "str|int", lab: Lab, dump_all: bool):
    with open(filename, "w", encoding="utf-8") as out:
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


def main():
    parser = argparse.ArgumentParser(
        description="Convert UNL/XML topologies to CML2 topologies"
    )
    parser.add_argument(
        "--level",
        default="warning",
        choices=["debug", "info", "warning", "error", "critical"],
        help="specify the log level",
    )
    parser.add_argument("-j", "--json", action="store_true", help="JSON output")
    parser.add_argument("-t", "--text", action="store_true", help="text output")
    parser.add_argument(
        "--all", action="store_true", help="print all objects in text mode"
    )
    parser.add_argument(
        "file_or_zip", help="Path to either a UNL or  ZIP with UNL file"
    )
    args = parser.parse_args()

    initialize_logging(args.level)

    if args.all and not args.text:
        _LOGGER.warn("--all is only relevant with text output, ignoring")

    if args.text and args.json:
        _LOGGER.error("Either Text or JSON, not both")
        return

    labs = convert_files(args.file_or_zip)

    if args.json:
        if len(labs) == 1:
            print(json.dumps(labs[0].as_cml_dict()))
            return
        for lab in labs:
            with open(lab.filename, "w", encoding="utf-8") as cml_file:
                cml_file.write(json.dumps(lab.as_cml_dict()))

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
        if len(labs) == 1:
            print(yaml.dump(labs[0].as_cml_dict(), sort_keys=False))
            return
        for lab in labs:
            with open(lab.filename, "w", encoding="utf-8") as cml_file:
                cml_file.write(yaml.dump(lab.as_cml_dict(), sort_keys=False))
        return

    # this is simply text output
    if len(labs) == 1:
        dump_as_text(sys.stdout.fileno(), labs[0], args.all)
    else:
        for lab in labs:
            dump_as_text(lab.filename, lab, args.all)
    return


if __name__ == "__main__":
    main()
