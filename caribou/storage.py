import os
import json
from .exceptions import MissingParameter

VERSION = 1


GLOBAL_STORAGE = {}
TEMPORARY_STORAGE = {}


def load_setting(name):
    return GLOBAL_STORAGE.get('setting.%s' % name)


def save_setting(name, value):
    GLOBAL_STORAGE['setting.%s' % name] = value


def save_parameter(prefix, parameter, value):
    GLOBAL_STORAGE[parameter.storage_path(prefix)] = value


def load_parameter(prefix, parameter):
    return GLOBAL_STORAGE.get(parameter.storage_path(prefix))


def save_request_result(route, value):
    TEMPORARY_STORAGE['%s.result' % route.storage_prefix] = value


def load_request_result(route):
    return TEMPORARY_STORAGE.get('%s.result' % route.storage_prefix)


def get_parameter_values(prefix, parameters):
    values = {}
    for param in parameters:
        storage_path = param.storage_path(prefix)

        value = GLOBAL_STORAGE.get(storage_path)

        if param.required and value in (None, ''):
            raise MissingParameter(param.name)

        if value in (None, ''):
            value = param.default
        else:
            value = param.process_value(value)

        values[param.name] = value
    return values


def get_parameter_values_for_route(route):
    if route.group is not None:
        group_values = get_parameter_values(
            route.group.storage_prefix,
            route.group.parameters
        )
    else:
        group_values = {}

    route_values = get_parameter_values(
        route.storage_prefix,
        route.parameters
    )
    return group_values, route_values


# XXX: cleanup
def load_storage():
    global GLOBAL_STORAGE
    if os.path.exists('/tmp/caribou'):
        with open('/tmp/caribou') as f:
            data = json.load(f)
            if data['version'] != VERSION:
                return
            GLOBAL_STORAGE = data['data']


def persist_storage():
    with open('/tmp/caribou', 'w') as f:
        json.dump({
            'version': VERSION,
            'data': GLOBAL_STORAGE
        }, f)
