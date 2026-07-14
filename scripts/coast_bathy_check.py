import joblib
import pickle
import numpy as np

#COASTLINE CHECK
EARTH_RADIUS_KM = 6371.0

def coast_distance_km(lat, lon, tree = pickle.load(open("./input/GEBCO/coast_tree.pkl", "rb"))):
    query = np.radians(
        np.column_stack([lat, lon])
    )
    dist_rad, ind = tree.query(
        query,
        k=1
    )
    return dist_rad[:, 0] * EARTH_RADIUS_KM

#Bathymerty check
def bathymetry_depth(lat, lon, interp=joblib.load("./input/GEBCO/gebco_interp.joblib")):

    pts = np.column_stack([lat, lon])

    return interp(pts)

def find_date_idx(dates_in,ds_in):
    idx = [
        np.where(ds_in.time.dt.floor("D") == np.datetime64(d))[0][0]
        for d in dates_in
        if (ds_in.time.dt.floor("D") == np.datetime64(d)).any()
    ]
    return np.array(idx)

def find_date_idx2(ds_in,freq_in='D'):
    d1,d2 = ds_in.time[[0,-1]]
    d1,d2 = str(d1.values),str(d2.values)
    d1d2 = np.arange(d1,d2,dtype='datetime64[%s]'%freq_in)
    idx = [
        np.where(ds_in.time.dt.floor(freq_in) == np.datetime64(d))[0][0]
        for d in d1d2
        if (ds_in.time.dt.floor(freq_in) == np.datetime64(d)).any()
    ]
    return np.array(idx)