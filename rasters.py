"""
Author: Darren Christopher Pinto
StudentID: 1033936
Email: darrenchrist@student.unimelb.edu.au

This file is written to support various functions of assessment 3.
A clear explanation and assumptions taken are provided along with
the function.

Conversions:
The coordinates are converted to UTM EPSG:3110 for all projections.
The time is taken in secs, distance in meters.

Note: warnings are used to suppress warnings regarding deprecations.
Re-sampling and re-projection has duplicate codes to avoid errors,
attempts where made to combine, which resulted in errors, thus
its duplicated two times for re-sampling and re-projection.
No  __name__ == '__main__': defined since this program is written
to support assessment3.ipynb program.
"""

import warnings

import cv2
import numpy as np
import pyproj
import rasterio
import rasterio.features
import rasterio.mask
from affine import Affine
from rasterio.warp import calculate_default_transform, reproject, \
    Resampling, transform_bounds
from scipy import ndimage
import ProjectModules.PrettyTable as ptable

"""constants for Pretty table display"""
FILENAME = 'Filename'
COORD_SYS = 'Coordinate System'
MIN_X_LON = 'Minimum x, Minimum longitude'
MAX_X_LON = 'Maximum x, Maximum longitude'
MIN_Y_LAT = 'Minimum y, Minimum latitude'
MAX_Y_LAT = 'Maximum y, Maximum latitude'
WIDTH_HEIGHT_SIZE = 'Width, Height, Cell Size (Resolution)'
NODATA = 'Nodata'
MIN_MAX_VALUE = 'Min value : Max value'
UNIT_PX = ' px'
PARAMETER = 'Parameter'
VALUE = 'Value'
EPSG_TO = 3110
EPSG_FROM = 4326
STRING_FORMAT = '10.10f'
EPSG = 'EPSG'


def get_units_epsg(epsg):
    """
    function for extracting the unit name based on the EPSG code
    :param epsg: EPSG code
    :return: meters or degrees based on epsg
    """
    try:
        crs_from = pyproj.CRS(epsg)
        return crs_from.coordinate_system.axis_list[0].unit_name
    except(ValueError, TypeError):
        print('Unable to retrieve unit, check epsg code')


def format_values(value):
    """
    Format the double to the given format, rounding of the digits
    :param value: a double number
    :return:  formatted double number as a string
    """
    try:
        return str(format(value, STRING_FORMAT))
    except ValueError:
        print('Value format incorrect')


def convert_dict_tolist(data):
    """
    Pretty table accepts list of lists, there we append an
    header and convert the rest of the dictionary into a
    list.
    :param data: dictionary
    :return: list of list
    """
    result = [[r'$' + PARAMETER + '$', r'$' + VALUE + '$']]
    for key, value in data.items():
        new_list = [key, value]
        result.append(new_list)
    return result


def convert_bounds(src_crs, epsg, bounds):
    """
    Convert the bounds
    :param src_crs: Crs of the source file
    :param epsg:  destination crs
    :param bounds: transform bounds
    :return: tuple with 4 bound values
    """
    return transform_bounds(src_crs, {'init': 'epsg:' + str(epsg)}, *bounds)


def summary_dem(filename):
    """
     function to display the raster properties as a dictionary
     and compute the boundary in x and y format using a default
     projected epsg (3110)
    :param filename: raster filename
    :return: a dictionary with raster properties
    """
    try:
        with rasterio.open(filename) as dem:
            band1 = dem.read(1)
            cell_size = (format_values(dem.res[0]), format_values(dem.res[1]))
            bbox = convert_bounds(dem.crs, EPSG_TO, dem.bounds)
            src_epsg = int(str(dem.crs).split(':')[1])
            unit_epsg_to = str(get_units_epsg(EPSG_TO))
            unit_epsg_src = str(get_units_epsg(src_epsg))
            width = str(dem.width)
            height = str(dem.height)
            raster_info = {FILENAME: dem.name,
                           COORD_SYS: str(src_epsg) + ' [' + str(EPSG) + ']',
                           MIN_X_LON: str(bbox[0]) + ' ' + unit_epsg_to +
                           ' , ' + str(dem.bounds.left) + ' ' + unit_epsg_src,
                           MAX_X_LON: str(bbox[2]) + ' ' + unit_epsg_to +
                           ' , ' + str(dem.bounds.right) + ' ' +
                           unit_epsg_src,
                           MIN_Y_LAT: str(bbox[1]) + ' ' + unit_epsg_to +
                           ' , ' + str(dem.bounds.bottom) + ' ' +
                           unit_epsg_src,
                           MAX_Y_LAT: str(bbox[3]) + ' ' + unit_epsg_to +
                           ' , ' + str(dem.bounds.top) + ' ' +
                           unit_epsg_src,
                           WIDTH_HEIGHT_SIZE: width + UNIT_PX + ' , ' + height
                           + UNIT_PX + ' , ' + str(cell_size) + ' ' +
                           unit_epsg_to,
                           NODATA: dem.nodata,
                           MIN_MAX_VALUE: str(band1.min()) + ' : ' + str(
                               band1.max())}
            return raster_info
    except IndexError:
        print('Column Index out of bounds')
    except IOError:
        print('Error in opening the raster, check for location/availability')


