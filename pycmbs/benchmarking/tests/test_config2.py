# -*- coding: utf-8 -*-
"""
This file is part of pyCMBS. (c) 2012-2014
For COPYING and LICENSE details, please refer to the file
COPYRIGHT.md
"""

import unittest
import json
from pycmbs.benchmarking import config2

class TestPycmbsBenchmarkingConfig(unittest.TestCase):

    def setUp(self):
        self.test_cfg = """
        {
            "general": "None",
            "models": "None",
            "observations": "None",
            "plots": "None"
        }
        """
    def test_parse_config_WorksWithJsonString(self):
        ref_list = json.loads(self.test_cfg)
        test_list = config2.parse_config(self.test_cfg, fmt='json')
        self.assertDictContainsSubset(ref_list, test_list)

if __name__ == "__main__":
    unittest.main()
# vim: expandtab shiftwidth=4 softtabstop=4
