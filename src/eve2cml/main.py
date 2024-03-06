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

    lab = Lab(
        name=lab_name,
        version=lab_version,
        scripttimeout=script_timeout,
        countdown=countdown,
        lock=lock,
        sat=sat,
        topology=Topology(nodes=Node.parse(lab), networks=Network.parse(lab)),
        objects=Objects.parse(lab, ".//objects"),
    )

    return lab


def main():
    parser = argparse.ArgumentParser(description="Convert XML data to dictionary")
    parser.add_argument("--level", default="info", help="log level")
    parser.add_argument("xml_file", help="Path to the XML file")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--text", action="store_true", help="text output")
    parser.add_argument(
        "--all", action="store_true", help="print all objects in text mode"
    )
    args = parser.parse_args()

    initialize_logging(args.level)
    xml_file = args.xml_file
    _LOGGER.info("parse XML file")
    lab = parse_xml(xml_file)
    _LOGGER.info("XML file parsed")

    if args.all and not args.text:
        _LOGGER.warn("all is only relevant with text output, ignoring")

    if args.text and args.json:
        _LOGGER.error("either Text or JSON, not both")
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

        # def str_presenter(dumper, data):
        #     """configures yaml for dumping multiline strings
        #     Ref: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data"""
        #     if data.count('\n') > 0:  # check for multiline string
        #         return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        #     return dumper.represent_scalar('tag:yaml.org,2002:str', data)
        # # def str_presenter(dumper, data):
        # #     """configures yaml for dumping multiline strings
        # #     Ref: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data"""
        # #     if len(data.splitlines()) > 1:  # check for multiline string
        # #         return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        # #     return dumper.represent_scalar('tag:yaml.org,2002:str', data)
        #
        # yaml.add_representer(str, str_presenter)
        # yaml.representer.SafeRepresenter.add_representer(str, str_presenter) # to use with safe_dum

        # class CorbinDumper(yaml.SafeDumper):
        #     def increase_indent(self, flow=False, indentless=False):
        #         return super(CorbinDumper, self).increase_indent(flow, False)
        # print(yaml.dump(lab.as_cml_dict(), Dumper=CorbinDumper,allow_unicode=True, default_flow_style=False))
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

    print(">>> Textobjects <<<")
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

    print(">>> Configsets <<<")
    for configset in lab.objects.configsets:
        print(f"Config Set ID: {configset.id}")
        print(f"Config Set Name: {configset.name}")
        print("Contained Configs:")
        for config in configset.configs:
            print(config)
        print()


if __name__ == "__main__":
    main()
