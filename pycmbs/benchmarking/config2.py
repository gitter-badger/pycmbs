# -*- coding: utf-8 -*-
"""
This file is part of pyCMBS. (c) 2012-2014
For COPYING and LICENSE details, please refer to the file
COPYRIGHT.md
"""

import json

class ConfigFile(object):
    """
    """
    pass

def load_config(filename):
    """
    Load benchmarking configuration from file
    """
    pass

def parse_config(config_string, fmt='json'):
    """
    Parse config from string
    Allow choice between config storage backends
    """
    if fmt is 'json':
        config_contents = parse_json_config(config_string)
    else:
        raise ValueError("config format not recognized")
    return config_contents

def parse_json_config(config_string):
    """
    Parse JSON file
    """
    config_contents = json.loads(config_string)
    return config_contents
    
def save_config(filename):
    """
    Save benchmarking configuration to file
    """
    pass
