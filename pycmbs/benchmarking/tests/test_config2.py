# -*- coding: utf-8 -*-
"""
This file is part of pyCMBS. (c) 2012-2014
For COPYING and LICENSE details, please refer to the file
COPYRIGHT.md
"""

import os
import unittest
import json
import yaml
import tempdir
from pycmbs.benchmarking import config2

class TestPycmbsBenchmarkingConfig(unittest.TestCase):

    def setUp(self):
        self.test_cfg = """
        {
            "general": "None",
            "models": "None",
            "observations": "None",
            "plots": {
                "Hovmoeller": "True"}
        }
        """

    def test_parse_config_WorksWithJsonString(self):
        ref_dict = json.loads(self.test_cfg)
        test_dict = config2.parse_config(self.test_cfg, fmt='json')
        self.assertDictContainsSubset(ref_dict, test_dict)

    def test_parse_config_WorksWithYamlString(self):
        self.yaml_cfg = "models: " + "None"
        ref_dict = yaml.load(self.yaml_cfg)
        test_dict = config2.parse_config(self.yaml_cfg, fmt='yaml')
        self.assertDictContainsSubset(ref_dict, test_dict)
    
    def test_load_config_LoadFromFile(self):
        with tempdir.TempDir() as tdir:
            tempfile_path = os.path.join(tdir, 'testfile.cfg')
            tempfile = open(tempfile_path, 'w')
            print >> tempfile, self.test_cfg
            tempfile.close()
            expected_dict = json.loads(self.test_cfg)
            actual_dict = config2.load_config(tempfile_path, fmt='json')
            self.assertEqual(expected_dict, actual_dict)

if __name__ == "__main__":
    unittest.main()
# vim: expandtab shiftwidth=4 softtabstop=4
