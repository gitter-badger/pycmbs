# -*- coding: utf-8 -*-
"""
This file is part of pyCMBS. (c) 2012-2014
For COPYING and LICENSE details, please refer to the file
COPYRIGHT.md
"""

import os
import numpy as np


class Region(object):
    """
    class to specify a Region in pyCMBS. A region defines either
    a rectangle in the data matrix or it can be defined by
    lat/lon coordinates
    """
    def __init__(self, x1, x2, y1, y2, label, type='index', mask=None):
        """
        constructor of class

        Parameters
        ----------
        x1 : float
            start position in x-direction (either x index or longitude)
        x2 : float
            stop position in x-direction (either x index or longitude)
        y1 : float
            start position in y-direction (either y index or latitude)
        y2 : float
            stop position in y-direction (either y index or latitude)
        label : str
            label of the region
        type : str
            type of coordiantes (x1,x2,y1,y2): I{index} or I{latlon}
        mask : ndarray
            mask that will be applied in addition to
            the coordinates/indices
        """

        raise ValueError('This class is depreciated! Use classes RegionPolygon, RegionIndex, RegionLatLon instead!')

    def get_subset(self, x):
        """
        extract region subset from data array x

        Parameters
        ----------
        x : ndarray
            array where the data is extracted from
        """
        if x.ndim == 3:
            return x[:, self.y1:self.y2, self.x1:self.x2]
        elif x.ndim == 2:
            return x[self.y1:self.y2, self.x1:self.x2]
        else:
            raise ValueError('Invalid data array for subsetting! %s'
                             % np.shape(x))


class RegionGeneric(object):
    """
    Generic class to define regions
    """
    def __init__(self, id, label=None):
        self.lon = None
        self.lat = None
        self.type = None
        self.id = id
        self.mask = None
        if label is None:
            raise ValueError('ERROR: a label needs to be given for regions')
        else:
            self.label = label

    def _check_bbox_validity(self, x1, x2, y1, y2):
        if x2 < x1:
            raise ValueError('Invalid X boundaries for region')
        if y2 < y1:
            raise ValueError('Invalid Y boundaries for region')

    def _get_label(self):
        return self.label.replace(' ', '')

    def get_Bbox(self):
        """
        return bounding box of coordinates
        """
        if self.type == 'index':
            return self._get_corners_index()
        else:
            return self._get_corners_latlon()

    def _get_corners_index(self):
        """ return a list of corner indices """
        l = [(self.x1, self.y1), (self.x1, self.y2),
             (self.x2, self.y2), (self.x2, self.y1)]
        return l

    def _get_corners_latlon(self):
        """ return a list of corner lat/lon """
        if self.lat is None:
            raise ValueError('ERROR: can not retrieve Bbox without latitudes!')
        if self.lon is None:
            raise ValueError('ERROR: can not retrieve Bbox without longitudes!')

        l = [(min(self.lon), min(self.lat)), (min(self.lon), max(self.lat)),
             (max(self.lon), max(self.lat)), (max(self.lon), min(self.lat))]
        return l


class RegionPolygon(RegionGeneric):
    def __init__(self, id, lon, lat, label=None):
        """
        define a region by a polygon

        Parameters
        ----------
        id : str/int
            unique identifier for region
        lon : ndarray/list
            sequence of longitudes
        lat : ndarray/list
            sequence of latitudes
        label : str
            label for region (used e.g. for plotting)
        """
        super(RegionPolygon, self).__init__(id, label=label)
        self.lon = lon
        self.lat = lat
        self.type = 'polygon'

    def _xcoords(self):
        return self.lon

    def _ycoords(self):
        return self.lat



