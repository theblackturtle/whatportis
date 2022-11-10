# -*- coding: utf-8 -*-

import os
from tinydb import TinyDB, where
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from collections import namedtuple


Port = namedtuple("Port", ["name", "port", "protocol", "description"])
path = os.path.join(os.path.expanduser("~"), ".whatportis_db.json")


def get_database():
    return TinyDB(path, storage=CachingMiddleware(JSONStorage))


def database_exists():
    return os.path.isfile(path)


def merge_protocols(ports=[]):
    """
    This function merge rows having the exact same data (port, name,
    description) but a different protocol.

    :param ports: the list of ports
    :return: all ports with merged protocols
    :rtype: list
    """
    keys = {}
    for port in ports:
        key = "{}-{}-{}".format(port.get("description"), port.get("name"), port.get("port"))
        if key not in keys:
            keys[key] = port
        else:
            keys[key]["protocol"] += ", {}".format(port.get("protocol"))
    return list(keys.values())


def get_ports(port, like=False):
    """
    This function creates the SQL query depending on the specified port and
    the --like option.

    :param port: the specified port
    :param like: the --like option
    :return: all ports matching the given ``port``
    :rtype: list
    """
    where_field = "port" if port.isdigit() else "name"
    db = get_database()

    if like:
        ports = db.search(where(where_field).search(port))
    else:
        ports = db.search(where(where_field) == port)

    ports = merge_protocols(ports)
    return [Port(**port) for port in ports]  # flake8: noqa (F812)


def get_description(protocol_name):
    """
    This function returns the description of the given protocol.

    :param protocol: the protocol
    :return: the description of the protocol
    :rtype: str
    """
    db = get_database()
    port = db.search(where("protocol") == protocol_name.lower())
    if port:
        return port[0].get("description")
    return ""
