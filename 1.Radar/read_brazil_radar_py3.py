# -*- coding: UTF-8 -*-
# Originally developed by Timothy Lang (https://github.com/tjlang)
# Adapted for Python 3 by Camila Lopes (camila.lopes@iag.usp.br)

from __future__ import print_function
import numpy as np
import h5py
from pyart.core import Radar
from pyart.config import FileMetadata
from pyart.io.common import make_time_unit_str
import datetime as dt


def _initial_process(r):
    """
    Performs initial processing of radar data from h5py.File object.
    Gathers all necessary fields and metadata and condenses them to
    a simple dictionary for ease of later processing.

    Parameters
    ----------
    r : h5py.File
        Open h5py.File object from which to ingest data

    Returns
    -------
    protoradar : dict
        Dictionary with preliminary data gathered from HDF5 file
    """
    # Initialize key variables
    bad = -32768
    elcnt = 0
    azimuths = []
    elevations = []
    urg = []
    nyq = []
    momlab = []
    data = {}
    for key in r.keys():
        if key[:4] == 'scan':
            elcnt += 1
    for key in r['scan0'].keys():
        if key[:6] == 'moment':
            momlab.append(key)
            data[key] = []
    shp = np.shape(r['scan0']['moment_0'])
    x = []
    y = []

    for i in range(elcnt):
        # Process each scan, gather and keep track of relevant metadata
        si = str(i)
        slab = 'scan' + si
        rayhead = np.array(r[slab]['ray_header'])
        az = np.array([rayhead[j][0] for j in range(len(rayhead))])
        azimuths.append(az)
        el = np.array([rayhead[j][2] for j in range(len(rayhead))])
        elevations.append(el)
        prf = r[slab]['how'].attrs['PRF'][0]
        wl = r[slab]['how'].attrs['radar_wave_length'][0]
        ur = el * 0 + 3e8 / (2 * prf)
        urg.append(ur)
        ny = el * 0 + prf * wl / 4.0
        nyq.append(ny)

        # Process each moment separately for each scan
        for mom in momlab:
            if str(r[slab][mom].attrs['format'][0]) == 'UV8':
                div = 254.0
            else:
                div = 65534.0
            if np.size(data[mom]) > 0:
                # After first sweep, fill in data out to all available ranges
                tmp = np.zeros(shp)
                shp_new = np.shape(r[slab][mom])
                tmp[:, :shp_new[1]] = np.array(r[slab][mom])[:, :]
                invalid = tmp
                tmp = r[slab][mom].attrs['dyn_range_min'][0] + \
                    tmp * (r[slab][mom].attrs['dyn_range_max'][0] -
                           r[slab][mom].attrs['dyn_range_min'][0]) / div
                tmp[np.where(invalid == 0)] = bad
                data[mom] = np.append(data[mom], tmp, axis=0)
            else:
                # First sweep - assumed to be longest possible range
                data[mom] = np.array(r[slab][mom])
                invalid = data[mom]
                data[mom] = r[slab][mom].attrs['dyn_range_min'][0] + \
                    data[mom] * (r[slab][mom].attrs['dyn_range_max'][0] -
                                 r[slab][mom].attrs['dyn_range_min'][0]) / div
                data[mom][np.where(invalid == 0)] = bad
            data[mom] = np.ma.masked_where(data[mom] == bad, data[mom])

        # Last sweep lacks completion time, need to infer from linear fit
        # to scan speed and time for each sweep.
        if i < elcnt - 1:
            dt1 = dt.datetime.strptime(
                str(r['scan' + str(i)]['how'].attrs['timestamp'][0]),
                '%Y-%m-%dT%H:%M:%S.000Z')
            dt2 = dt.datetime.strptime(
                str(r['scan' + str(i+1)]['how'].attrs['timestamp'][0]),
                '%Y-%m-%dT%H:%M:%S.000Z')
            x.append((dt2-dt1).total_seconds())
            y.append(r['scan' + str(i)]['how'].attrs['scan_speed'][0])
        if i == elcnt - 1:
            m, b = np.polyfit(x, y, 1)
            dsec = np.round(
                (r['scan' + str(i)]['how'].attrs['scan_speed'][0] - b) / m)
            totsec = np.sum(x) + dsec

    # Finalize all arrays, add to protoradar dictionary
    azimuths = np.concatenate(azimuths)
    elevations = np.concatenate(elevations)
    nyq = np.concatenate(nyq)
    urg = np.concatenate(urg)
    dstart = dt.datetime.strptime(
            str(r['scan0']['how'].attrs['timestamp'][0]),
            '%Y-%m-%dT%H:%M:%S.000Z')
    dtime = np.array(
        [dstart + dt.timedelta(microseconds=int(j*1e6*totsec/len(azimuths)))
         for j in np.arange(len(azimuths))])
    rng = r['scan0']['how'].attrs['range_step'][0] + \
        r['scan0']['how'].attrs['range_step'][0] * \
        np.arange(np.shape(data['moment_0'])[1])
    protoradar = {}
    protoradar['azimuths'] = azimuths
    protoradar['elevations'] = elevations
    protoradar['fields'] = data
    protoradar['datetime'] = dtime
    protoradar['range'] = np.array(rng, dtype='f4')
    protoradar['unambiguous_range'] = urg
    protoradar['nyquist_velocity'] = nyq
    return protoradar