def display_summary(raster_info):
    """
    function uses pretty table module to display the table based on
    requirement. (latex or ipython)
    :param raster_info: dictionary containing dem information
    :return: a pretty table object for rendering table in suitable format
    """
    raster_list = convert_dict_tolist(raster_info)
    raster_table = ptable.PrettyTable(raster_list)
    return raster_table


def right_multiplication(row, column, transform1):
    """
    function to preform right multiplication similar to
    lambda operation: lambda r, c: (c, r) * transform1
    :param row: the row
    :param column: the column
    :param transform1: transform matrix
    :return: tuple (x,y)
    """
    return (column, row) * transform1


def get_highest_value_coord(filename):
    """
    the function returns the coordinates of the highest value in the band.
    For this project, raster is considered to have 1 band.
    Methodology: sort the band in descending order, get the indices
    and do right multiplication on transform to get the actual coordinates.

    Warning is used to hide the depreciation warning.
    :param filename: raster filename
    :return: a tuple with coordinates of the highest value
    """
    try:
        warnings.filterwarnings('ignore')
        with rasterio.open(filename) as dem:
            band1 = np.array(dem.read(1))
            sorted_ind = band1.argsort(axis=None)[::-1]
            transform0 = dem.transform
            transform1 = transform0 * Affine.translation(0.5, 0.5)
            for index in sorted_ind[:1]:
                row, column = np.unravel_index(index, band1.shape)
                return right_multiplication(row, column, transform1)
        warnings.filterwarnings('default')
    except IOError:
        print('Error in opening the raster, check for location/availability')


def raster_reproject(rastername, save_as_filename, epsg):
    """
    function to reproject the data using epsg.
    The default transform is updated with new crs and meta data is
    added to the new projection. Resampling is done by bilinear
    :param rastername: input raster filename
    :param save_as_filename: save the file as
    :param epsg: input re-projection EPSG code
    :return: None
    """
    dst_crs = 'EPSG:' + str(epsg)
    try:
        with rasterio.open(rastername) as src:
            transform, width, height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds)
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': dst_crs,
                'transform': transform,
                'width': width,
                'height': height
            })

            with rasterio.open(save_as_filename, 'w', **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=dst_crs,
                        resampling=Resampling.bilinear)
    except IOError:
        print('Error in opening the raster, check for location/availability')


def raster_resample(raster_name, save_as_filename, epsg, upscale_factor):
    """
    raster resampling code to reduce or increase the no.of pixels in a given
    raster. Upscale factor determines whether it is upscaled or downscaled.
    Upscale has lesser cell size and downscale has higher cell size.
    :param raster_name: raster filename
    :param save_as_filename: save as file name
    :param epsg: epsg code for reprojection
    :param upscale_factor: the factor for upscaling or downscaling
    :return: None
    """
    try:
        with rasterio.open(raster_name) as dem:
            dst_crs = 'EPSG:' + str(epsg)

            data = dem.read(
                out_shape=(
                    dem.count,
                    int(dem.height * upscale_factor),
                    int(dem.width * upscale_factor)
                ),
                resampling=Resampling.bilinear
            )

            transform = dem.transform * dem.transform.scale(
                (dem.width / data.shape[-1]),
                (dem.height / data.shape[-2])
            )
            kwargs = dem.meta.copy()
            kwargs.update({
                'crs': dem.crs,
                'transform': transform,
                'width': dem.width * upscale_factor,
                'height': dem.height * upscale_factor
            })
            with rasterio.open(save_as_filename, 'w', **kwargs) as dst:
                for i in range(1, dem.count + 1):
                    reproject(
                        source=rasterio.band(dem, i),
                        destination=rasterio.band(dst, i),
                        src_transform=dem.transform,
                        src_crs=dem.crs,
                        dst_crs=dst_crs,
                        dst_transform=transform,
                        resampling=Resampling.bilinear)
    except IOError:
        print('Error in opening the raster, check for location/availability')


