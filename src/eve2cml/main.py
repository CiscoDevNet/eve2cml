import argparse
import xml.etree.ElementTree as ET
import json
import log
import logging
from typing import List
from eve_models import (
    Lab,
    Topology,
    Objects,
    Node,
    Interface,
    Network,
    Config,
    ConfigSet,
    Task,
    TextObject,
)

_LOGGER = logging.getLogger(__name__)


def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    lab = tree.getroot()
    nodes = []
    networks = []
    text_objects = []
    tasks: List[Task] = []
    configs: List[Config] = []
    configsets: List[ConfigSet] = []

    lab_name = lab.attrib.get("name")
    lab_version = lab.attrib.get("version")
    script_timeout = lab.attrib.get("scripttimeout")
    countdown = lab.attrib.get("countdown")
    lock = lab.attrib.get("lock")
    sat = lab.attrib.get("sat")

    for node_elem in lab.findall(".//node"):
        node = Node(
            id=node_elem.attrib.get("id"),
            name=node_elem.attrib.get("name"),
            type=node_elem.attrib.get("type"),
            template=node_elem.attrib.get("template"),
            image=node_elem.attrib.get("image"),
            console=node_elem.attrib.get("console"),
            cpu=node_elem.attrib.get("cpu"),
            cpulimit=node_elem.attrib.get("cpulimit"),
            ram=node_elem.attrib.get("ram"),
            ethernet=node_elem.attrib.get("ethernet"),
            uuid=node_elem.attrib.get("uuid"),
            firstmac=node_elem.attrib.get("firstmac"),
            qemu_options=node_elem.attrib.get("qemu_options"),
            qemu_version=node_elem.attrib.get("qemu_version"),
            qemu_arch=node_elem.attrib.get("qemu_arch"),
            delay=node_elem.attrib.get("delay"),
            sat=node_elem.attrib.get("sat"),
            icon=node_elem.attrib.get("icon"),
            config=node_elem.attrib.get("config"),
            left=node_elem.attrib.get("left"),
            top=node_elem.attrib.get("top"),
            e0dhcp=node_elem.attrib.get("e0dhcp"),
        )

        for interface_elem in node_elem.findall(".//interface"):
            interface = Interface(
                id=interface_elem.attrib.get("id"),
                name=interface_elem.attrib.get("name"),
                type=interface_elem.attrib.get("type"),
                network_id=interface_elem.attrib.get("network_id"),
                labelpos=interface_elem.attrib.get("labelpos"),
                curviness=interface_elem.attrib.get("curviness"),
                beziercurviness=interface_elem.attrib.get("beziercurviness"),
                midpoint=interface_elem.attrib.get("midpoint"),
                srcpos=interface_elem.attrib.get("srcpos"),
                dstpos=interface_elem.attrib.get("dstpos"),
            )
            node.interfaces.append(interface)

        nodes.append(node)

    for network_elem in lab.findall(".//networks/network"):
        network = Network(
            id=network_elem.attrib.get("id"),
            type=network_elem.attrib.get("type"),
            name=network_elem.attrib.get("name"),
            left=network_elem.attrib.get("left"),
            top=network_elem.attrib.get("top"),
        )
        networks.append(network)

    for text_elem in lab.findall(".//objects/textobjects/textobject"):
        text_object = TextObject(
            id=text_elem.attrib.get("id"),
            name=text_elem.attrib.get("name"),
            type=text_elem.attrib.get("type"),
        )
        data = text_elem.find("data")
        if data is not None:
            text_object.data = data.text
        text_objects.append(text_object)

    for task_elem in lab.findall(".//objects/tasks/task"):
        task = Task(
            id=task_elem.attrib.get("id"),
            name=task_elem.attrib.get("name"),
            type=task_elem.attrib.get("type"),
        )
        data = task_elem.find("data")
        if data is not None:
            task.data = data.text
        tasks.append(task)

    for config_elem in lab.findall(".//objects/configs/config"):
        config = Config(id=config_elem.attrib.get("id"), data=config_elem.text)
        configs.append(config)

    for configset_elem in lab.findall(".//objects/configsets/configset"):
        configs: List[Config] = []
        configset = ConfigSet(
            id=configset_elem.attrib.get("id", "unknown"),
            name=configset_elem.attrib.get("name", "unknown"),
            configs=configs,
        )
        for config_elem in configset_elem.findall("config"):
            config = Config(id=config_elem.attrib.get("id"), data=config_elem.text)
            configset.configs.append(config)
        configsets.append(configset)

    lab = Lab(
        name=lab_name,
        version=lab_version,
        scripttimeout=script_timeout,
        countdown=countdown,
        lock=lock,
        sat=sat,
        topology=Topology(nodes=nodes, networks=networks),
        objects=Objects(tasks, configs, configsets, text_objects),
    )

    return lab


def main():
    parser = argparse.ArgumentParser(description="Convert XML data to dictionary")
    parser.add_argument("--level", default="info", help="log level")
    parser.add_argument("xml_file", help="Path to the XML file")
    args = parser.parse_args()

    log.init(args.level)
    xml_file = args.xml_file
    lab = parse_xml(xml_file)

    _LOGGER.info("xml file parsed")

    # print(lab)
    # print("Nodes:")
    # for node in lab.topology.nodes:
    #     print(node)
    #     for interface in node.interfaces:
    #         print("\t", interface)
    #
    # print("Networks:")
    # for network in lab.topology.networks:
    #     # print(f"  Network ID: {network.id}")
    #     # print(f"  Network Type: {network.type}")
    #     # print(f"  Network Name: {network.name}")
    #     # print(f"  Network Left: {network.left}")
    #     # print(f"  Network Top: {network.top}")
    #     print(network)
    #
    # print("Textobjects")
    # for text_object in lab.objects.textobjects:
    #     print(text_object)
    #     print()
    #
    # print("Tasks")
    # for task in lab.objects.tasks:
    #     print(task)
    #     print()
    #
    # print("Configs")
    # for config in lab.objects.configs:
    #     print(config)
    #     print()
    #
    # print("Configsets")
    # for configset in lab.objects.configsets:
    #     print(f"Config Set ID: {configset.id}")
    #     print(f"Config Set Name: {configset.name}")
    #     print("Contained Configs:")
    #     for config in configset.configs:
    #         print(config)
    #     print()

    print(json.dumps(lab.as_cml_dict()))


if __name__ == "__main__":
    main()
