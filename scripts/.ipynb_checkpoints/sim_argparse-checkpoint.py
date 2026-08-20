# Re-simulating different icebergs along their observed trajectory

#How to run. First go to directory, then run file:
    # cd ~/work/tutorials/sources/OpenDrift/openberg_july2026
# python3 -m openberg_july2026.scripts.sim_argparse       --argib 'iceberg2018b'       --argoc '[["gebco","glorys"],["gebco","topaz4"]]'       --argwind '["windglophyre"]'       --argdrift '{"wind_drag": true, "sea_ice_drag": true,  "wave_rad": false, "stokes_drift": false, "vertical_profile": false}'       --argname ''       --argopenberg 'lia' --argidx '[[0, 0], [1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8], [9, 9], [10, 10]]' --argmainrun 1
# python3 -m openberg_july2026.scripts.sim_argparse       --argib 'iceberg2026e'       --argoc '[["gebco","topaz5"],["gebco","topaz6","topaz5"]]'       --argwind '["windglophynrt"]'  --argobs './openberg_july2026/input/merged_obs_iceberg2026e_3D.nc' --argname 'radius' --argradius 1000 --argidx '[[30,36]]'


# --- IMPORTS ---
from src.utils import *
from openberg_july2026.src2.utils2 import *
from openberg_july2026.src2.utils0 import env_dict
from opendrift.readers.reader_netCDF_CF_generic import Reader    
import gc
import argparse
import json

# --- Get Arguments from terminal
parser = argparse.ArgumentParser()
parser.add_argument("--argib", type=str, required=True, help='Iceberg id as str: [iceberg2011w1, iceberg2011w2, iceberg2017b, iceberg2018b, iceberg2021b, iceberg2021w, iceberg2024e, iceberg2025w]')
parser.add_argument("--argoc", type=json.loads, required=True, help='JSON list of lists, e.g. \'["topaz5", ["topaz6","topaz5"]]\'')
parser.add_argument("--argwind", type=json.loads, default='["windglophynrt"]', help='JSON list, e.g. \'["windglophynrt"]\'')
parser.add_argument("--argdrift", type=json.loads, default={"wind_drag": True, "sea_ice_drag": True, "wave_rad": False, "stokes_drift": False}, 
                    help='JSON dict, e.g. \'{"wind_drag": true}\'')
parser.add_argument("--argname", type=str, help='str to be added to filename (optional)', default='')
parser.add_argument("--argopenberg", type=str, help='Which openberg.py to use', default='lia')
# parser.add_argument("--argidx",type=int, nargs=2, metavar=("INT1", "INT2"), default=[0, 999],
#                     help="Range of seeding time-positions,e .g. 0,1 for seeding rounds 0 to (incl.) 1")
parser.add_argument("--argidx", type=json.loads, required=False, default=[],
                    help="LIst of range of seeding time-positions,e .g. [[0,1] for seeding rounds 0 to (incl.) 1")
# parser.add_argument("--argmainrun", type=bool, default= False, help='False= n icebergs with varied coef, size and radius, True= no variations')
parser.add_argument("--argmainrun", type=int, default=0, help='0= n icebergs with varied coef, size and radius, 1= no variations')
parser.add_argument("--argobs", type=str, default='./openberg_july2026/input/merged_obs10.nc', help='File with iceberg observations')
parser.add_argument("--argradius", type=int, default=3125, help='Seeding radius in m')

args = parser.parse_args()
argdrift = args.argdrift
argname = args.argname


# --- Read correct Openberg version (on top of pre-loaded one in edito service) ---
openbergvers = args.argopenberg
if openbergvers=='orig': from openberg_july2026.src2.openberg_orig import OpenBerg
elif openbergvers=='lia': from openberg_july2026.src2.openberg_lia import OpenBerg
print('Openberg.py used from ',args.argopenberg)


# --- Input data ---
oc_in = args.argoc 
wind_in = args.argwind
idxargs = args.argidx 
# --- More Arguments
idx_l = [np.arange(idx_i[0],idx_i[1]+1,1) for idx_i in idxargs]
mainrun = args.argmainrun
argobs = args.argobs
argradius = args.argradius
print('Arguments: ',argobs,argradius,oc_in,wind_in,argdrift,idx_l,mainrun)

# --- Clean up ---
for _ in range(2):
    gc.collect()

