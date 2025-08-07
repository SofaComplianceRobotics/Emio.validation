import csv
import numpy as np
import matplotlib.pyplot as plt


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
    plt.show()


def plotPointCloud(ax, cloud):
    ax.scatter(cloud[:,0], cloud[:,1], cloud[:,2])


def main():
    targets, simulations, camera, polhemus = loadPositions("data/results/blueleg_tetra_sphere.csv")

    plotPointClouds(clouds=[targets, simulations])
    print("[Target/Simulation] mean error:", getMeanError(targets, simulations))
    print("[Target/Simulation] std:", getErrorStandardDeviation(targets, simulations))

    plotPointClouds(clouds=[targets, camera])
    print("[Target/Camera] mean error:", getMeanError(targets, camera))
    print("[Target/Camera] std:", getErrorStandardDeviation(targets, camera))


if __name__ == "__main__":
   main()