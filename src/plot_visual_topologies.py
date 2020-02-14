import argparse

import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

# Fixing random state for reproducibility
seed = 772723
# seed = 5842005
np.random.seed(seed)

class TopData:
    def __init__(self):
        self.data = None
        self.metadata = None
        self.color = None
        self.marker = None
        self.size = 150

def distance(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.linalg.norm(a-b)

def calculate_base_station_locations(avg_value, x, y):
    ''' Normal distribution of base stations based on avg_value 
        with 500 meter distance between BS.
    '''
    avg_number_of_base_stations = x * y * avg_value
    number_of_base_stations = int(max(avg_number_of_base_stations, 
                                  np.random.normal(avg_number_of_base_stations)))

    x_data = []
    y_data = []
    for base_station in range(number_of_base_stations):
        # Keep at least 500m distance between BS's
        distances_ok = False
        while not distances_ok:
            x, y = 3 * np.random.rand(1, 2)[0]
            if not x_data:
                break
            for x2, y2 in zip(x_data, y_data): 
                if distance((x2, y2), (x, y)) < 0.5:
                    distances_ok = False
                    break
                distances_ok = True
                
        x_data.append(x)
        y_data.append(y)
    
    BaseStationData = TopData()
    BaseStationData.data = (x_data, y_data)
    BaseStationData.color = 'red'
    BaseStationData.marker = '^'

    return BaseStationData

def calculate_uav_locations_by_bs_locations():
    pass

if __name__ == "__main__":
    sns.set()
    sns.set_style('whitegrid')
    BaseStations = calculate_base_station_locations(0.8386, 5, 5)
    x, y = BaseStations.data
    plt.scatter(x, y, color=BaseStations.color, 
                      marker=BaseStations.marker, s=BaseStations.size)
    plt.xlabel('km')
    plt.ylabel('km')
    plt.title(f'Normal Distributed Macro Base Station Locations\nrandom seed: {seed}')
    plt.show()