# Re-simulating different icebergs along their observed trajectory

#How to run. First go to directory, then run file:
    # cd ~/work/tutorials/sources/OpenDrift/openberg_july2026
# python3 -m openberg_july2026.scripts.sim_argparse       --argib 'iceberg2018b'       --argoc '[["gebco","glorys"],["gebco","topaz4"]]'       --argwind '["windglophyre"]'       --argdrift '{"wind_drag": true, "sea_ice_drag": true,  "wave_rad": false, "stokes_drift": false, "vertical_profile": false}'       --argname ''       --argopenberg 'lia' --argidx '[[0, 0], [1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8], [9, 9], [10, 10]]' --argmainrun 1
# python3 -m openberg_july2026.scripts.sim_argparse       --argib 'iceberg2026e'       --argoc '[["gebco","topaz5"]]'       --argwind '["windglophynrt"]'  --argobs './openberg_july2026/input/merged_obs_iceberg2026e_1D.nc' --argradius 10000 --argidx '[[30,36]]' --argiceberg '{"n":20,"length":50,"maxdraft":150}' --argname 'debris_radius10000_n20_l50_maxdraft' 
# python3 -m openberg_july2026.scripts.sim_argparse       --argib 'iceberg2026e'       --argoc '[["gebco","topaz5"]]'       --argwind '["windglophynrt"]'  --argobs './openberg_july2026/input/merged_obs_iceberg2026e_1D.nc' --argradius 10000 --argidx '[[29,29]]' --argiceberg '{"n":20,"length":50,"maxdraft":150}' --argleadtime 55 --argname 'debris_radius10000_n20_l50_maxdraft' 
# python3 -m openberg_july2026.scripts.sim_argparse       --argib 'iceberg2026e'       --argoc '[["gebco","topaz5"]]'       --argwind '["windglophynrt"]'  --argobs './openberg_july2026/input/merged_obs_iceberg2026e_1D.nc' --argmainrun 1 --argidx '[[29,29]]' --argiceberg '{"n":1,"length":5000, "width":3000, "draft": 100}' --argleadtime 55 --argtimestep 60*15 --argname 'longrun_1Jul_timestep15min'

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
parser.add_argument("--argobs", type=str, default='./openberg_july2026/input/merged_obs10.nc', help='File with iceberg observations')
parser.add_argument("--argiceberg", type=json.loads, default={}, help='JSON dict on initial iceberg charcateristics, e.g. \'{"n":10,"length": 100, "width":100, "draft":10}\'')

parser.add_argument("--argoc", type=json.loads, required=True, help='JSON list of lists, e.g. \'["topaz5", ["topaz6","topaz5"]]\'')
parser.add_argument("--argwind", type=json.loads, default='["windglophynrt"]', help='JSON list, e.g. \'["windglophynrt"]\'')
parser.add_argument("--argdrift", type=json.loads, default={"wind_drag": True, "sea_ice_drag": True, "wave_rad": False, "stokes_drift": False}, 
                    help='JSON dict, e.g. \'{"wind_drag": true}\'')

parser.add_argument("--argopenberg", type=str, help='Which openberg.py to use', default='lia')
parser.add_argument("--argmainrun", type=int, default=0, help='0= n icebergs with varied coef, size and radius, 1= no variations')
parser.add_argument("--argradius", type=int, default=3125, help='Seeding radius in m')
parser.add_argument("--argleadtime", type=int, default=None, help='Lead time in D')
# parser.add_argument("--argidx",type=int, nargs=2, metavar=("INT1", "INT2"), default=[0, 999],
#                     help="Range of seeding time-positions,e .g. 0,1 for seeding rounds 0 to (incl.) 1")
parser.add_argument("--argidx", type=json.loads, required=False, default=[],
                    help="LIst of range of seeding time-positions,e .g. [[0,1] for seeding rounds 0 to (incl.) 1")
parser.add_argument("--argtimestep", type=int, default=3600, help='Simulation time steps in seconds')

