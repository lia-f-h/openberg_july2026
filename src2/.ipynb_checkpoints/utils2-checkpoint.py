from src.utils import *
# import copernicusmarine
# from datetime import datetime,timedelta, timezone
# from src.copernicusmarine_Parser import BucketParser
# from src.leaflet_maps import map_icebergs, markers_from_geojson, get_ids, filter_markers, seed_from_geopandas
# import ipywidgets as widgets
# from ipywidgets import HTML, interact, interact_manual
# from IPython.display import Image, clear_output, display
# import yaml
# import geopandas as gpd
# import logging
# import numpy as np
# import matplotlib.pyplot as plt
# import requests
# import json
# import xarray as xr
# from shapely.geometry import LineString, Point
# import sqlite3
# import shutil
# import os
# import pandas as pd
# import time
    
def calc_iceberg_size(iceberg_in):
    """
    Estimate missing iceberg properties (width, draft, sail)
    using empirical relationships based on length.
    
    Parameters
    ----------
    iceberg : dict
        Dictionary containing iceberg properties. Must include 'length'.
    
    Returns
    -------
    dict
        Updated iceberg dictionary with estimated values filled in.
    """
    iceberg_out = iceberg_in.copy()

    if 'length' not in iceberg_out:
        raise ValueError("Input must contain 'length'.")

    lengths = np.array(iceberg_out['length'])

    # --- Estimate width ---
    if 'width' not in iceberg_out:
        iceberg_out['width'] = 0.7 * lengths * np.exp(-0.00062 * lengths)

    # --- Estimate height ---
    height = 0.4 * lengths * np.exp(-0.00062 * lengths)

    # Physical constants (kg/m³)
    rho_i = 900   # ice density
    rho_w = 1027  # seawater density

    # Fraction below and above water
    frac_draft = rho_i / rho_w
    frac_sail = 1 - frac_draft

    # --- Handle draft and sail ---
    has_draft = 'draft' in iceberg_out
    has_sail = 'sail' in iceberg_out

    if not has_draft and not has_sail:
        # Compute both directly
        iceberg_out['draft'] = height * frac_draft
        iceberg_out['sail'] = height * frac_sail

    elif has_draft and not has_sail:
        # Compute sail from draft
        iceberg_out['sail'] = iceberg_out['draft'] * (frac_sail / frac_draft)

    elif has_sail and not has_draft:
        # Compute draft from sail
        iceberg_out['draft'] = iceberg_out['sail'] * (frac_draft / frac_sail)

    # If both exist, leave as is

    return iceberg_out
    
# def calc_iceberg_size(iceberg_in1):
#     '''Correct iceberg size not supplied with empirical relations before seeding iceberg.
#     '''
#     lengths = iceberg_in1['length']
#     if 'length' in iceberg_in1 and 'width' not in iceberg_in1:
#         iceberg_in1['width'] = 0.7*lengths*np.exp(-0.00062*length)
#     if 'length' in iceberg_in1 and np.logical_or('draft' not in iceberg_in1,'sail' not in iceberg_in1):
#         rho_i, rho_w = 900,1027 #kg/m3
#         height = np.array(0.4*lengths*np.exp(-0.00062*lengths))
#         if np.logical_and('draft' not in iceberg_in1, 'sail' in iceberg_in1): print('Implement')
#         elif np.logical_and('draft' not in iceberg_in1, 'sail' not in iceberg_in1): draft = height*(rho_i/rho_w)
#         if np.logical_and('sail' not in iceberg_in1, 'draft' not in iceberg_in1): sail = height*(1-rho_i/rho_w) 
#         elif np.logical_and('sail' not in iceberg_in1, 'draft' in iceberg_in1): print('Implement')
#         iceberg_in1['draft'] = draft
#         iceberg_in1['sail'] = sail
    # return iceberg_in1
    

# CHECKS
def check_simulation_results(oi_in, dict_in_in, logger):
    '''
    Checks if icebrg seeding, model configurations and variable reading worked correctly.
    '''
    logger.info('Performing checks..')
    #Checks model configurations
    for c in dict_in_in['config']:
        if 'seed' in c: test = abs(dict_in_in['config'][c]-oi_in[c.split(':')[1]][:,0].values[0])>0.01 #Some configurations can be accessed as dataset variables
        else: test = str(dict_in_in['config'][c])==str(oi_in.attrs['config_'+c]) #Some configurations can be accessed as attributes
        if test==True: print('Checks: ',c,' not defined corretly in the model: ',dict_in_in['config'][c],oi_in.attrs['config_'+c])
    #Checks if iceberg(s) were seeded correctly
    for s in dict_in_in['seed']:
        if s not in ('number','time','radius'): 
            test = np.any(np.abs(dict_in_in['seed'][s]-oi_in[s][:,0].values)>0.01)
            if test==True: print('Checks: ',s,' not seeded correctly, difference: ',np.abs(dict_in_in['seed'][s]-oi_in[s][:,0].values))
    #Checks if input variables were read (if Readers worked)
    #list of mmost important input variables
    v_l = ['x_sea_water_velocity',  'y_sea_water_velocity', 'x_wind', 'y_wind',  'sea_water_temperature', 'sea_water_salinity', 
           'sea_ice_area_fraction','sea_ice_thickness', 'sea_ice_x_velocity', 'sea_ice_y_velocity','sea_surface_wave_stokes_drift_x_velocity', 'sea_surface_wave_stokes_drift_y_velocity',] #'sea_surface_wave_significant_height', 'sea_surface_wave_from_direction',  
    test=np.all(oi_in[v_l] == 0) #checks all variable arrays  at once
    for v in v_l: 
        if test[v]==True: print('Checks: ',v, 'NOT imported!') #print warning if variable all zero
    logger.info('Checks done.')
    return

