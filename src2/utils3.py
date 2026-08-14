from src.utils import *

legenddict_full = {       
                  'WINDGLOPHYRE':{'col':'lightcoral','alpha':1},
              'WINDGLOPHYNRT':{'col':'lightcoral','alpha':1},
              'ERA5':{'col':'firebrick','alpha':1},
              'ICEBERG':{'col':'k','alpha':1},
            'GLORYS':{'col':'darkolivegreen','alpha':1},
            'GLOPHYANFCH':{'col':'darkseagreen','alpha':1},
            'GLOPHYANFCD':{'col':'darkseagreen','alpha':1},
              'TOPAZ4':{'col':'darkslateblue','alpha':1},
              'TOPAZ5':{'col':'cornflowerblue','alpha':1},
              'TOPAZ6+5':{'col':'turquoise','alpha':1},
              'WAVERYS (alpha=1)':{'col':'deeppink','alpha':1},
              'MFWAM (alpha=0.7)':{'col':'deeppink','alpha':0.7},
              'ARCMFCWAM (alpha=0.4)':{'col':'deeppink','alpha':0.4},
                'NEXTSIMRE':{'col':'plum','alpha':1},
                'NEXTSIMANFC':{'col':'plum','alpha':1},
                'SATSI':{'col':'purple','alpha':1},

             }

dict_analysis_period = {
    'iceberg2017b':{
        0:slice('2017-10-24','2018-03-06'),
        1:slice('2018-03-07','2018-08-25'),
        'seaice':slice('2017-10-24','2018-06-01'),
        'noseaice':slice('2018-06-01','2018-08-25'),    
    }
    }
dict_traj = {#only added when restrictions are in place
    # 'iceberg2017b':{'iceberg2017b_gebco_topaz4_windglophyre':np.arange(187)}#187
}

