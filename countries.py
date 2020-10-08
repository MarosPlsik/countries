#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from osgeo import ogr
import pandas as pd

class Point(object):
    """ Wrapper for ogr point """
    def __init__(self, lat, lng):
        """ Coordinates are in degrees """
        self.point = ogr.Geometry(ogr.wkbPoint)
        self.point.AddPoint(lng, lat)
    
    def getOgr(self):
        return self.point
    ogr = property(getOgr)

class Country(object):
    """ Wrapper for ogr country shape. Not meant to be instantiated directly. """
    def __init__(self, shape):
        self.shape = shape
    
    def getIso(self):
        return self.shape.GetField('ISO2')
    iso = property(getIso)
    
    def __str__(self):
        return self.shape.GetField('NAME')
    
    def contains(self, point):
        return self.shape.geometry().Contains(point.ogr)

class CountryChecker(object):
    """ Loads a country shape file, checks coordinates for country location. """
    
    def __init__(self, country_file):
        driver = ogr.GetDriverByName('ESRI Shapefile')
        self.countryFile = driver.Open(country_file)
        self.iso_to_id_dict = pd.read_csv(os.path.join(country_file, 'iso_to_id.csv'))
        self.layer = self.countryFile.GetLayer()
    
    def getCountry(self, point):
        """
        Checks given gps-incoming coordinates for country.
        Output is either country shape index or None
        """
        
        for i in range(self.layer.GetFeatureCount()):
            country = self.layer.GetFeature(i)
            if country.geometry().Contains(point.ogr):
                return Country(country)

        # nothing found
        return None

    def coord_in_countries(self, point, allowed_iso_codes):
        """

        """
        iso_to_id_dict = dict(zip(self.iso_to_id_dict.ISO, self.iso_to_id_dict.ID))
        for iso in allowed_iso_codes:
            country_ix = iso_to_id_dict[iso]
            country_feature = self.layer.GetFeature(country_ix)
            if country_feature.geometry().Contains(point.ogr):
                return iso
        return ''
