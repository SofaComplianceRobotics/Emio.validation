import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable


def loadPositions(filename):

    targets, simulations, camera, polhemus = [], [], [], []
    with open(filename, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        for l, row in enumerate(csvreader):
            if l > 8:
                for i, positions in enumerate([targets, simulations, camera, polhemus]):
                    positions.append(np.fromstring(row[i][1:-1], dtype=float, sep=' '))
    return np.array(targets), np.array(simulations), np.array(camera), np.array(polhemus)


def getMeanError(positions1, positions2):
    return np.mean([np.linalg.norm(p) for p in positions1 - positions2])


def getErrorStandardDeviation(positions1, positions2):
    return np.std([np.linalg.norm(p) for p in positions1 - positions2])


def plotPointClouds(clouds):
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    for cloud in clouds:
        plotPointCloud(ax, cloud)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()


def plotPointCloud(ax, cloud):
    ax.scatter(cloud[:,0], cloud[:,1], cloud[:,2])


def plotPointCloudInAxis(ax, cloud, target, label):
    """Plot a single point cloud in an existing axis with error colors and colorbar."""
    # Calculate errors
    errors = np.array([np.linalg.norm(p) for p in cloud - target])
    
    # Calculate statistics
    mean_error = np.mean(errors)
    std_error = np.std(errors)
    
    # Plot with color gradient
    cmap = plt.cm.RdYlGn_r  # Red (high error) to Green (low error)
    norm = Normalize(vmin=np.min(errors), vmax=np.max(errors))
    colors = cmap(norm(errors))
    
    scatter = ax.scatter(cloud[:, 0], cloud[:, 2], cloud[:, 1], c=colors, s=20)
    ax.set_xlabel('X')
    ax.set_ylabel('Z')
    ax.set_zlabel('Y')
    ax.set_title(label)
    
    # Add colorbar for this subplot
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, pad=0.1, shrink=0.8)
    cbar.set_label('Error')
    
    # Add text with mean and std
    textstr = f'Mean: {mean_error:.4f}\nStd: {std_error:.4f}'
    ax.text2D(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=9,
              verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    return errors


def plotPointCloud(ax, cloud):
    ax.scatter(cloud[:,0], cloud[:,1], cloud[:,2])


def main():
    # Create a single figure with 2x3 subplots
    fig = plt.figure(figsize=(15, 10))
    subplot_index = 1

    # Plot Simulation data for different models
    for model in ["tetra", "beam", "cosserat"]:
        targets, simulations, _, _ = loadPositions("data/results/blueleg_"+model+"_polhemus_sphere.csv")
        ax = fig.add_subplot(3, 3, subplot_index, projection="3d")
        plotPointCloudInAxis(ax, simulations, targets, f"Simulation ({model})")
        subplot_index += 1
    
    # Plot Polhemus data for different models
    for model in ["tetra", "beam", "cosserat"]:
        target, _, _, polhemus = loadPositions("data/results/blueleg_"+model+"_polhemus_sphere.csv")
        ax = fig.add_subplot(3, 3, subplot_index, projection="3d")
        plotPointCloudInAxis(ax, polhemus, targets, f"Polhemus ({model})")
        subplot_index += 1

    # Process Camera data for tetra model
    target, _, camera, _ = loadPositions("data/results/blueleg_tetra_camera_sphere.csv")
    ax = fig.add_subplot(3, 3, subplot_index, projection="3d")
    plotPointCloudInAxis(ax, camera, target, "Camera (tetra)")
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
   main()