def calc_slope_2fd(filename):
    """
    function for implementing 2FD, using the kernels given in the papers
    referred in iPython assessment3. the deltaX and deltaY are divided with
    the cell size respectively.
    Ndi convolve flips the kernels therefore, the following kernels are used.
    :param filename: raster file name
    :return: np array with the slope values
    """
    try:
        warnings.filterwarnings('ignore')
        with rasterio.open(filename) as dem:
            band = np.array(dem.read(1), dtype='f4', copy=False)
            x_kernel = np.array([[0, 0, 0], [-0.5, 0, 0.5], [0, 0, 0]])
            y_kernel = np.array([[0, -0.5, 0], [0, 0, 0], [0, 0.5, 0]])
            temp = np.where(np.not_equal(band, dem.nodata), band, band)
            resoln = dem.res
            delta_x = ndimage.convolve(temp, x_kernel)
            delta_y = ndimage.convolve(temp, y_kernel)
            if (resoln[0] <= 0) | (resoln[1] <= 0):
                raise Exception("Input raster cell size is invalid.")
            dx = delta_x / resoln[0]
            dy = delta_y / resoln[1]
            slope_tangent = np.arctan(np.sqrt((dx * dx) + (dy * dy)))
        warnings.filterwarnings('default')
        return slope_tangent
    except IOError:
        print('Error in opening the raster, check for location/availability')


def solve_maximum_max(image, res):
    """
    function for solving max max, cv2 is used for padding the border
    with replication values, so that there's multiple of 3*3 cell window
    for moving window computation.
    pad is taken as 1 since, (windowsize -1)/2 = (3-1)/2=1

    if the window contains zero i.e no data value turned to zero,
    we skip the entire slope commutation so that it doesnt effect
    other values since max max uses absolute.
    :param image: the np array containing the elevation data
    :param res: resolution of the cell/ cell size
    :return: np array containing the slope
    """
    cell_size = res[0]
    sqrt_2 = np.sqrt(2)
    (iH, iW) = image.shape[:2]
    pad = 1
    image = cv2.copyMakeBorder(image, pad, pad, pad, pad,
                               cv2.BORDER_REPLICATE)
    output_slope = np.zeros((iH, iW), dtype="float32")
    for y in np.arange(pad, iH + pad):
        for x in np.arange(pad, iW + pad):
            window = image[y - pad:y + pad + 1, x - pad:x + pad + 1]
            if 0 in window:
                continue
            try:
                z5 = window[1, 1]
                z5_z1 = abs((z5 - window[2, 2]) / (sqrt_2 * cell_size))
                z5_z2 = abs((z5 - window[2, 1]) / cell_size)
                z5_z3 = abs((z5 - window[2, 0]) / (sqrt_2 * cell_size))
                z5_z9 = abs((z5 - window[0, 0]) / (sqrt_2 * cell_size))
                z5_z7 = abs((z5 - window[0, 2]) / (sqrt_2 * cell_size))
                z5_z6 = abs((z5 - window[1, 0]) / cell_size)
                z5_z8 = abs((z5 - window[0, 1]) / cell_size)
                z5_z4 = abs((z5 - window[2, 1]) / cell_size)
                mid = max(z5_z1, z5_z2, z5_z3, z5_z9, z5_z7, z5_z6,
                          z5_z8, z5_z4)
                output_slope[y - pad, x - pad] = mid
            except ZeroDivisionError:
                print('Zero division error occurred, skipping')
                continue
            except IndexError:
                print('Value not found at an index, skipping')
                continue

    return output_slope


def calc_slope_maxmax(filename):
    """
    function for calculating for slope using max max.
    Filter the band values for no data values, then apply max max method
    :param filename: raster name
    :return: np array with the slope values
    """
    try:
        with rasterio.open(filename) as dem:
            band = np.array(dem.read(1), dtype='f4', copy=False)
            filtered_band = np.where(np.not_equal(band, dem.nodata), band, 0)
            resoln = dem.res
            if (resoln[0] <= 0) | (resoln[1] <= 0):
                raise Exception("Input raster cell size is invalid.")
            slope_array = solve_maximum_max(filtered_band, resoln)
        return slope_array
    except IOError:
        print('Error in opening the raster, check for location/availability')