# --- Combintaions of inputs ---
if np.logical_and(wind_in!=[],oc_in!=[]): input_l = [(oc if isinstance(oc, list) else [oc]) + [wi] for wi in wind_in for oc in oc_in ] 
elif np.logical_and(wind_in==[],oc_in!=[]): input_l = [(oc if isinstance(oc, list) else [oc]) for oc in oc_in]
elif np.logical_and(wind_in!=[],oc_in==[]): input_l = [(wi if isinstance(wi, list) else [wi]) for wi in wind_in]
else: print('Provide input data!')
print("\nAvailable forcing configurations:")
for i, envinput in enumerate(input_l):
    print(i, envinput)

# --- Read and subset tracker data ---
ib = args.argib
with xr.open_dataset(argobs) as ds:
    #obs = ds.where(ds.seed_idx, drop=True).sel(iceberg=ib)  
    obs = ds.sel(iceberg=ib) 
    obs = obs.isel(time=(obs.seed_idx==1))

# --- Simulation definitions ---
n = 1 if mainrun==True else 11 #number of icebergs released on every initialisation

sim_freq = str(obs.seed_freq.values)
if sim_freq[-1]=='D': ib_duration = float(sim_freq[:-1])#in days, How long every iceberg is simulated after its individual initialisation (iceberg age)
else: 
    print('Provide ib_duration in days by providing the simulation frequncy in days, e.g. 3D')


# --- Random or linear variation of seeding and settings ---
# rng = np.random.default_rng(42)  # "seed" random drawing so it is the same for every simulation
# randspace = rng.random(n)
#randdim= np.random.rand(n) * 0.1 + 0.955 #for 10% variation
linspace = np.linspace(0,1,n) #linearly distributed
logspace = np.geomspace(0.1, 10.0, n) #uinformely distributed in logarithmic space


# --- Initial iceberg conditions ---
#---Iceberg size---
obslength = obs.length.values if not np.isnan(obs.length.values) else 100
randlength = obslength * logspace
if np.any(randlength>10000): 
    print('Iceberg too large, correct size.')
    randlength = np.geomspace(0.1*obslength, 10000, n) #correction for too large icebergs
randcoefwa = linspace*1.25+0.25
randcoefwi = linspace*1+0.5
if mainrun==True: 
    iceberg = {'length': [obslength,], 
           'water_form_drag_coef': [0.25,], 'wind_form_drag_coef': [0.8,],
           'radius':1}
else:
    iceberg = {'length': randlength, 
           'water_form_drag_coef': randcoefwa, 'wind_form_drag_coef': randcoefwi,
           'radius':argradius}
#---Size correction---
iceberg = calc_iceberg_size(iceberg) #this function adds missing iceberg sizes
#---Add draft maximum---
#iceberg['draft'] = np.where(iceberg['draft']<100, iceberg['draft'], 100)
#---Add original size---
if mainrun==True: idx0=0
else:
    try: idx0 = np.where(iceberg['length']==obslength)[0][0]#identity of  "member" that should contain observed size for every time-position-intitialisation, here due to the log spacing
    except: 
        idx0 = np.abs(iceberg['length'] - obslength).argmin() #if not available, find nearest and replace with original value
        iceberg['length'][idx0] = obslength
if not np.isnan(obs.width.values): iceberg['width'][idx0] = obs.width.values  #correct for meassured width
if not np.isnan(obs.draft.values): iceberg['draft'][idx0] = obs.draft.values  #correct for meassured width
print(iceberg)

if idx_l==[]: idx_l = [np.arange(obs.time.size),] #define specific indeces to be simulated, here full seed_idx selected