def polarplot_m(sim_in,obs_in,legenddict,RLIM=10,
                save=False, title=False,
               ):
    import pyproj
    from scipy.stats import circmean
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    geod = pyproj.Geod(ellps="WGS84")

    url_letters,name_letters,note_letters, fileending_letter=10,14,0,3
    # cmap = plt.get_cmap('tab20')  # or 'viridis', 'plasma', etc.
    # col = cmap(np.linspace(0, 1, 20))[::2]#20 colors
    # url_letters, name_letters,note_letters, fileending_letters = 10,14,0,3
    means_save = {}
    spread_save = {}
    
    
    # observation = ref
    azimuth_alpha, a2, distance0 = geod.inv(
        obs_in.lon[:-1],obs_in.lat[:-1],obs_in.lon[1:],obs_in.lat[1:])
    dt = np.diff(obs_in.time) / np.timedelta64(1, "s")  #individual timesteps between the points
    # vel0 = distance0 / dt #distance/seconds
    # vel0
    
    # simulation results of all together -> density
    azimuth_betha, a2, distance1 = geod.inv(
        sim_in.lon[:,:,:-1],sim_in.lat[:,:,:-1],sim_in.lon[:,:,1:],sim_in.lat[:,:,1:])
    # dt = np.diff(sim_in.time) / np.timedelta64(1, "s") #individual timesteps between the points
    # vel1 = distance1 / dt #distance/seconds
    
    # calculate the coordinates in the polar plot
    # THETA = np.array((azimuth_betha - azimuth_alpha + 360) % 360) #old
    THETA = (azimuth_betha - azimuth_alpha + 180) % 360 - 180 #all
    # R = np.where(vel0>0,vel1 / vel0,np.nan) # if vel0 > 0 else 0
    # R = np.where((R <= 3)&(R > 0.0),R,np.nan) #correction for outliers and non-drifting icebergs
    R = np.where(distance0>0,distance1 / distance0,np.nan)
    R = np.where((R <= RLIM)&(R > 0.0),R,np.nan)
    
    # #average meassures (incl outsiders)
    # r_avg_with_outsiders = np.nanmean(R)
    # theta_avg_with_outsiders = circmean(THETA[~np.isnan(THETA)])
    # print(theta_avg_with_outsiders, r_avg_with_outsiders, np.nanmax(R))
    # outsiders = (R > 3).sum() / len(R) * 100#calc insiders and gridded densities:
    # x_outsiders, y_outsiders = polar_to_cartesian(
    #     np.pi / 2 - np.radians(theta_avg_with_outsiders), r_avg_with_outsiders)
    
    #calc average of insiders (old methd)
    # x, y = polar_to_cartesian(np.pi / 2 - np.radians(THETA[R <= 3]), R[R <= 3]) #used in scatterplot
    # r_avg_insiders_all = np.mean(R[R <= 3])
    # # theta_avg_insiders_all = circmean(THETA[R <= 3], high=360, low=0)
    # theta_avg_insiders_all = circmean(THETA[R <= 3], high=180, low=-180)
    # x_insiders_all, y_insiders_all = polar_to_cartesian(
    #     np.pi / 2 - np.radians(theta_avg_insiders_all), r_avg_insiders_all)
    
    # #new vectorised method to get averag theta and r
    # r = R[R <= 3]
    # angles = np.radians(THETA[R <= 3])
    # theta_plot = np.pi/2 - angles
    # # x = r * np.cos(theta_plot) #used in scatterplot
    # # y = r * np.sin(theta_plot)
    # # x_insiders_all, y_insiders_all = np.mean(x),np.mean(y) #used for plotting average
    # # theta_avg_insiders_all = np.arctan2(np.mean(y), np.mean(x)) #used as text output
    # # r_avg_insiders_all = np.sqrt(np.mean(x)**2 + np.mean(y)**2)
    # #other new method
    # x = np.cos(theta_plot)
    # y = np.sin(theta_plot)
    # x_insiders_all, y_insiders_all = np.mean(x),np.mean(y) #used for plotting average
    # theta_avg_insiders_all = np.arctan2(np.mean(np.sin(angles)),
    #                        np.mean(np.cos(angles)))
    
    # --- compute centroid in cartesian space ---
    x, y = polar_to_cartesian(np.pi / 2 - np.radians(THETA[R <= RLIM]), R[R <= RLIM]) #used in scatterplot
    x_insiders_all = np.nanmean(x)
    y_insiders_all = np.nanmean(y)
    # --- convert centroid BACK to polar (for text output) ---
    r_avg_insiders_all = np.sqrt(x_insiders_all**2 + y_insiders_all**2)
    # r_avg_insiders_all = np.nanmean(R[R <= 3])
    theta_plot = np.arctan2(y_insiders_all, x_insiders_all)
    # convert back to your angle convention (0° = north)
    theta_avg_insiders_all = np.degrees(np.pi/2 - theta_plot)
    # normalize to [-180, 180]
    theta_avg_insiders_all = (theta_avg_insiders_all + 180) % 360 - 180
    means_save['all'] = [np.round(vals,2) for vals in (r_avg_insiders_all,theta_avg_insiders_all)]
    spread_save['all'] = [np.round(vals,2) 
                          for vals in (np.nanmax(R) - np.nanmin(R),
                                       np.nanpercentile(R, 90) - np.nanpercentile(R, 10),
                                       np.nanmax(THETA) - np.nanmin(THETA),
                                       np.nanpercentile(THETA, 90) - np.nanpercentile(THETA, 10))] #range as in max-min and IQR range (from 90 to 10%)
    
    #density grid
    grid_size = 100
    percentages = [0.9, 0.75, 0.5, 0.25, 0.1, 0]
    points_insiders = np.vstack((x, y)).T
    X, Y, density_grid = create_density_grid(points_insiders, grid_size, c=0.5)
    levels = find_contour_levels(density_grid, percentages)
    
    fig, ax = plt.subplots(figsize=(6, 6))
    contourf = ax.contourf(
        X,
        Y,
        density_grid,
        levels=levels,
        cmap="viridis",
        alpha=0.9,
    )
    contour = ax.contour(
        X,
        Y,
        density_grid,
        levels=levels,
        colors="k",
        linewidths=(0.5,),
    )
    clabels = ax.clabel(
        contour,
        inline=True,
        fontsize=12,
        fmt={level: f"{int(p*100)}%" for level, p in zip(levels, percentages)},
    )
    ## Customize clabels
    for txt in clabels:
        txt.set_bbox(
            dict(facecolor="white", edgecolor=txt.get_color(), boxstyle="round,pad=0.2")
        )
        txt.set_color("black")
    
    # ax.scatter(
    #     x, y, alpha=0.5, marker="v", color='w', edgecolor="k", label="6-hourly Data points \nof simulations using input from"
    # )
    
    
    #simulation reuslts per run seperately
    for runn,run in enumerate(list(sim_in.run.values)):
        # print(runn,run.run.values)
        # inputdata = str(run.run.values)[url_letters:-(note_letters+fileending_letters)]
        sub_run = sim_in.sel(run=run)
        inputtraj = np.intersect1d(sub_run.trajectory.values,legenddict[run]['traj'])
        sub_run = sub_run.sel(trajectory=inputtraj)
        col_run = legenddict[run]['col']
    
        print(run,inputtraj[0],inputtraj[-1],sub_run.trajectory.values[0],sub_run.trajectory.values[-1],col_run)
        
    
        # simulation
        azimuth_betha, a2, distance1 = geod.inv(
            sub_run.lon[:,:-1],sub_run.lat[:,:-1],sub_run.lon[:,1:],sub_run.lat[:,1:])
        # dt = np.diff(sub_run.time) / np.timedelta64(1, "s") #individual timesteps between the points
        # vel1 = distance1 / dt #distance/seconds
        
        # calculate the coordinates in the polar plot
        # THETA = np.array((azimuth_betha - azimuth_alpha + 360) % 360) #indv
        THETA = (azimuth_betha - azimuth_alpha + 180) % 360 - 180 #all
        # R = np.where(vel0>0,vel1 / vel0,np.nan) # if vel0 > 0 else 0
        # R = np.where((R <= 3)&(R > 0.0),R,np.nan) #correction for outliers and non-drifting icebergs
        R = np.where(distance0>0,distance1 / distance0,np.nan) # if vel0 > 0 else 0
        R = np.where((R <= RLIM)&(R > 0.0),R,np.nan) #correction for outliers and non-drifting icebergs
        
        # #average meassures (incl outisders):
        # r_avg_with_outsiders = np.nanmean(R)
        # theta_avg_with_outsiders = circmean(THETA[~np.isnan(THETA)])
        # print(theta_avg_with_outsiders, r_avg_with_outsiders, np.nanmax(R))
        # outsiders = (R > 3).sum() / len(R) * 100
        # x_outsiders, y_outsiders = polar_to_cartesian(
        # np.pi / 2 - np.radians(theta_avg_with_outsiders), r_avg_with_outsiders)
        
        # # insiders and means (Old)
        # x, y = polar_to_cartesian(np.pi / 2 - np.radians(THETA[R <= 3]), R[R <= 3])
        # r_avg_insiders = np.mean(R[R <= 3])
        # theta_avg_insiders = circmean(THETA[R <= 3], high=360, low=0)
        # x_insiders, y_insiders = polar_to_cartesian(
        #     np.pi / 2 - np.radians(theta_avg_insiders), r_avg_insiders)
        # means_save[run.item()] = [r_avg_insiders,theta_avg_insiders]
        # insiders and means (new)
        x, y = polar_to_cartesian(np.pi / 2 - np.radians(THETA[R <= RLIM]), R[R <= RLIM]) #used in scatterplot
        x_insiders = np.mean(x)
        y_insiders = np.mean(y)
        r_avg_insiders = np.sqrt(x_insiders**2 + y_insiders**2)     # r_avg_insiders_all = np.mean(R[R <= 3])
        theta_plot = np.arctan2(y_insiders, x_insiders)
        theta_avg_insiders = np.degrees(np.pi/2 - theta_plot)
        theta_avg_insiders = (theta_avg_insiders + 180) % 360 - 180
        means_save[run.item()] = [np.round(vals,2) for vals in (r_avg_insiders,theta_avg_insiders)]
        spread_save[run.item()] = [np.round(vals,2)
                                   for vals in (np.nanmax(R) - np.nanmin(R),
                                                np.nanpercentile(R, 90) - np.nanpercentile(R, 10),
                                                np.nanmax(THETA) - np.nanmin(THETA),
                                                np.nanpercentile(THETA, 90) - np.nanpercentile(THETA, 10))] #range as in max-min and IQR range (from 90 to 10%)
    
        ax.scatter(
            x, y, alpha=legenddict[run]['alpha'], marker="v", color=col_run, edgecolor="k", 
            label=f"{run.item()[19:-3]} \nmean (R={np.round(r_avg_insiders,1)},theta={np.round(theta_avg_insiders,1) if theta_avg_insiders<180 else np.round(theta_avg_insiders-360,1)}°)"
        )
        ax.scatter(
            x_insiders,
            y_insiders,
            marker="o",
            s=50,
            c=col_run,
            alpha=legenddict[run]['alpha'],edgecolor='w',
            # label=f"Mean (R={np.round(r_avg_insiders,1)},theta={np.round(theta_avg_insiders,1) if theta_avg_insiders<180 else np.round(theta_avg_insiders-360,1)}°)",
            zorder=30,
        )
    
        ax.plot(
            np.linspace(-3, 3, 100),
            np.tan(np.pi / 2 - np.deg2rad(theta_avg_insiders)) * np.linspace(-3, 3, 100),
            color=col_run,alpha=legenddict[run]['alpha'],
            linestyle="--",
            # label=f"average deviation : {np.round(theta_avg_insiders,1) if theta_avg_insiders<180 else np.round(theta_avg_insiders-360,1)}°",
        )
        # print(inputdata,f"Mean (R={np.round(r_avg_insiders,1)},theta={np.round(theta_avg_insiders,1) if theta_avg_insiders<180 else np.round(theta_avg_insiders-360,1)}°)")
    
    #all simulations again
    if sim_in.run.size>1:
        ax.scatter(
            x_insiders_all,
            y_insiders_all,
            marker="o",
            s=50,
            facecolor='w',edgecolor='k',
            # label=f"mean without ouliers (R={np.round(r_avg_insiders,1)},theta={np.round(theta_avg_insiders,1) if theta_avg_insiders<180 else np.round(theta_avg_insiders-360,1)}°)",
            label=f"Mean error distance (R={np.round(r_avg_insiders_all,1)})",
            zorder=30,
        )
        # print('all',f"Mean error velocity (R={np.round(r_avg_insiders_all,1)}) & direction (theta={np.round(theta_avg_insiders_all,1) if theta_avg_insiders_all<180 else np.round(theta_avg_insiders_all-360,1)}°) (all input)")
        ax.plot(
            np.linspace(-3, 3, 100),
            np.tan(np.pi / 2 - np.deg2rad(theta_avg_insiders_all)) * np.linspace(-3, 3, 100),
            color="k",
            linestyle="--",
            label=f"Mean error direction (theta={np.round(theta_avg_insiders_all,1) if theta_avg_insiders_all<180 else np.round(theta_avg_insiders_all-360,1)}°)" #f"average deviation : {np.round(theta_avg_insiders,1) if theta_avg_insiders<180 else np.round(theta_avg_insiders-360,1)}°",
        )
        
    #other plots things
    ax.scatter(0, 1, marker="x", s=200, c="r", label="Target", zorder=20)
    ax.hlines(0, xmin=-5, xmax=5, linestyle=":", color="r", alpha=0.5)
    ax.set_xlim([-2.5, 2.5])
    ax.set_ylim([-2.5, 2.5])
    # ax.set_xlim([-3.5, 3.5])
    # ax.set_ylim([-3.5, 3.5])
    circle1 = plt.Circle(
        (0, 0), 1, edgecolor="r", linestyle="--", fc=None, fill=False, zorder=30
    )
    ax.add_patch(circle1)
    plt.gca().set_aspect(
        "equal", adjustable="box"
    )  # Set aspect ratio to make it look polar
    if title!=False: ax.set_title(title)
    #legend
    # fig.legend(fontsize=12)
    #6h data points
    legend_elements = [Line2D([0], [0],linestyle='-', color='w', marker='v', markerfacecolor='w',markeredgecolor='k', lw=1,
                              label=f"6-hourly data points of simulations using input from "),]
    #runs
    # legend_elements = legend_elements+[Line2D([0], [0],linestyle='-', color='w', marker='v', markerfacecolor=col[runn],markeredgecolor='k', lw=1,
    #                           label=f"{run.item()[19:-3].replace('_',', ').title()} mean error (R={np.round(means_save[run.item()][0],1)},theta={np.round(means_save[run.item()][1],1) if means_save[run.item()][1]<180 else np.round(means_save[run.item()][1]-360,1)}°)") for runn,run in enumerate(sim_in.run)]
                            #Line2D([0], [0],linestyle='-', color=legenddict[el]['col'],alpha=legenddict[el]['alpha'], lw=1, label=el) for el in legenddict]
    legend_elements = legend_elements+[Line2D([0], [0],linestyle='-', color='w', markerfacecolor=legenddict[run]['col'],
                                              alpha=legenddict[run]['alpha'], marker='v',markeredgecolor='k', lw=1,
                                       label=f"{legenddict[run]['kw']} ($R$={np.round(means_save[run][0],2)},$theta$={np.round(means_save[run][1],1) 
                                       if means_save[run][1]<180 else np.round(means_save[run][1]-360,1)}°)") 
                                    for run in list(sim_in.run.values)]
    #mean error all
    legend_elements = legend_elements+[                      
                      Line2D([0], [0],linestyle='--', color='k',marker='o',markerfacecolor='w' if sim_in.run.size>1 else col_run,
                             markeredgecolor='k', lw=1,
                             label=f"Mean error distance ($R$={np.round(r_avg_insiders_all,2)}) & \ndirection ($theta$={np.round(theta_avg_insiders_all,1) if theta_avg_insiders_all<180 else np.round(theta_avg_insiders_all-360,1)}°) (all input)")]
    #contours
    legend_elements = legend_elements+[Line2D([0], [0],linestyle='--', color='r',marker='x', lw=1,label='Target (Observation)'),
                      Patch(facecolor=plt.colormaps['viridis'](0.2), edgecolor='k',label='Confidence contours (all input)'),
                      ]
    leg = fig.legend(handles=legend_elements,fontsize=12,#,ncol=len(legend_elements0+legend_elements2), columnspacing=0.6,labelspacing=0.3,loc='center',bbox_to_anchor=bbox_dict[kw][0])
                       loc='upper center', bbox_to_anchor=(0.5,0.05))
                       # loc='center left', bbox_to_anchor=(0.9,0.5))
    
    if save!=False: plt.savefig('./results/analysis_polarplot_%s.png'%(save), bbox_inches="tight", dpi=400)
    plt.show()
    return {'mean':means_save,'spread':spread_save}

