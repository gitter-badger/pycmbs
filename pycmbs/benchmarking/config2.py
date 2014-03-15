# -*- coding: utf-8 -*-
"""
This file is part of pyCMBS. (c) 2012-2014
For COPYING and LICENSE details, please refer to the file
COPYRIGHT.md
"""
class ConfigFile(object):
    """
    """
    pass

def load_config(filename, fmt=None):
    """
    Load benchmarking configuration from file
    """
    fh = open(filename, 'r')
    file_contents = fh.read()
    config_contents = parse_config(file_contents, fmt=fmt)
    fh.close()
    return config_contents

def parse_config(config_string, fmt=None):
    """
    Parse config from string
    Allow choice between config storage backends
    """
    if fmt is 'json':
        config_contents = parse_json_config(config_string)
    elif fmt is 'yaml' or None:
        config_contents = parse_yaml_config(config_string)
    else:
        raise ValueError("config format not recognized")
    return config_contents

def parse_json_config(config_string):
    """
    Parse JSON file
    """
    import json
    config_contents = json.loads(config_string)
    return config_contents
    
def parse_yaml_config(config_string):
    """
    Parse YAML string
    """
    import yaml
    config_contents = yaml.load(config_string)
    return config_contents

def save_config(filename):
    """
    Save benchmarking configuration to file
    """
    pass
