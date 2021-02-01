#!/usr/bin/python3

"""This script is boilerplate designed to write test
    cases for assessment 3 of the class
    GEOM90042: Spatial Information Programming.

    Execute by entering your Anaconda environment and
    typing from the command line:

    python test_assessment3.py -v

    The examples here are given from assessment 2, you are
    to create your own and replace the docstrings. Remember
    to keep it simple. The purpose of a unit test is to test
    each operation independently of all others in the program
    to help identify small mistakes.

    Please refer to https://docs.python.org/3/library/unittest.html


    Modified by Darren Christopher Pinto
    Assessment 3 submission.
"""
import os
import unittest
import rasterio
import rasters
import numpy as np


class TestTaskOne(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.join(os.getcwd(), "CLIP.tif")
        self.highest_value = (146.29444444497085, -37.83138888914557)
        self.bounds = (2539847.5829088255, 2627857.0704815458,
                       4390250.007648419, 4451265.383560181)
        self.destn_epsg = 3110

    """check for output type of summary dem"""

    def test_raster_import(self):
        raster_output = rasters.summary_dem(self.filename)
        self.assertTrue(isinstance(raster_output, (list, dict, tuple)))

    """check for highest band value coordinate"""
    def test_highest_value_coord(self):
        comm_result = rasters.get_highest_value_coord(self.filename)
        self.assertTrue(isinstance(comm_result, (list, dict, tuple)))
        self.assertAlmostEqual(self.highest_value[0], comm_result[0])
        self.assertAlmostEqual(self.highest_value[1], comm_result[1])

    """check the bounding box of the dem  """
    def test_projection_bounds(self):
        with rasterio.open(self.filename) as dem:
            raster_bounds = rasters.convert_bounds(dem.crs, self.destn_epsg,
                                                   dem.bounds)
            self.assertAlmostEqual(self.bounds[0], raster_bounds[0])
            self.assertAlmostEqual(self.bounds[1], raster_bounds[2])
            self.assertAlmostEqual(self.bounds[2], raster_bounds[1])
            self.assertAlmostEqual(self.bounds[3], raster_bounds[3])


class TestTaskTwo(unittest.TestCase):

    def setUp(self):
        projection_name = "Scaled_1_4Reprojected_CLIP.tif"
        self.filename = os.path.join(os.getcwd(), projection_name)
        self.projected_crs = 'EPSG:3110'

    """Check for projection of the raster via a simple test for meta
     data testing"""

    def test_projection(self):
        with rasterio.open(self.filename) as dem:
            self.assertTrue(self.projected_crs, dem.crs)

    """check if some computations are carried out for slope instead of error
    exception"""

    def test_2fd(self):
        result = rasters.calc_slope_2fd(self.filename)
        self.assertFalse(np.all(result == 0))

    """check if some computations are carried out for slope instead of error
    exception"""

    def test_maxmax(self):
        result = rasters.calc_slope_maxmax(self.filename)
        self.assertFalse(np.all(result == 0))


if __name__ == '__main__':
    unittest.main()
