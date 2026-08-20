from src.utils import *

legenddict_full = {       
                  'WINDGLOPHYRE':{'col':'lightcoral','alpha':1,'zo':10},
                  'WINDGLOPHYNRT':{'col':'lightcoral','alpha':1,'zo':10},
                  'ERA5':{'col':'firebrick','alpha':1,'zo':10},
                  'ICEBERG':{'col':'k','alpha':1,'zo':60},
                'GLORYS':{'col':'darkolivegreen','alpha':1,'zo':20},
                'GLOPHYANFCH':{'col':'darkseagreen','alpha':1,'zo':21},
                'GLOPHYANFCD':{'col':'darkseagreen','alpha':1,'zo':21},
              'TOPAZ4':{'col':'darkslateblue','alpha':1,'zo':22},
              'TOPAZ5':{'col':'cornflowerblue','alpha':1,'zo':23},
              'TOPAZ6':{'col':'turquoise','alpha':1,'zo':24},
              'WAVERYS':{'col':'deeppink','alpha':1,'zo':30},
              'MFWAM':{'col':'deeppink','alpha':0.7,'zo':31},
              'ARCMFCWAM':{'col':'deeppink','alpha':0.4,'zo':32},
                'NEXTSIMRE':{'col':'plum','alpha':1,'zo':40},
                'NEXTSIMANFC':{'col':'plum','alpha':1,'zo':40},
                'SATSI':{'col':'purple','alpha':1,'zo':41},
                'mainrun':{'col':'w','alpha':1,'lsty':'--','zo':50},

             }

dict_analysis_period = {
    'iceberg2017b':{
        0:slice('2017-10-24','2018-03-06'),
        1:slice('2018-03-07','2018-08-25'),
        'seaice':slice('2017-10-24','2018-06-01'),
        'noseaice':slice('2018-06-01','2018-08-25'),    
        'full':slice('2017-10-24','2018-08-25')},    
    'iceberg2018b':{
        'full':slice('2018-12-11', '2019-06-18'),    
        0:slice('2018-12-11','2019-03-20' ),
        1:slice('2019-03-21','2019-06-18'),
        'seaice':slice('2018-12-11','2019-05-29'),
        'noseaice':slice('2019-05-29','2019-06-18'),
        'wave':slice('2019-04-30','2019-06-18')
        },
    'iceberg2026e':    {
        'full': slice('2026-05-28','2026-08-20'),
        1:slice('2026-07-03','2026-08-20'),
    }
    }
dict_traj = {#only added when restrictions are in place
    # 'iceberg2017b':{'iceberg2017b_gebco_topaz4_windglophyre':np.arange(187)}#187
}

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