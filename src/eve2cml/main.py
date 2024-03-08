import argparse
import json
import logging
import xml.etree.ElementTree as ET

import yaml

from .eve import *
from .log import initialize_logging

_LOGGER = logging.getLogger(__name__)

UNKNOWN = "unknown"


def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    lab = tree.getroot()

    lab_name = lab.attrib.get("name")
    lab_version = lab.attrib.get("version")
    script_timeout = lab.attrib.get("scripttimeout")
    countdown = lab.attrib.get("countdown")
    lock = lab.attrib.get("lock")
    sat = lab.attrib.get("sat")

    desc = lab.find(".//description")
    task = lab.find(".//body")

    description = ""
    if desc is not None and desc.text:
        description += f"## Description: \n\n{desc.text}\n"
    if task is not None and task.text:
        description += f"## Task: \n\n{task.text}\n"
    description += "\n\nImported via `eve2cml` converter"

    lab = Lab(
        name=lab_name,
        version=lab_version,
        scripttimeout=script_timeout,
        countdown=countdown,
        lock=lock,
        sat=sat,
        description=description,
        topology=Topology(nodes=Node.parse(lab), networks=Network.parse(lab)),
        objects=Objects.parse(lab, ".//objects"),
    )

    return lab


def main():
    parser = argparse.ArgumentParser(
        description="Convert UNL/XML topologies to CML2 topologies"
    )
    parser.add_argument("-l", "--level", default="info", help="log level")
    parser.add_argument("-j", "--json", action="store_true", help="JSON output")
    parser.add_argument("-t", "--text", action="store_true", help="text output")
    parser.add_argument(
        "--all", action="store_true", help="print all objects in text mode"
    )
    parser.add_argument("xml_file", help="Path to the XML file")
    args = parser.parse_args()

    initialize_logging(args.level)
    xml_file = args.xml_file
    _LOGGER.info("Parse XML file")
    lab = parse_xml(xml_file)
    _LOGGER.info("XML file parsed")

    if args.all and not args.text:
        _LOGGER.warn("--all is only relevant with text output, ignoring")

    if args.text and args.json:
        _LOGGER.error("Either Text or JSON, not both")
        return

    if args.json:
        print(json.dumps(lab.as_cml_dict()))
        return

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

        print(yaml.dump(lab.as_cml_dict(), sort_keys=False))
        return

    print(lab)
    print()

    print(">>> Nodes <<<")
    for node in lab.topology.nodes:
        print(node)
        for interface in node.interfaces:
            print("\t", interface)
        print()

    print(">>> Networks <<<")
    for network in lab.topology.networks:
        print(network)
    print()

    print(">>> Text objects <<<")
    for text_object in lab.objects.textobjects:
        print(text_object)
    print()

    if not args.all:
        return

    print(">>> Tasks <<<")
    for task in lab.objects.tasks:
        print(task)
    print()

    print(">>> Configs <<<")
    for config in lab.objects.configs:
        print(config)
    print()

    print(">>> Config sets <<<")
    for configset in lab.objects.configsets:
        print(f"Config Set ID: {configset.id}")
        print(f"Config Set Name: {configset.name}")
        print("Contained Configs:")
        for config in configset.configs:
            print(config)
        print()


if __name__ == "__main__":
    main()
