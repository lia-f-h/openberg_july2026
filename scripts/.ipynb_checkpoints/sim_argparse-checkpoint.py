# Re-simulating different icebergs along their observed trajectory

#How to run. First go to directory, then run file:
    # cd ~/work/tutorials/sources/OpenDrift/openberg_july2026
    # python3 -m openberg_july2026.scripts.sim_argparse \
    #   --argib 'iceberg2025w' \
    #   --argoc '[["gebco","glorys"]]' \
    #   --argwind '["windglophynrt"]' \
    #   --argdrift '{"wind_drag": true, "sea_ice_drag": true,  "wave_rad": false, "stokes_drift": false}' \
    #   --argname '' \
    #   --argopenberg 'lia'


# --- IMPORTS ---
from src.utils import *
from openberg_july2026.src2.utils2 import *
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
print('Arguments: ',oc_in,wind_in,argdrift)

# --- Clean up ---
for _ in range(2):
    gc.collect()

# --- Read and subset tracker data ---
ib = args.argib
with xr.open_dataset('./openberg_july2026/input/merged_obs4.nc') as ds:
    #obs = ds.where(ds.seed_idx, drop=True).sel(iceberg=ib)  
    obs = ds.sel(iceberg=ib) 
    obs = obs.isel(time=(obs.seed_idx==1))
idx = np.arange(obs.time.size) #define specific indeces to be simulated, here full seed_idx selected

# --- Dictionary of available environmental input datasets ---
env_dict = {
    # --- Ocean ---
    'topaz4': 'cmems_mod_arc_phy_my_topaz4_P1D-m',
    'topaz4-ensemble':['https://thredds.met.no/thredds/dodsC/accibergt42/topaz4_be_mem0%s.ncml'%membnr for membnr in [('0'+str(memb)) 
                        if memb<10 else str(memb) for memb in range(1,11)]],
                        #find under:'https://thredds.met.no/thredds/catalog/accibergt42/catalog.html',
    'topaz5': 'cmems_mod_arc_phy_anfc_6km_detided_PT1H-i',
    'topaz5-ensemble': ['https://thredds.met.no/thredds/dodsC/accibergt5/topaz5_be_mem0%s.ncml'%membnr for membnr in [('0'+str(memb)) 
                        if memb<10 else str(memb) for memb in range(1,11)]],                      
                       #find under: https://thredds.met.no/thredds/catalog/accibergt5/catalog.html',
    'topaz6': 'https://thredds.met.no/thredds/dodsC/cmems/topaz6/dataset-topaz6-arc-15min-3km-be.ncml', 
    'topaz6-lowres': 'dataset-topaz6-arc-15min-3km-be',
    'glophyanfcH': 'cmems_mod_glo_phy_anfc_0.083deg_PT1H-m', #Global anfc (mercator), hourly variables
    'glophyanfcD': 'cmems_mod_glo_phy_anfc_0.083deg_P1D-m', #daily variables (sea ice)
    'glorys': 'cmems_mod_glo_phy_my_0.083deg_P1D-m',
    # --- Sea ice ---
    'nextsimanfc':'cmems_mod_arc_phy_anfc_nextsim_hm',
    'nextsimre':'cmems_mod_arc_phy_my_nextsim_P1D-m',
    # --- Wave ---
    'arcmfcwam':'dataset-wam-arctic-1hr3km-be',
    'arcmfcwam_vars':{'id':"dataset-wam-arctic-1hr3km-be",'variables':["VHM0","VMDR","VSDX","VSDY"]},
    'arcmfcwamre':'cmems_mod_arc_wav_my_3km_PT1H-i',
    'mfwam':'cmems_mod_glo_wav_anfc_0.083deg_PT3H-i',
    'waverys':'cmems_mod_glo_wav_my_0.2deg_PT3H-i',
    # --- Wind ---
    'windglophyre':'cmems_obs-wind_glo_phy_my_l4_0.125deg_PT1H', #availability; 2007-2026
    'windglophynrt':'cmems_obs-wind_glo_phy_nrt_l4_0.125deg_PT1H', #availability: 2024-2026
    'era5':'', #Download
    'carra2': '', #Download
    # --- Bathymetry---
    'gebco':'./openberg_july2026/input/gebco_2026_n85.0_s35.0_w-80.0_e0.0.nc'}

