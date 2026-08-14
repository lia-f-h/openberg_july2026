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

