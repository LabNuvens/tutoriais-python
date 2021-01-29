# Adapted from "Reading ARM VPT data"
# http://arm-doe.github.io/pyart/_modules/pyart/aux_io/arm_vpt.html


import netCDF4
import numpy as np
from skimage.measure import block_reduce

from pyart.io import cfradial
from pyart.config import FileMetadata
from pyart.core.radar import Radar
from pyart.util import join_radar


def read_mira(
    filename,
    for_quicklooks=False,
    ql_res=5,
    field_names=None,
    additional_metadata=None,
    file_field_names=False,
    exclude_fields=None,
    include_fields=None,
):
    """
    Read MIRA-35C NetCDF ingest data.

    Parameters
    ----------
    filename : str
        Name of NetCDF file to read data from.
    for_quicklooks : bool, optional
        True if data is for quicklooks, averaging according to ql_res.
    ql_res : int, optional
        If for_quicklooks is true, data resolution in minutes.
    field_names : dict, optional
        Dictionary mapping field names in the file names to radar field names.
        Unlike other read functions, fields not in this dictionary or having a
        value of None are still included in the radar.fields dictionary, to
        exclude them use the `exclude_fields` parameter. Fields which are
        mapped by this dictionary will be renamed from key to value.
    additional_metadata : dict of dicts, optional
        This parameter is not used, it is included for uniformity.
    file_field_names : bool, optional
        True to force the use of the field names from the file in which
        case the `field_names` parameter is ignored. False will use to
        `field_names` parameter to rename fields.
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
    radar : Radar
        Radar object.
    """

    # create metadata retrieval object
    filemetadata = FileMetadata(
        "cfradial",
        field_names,
        additional_metadata,
        file_field_names,
        exclude_fields,
        include_fields,
    )

    # read the data
    ncobj = netCDF4.Dataset(filename)
    ncvars = ncobj.variables

    # 4.1 Global attribute -> move to metadata dictionary
    metadata = dict([(k, getattr(ncobj, k)) for k in ncobj.ncattrs()])
    metadata["n_gates_vary"] = "false"

    # 4.2 Dimensions
    # If averaging, increase temporal resolution with res
    if for_quicklooks:
        orig_res = round(
            float(ncobj.hrd[ncobj.hrd.find("AVE") + 4 : ncobj.hrd.find("\nC")])
        )
        res = round(ql_res * 60 / orig_res)

    # 4.3 Global variable -> move to metadata dictionary
    if "volume_number" in ncvars:
        metadata["volume_number"] = int(ncvars["volume_number"][:])
    else:
        metadata["volume_number"] = 0

    global_vars = {
        "platform_type": "fixed",
        "instrument_type": "radar",
        "primary_axis": "axis_z",
    }
    # ignore time_* global variables, these are calculated from the time
    # variable when the file is written.
    for var, default_value in global_vars.items():
        if var in ncvars:
            metadata[var] = str(netCDF4.chartostring(ncvars[var][:]))
        else:
            metadata[var] = default_value

    # 4.4 coordinate variables -> create attribute dictionaries
    time = cfradial._ncvar_to_dict(ncvars["time"])
    time["units"] = "seconds since 1970-01-01 00:00:00"
    time["data"] = np.array(
        np.ma.MaskedArray.tolist(time["data"]), dtype="int64"
    )
    _range = cfradial._ncvar_to_dict(ncvars["range"])
    if for_quicklooks:
        time["data"] = time["data"][::res]

    # 4.5 Ray dimension variables

    # 4.6 Location variables -> create attribute dictionaries
    # the only difference in this section to cfradial.read_cfradial is the
    # minor variable name differences:
    # latitude -> lat
    # longitude -> lon
    # altitdue -> alt
    latitude = {
        "_FillValue": -9999.0,
        "data": np.ma.array(
            data=[-float(ncobj.Latitude[:-1])],
            mask=False,
            fill_value=1e20,
            dtype=np.float32,
        ),
        "long_name": "Latitude",
        "standard_name": "latitude",
        "units": "degree_N",
        "valid_max": 90.0,
        "valid_min": -90.0,
    }
    longitude = {
        "_FillValue": -9999.0,
        "data": np.ma.array(
            data=[-float(ncobj.Longitude[:-1])],
            mask=False,
            fill_value=1e20,
            dtype=np.float32,
        ),
        "long_name": "Longitude",
        "standard_name": "longitude",
        "units": "degree_E",
        "valid_max": 180.0,
        "valid_min": -180.0,
    }
    altitude = {
        "_FillValue": -9999.0,
        "data": np.ma.array(
            data=[float(ncobj.Altitude[:-1])],
            mask=False,
            fill_value=1e20,
            dtype=np.float32,
        ),
        "long_name": "Altitude",
        "standard_name": "altitude",
        "units": "m",
    }

    # 4.7 Sweep variables -> create atrribute dictionaries
    # this is the section that needed the most work since the initial NetCDF
    # file did not contain any sweep information
    sweep_number = filemetadata("sweep_number")
    sweep_number["data"] = np.array([0], dtype=np.int32)

    sweep_mode = filemetadata("sweep_mode")
    sweep_mode["data"] = np.array(["vertical_pointing"], dtype=np.str)

    fixed_angle = filemetadata("fixed_angle")
    fixed_angle["data"] = np.array([90.0], dtype=np.float32)

    sweep_start_ray_index = filemetadata("sweep_start_ray_index")
    sweep_start_ray_index["data"] = np.array([0], dtype=np.int32)

    sweep_end_ray_index = filemetadata("sweep_end_ray_index")
    sweep_end_ray_index["data"] = np.array(
        [ncvars["time"].size - 1], dtype=np.int32
    )

    # first sweep mode determines scan_type
    # this module is specific to vertically-pointing data
    scan_type = "vpt"

    # 4.8 Sensor pointing variables -> create attribute dictionaries
    # this section also required some changes since the initial NetCDF did not
    # contain any sensor pointing variables
    azimuth = filemetadata("azimuth")
    azimuth["data"] = 0.0 * np.ones(ncvars["time"].size, dtype=np.float32)

    elevation = filemetadata("elevation")
    elevation["data"] = 90.0 * np.ones(ncvars["time"].size, dtype=np.float32)

    # 4.9 Moving platform geo-reference variables

    # 4.10 Moments field data variables -> field attribute dictionary
    # all variables with dimensions of 'time', 'range' are fields
    keys = [k for k, v in ncvars.items() if v.dimensions == ("time", "range")]

    fields = {}
    for key in keys:
        field_name = filemetadata.get_field_name(key)
        if field_name is None:
            if exclude_fields is not None and key in exclude_fields:
                continue
            if include_fields is not None and not key in include_fields:
                continue
            field_name = key
        fields[field_name] = cfradial._ncvar_to_dict(ncvars[key])
        if for_quicklooks:
            fields[field_name]["data"] = block_reduce(
                fields[field_name]["data"],
                block_size=(res, 1),
                func=np.nanmean,
                cval=1e20,
            )
        if field_name in ("SNRg", "SNR", "Ze", "Zg", "Z", "LDRg", "LDR"):
            fields[field_name]["data"] = 10 * np.log10(
                fields[field_name]["data"]
            )
            fields[field_name]["units"] = "dBZ"

    # 4.5 instrument_parameters sub-convention -> instrument_parameters dict
    # this section needed multiple changes and/or additions since the
    # instrument parameters were primarily located in the global attributes
    # this section is likely still incomplete
    omega = float(299792458 / ncvars["lambda"][:])
    frequency = filemetadata("frequency")
    frequency["data"] = np.array([omega / 1e9], dtype=np.float32)

    prt_mode = filemetadata("prt_mode")
    prt_mode["data"] = np.array(["fixed"], dtype=np.str)

    prf = float(ncvars["prf"][:])
    prt = filemetadata("prt")
    prt["data"] = (1.0 / prf) * np.ones(ncvars["time"].size, dtype=np.float32)

    v_nq = float(ncvars["NyquistVelocity"][:])
    nyquist_velocity = filemetadata("nyquist_velocity")
    nyquist_velocity["data"] = (
        v_nq * np.ones(ncvars["time"].size, dtype=np.float32),
    )
    samples = int(ncvars["nave"][:])
    n_samples = filemetadata("n_samples")
    n_samples["data"] = samples * np.ones(ncvars["time"].size, dtype=np.int32)

    # 4.6 radar_parameters sub-convention -> instrument_parameters dict
    # this section needed multiple changes and/or additions since the
    # radar instrument parameters were primarily located in the global
    # attributes
    # this section is likely still incomplete
    instrument_parameters = {
        "frequency": frequency,
        "prt_mode": prt_mode,
        "prt": prt,
        "nyquist_velocity": nyquist_velocity,
        "n_samples": n_samples,
    }

    # 4.7 lidar_parameters sub-convention -> skip
    # 4.8 radar_calibration sub-convention -> skip

    # 4.9 Getting Melting Layer Height data to a new file
    melthei = {
        "var": "MeltHei",
        "long_name": ncvars["MeltHei"].long_name,
        "units": ncvars["MeltHei"].units,
        "yrange": ncvars["MeltHei"].yrange,
    }
    melthei_det = {
        "var": "MeltHeiDet",
        "long_name": "Melting Layer Height detected from LDR",
        "units": ncvars["MeltHeiDet"].units,
        "yrange": ncvars["MeltHeiDet"].yrange,
    }
    melthei_db = {
        "var": "MeltHeiDB",
        "long_name": ncvars["MeltHeiDB"].long_name,
        "units": ncvars["MeltHeiDB"].units,
        "yrange": ncvars["MeltHeiDB"].yrange,
    }
    if for_quicklooks:
        melthei["data"] = block_reduce(
            ncvars["MeltHei"][:],
            block_size=(res,),
            func=np.nanmean,
            cval=np.nanmean(ncvars["MeltHei"][:]),
        )
        melthei_det["data"] = block_reduce(
            ncvars["MeltHeiDet"][:],
            block_size=(res,),
            func=np.nanmean,
            cval=np.nanmean(ncvars["MeltHeiDet"][:]),
        )
        melthei_db["data"] = block_reduce(
            ncvars["MeltHeiDB"][:],
            block_size=(res,),
            func=np.nanmean,
            cval=np.nanmean(ncvars["MeltHeiDB"][:]),
        )
    else:
        melthei["data"] = ncvars["MeltHei"][:]
        melthei_det["data"] = ncvars["MeltHeiDet"][:]
        melthei_db["data"] = ncvars["MeltHeiDB"][:]

    # close NetCDF object
    ncobj.close()

    return (
        Radar(
            time,
            _range,
            fields,
            metadata,
            scan_type,
            latitude,
            longitude,
            altitude,
            sweep_number,
            sweep_mode,
            fixed_angle,
            sweep_start_ray_index,
            sweep_end_ray_index,
            azimuth,
            elevation,
            instrument_parameters=instrument_parameters,
        ),
        (melthei, melthei_det, melthei_db),
    )


def read_multi_mira(filenames, for_quicklooks=False, ql_res=5):
    """
    Read and join multiple MIRA-35C radar files

    Parameters
    ----------
    filenames : list of filenames


    Returns
    -------
    radar : Py-ART radar object
    """

    radar, melt_hei = read_mira(filenames[0], for_quicklooks, ql_res)
    for i in range(1, len(filenames)):
        radar_i, melt_hei_i = read_mira(filenames[i], for_quicklooks, ql_res)
        radar = join_radar(radar, radar_i)
        for j in range(3):
            melt_hei[j]["data"] = np.ma.append(
                melt_hei[j]["data"], melt_hei_i[j]["data"]
            )
    return radar, melt_hei