class RegionShape(object):
    """
    This is a container that reads a shapefile and stores
    all shapes in that shapefile as individual regions

    https://code.google.com/p/pyshp/
    """
    def __init__(self, shp_file):
        """
        Parameters
        ----------
        shp_file : str
            name of shapefile (WITHOUT extension)
        """
        import shapefile
        if not os.path.exists(shp_file + '.shp'):
            raise ValueError('Shapefile not existing: ', shp_file + '.shp')

        self.regions = {}

        sf = shapefile.Reader(shp_file)
        #~ print sf.fields
        #~ print sf.records[0]

        # loop over all shapes. Each shape will specify a new region
        id = 1
        for s in sf.shapes():
            lon = [p[0] for p in s.points]
            lat = [p[1] for p in s.points]
            self.regions.update({id: RegionPolygon(id, lon, lat, label='reg#' + str(id))})
            id += 1


class RegionIndex(RegionGeneric):
    def __init__(self, id, x1, x2, y1, y2, label=None):
        self._check_bbox_validity(x1, x2, y1, y2)
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        super(RegionIndex, self).__init__(id, label=label)
        self.type = 'index'


class RegionBboxLatLon(RegionPolygon):
    """
    specify region through a Bounding box using
    lat/lon coordinates
    """
    def __init__(self, id, x1, x2, y1, y2, label=None):
        self._check_bbox_validity(x1, x2, y1, y2)
        self.latmin = y1
        self.latmax = y2
        self.lonmin = x1
        self.lonmax = x2
        lon, lat = self._bbox_to_points()  # create vector with coordinates
        super(RegionBboxLatLon, self).__init__(id, lon, lat, label=label)

    def _bbox_to_points(self):
        """ write Bbox corners to sequence of coordinates of points """
        lon = np.asarray([self.lonmin, self.lonmin, self.lonmax, self.lonmax])
        lat = np.asarray([self.latmin, self.latmax, self.latmax, self.latmin])
        return lon, lat


class RegionParser(object):
    """
    class to parse region definitions in differnt formats
    reads regions from files and provides them in a list of  Region
    objects
    """

    def __init__(self, filename, format='ini'):
        """
        Parameters
        ----------
        filename : str
            name of file to read
        format : str
            data format of region file ['ini']
            ini : windows like INI file structure
        """
        self.format = format
        self.filename = filename

        self._check()

        self.regions = {}
        self._read()

    def _check(self):
        if not os.path.exists(self.filename):
            raise ValueError('ERROR: Regionfile not existing!')
        if self.format not in ['ini']:
            raise ValueError('ERROR: Format not correctly specified!')

    def _read(self):
        if self.format == 'ini':
            self._parse_ini_file()
        else:
            raise ValueError('ERROR: invalid format!')

    def _parse_ini_file(self):
        """
        parse a region file that has the structure of a Windows INI file
        """
        from ConfigParser import SafeConfigParser
        parser = SafeConfigParser()
        parser.read(self.filename)

        for section in parser.sections():
            if section.upper() == 'COMMENT':
                for name, value in parser.items(section):
                    if name.upper() == 'LABEL':
                        self.label = value
                    elif name.upper() == 'DESCRIPTION':
                        self.description = value
                    else:
                        raise ValueError('ERROR: Invalid option for COMMENT')
            else:  # read region sections
                tmp_lon = None
                tmp_lat = None
                tmp_id = None
                for name, value in parser.items(section):

                    if name.upper() == 'COORDINATES':
                        # the coordinates come as a list of tuples. Split them
                        # into lat/lon
                        coord = eval(value)
                        lat = []
                        lon = []
                        for la, lo in coord:
                            lat.append(la)
                            lon.append(lo)
                        tmp_lat = np.asarray(lat)
                        tmp_lon = np.asarray(lon)
                    elif name.upper() == 'ID':
                        tmp_id = int(value)
                    else:
                        print section, name
                        raise ValueError('Unsupported attribute!')

                if tmp_lon is None:
                    raise ValueError('ERROR: no longitudes found!')
                if tmp_lat is None:
                    raise ValueError('ERROR: no latitudes found!')
                if tmp_id is None:
                    raise ValueError('ERROR: no ID specified!')

                self.regions.update({section: RegionPolygon(tmp_id, tmp_lon, tmp_lat, label=section)})
                del tmp_lon, tmp_lat, tmp_id
