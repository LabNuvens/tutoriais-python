"""
Reading SIPAM CAPPI (level 2) objects.

Data source: https://adc.arm.gov/discovery/#/results/id::3900_macro_sipam-s-band-cappi_cloud_radardoppler?showDetails=true

Adapted from pyart.io.read_grid source code
(https://arm-doe.github.io/pyart/_modules/pyart/io/grid_io.html)

@author: Camila Lopes (camila.lopes@iag.usp.br)

"""

import datetime
import warnings

import netCDF4
import numpy as np

from pyart.core.grid import Grid
from pyart.io.cfradial import _ncvar_to_dict, _create_ncvar
from pyart.io.common import _test_arguments


def read_sipam_cappi(
    filename,
    exclude_fields=[
        "start_time",
        "stop_time",
        "time_bounds",
        "x0",
        "y0",
        "lat0",
        "lon0",
        "z0",
        "grid_mapping_0",
    ],
    include_fields=None,
    **kwargs
):
    """
    Read a netCDF grid file produced by Py-ART.

    Parameters
    ----------
    filename : str
        Filename of netCDF grid file to read. This file must have been
        produced by :py:func:`write_grid` or have identical layout.

    Other Parameters
    ----------------
    exclude_fields : list or None, optional
        List of fields to exclude from the radar object. This is applied
        after the `file_field_names` and `field_names` parameters. Set
        to None to include all fields specified by include_fields.
    include_fields : list or None, optional
        List of fields to include from the radar object. This is applied
        after the `file_field_names` and `field_names` parameters. Set
        to None to include all fields not specified by exclude_fields.

    Returns
    -------
    grid : Grid
        Grid object containing gridded data.

    """
    # test for non empty kwargs
    _test_arguments(kwargs)

    if exclude_fields is None:
        exclude_fields = []

    reserved_variables = [
        "time",
        "x",
        "y",
        "z",
        "origin_latitude",
        "origin_longitude",
        "origin_altitude",
        "point_x",
        "point_y",
        "point_z",
        "projection",
        "point_latitude",
        "point_longitude",
        "point_altitude",
        "radar_latitude",
        "radar_longitude",
        "radar_altitude",
        "radar_name",
        "radar_time",
        "base_time",
        "time_offset",
        "ProjectionCoordinateSystem",
    ]

    dset = netCDF4.Dataset(filename, mode="r")

    # metadata
    metadata = dict([(k, getattr(dset, k)) for k in dset.ncattrs()])

    # required reserved variables
    time = _ncvar_to_dict(dset.variables["time"])
    origin_latitude = {
        "data": [dset.variables["grid_mapping_0"].latitude_of_projection_origin],
        "long_name": "Latitude of projection origin",
        "units": "degree_N",
    }
    origin_longitude = {
        "data": [dset.variables["grid_mapping_0"].longitude_of_projection_origin],
        "long_name": "Longitude of projection origin",
        "units": "degree_E",
    }
    origin_altitude = None
    x = _ncvar_to_dict(dset.variables["x0"])
    x["data"] = x["data"] * 1000
    x["units"] = "m"
    y = _ncvar_to_dict(dset.variables["y0"])
    y["data"] = y["data"] * 1000
    y["units"] = "m"
    z = _ncvar_to_dict(dset.variables["z0"])
    z["data"] = z["data"] * 1000
    z["units"] = "m"

    # projection
    projection = {"data": [], "proj": "aeqd", "_include_lon_0_lat_0": "true"}
    projection.pop("data")
    # map _include_lon_0_lat_0 key to bool type
    if "_include_lon_0_lat_0" in projection:
        v = projection["_include_lon_0_lat_0"]
        projection["_include_lon_0_lat_0"] = {"true": True, "false": False}[v]

    # read in the fields
    fields = {}

    # fields in the file has a shape of (1, nz, ny, nx) with the leading 1
    # indicating time but should shaped (nz, ny, nx) in the Grid object
    field_shape = tuple([len(dset.dimensions[d]) for d in ["z0", "y0", "x0"]])
    field_shape_with_time = (1,) + field_shape

    # check all non-reserved variables, those with the correct shape
    # are added to the field dictionary, if a wrong sized field is
    # detected a warning is raised
    field_keys = [k for k in dset.variables if k not in reserved_variables]
    for field in field_keys:
        if field in exclude_fields:
            continue
        if include_fields is not None:
            if field not in include_fields:
                continue
        field_dic = _ncvar_to_dict(dset.variables[field])
        if field_dic["data"].shape == field_shape_with_time:
            field_dic["data"].shape = field_shape
            fields[field] = field_dic
        else:
            bad_shape = field_dic["data"].shape
            warnings.warn(
                "Field %s skipped due to incorrect shape %s" % (field, bad_shape)
            )

    # radar_ variables
    if "radar_latitude" in dset.variables:
        radar_latitude = _ncvar_to_dict(dset.variables["radar_latitude"])
    else:
        radar_latitude = {
            "long_name": "Latitude of radars used to make the grid.",
            "units": "degrees_north",
            "data": np.array([-3.1493]),
        }

    if "radar_longitude" in dset.variables:
        radar_longitude = _ncvar_to_dict(dset.variables["radar_longitude"])
    else:
        radar_longitude = {
            "long_name": "Longitude of radars used to make the grid.",
            "units": "degrees_east",
            "data": np.array([-59.992]),
        }

    if "radar_altitude" in dset.variables:
        radar_altitude = _ncvar_to_dict(dset.variables["radar_altitude"])
    else:
        radar_altitude = {
            "long_name": "Altitude of radars used to make the grid.",
            "units": "m",
            "data": np.array([102.4]),
        }

    if "radar_name" in dset.variables:
        radar_name = _ncvar_to_dict(dset.variables["radar_name"])
    else:
        radar_name = {
            "long_name": "Name of radar used to make the grid",
            "data": np.array(["SIPAM"], dtype="<U1"),
        }

    if "radar_time" in dset.variables:
        radar_time = _ncvar_to_dict(dset.variables["radar_time"])
    else:
        radar_time = None

    dset.close()

    return Grid(
        time,
        fields,
        metadata,
        origin_latitude,
        origin_longitude,
        origin_altitude,
        x,
        y,
        z,
        projection=projection,
        radar_latitude=radar_latitude,
        radar_longitude=radar_longitude,
        radar_altitude=radar_altitude,
        radar_name=radar_name,
        radar_time=radar_time,
    )