# --- Combintaions of inputs ---
if np.logical_and(wind_in!=[],oc_in!=[]): input_l = [(oc if isinstance(oc, list) else [oc]) + [wi] for wi in wind_in for oc in oc_in ] 
elif np.logical_and(wind_in==[],oc_in!=[]): input_l = [(oc if isinstance(oc, list) else [oc]) for oc in oc_in]
elif np.logical_and(wind_in!=[],oc_in==[]): input_l = [(wi if isinstance(wi, list) else [wi]) for wi in wind_in]
else: print('Provide input data!')
print("\nAvailable forcing configurations:")
for i, envinput in enumerate(input_l):
    print(i, envinput)

# --- Simulation definitions ---
n=11 #number of icebergs released on every initialisation

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
#---Trajectory information---
lons = obs.lon[idx].values
lats = obs.lat[idx].values
times = pd.to_datetime(obs.time[idx].values).to_pydatetime().tolist()
#---Iceberg size---
obslength = obs.length.values if not np.isnan(obs.length.values) else 100
randlength = obslength * logspace
if np.any(randlength>10000): 
    print('Iceberg too large, correct size.')
    randlength = np.geomspace(0.1*obslength, 10000, n) #correction for too large icebergs
randcoefwa = linspace*1.25+0.25
randcoefwi = linspace*1+0.5
iceberg = {'length': randlength, 
           'water_form_drag_coef': randcoefwa, 'wind_form_drag_coef': randcoefwi,
           'radius':1000}
#---Size correction---
iceberg = calc_iceberg_size(iceberg) #this function adds missing iceberg sizes
#---Add draft maximum---
#iceberg['draft'] = np.where(iceberg['draft']<100, iceberg['draft'], 100)
#---Add original size---
try: idx0 = np.where(iceberg['length']==obslength)[0][0]#identity of  "member" that should contain observed size for every time-position-intitialisation, here due to the log spacing
except: 
    idx0 = np.abs(iceberg['length'] - obslength).argmin() #if not available, find nearest and replace with original value
    iceberg['length'][idx0] = obslength
if not np.isnan(obs.width.values): iceberg['width'][idx0] = obs.width.values  #correct for meassured width
if not np.isnan(obs.draft.values): iceberg['draft'][idx0] = obs.width.values  #correct for meassured width
print(iceberg)

# --- Runs simulations ---
for envinput in input_l: #Loops through the ocean and wind input
    print(f"\nRunning with inputs: {envinput}")
    #---Initialisation---
    o=OpenBerg(loglevel=10,logfile='./openberg_july2026/results/out_%s_%s%s.log'%(ib,'_'.join(envinput),'_'+argname if argname!='' else ''))
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
               outfile='./openberg_july2026/results/%s_%s%s.nc'%(ib,'_'.join(envinput),'_'+argname if argname!='' else ''))
    #---Plot map---
    # o.plot(fast=True,filename='./openberg_july2026/results/%s_map_%s%s.png'%(ib,'_'.join(envinput),'_'+argname if argname!='' else ''))
    # --- collect left over data ---
    for _ in range(2):
        gc.collect()
        
print(oi)
print('\a')


# Regularely do in terminal:
# - processes: ps aux | grep python
# - kill kernels (too many open kernels are a problem): pkill -f ipykernel
# - or check kernels: ps aux | grep ipykernel
# - and kill individual ones: kill -9 2260
# - but then they will restart automatically, instead use taskline-Kernels-Shut down all Kernels! Works only 1 kernel left