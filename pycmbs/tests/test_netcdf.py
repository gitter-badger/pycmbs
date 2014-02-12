# -*- coding: utf-8 -*-

import unittest
from pycmbs import netcdf

class TestPycmbsNetcdf(unittest.TestCase):

    def setUp(self):
        pass

    def test_netCDFHandlerinit_WithInvalidValue(self):
        with self.assertRaises(ValueError):
            cdf = netcdf.NetCDFHandler(netcdf_backend='invalid_backend')

    def test_netCDF_openFile_InvalidMode(self):
        with self.assertRaises(ValueError):
            cdf = netcdf.NetCDFHandler()
            cdf.open_file('nix.nc', 'xxx')

    def test_netCDF_openFile_InvalidFile(self):
        with self.assertRaises(ValueError):
            cdf = netcdf.NetCDFHandler()
            cdf.open_file('nopefile.nc', 'r')

    def test_netCDFHandlerinit_Default(self):
        cdf = netcdf.NetCDFHandler()

    @unittest.skip('Nio will be deprecated')
    def test_netCDFHandlerinit_Nio(self):
        cdf = netcdf.NetCDFHandler(netcdf_backend='Nio')
        self.assertEqual(cdf.type, 'Nio')  # could be that this fails if Nio not existing!
        cdf = netcdf.NetCDFHandler(netcdf_backend='nio')
        self.assertEqual(cdf.type, 'nio')

if __name__ == "__main__":
    unittest.main()

# vim: expandtab shiftwidth=4 softtabstop=4