parser.add_argument("--argname", type=str, help='str to be added to filename (optional)', default='')

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
leadtime = args.argleadtime
argtimestep = args.argtimestep
argiceberg = args.argiceberg
print('Arguments: ',argobs,mainrun,argiceberg,argradius,leadtime,argtimestep,idx_l,oc_in,wind_in,argdrift)

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
    obs = ds.sel(iceberg=ib).copy() 
    obs = obs.isel(time=(obs.seed_idx==1))

# --- Simulation definitions ---
#number of icebergs released on every initialisation
if mainrun==True: n=1
elif 'n' in argiceberg: n = argiceberg['n']
else: n=11

sim_freq = str(obs.seed_freq.values)
if leadtime!=None: ib_duration = float(leadtime)
elif sim_freq[-1]=='D': ib_duration = float(sim_freq[:-1])#in days, How long every iceberg is simulated after its individual initialisation (iceberg age)
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
    #Obs size or size from argument
if 'length' in argiceberg: obslength=argiceberg['length']
elif np.isnan(obs.length.values)==False: obslength = obs.length.values
else: obslength = 100
obswidth =  argiceberg['width'] if 'width' in argiceberg else obs.width.values
obsdraft =  argiceberg['draft'] if 'draft' in argiceberg else obs.draft.values
    #variability
randlength = obslength * logspace
if np.any(randlength>10000): 
    print('Iceberg too large, correct size.')
    randlength = np.geomspace(0.1*obslength, 10000, n) #correction for too large icebergs
randcoefwa = linspace*1.25+0.25
randcoefwi = linspace*1+0.5
if mainrun==True: #mainrun means no variations
    iceberg = {'length': [obslength,], 
           'water_form_drag_coef': [0.25,], 'wind_form_drag_coef': [0.8,],
           'radius':1}
else: #variations 
    iceberg = {'length': randlength, 
           'water_form_drag_coef': randcoefwa, 'wind_form_drag_coef': randcoefwi,
           'radius':argradius}

#---Size correction---
iceberg = calc_iceberg_size(iceberg) #this function adds missing iceberg sizes
#---Add draft maximum---
if 'maxdraft' in argiceberg: 
    iceberg['draft'] = np.where(iceberg['draft']<=argiceberg['maxdraft'], iceberg['draft'], argiceberg['maxdraft'])
    print('maxdraft of %s applied'%argiceberg['maxdraft'])
#---Add original size---
if mainrun==True: idx0=0
else:
    try: idx0 = np.where(iceberg['length']==obslength)[0][0]#identity of  "member" that should contain observed size for every time-position-intitialisation, here due to the log spacing
    except: 
        idx0 = np.abs(iceberg['length'] - obslength).argmin() #if not available, find nearest and replace with original value
        iceberg['length'][idx0] = obslength
if not np.isnan(obswidth): iceberg['width'][idx0] = obswidth  #correct for meassured width
if not np.isnan(obsdraft): iceberg['draft'][idx0] = obsdraft  #correct for meassured width
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
        o=OpenBerg(loglevel=10,logfile='./openberg_july2026/results/out_%s_%s%s%s%s%s.log'%(ib,'_'.join(envinput),'_idx%s-%s'%(idx[0],idx[-1]) if idxargs!=[] else '','_lead%s'%leadtime if leadtime!=None else '','_mainrun' if mainrun==True else '','_'+argname if argname!='' else ''))
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
        run_dict = {'duration':full_duration, 'outfile':'./openberg_july2026/results/%s_%s%s%s%s%s.nc'%(ib,'_'.join(envinput),'_idx%s-%s'%(idx[0],idx[-1]) if idxargs!=[] else '','_lead%s'%leadtime if leadtime!=None else '','_mainrun' if mainrun==True else '', '_'+argname if argname!='' else ''),
                   }
        if argtimestep!=3600: 
            run_dict['time_step']=argtimestep
            run_dict['time_step_output']=3600
        oi = o.run(**run_dict)
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