from scipy.spatial.distance import pdist

def polar_to_cartesian(theta, r):
    """Convert polar coordinates to Cartesian coordinates."""
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y

def create_density_grid(points, grid_size=100, c=0.5):
    points = points[~np.isnan(points).any(axis=1)]
    # Calculer la distance moyenne entre les points
    d_avg = calculate_average_distance(points) + 1
    # Déterminer sigma en fonction de d_avg et du paramètre c
    sigma = c * d_avg

    # Déterminer les limites de la grille
    x_min, x_max = min(points[:, 0]) - 2 * sigma, max(points[:, 0]) + 2 * sigma
    y_min, y_max = min(points[:, 1]) - 2 * sigma, max(points[:, 1]) + 2 * sigma

    # Créer une grille de coordonnées
    x = np.linspace(x_min, x_max, grid_size)
    y = np.linspace(y_min, y_max, grid_size)
    X, Y = np.meshgrid(x, y)

    # Initialiser la grille de densité
    density_grid = np.zeros((grid_size, grid_size))

    # Nombre de points
    N = len(points)

    # Appliquer la distribution gaussienne à chaque point
    for point in points:
        dx = X - point[0]
        dy = Y - point[1]
        r = np.sqrt(dx**2 + dy**2)
        density_grid += gaussian_kernel(r, sigma) / N

    return X, Y, density_grid

def calculate_average_distance(points):
    if len(points) > 1000:
        distances = pdist(points[::50])
    else:
        distances = pdist(points)
    d_avg = np.mean(distances)
    return d_avg
    
def gaussian_kernel(r, sigma):
    return np.exp(-(r**2) / (2 * sigma**2)) / (2 * np.pi * sigma**2)

def find_contour_levels(density_grid, percentages):
    sorted_density = np.sort(density_grid.ravel())[::-1]
    cumsum_density = np.cumsum(sorted_density)
    total_density = cumsum_density[-1]
    levels = [
        sorted_density[np.searchsorted(cumsum_density, p * total_density)]
        for p in percentages
    ]
    levels.sort()  # S'assurer que les niveaux sont dans l'ordre croissant
    return levels