def read_rainbow_hdf5(fname):
    """
    Ingest a Brazilian radar HDF5 file into Py-ART. Requires h5py.

    Parameters
    ----------
    fname : str
        Name of Brazilian HDF5 radar file

    Returns
    -------
    Radar : pyart.core.radar.Radar
        Py-ART Radar object, ready for processing, diplay, gridding,
        and writing to file
    """
    # Field names
    field_names = {
        'moment_0': 'corrected_reflectivity',
        'moment_1': 'reflectivity',
        'moment_2': 'velocity',
        'moment_3': 'spectrum_width',
        'moment_4': 'differential_reflectivity',
        'moment_5': 'filtered_differential_phase',
        'moment_6': 'differential_phase',
        'moment_7': 'specific_differential_phase',
        'moment_8': 'cross_correlation_ratio'}
    filemetadata = FileMetadata('cfradial', field_names, None,
                                False, None)

    r = h5py.File(fname)
    pr = _initial_process(r)

    # fixed_angle
    fixed_angle = filemetadata('fixed_angle')
    fixed_angle['data'] = np.unique(pr['elevations'])

    # elevation
    elevation = filemetadata('elevation')
    elevation['data'] = pr['elevations']

    # azimuth
    azimuth = filemetadata('azimuth')
    azimuth['data'] = pr['azimuths']

    # sweep_number
    sweep_number = filemetadata('sweep_number')
    nsweeps = len(fixed_angle['data'])
    sweep_number['data'] = np.arange(nsweeps, dtype='int32')

    # sweep_mode
    sweep_mode = filemetadata('sweep_mode')
    scan_type = str(r['scan0']['what'].attrs['scan_type'][0]).lower()
    if scan_type in ['ppi', 'rhi']:
        sweep_mode['data'] = np.array(nsweeps * ['manual_' + scan_type])
    else:  # Guessing that if not RHI or PPI, then a pointing scan
        sweep_mode['data'] = np.array(nsweeps * ['pointing'])

    # sweep_start_ray_index, sweep_end_ray_index
    sweep_start_ray_index = filemetadata('sweep_start_ray_index')
    sweep_end_ray_index = filemetadata('sweep_end_ray_index')
    ssri = []
    ssre = []
    for ang in fixed_angle['data']:
        index = np.where(pr['elevations'] == ang)[0]
        ssri.append(np.min(index))
        ssre.append(np.max(index))
    sweep_start_ray_index['data'] = np.array(ssri, dtype='int')
    sweep_end_ray_index['data'] = np.array(ssre, dtype='int')

    # radar location
    latitude = filemetadata('latitude')
    longitude = filemetadata('longitude')
    altitude = filemetadata('altitude')
    latitude['data'] = np.array(r['where'].attrs['lat'])
    longitude['data'] = np.array(r['where'].attrs['lon'])
    altitude['data'] = np.array(r['where'].attrs['height'])

    # time
    _time = filemetadata('time')
    start_time = pr['datetime'][0]
    _time['units'] = make_time_unit_str(start_time)
    _time['data'] = np.array(
        [(dti-start_time).total_seconds() for dti in pr['datetime']])

    # range
    _range = filemetadata('range')
    _range['data'] = pr['range']
    _range['meters_to_center_of_first_gate'] = _range['data'][0] / 2.0
    _range['meters_between_gates'] = np.median(np.diff(_range['data']))
    _range['spacing_is_constant'] = 1

    # instrument_parameters
    instrument_parameters = {}
    for lab in ['nyquist_velocity', 'unambiguous_range']:
        tmpdic = filemetadata(lab)
        instrument_parameters[lab] = tmpdic
        tmpdic['data'] = pr[lab]

    # fields
    keys = [k for k in field_names.keys()]
    fields = {}
    for key in keys:
        field_name = filemetadata.get_field_name(key)
        fields[field_name] = {}
        fields[field_name]['data'] = pr['fields'][key]
        fields[field_name]['long_name'] = field_name
        fields[field_name]['standard_name'] = field_name.replace('_', ' ')
        fields[field_name]['units'] = str(
            r['scan0'][key].attrs['unit'][0])
        fields[field_name]['coordinates'] = 'elevation azimuth range'

    # metadata
    metadata = filemetadata('metadata')
    metadata['source'] = 'Brazil Radar'
    metadata['original_container'] = fname

    return Radar(
        _time, _range, fields, metadata, scan_type,
        latitude, longitude, altitude,
        sweep_number, sweep_mode, fixed_angle, sweep_start_ray_index,
        sweep_end_ray_index,
        azimuth, elevation,
        instrument_parameters=instrument_parameters)