# --- Runs simulations ---
for envinput in input_l: #Loops through the ocean and wind input
    for idx in idx_l:#loops through ranges of seeding rounds
        #---Trajectory information---
        lons = obs.lon[idx].values
        lats = obs.lat[idx].values
        times = pd.to_datetime(obs.time[idx].values).to_pydatetime().tolist()
        print(f"\nRunning with inputs: {envinput} for idx {idx}")
        #---Initialisation---
        o=OpenBerg(loglevel=10,logfile='./openberg_july2026/results/out_%s_%s%s%s%s.log'%(ib,'_'.join(envinput),'_idx%s-%s'%(idx[0],idx[-1]) if idxargs!=[] else '','_mainrun' if mainrun==True else '','_'+argname if argname!='' else ''))
        #---Model configuration---
        o.set_config('drift:max_age_seconds', ib_duration*3600*24) #Terminates simulations  ib_duration seconds after their individual initialisation
        o.set_config('drift:vertical_profile',argdrift['vertical_profile'] if 'vertical_profile' in argdrift else False)
        o.set_config('drift:stokes_drift',argdrift['stokes_drift'] if 'stokes_drift' in argdrift else False)
        o.set_config('drift:wave_rad',argdrift['wave_rad'] if 'wave_rad' in argdrift else False)
        if openbergvers=='lia':
            o.set_config('drift:wind_drag',argdrift['wind_drag'] if 'wind_drag' in argdrift else True)
            o.set_config('drift:sea_ice_drag',argdrift['sea_ice_drag'] if 'sea_ice_drag' in argdrift else True)
        # o.set_config('general:seafloor_action','previous')
        o.set_config('general:use_auto_landmask', False)
        #---Readers
        for envin in envinput:
            dataset_id = env_dict[envin]
            print(f"Loading dataset: {dataset_id}")
            try:
                if envin=='gebco':
                    mapping_dict = {}
                    mapping_dict['standard_name_mapping']={'sea_floor_depth_below_sea_level':'sea_floor_depth_below_sea_level',
                             'land_binary_mask':'land_binary_mask'}
                    with xr.open_mfdataset(dataset_id) as ds_env:
                        ds_env['sea_floor_depth_below_sea_level'] = (('lat','lon'),np.where(-ds_env.elevation.data>0,-ds_env.elevation.data,1))
                        ds_env.sea_floor_depth_below_sea_level.attrs['standard_name']='sea_floor_depth_below_sea_level'
                        ds_env['land_binary_mask'] = (('lat','lon'),np.where(-ds_env.elevation.data>0,0,1))
                    reader_env = Reader(ds_env,name=envin,**mapping_dict)
                    o.add_reader(reader_env)
            #     # if 'vars' in envin: #load only custom variables of dataset, does not work
            #     #     ds_env=read_cmems_custom_variables(dataset_id['id'],dataset_id['variables'])
            #     #     ds_env = ds_env.chunk({"time": 1})
            #     #     reader_env = Reader(ds_env,name=envin)
            #     #     o.add_reader(reader_env) 
                elif isinstance(dataset_id, str) and dataset_id.endswith('.nc'): #local files, e.g. era5
                    mapping_dict = {}
                    ds_env = xr.open_mfdataset(dataset_id)
                    if 'era5' in dataset_id:
                        ds_env = ds_env.chunk({"valid_time": 1})
                        mapping_dict['standard_name_mapping']={'u10': 'x_wind','v10': 'y_wind'}
                    if 'carra' in dataset_id: 
                        ds_env['longitude'] = ds_env['longitude'] - 360
                        mapping_dict['standard_name_mapping']={'u10': 'x_wind','v10': 'y_wind'}
                    if 'ensemble' not in dataset_id: 
                        try: ds_env = ds_env.drop_vars(['number','expver']) #if not ensemble
                        except: continue
                    mappping_dict['name'] = envin
                    reader_env = Reader(ds_env,**mapping_dict)
                    o.add_reader(reader_env)
                elif isinstance(dataset_id, list) and 'ensemble' in envin: #list of urls or files, eg. for topaz4 ensemble
                    ds_env = xr.open_mfdataset(dataset_id,
                                concat_dim=xr.DataArray(members, dims='member', name='member',
                                attrs={'standard_name': 'realization'}),
                                combine='nested', data_vars='all', coords='all', chunks={'time': 1}) #Solution from KF!
                    reader_env = Reader(ds_env)
                    o.add_reader(reader_env)
                else: o.add_readers_from_list([dataset_id]) 
            except Exception as e:
                print(f"❌ Failed to load {dataset_id}: {e}")
    
        #---Seed icebergs---
        for lon, lat, time in zip(lons, lats, times): #Loops through initialisations of time-positions
            o.seed_elements(
                lon=lon,
                lat=lat,
                time=time,
                number=n,
                **iceberg)
        #---Run---
        # full_duration = timedelta(days=int(idx.size*ib_duration)) #old
        full_duration = (times[-1]-times[0])+timedelta(days=ib_duration) #new
        oi = o.run(duration=full_duration, 
                   outfile='./openberg_july2026/results/%s_%s%s%s%s.nc'%(ib,'_'.join(envinput),'_idx%s-%s'%(idx[0],idx[-1]) if idxargs!=[] else '','_mainrun' if mainrun==True else '', '_'+argname if argname!='' else ''))
        #---Plot map---
        # o.plot(fast=True,filename='./openberg_july2026/results/%s_map_%s%s.png'%(ib,'_'.join(envinput),'_'+argname if argname!='' else ''))
        # --- collect left over data ---
        for _ in range(2):
            gc.collect()
        
# print(oi)
# print('\a')


# Regularely do in terminal:
# - processes: ps aux | grep python
# - kill kernels (too many open kernels are a problem): pkill -f ipykernel
# - or check kernels: ps aux | grep ipykernel
# - and kill individual ones: kill -9 2260
# - but then they will restart automatically, instead use taskline-Kernels-Shut down all Kernels! Works only 1 kernel left