def read_tracker(csv_in):
    # Load data
    df = pd.read_csv(csv_in, sep=';')
    # Create a proper datetime column
    df['time'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    # Sort by time (important before grouping/subsampling)
    df = df.sort_values('time')
    # Convert to xarray Dataset
    ds = xr.Dataset.from_dataframe(df)
     # Remove old time variable if present (to avoid conflict)
    try:
        ds = ds.drop_vars('Date')
        ds = ds.drop_vars('Time')
    except: pass
    # Set time as dimensions and coordinate
    ds = ds.set_coords("time")
    ds = ds.swap_dims({"index": "time"})
    ds = ds.drop_vars("index")  # optional
    # Daily subset: take first observation per day
    # ds_daily = ds.groupby("time").first()
    ds_daily = ds.resample(time="1D",origin="start_day").first() #.mean() 
    # Remove old time variable if present (to avoid conflict)
    # if 'time' in ds_daily:
    #     ds_daily = ds_daily.drop_vars('time')
    # # Rename dimension
    # ds_daily = ds_daily.rename({'date': 'time'})
    # # Convert to datetime64
    # ds_daily['time'] = pd.to_datetime(ds_daily['time'])
    # 3-day subset
    # ds_3day = ds_daily.isel(time=slice(0, None, 3))
    ds_3day = ds.resample(time="3D",origin="start_day").nearest()

    return {'full':ds,'D':ds_daily,'3D':ds_3day}

def read_cmems_custom_variables(dataset_id_in, variable_list_in):
    import copernicusmarine as cm
    
    ds = cm.open_dataset(
        dataset_id=dataset_id_in,
        variables=variable_list_in,
        minimum_longitude=-80,
        maximum_longitude=-50,
        minimum_latitude=70,
        maximum_latitude=80,
        start_datetime="2025-09-01T00:00:00",
        end_datetime="2025-12-31T00:00:00"
    )
    
    ds = ds.rename({"longitude": "lon", "latitude": "lat"})

    for v in ds.variables:
        ds[v].attrs.pop("coordinates", None)
        ds[v].attrs.pop("grid_mapping", None)

    return ds

def join_ds_by_idx(file_l_in):
    import re

    def preprocess(ds):
        source = ds.encoding["source"]
    
        m = re.search(r"_idx(\d+)-(\d+)", source)
        if m is None:
            raise ValueError(f"Could not parse idx range from {source}")
    
        idx_start = int(m.group(1))
    
        return ds.assign_coords(
            trajectory=ds.trajectory + 11 * idx_start
        )
    
    ds = xr.open_mfdataset(
        file_l_in,
        preprocess=preprocess,
        combine="nested",
        concat_dim='trajectory'
    )
    outname =  '_'.join([fs if 'idx' not in fs else '' for fs in file_l_in[0].split('_')]).replace('.nc','_joined.nc') 
    try: outname.replace('__','_')
    except: pass
    return  ds.to_netcdf(outname,'w')
    # return ds.to_netcdf('_'.join([fs if 'idx' not in fs else 'joined' for fs in file_l_in[0].split('_')]),'w')
    
def file_dict_idx(file_l_in):
    from pathlib import Path
    import re

    result = {}

    for f in file_l_in:
        stem = Path(f).stem

        m = re.match(
            r'^(.*?)_idx(\d+(?:-\d+)?)(.*)$',
            stem
        )

        if m:
            prefix = m.group(1)
            idx_str = m.group(2)
            suffix = m.group(3)  # '', '_mainrun', ...

            key = f"{prefix}{suffix}.nc"

            if key not in result:
                result[key] = {"files": [], "idx": []}

            if '-' in idx_str:
                idx = [int(x) for x in idx_str.split('-')]
            else:
                idx = [int(idx_str), int(idx_str)]

            result[key]["files"].append(f)
            result[key]["idx"].append(idx)

        else:
            result[f] = {}

    for v in result.values():
        if "idx" in v:
            order = sorted(
                range(len(v["idx"])),
                key=lambda i: v["idx"][i][0]
            )
            v["files"] = [v["files"][i] for i in order]
            v["idx"] = [v["idx"][i] for i in order]

    return result
    
# def file_dict_idx(file_l_in):
#     from collections import defaultdict
#     from pathlib import Path
#     import re
    
#     result = {}
    
#     for f in file_l_in:
#         stem = Path(f).stem
    
#         m = re.search(r'^(.*?)_idx(\d+(?:-\d+)?)', stem)
    
#         if m:
#             # key = f.split('_idx')[0]  # full path prefix
#             key = f.split('_idx')[0] + '.nc'
    
#             if key not in result:
#                 result[key] = {"files": [], "idx": []}
    
#             idx_str = m.group(2)
    
#             if '-' in idx_str:
#                 idx = [int(x) for x in idx_str.split('-')]
#             else:
#                 idx = [int(idx_str), int(idx_str)]
    
#             result[key]["files"].append(f)
#             result[key]["idx"].append(idx)
    
#         else:
#             result[f] = {}
#     for v in result.values():
#         if "idx" in v:
#             order = sorted(
#                 range(len(v["idx"])),
#                 key=lambda i: v["idx"][i][0]
#             )
#             v["files"] = [v["files"][i] for i in order]
#             v["idx"] = [v["idx"][i] for i in order]
#     return result